import json
import os

import pytest

from geff_spec import GeffMetadata, RelatedObject

try:
    import tifffile

    from geff.convert import convert_ctc, ctc_tiffs_to_zarr, from_ctc_to_geff
except ImportError:
    pytest.skip("geff[ctc] not installed", allow_module_level=True)

from pathlib import Path

import numpy as np
import zarr
import zarr.storage

from geff._graph_libs._networkx import NxBackend
from geff.core_io import read_to_memory


def create_mock_data(
    tmp_path: Path,
    is_gt: bool,
    is_3d: bool = False,
    v2: bool = False,  # generates a slightly different dataset
) -> Path:
    """
    mock graph is:

    t=0      1       7
             |       |
    t=1      1       |
            / \\     |
    t=2    2   5     9
    """
    if is_3d:
        # for 3D example data, we created a different function to avoid littering this one with
        # if-statements. But please keep the mock graph structure of both in sync!
        if v2:
            raise ValueError("v2=True not implemented for 3D data")
        return _create_mock_data_3d(tmp_path, is_gt)

    mod_value = 9 if not v2 else 10

    labels = np.zeros((3, 10, 10), dtype=np.uint16)

    labels[0, 3, 3] = 1
    labels[0, 8, 8] = 7

    labels[1, 3, 4] = 1

    labels[2, 2, 3] = 5
    labels[2, 4, 5] = 2
    labels[2, 8, 9] = mod_value

    fmt = "man_track{:03d}.tif" if is_gt else "mask{:03d}.tif"

    for t in range(labels.shape[0]):
        tifffile.imwrite(
            tmp_path / fmt.format(t),
            labels[t],
            compression="LZW",
        )

    tracks_file = tmp_path / ("man_track.txt" if is_gt else "res_track.txt")
    # track_id, start, end, parent_id
    tracks_table = [[1, 0, 1, 0], [2, 2, 2, 1], [5, 2, 2, 1], [7, 0, 0, 0], [mod_value, 2, 2, 7]]

    np.savetxt(
        tracks_file,
        tracks_table,
        fmt="%d",
    )

    return tmp_path


def _create_mock_data_3d(tmp_path: Path, is_gt: bool) -> Path:
    """
    mock graph is:

    t=0      1       7
             |       |
    t=1      1       |
            / \\     |
    t=2    2   5     9
    """

    labels = np.zeros((3, 10, 10, 10), dtype=np.uint16)

    labels[0, 1, 3, 3] = 1
    labels[0, 2, 8, 8] = 7

    labels[1, 2, 3, 4] = 1

    labels[2, 3, 2, 3] = 5
    labels[2, 2, 4, 5] = 2
    labels[2, 4, 8, 9] = 9

    fmt = "man_track{:03d}.tif" if is_gt else "mask{:03d}.tif"

    for t in range(labels.shape[0]):
        tifffile.imwrite(
            tmp_path / fmt.format(t),
            labels[t],
            compression="LZW",
        )

    tracks_file = tmp_path / ("man_track.txt" if is_gt else "res_track.txt")
    # track_id, start, end, parent_id
    tracks_table = [[1, 0, 1, 0], [2, 2, 2, 1], [5, 2, 2, 1], [7, 0, 0, 0], [9, 2, 2, 7]]

    np.savetxt(
        tracks_file,
        tracks_table,
        fmt="%d",
    )

    return tmp_path


@pytest.mark.parametrize("is_gt", [True, False])
@pytest.mark.parametrize("is_3d", [True, False])
@pytest.mark.parametrize("tczyx", [True, False])
class Test_ctc_to_geff:
    def test_basic(
        self,
        tmp_path: Path,
        is_gt: bool,
        is_3d: bool,
        tczyx: bool,
    ) -> None:
        ctc_path = create_mock_data(tmp_path, is_gt, is_3d=is_3d)
        geff_path = tmp_path / "little.geff"

        from_ctc_to_geff(
            ctc_path=ctc_path,
            geff_path=geff_path,
            tczyx=tczyx,
        )

        assert geff_path.exists()

        # Check graph that was written to geff
        graph, metadata = NxBackend.read(geff_path)

        expected_nodes = {0, 1, 2, 3, 4, 5}
        expected_edges = {(0, 2), (2, 3), (2, 4), (1, 5)}

        assert set(graph.nodes()) == expected_nodes
        assert set(graph.edges()) == expected_edges

        for _, data in graph.nodes(data=True):
            for key in ["tracklet_id", "t", "y", "x"]:
                assert key in data

        # Check metadata
        assert metadata.track_node_props == {"tracklet": "tracklet_id"}
        assert metadata.related_objects is None

    def orig_test(
        self,
        tmp_path: Path,
        is_gt: bool,
        tczyx: bool,
    ):
        ctc_path = create_mock_data(tmp_path, is_gt)
        geff_path = tmp_path / "little.geff"
        segm_path = tmp_path / "segm.zarr"

        from_ctc_to_geff(
            ctc_path=ctc_path,
            geff_path=geff_path,
            segmentation_store=segm_path,
            tczyx=True,
        )

        assert geff_path.exists()

        # Check graph that was written to geff
        graph, metadata = NxBackend.read(geff_path)

        expected_nodes = {0, 1, 2, 3, 4, 5}
        expected_edges = {(0, 2), (2, 3), (2, 4), (1, 5)}

        assert set(graph.nodes()) == expected_nodes
        assert set(graph.edges()) == expected_edges

        for _, data in graph.nodes(data=True):
            for key in ["tracklet_id", "t", "y", "x"]:
                assert key in data

        # Check segmentation that was written to zarr
        expected_segm = np.stack([tifffile.imread(p) for p in sorted(ctc_path.glob("*.tif"))])

        segm = zarr.open_array(segm_path / "0", mode="r")[...]

        assert segm.shape[0] == expected_segm.shape[0]

        if tczyx:
            assert segm.ndim == 5

        segm = np.squeeze(segm)
        np.testing.assert_array_equal(segm, expected_segm)

        # Check metadata
        assert metadata.track_node_props == {"tracklet": "tracklet_id"}
        assert metadata.related_objects is not None
        assert metadata.related_objects[0] == RelatedObject(
            type="labels", node_prop="tracklet_id", path="../segm.zarr"
        )

        # Test without exporting segmentation
        geff_path = tmp_path / "noseg.geff"

        from_ctc_to_geff(
            ctc_path=ctc_path,
            geff_path=geff_path,
            tczyx=True,
        )

        assert geff_path.exists()
        graph, metadata = NxBackend.read(geff_path)
        # Check for no related objects
        assert metadata.related_objects is None

        # Writing again fails if overwrite False
        with pytest.raises(FileExistsError, match="Found an existing geff present in `geff_path`"):
            from_ctc_to_geff(
                ctc_path=ctc_path,
                geff_path=geff_path,
                segmentation_store=segm_path,
                tczyx=True,
            )

        # Writing works if overwrite True
        os.mkdir(tmp_path / "v2")
        ctc_path = create_mock_data(tmp_path / "v2", is_gt, v2=True)
        from_ctc_to_geff(
            ctc_path=ctc_path,
            geff_path=geff_path,
            segmentation_store=segm_path,
            tczyx=True,
            overwrite=True,
        )

        # Check that v2 data was written
        segm = zarr.open_array(segm_path / "0", mode="r")[...]
        assert 10 in segm and 9 not in segm
        mem_geff = read_to_memory(geff_path)
        tracklet_ids = mem_geff["node_props"]["tracklet_id"]["values"]
        assert 10 in tracklet_ids and 9 not in tracklet_ids

    def test_seg_to_path(
        self,
        tmp_path: Path,
        is_gt: bool,
        is_3d: bool,
        tczyx: bool,
    ):
        ctc_path = create_mock_data(tmp_path, is_gt, is_3d=is_3d)
        geff_path = tmp_path / "little.geff"
        segm_path = tmp_path / "segm.zarr"

        from_ctc_to_geff(
            ctc_path=ctc_path,
            geff_path=geff_path,
            segmentation_store=segm_path,
            tczyx=tczyx,
        )

        assert geff_path.exists()

        # Check graph that was written to geff
        _graph, metadata = NxBackend.read(geff_path)

        # Check segmentation that was written to zarr
        expected_segm = np.stack([tifffile.imread(p) for p in sorted(ctc_path.glob("*.tif"))])

        segm = zarr.open_array(segm_path / "0", mode="r")[...]

        assert segm.shape[0] == expected_segm.shape[0]

        if tczyx:
            assert segm.ndim == 5

        segm = np.squeeze(segm)
        np.testing.assert_array_equal(segm, expected_segm)

        # Check metadata
        assert metadata.track_node_props == {"tracklet": "tracklet_id"}
        assert metadata.related_objects is not None
        assert metadata.related_objects[0] == RelatedObject(
            type="labels", node_prop="tracklet_id", path=os.path.join("..", "segm.zarr")
        )

    def test_seg_to_store(
        self,
        tmp_path: Path,
        is_gt: bool,
        is_3d: bool,
        tczyx: bool,
    ):
        ctc_path = create_mock_data(tmp_path, is_gt)
        geff_path = tmp_path / "little.geff"
        segm_path = tmp_path / "segm.zarr"

        store = zarr.storage.LocalStore(segm_path)

        from_ctc_to_geff(
            ctc_path=ctc_path,
            geff_path=geff_path,
            segmentation_store=store,
            tczyx=tczyx,
        )

        assert geff_path.exists()

        # Check graph that was written to geff
        _graph, metadata = NxBackend.read(geff_path)

        # Check segmentation that was written to zarr
        expected_segm = np.stack([tifffile.imread(p) for p in sorted(ctc_path.glob("*.tif"))])

        segm = zarr.open_array(segm_path / "0", mode="r")[...]

        assert segm.shape[0] == expected_segm.shape[0]

        if tczyx:
            assert segm.ndim == 5

        segm = np.squeeze(segm)
        np.testing.assert_array_equal(segm, expected_segm)

        # Check metadata
        assert metadata.track_node_props == {"tracklet": "tracklet_id"}
        assert metadata.related_objects is not None
        assert metadata.related_objects[0] == RelatedObject(
            type="labels", node_prop="tracklet_id", path=os.path.join("..", "segm.zarr")
        )

    def test_seg_to_bad_store(
        self,
        tmp_path: Path,
        is_gt: bool,
        is_3d: bool,
        tczyx: bool,
    ):
        # A memory store has no local path, so it can't hold an OME-Zarr label image

        ctc_path = create_mock_data(tmp_path, is_gt, is_3d=is_3d)
        geff_path = tmp_path / "little.geff"
        store = zarr.storage.MemoryStore()

        with pytest.raises(TypeError, match="requires a path or a store backed by a local"):
            from_ctc_to_geff(
                ctc_path=ctc_path,
                geff_path=geff_path,
                segmentation_store=store,
                tczyx=tczyx,
            )

        assert not geff_path.exists()


@pytest.mark.parametrize("ctzyx", [True, False])
def test_ctc_image_to_zarr(tmp_path: Path, ctzyx: bool) -> None:
    ctc_path = create_mock_data(tmp_path, is_gt=False)
    zarr_path = tmp_path / "segm.zarr"

    ctc_tiffs_to_zarr(ctc_path, zarr_path, ctzyx=ctzyx)

    expected_arr = np.stack([tifffile.imread(p) for p in sorted(ctc_path.glob("*.tif"))])
    copied_arr = zarr.open_array(zarr_path / "0", mode="r")

    if ctzyx:
        assert copied_arr.ndim == 5

    copied_arr = np.squeeze(copied_arr)
    np.testing.assert_array_equal(copied_arr, expected_arr)


SCALING_KWARGS = {
    "pixel_size": [0.5, 0.25],
    "pixel_unit": "micrometer",
    "time_scale": 2.0,
    "time_unit": "second",
}


def _assert_ome_axes_and_scales(
    zarr_path: Path, names: list[str], scales: list[float]
) -> list[dict]:
    ome = json.loads((zarr_path / "zarr.json").read_text())["attributes"]["ome"]
    multiscale = ome["multiscales"][0]
    axes = multiscale["coordinateSystems"][0]["axes"]
    assert [a["name"] for a in axes] == names
    assert multiscale["datasets"][0]["coordinateTransformations"][0]["scale"] == scales
    return axes


class Test_from_ctc_to_geff:
    def test_scales_and_units_are_written(self, tmp_path: Path) -> None:
        ctc_path = create_mock_data(tmp_path, is_gt=True)
        geff_path = tmp_path / "little.geff"
        segm_path = tmp_path / "segm.zarr"

        from_ctc_to_geff(ctc_path, geff_path, segmentation_store=segm_path, **SCALING_KWARGS)

        axes = _assert_ome_axes_and_scales(segm_path, ["t", "y", "x"], [2.0, 0.5, 0.25])
        assert [a.get("unit") for a in axes] == ["second", "micrometer", "micrometer"]

        metadata = GeffMetadata.read(geff_path)
        assert [(a.unit, a.scale, a.scaled_unit) for a in metadata.axes] == [
            ("frame", 2.0, "second"),
            ("pixel", 0.5, "micrometer"),
            ("pixel", 0.25, "micrometer"),
        ]

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"pixel_unit": "micrometer", "time_unit": "second"},
            {"pixel_size": [0.5, 0.25], "time_scale": 2.0},
        ],
        ids=["unit_without_scale", "scale_without_unit"],
    )
    def test_geff_scale_and_scaled_unit_are_both_or_neither(
        self, tmp_path: Path, kwargs: dict
    ) -> None:
        ctc_path = create_mock_data(tmp_path, is_gt=True)
        geff_path = tmp_path / "little.geff"

        from_ctc_to_geff(ctc_path, geff_path, **kwargs)

        metadata = GeffMetadata.read(geff_path)
        assert [(a.unit, a.scale, a.scaled_unit) for a in metadata.axes] == [
            ("frame", None, None),
            ("pixel", None, None),
            ("pixel", None, None),
        ]

    @pytest.mark.parametrize("with_segmentation", [True, False])
    def test_wrong_number_of_pixel_sizes_raises(
        self, tmp_path: Path, with_segmentation: bool
    ) -> None:
        ctc_path = create_mock_data(tmp_path, is_gt=True, is_3d=True)
        segm_path = tmp_path / "segm.zarr" if with_segmentation else None

        with pytest.raises(ValueError, match="one entry per spatial dimension"):
            from_ctc_to_geff(
                ctc_path,
                tmp_path / "little.geff",
                segmentation_store=segm_path,
                pixel_size=[0.5, 0.5],
            )

    @pytest.mark.parametrize("label_source", [None, "../source_image"])
    def test_label_source_is_written(self, tmp_path: Path, label_source: str | None) -> None:
        ctc_path = create_mock_data(tmp_path, is_gt=True)
        segm_path = tmp_path / "segm.zarr"

        from_ctc_to_geff(
            ctc_path,
            tmp_path / "little.geff",
            segmentation_store=segm_path,
            raw_image_path=label_source,
        )

        ome = json.loads((segm_path / "zarr.json").read_text())["attributes"]["ome"]
        if label_source is None:
            assert "source" not in ome["image-label"]
        else:
            assert ome["image-label"]["source"] == {"image": label_source}

    def test_non_integer_segmentation_raises(self, tmp_path: Path) -> None:
        ctc_path = create_mock_data(tmp_path, is_gt=True)
        for path in ctc_path.glob("*.tif"):
            tifffile.imwrite(path, tifffile.imread(path).astype("float32"))

        with pytest.raises(ValueError, match="must have an integer data type"):
            from_ctc_to_geff(
                ctc_path, tmp_path / "little.geff", segmentation_store=tmp_path / "segm.zarr"
            )


class Test_ctc_tiffs_to_zarr:
    def test_scales_and_units_are_written(self, tmp_path: Path) -> None:
        ctc_path = create_mock_data(tmp_path, is_gt=False)
        zarr_path = tmp_path / "image.zarr"

        ctc_tiffs_to_zarr(ctc_path, zarr_path, **SCALING_KWARGS)

        axes = _assert_ome_axes_and_scales(zarr_path, ["t", "y", "x"], [2.0, 0.5, 0.25])
        assert [a.get("unit") for a in axes] == ["second", "micrometer", "micrometer"]

    def test_ctzyx_axes_and_scales(self, tmp_path: Path) -> None:
        ctc_path = create_mock_data(tmp_path, is_gt=False)
        zarr_path = tmp_path / "image.zarr"

        ctc_tiffs_to_zarr(ctc_path, zarr_path, ctzyx=True, **SCALING_KWARGS)

        _assert_ome_axes_and_scales(
            zarr_path, ["t", "c", "z", "y", "x"], [2.0, 1.0, 1.0, 0.5, 0.25]
        )

    def test_wrong_number_of_pixel_sizes_raises(self, tmp_path: Path) -> None:
        ctc_path = create_mock_data(tmp_path, is_gt=False)

        with pytest.raises(ValueError, match="one entry per spatial dimension"):
            ctc_tiffs_to_zarr(ctc_path, tmp_path / "image.zarr", pixel_size=[0.5])

    def test_store_without_local_path_raises(self, tmp_path: Path) -> None:
        ctc_path = create_mock_data(tmp_path, is_gt=False)

        with pytest.raises(TypeError, match="requires a path or a store backed by a local"):
            ctc_tiffs_to_zarr(ctc_path, zarr.storage.MemoryStore())


def _create_ctc_and_image_dirs(tmp_path: Path) -> tuple[Path, Path]:
    """Mock CTC tracks + segmentation directory, and a separate raw image directory."""
    ctc_path, image_dir = tmp_path / "ctc", tmp_path / "images"
    ctc_path.mkdir()
    image_dir.mkdir()
    return create_mock_data(ctc_path, is_gt=True), create_mock_data(image_dir, is_gt=False)


class Test_convert_ctc:
    def test_layout_follows_ome_zarr_labels_convention(self, tmp_path: Path) -> None:
        ctc_path, image_dir = _create_ctc_and_image_dirs(tmp_path)
        zarr_path = tmp_path / "root.zarr"

        convert_ctc(ctc_path, image_dir, zarr_path, label_name="cells", **SCALING_KWARGS)

        labels_ome = json.loads((zarr_path / "labels" / "zarr.json").read_text())["attributes"]
        assert labels_ome["ome"]["labels"] == ["cells"]

        label_path = zarr_path / "labels" / "cells"
        label_ome = json.loads((label_path / "zarr.json").read_text())["attributes"]["ome"]
        source = label_ome["image-label"]["source"]
        assert source == {"image": "../../"}
        assert (label_path / source["image"]).resolve() == zarr_path.resolve()

        # image and label share axes and scales
        _assert_ome_axes_and_scales(zarr_path, ["t", "y", "x"], [2.0, 0.5, 0.25])
        _assert_ome_axes_and_scales(label_path, ["t", "y", "x"], [2.0, 0.5, 0.25])

        expected_image = np.stack([tifffile.imread(p) for p in sorted(image_dir.glob("*.tif"))])
        expected_segm = np.stack([tifffile.imread(p) for p in sorted(ctc_path.glob("*.tif"))])
        np.testing.assert_array_equal(
            zarr.open_array(zarr_path / "0", mode="r")[...], expected_image
        )
        np.testing.assert_array_equal(
            zarr.open_array(label_path / "0", mode="r")[...], expected_segm
        )

        metadata = GeffMetadata.read(zarr_path / "tracks.geff")
        assert metadata.related_objects == [
            RelatedObject(
                type="labels",
                path=os.path.join("..", "labels", "cells"),
                node_prop="tracklet_id",
            )
        ]

    def test_output_is_valid_ome_zarr(self, tmp_path: Path) -> None:
        import yaozarrs

        ctc_path, image_dir = _create_ctc_and_image_dirs(tmp_path)
        zarr_path = tmp_path / "root.zarr"

        convert_ctc(ctc_path, image_dir, zarr_path, tczyx=True)

        yaozarrs.validate_zarr_store(zarr_path)

    def test_existing_output_requires_overwrite(self, tmp_path: Path) -> None:
        ctc_path, image_dir = _create_ctc_and_image_dirs(tmp_path)
        zarr_path = tmp_path / "root.zarr"
        convert_ctc(ctc_path, image_dir, zarr_path)

        with pytest.raises(FileExistsError, match="already exists"):
            convert_ctc(ctc_path, image_dir, zarr_path)

        convert_ctc(ctc_path, image_dir, zarr_path, overwrite=True)
        labels = json.loads((zarr_path / "labels" / "zarr.json").read_text())
        assert labels["attributes"]["ome"]["labels"] == ["segmentation"]

    @pytest.mark.parametrize("label_name", ["", "a/b", "..", "."])
    def test_label_name_must_be_a_plain_name(self, tmp_path: Path, label_name: str) -> None:
        with pytest.raises(ValueError, match="`label_name` must be a plain name"):
            convert_ctc(tmp_path, tmp_path, tmp_path / "root.zarr", label_name=label_name)
