import pytest

try:
    import tifffile

    from geff.interops import ctc
except ImportError:
    pytest.skip("geff[ctc] not installed", allow_module_level=True)

import itertools
from pathlib import Path

import numpy as np
import zarr
from typer.testing import CliRunner

from geff.networkx.io import read_nx


def create_mock_data(
    tmp_path: Path,
    is_gt: bool,
) -> Path:
    """
    mock graph is:

    t=0      1       7
             |       |
    t=1      1       |
            / \\     |
    t=2    2   5     9
    """
    labels = np.zeros((3, 10, 10), dtype=np.uint16)

    labels[0, 3, 3] = 1
    labels[0, 8, 8] = 7

    labels[1, 3, 4] = 1

    labels[2, 2, 3] = 5
    labels[2, 4, 5] = 2
    labels[2, 8, 9] = 9

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


@pytest.mark.parametrize(
    "cli,is_gt,tczyx",
    list(itertools.product([False, True], [True, False], [True, False])),
)
def test_ctc_to_geff(
    tmp_path: Path,
    cli: bool,
    is_gt: bool,
    tczyx: bool,
) -> None:
    ctc_path = create_mock_data(tmp_path, is_gt)
    geff_path = ctc_path / "little.geff"
    segm_path = ctc_path / "segm.zarr"

    if cli:
        cmd_args = [
            str(ctc_path),
            str(geff_path),
            "--segm-path",
            str(segm_path),
            "--input-image-dir",
            str(ctc_path),
            "--output-image-path",
            str(tmp_path / "output_image.zarr"),
        ]
        if tczyx:
            cmd_args.append("--tczyx")
        result = CliRunner().invoke(ctc.app, cmd_args)
        assert result.exit_code == 0, (
            f"{cmd_args} failed with exit code {result.exit_code} and "
            f"message:\n{result.stdout}\n{result.stderr}"
        )
    else:
        ctc.from_ctc_to_geff(
            ctc_path=ctc_path,
            geff_path=geff_path,
            segmentation_store=segm_path,
            tczyx=True,
        )

    assert geff_path.exists()

    graph, _ = read_nx(geff_path)

    expected_nodes = {0, 1, 2, 3, 4, 5}
    expected_edges = {(0, 2), (2, 3), (2, 4), (1, 5)}

    assert set(graph.nodes()) == expected_nodes
    assert set(graph.edges()) == expected_edges

    for _, data in graph.nodes(data=True):
        for key in ["tracklet_id", "t", "y", "x"]:
            assert key in data

    expected_segm = np.stack([tifffile.imread(p) for p in sorted(ctc_path.glob("*.tif"))])

    segm = zarr.open(segm_path, mode="r")[...]

    assert segm.shape[0] == expected_segm.shape[0]

    if tczyx:
        assert segm.ndim == 5

    segm = np.squeeze(segm)
    np.testing.assert_array_equal(segm, expected_segm)


@pytest.mark.parametrize("ctzyx", [True, False])
def test_ctc_image_to_zarr(tmp_path: Path, ctzyx: bool) -> None:
    ctc_path = create_mock_data(tmp_path, is_gt=False)
    zarr_path = tmp_path / "segm.zarr"

    ctc.ctc_tiffs_to_zarr(ctc_path, zarr_path, ctzyx=ctzyx)

    expected_arr = np.stack([tifffile.imread(p) for p in sorted(ctc_path.glob("*.tif"))])
    copied_arr = zarr.open(zarr_path, mode="r")

    if ctzyx:
        assert copied_arr.ndim == 5

    copied_arr = np.squeeze(copied_arr)
    np.testing.assert_array_equal(copied_arr, expected_arr)
