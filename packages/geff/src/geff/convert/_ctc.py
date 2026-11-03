import json
import os
import warnings
from pathlib import Path
from typing import Any, Literal, cast

from yaozarrs import DimSpec
from yaozarrs.v06 import Image, ImageLabel, LabelImage, LabelsGroup, LabelSource, Multiscale
from yaozarrs.write.v06 import prepare_image

from geff.convert._scale_pyramid import default_chunks_and_shards, generate_scale_pyramid
from geff.core_io._utils import check_for_geff, delete_geff
from geff_spec._valid_values import SpaceUnits, TimeUnits

try:
    # TODO: would be nice to remove dask dependency just to create Zarr from Tiff
    # tifffile directly supports creating Zarr stores from sequences of Tiff files
    # The only convenience added is the ability to easily expand the data to (T, C, Z, Y, X)
    # in the case of images that cannot fit into memory.
    import dask.array as da
    import tifffile
    from dask.array.image import imread
    from skimage.measure import regionprops
except ImportError as e:
    raise ImportError("Please install with geff[ctc] to use this module.") from e


import numpy as np
import zarr
from zarr.storage import StoreLike

import geff
from geff.core_io import write_arrays
from geff_spec import Axis, GeffMetadata, RelatedObject


def _scaled_axis(
    name: str,
    axis_type: Literal["space", "time"],
    unit: str,
    scale: float | None,
    scaled_unit: str | None,
) -> Axis:
    """Axis for values in pixels / frames, with `scale` converting to physical `scaled_unit`."""
    if scale is None and scaled_unit is None:
        return Axis(name=name, type=axis_type, unit=unit)
    return Axis(
        name=name,
        type=axis_type,
        unit=unit,
        scale=1.0 if scale is None else scale,
        scaled_unit=scaled_unit,
    )


def _store_to_local_path(store: StoreLike) -> Path:
    """Resolve a path or local zarr store to a filesystem path.

    Raises:
        TypeError: If `store` is not a path and does not expose a local filesystem path
            (e.g. an in-memory store).
    """
    if isinstance(store, (str, os.PathLike)):
        return Path(store)
    try:
        # zarr 2 stores expose `path`, zarr 3 local stores expose `root`
        path = store.path if zarr.__version__.startswith("2") else store.root  # type: ignore
    except AttributeError:
        path = None
    if path is None:
        raise TypeError(
            "Writing an OME-Zarr requires a path or a store backed by a local directory, "
            f"got {type(store).__name__}."
        )
    return Path(path)


def _ome_dims(
    frame_ndim: int,
    tczyx: bool,
    pixel_size: list[float] | None,
    pixel_unit: SpaceUnits | None,
    time_scale: float | None,
    time_unit: TimeUnits | None,
) -> list[DimSpec]:
    """OME-Zarr dimensions for a (T,) + frame, or (T, C, Z, Y, X) if `tczyx`, array."""
    if pixel_size is not None and len(pixel_size) != frame_ndim:
        raise ValueError(
            f"`pixel_size` must have one entry per spatial dimension ({frame_ndim}), "
            f"got {len(pixel_size)}."
        )
    spatial_names = ("z", "y", "x")[-frame_ndim:]
    spatial_scales = pixel_size if pixel_size is not None else (1.0,) * frame_ndim
    dims = [DimSpec(name="t", scale=time_scale or 1.0, unit=time_unit)]
    if tczyx:
        dims.append(DimSpec(name="c"))
        if frame_ndim == 2:
            dims.append(DimSpec(name="z"))
    dims.extend(
        DimSpec(name=name, scale=scale, unit=pixel_unit)
        for name, scale in zip(spatial_names, spatial_scales, strict=True)
    )
    return dims


def _chunks_and_shards(
    shape: tuple[int, ...], tczyx: bool
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Chunks and shards for a (T, ...) array, whose spatial axes are the trailing ones."""
    n_spatial = 3 if tczyx else len(shape) - 1
    return default_chunks_and_shards(shape, range(len(shape) - n_spatial, len(shape)))


def ctc_tiffs_to_zarr(
    ctc_path: Path,
    output_store: StoreLike,
    ctzyx: bool = False,
    overwrite: bool = False,
    pixel_size: list[float] | None = None,
    pixel_unit: SpaceUnits | None = None,
    time_scale: float | None = None,
    time_unit: TimeUnits | None = None,
) -> None:
    """
    Convert a CTC file to an OME-Zarr image.

    Args:
        ctc_path (Path): The path to the CTC file.
        output_store (StoreLike): The path or local store to write the OME-Zarr image to.
            Stores without a local path (e.g. in-memory) are not supported.
        ctzyx (optional, bool): Expand data to make it (T, C, Z, Y, X)
            otherwise it's (T,) + Frame shape. Defaults to False.
        overwrite (optional, bool): Whether to overwrite the Zarr file if it already exists.
            Defaults to False.
        pixel_size (optional, list[float]): Physical size of a pixel along each spatial
            dimension (z, y, x or y, x). Defaults to 1.0.
        pixel_unit (optional): Unit of `pixel_size`.
        time_scale (optional, float): Physical time between frames. Defaults to 1.0.
        time_unit (optional): Unit of `time_scale`.
    """
    out_path = _store_to_local_path(output_store)
    array = imread(str(ctc_path / "*.tif"))
    frame_shape = array.shape[1:]
    dims = _ome_dims(len(frame_shape), ctzyx, pixel_size, pixel_unit, time_scale, time_unit)
    if ctzyx:
        n_missing_dims = 5 - array.ndim  # (T, C, Z, Y, X)
        expand_dims = (slice(None),) + (np.newaxis,) * n_missing_dims
        array = array[expand_dims]

    image = Image(multiscales=[Multiscale.from_dims(dims)])
    chunks, shards = _chunks_and_shards(array.shape, ctzyx)
    _, arrays = prepare_image(
        out_path,
        image,
        (array.shape, array.dtype),
        chunks=chunks,
        shards=shards,
        writer="zarr",
        overwrite=overwrite,
    )
    da.store(array, cast("Any", arrays["0"]), lock=False)


def from_ctc_to_geff(
    ctc_path: Path,
    geff_path: Path,
    segmentation_store: StoreLike | None = None,
    tczyx: bool = False,
    overwrite: bool = False,
    pixel_size: list[float] | None = None,
    pixel_unit: SpaceUnits | None = None,
    time_scale: float | None = None,
    time_unit: TimeUnits | None = None,
    label_source: str | None = None,
) -> None:
    """
    Convert a CTC file to a GEFF file.

    Segmentation is written to a OME-Zarr v0.6 and the GEFF defaults to zarr v3 as a result.

    Args:
        ctc_path: The path to the CTC file.
        geff_path: The path to the GEFF file.
        segmentation_store: The path or local store to save the segmentation to, written as
                            an OME-Zarr label image (always Zarr v3, `zarr_format` does not
                            apply). Stores without a local path (e.g. in-memory) are not
                            supported. If not provided, it won't be exported.
        tczyx: Expand data to make it (T, C, Z, Y, X) otherwise it's (T,) + Frame shape.
        overwrite: Whether to overwrite the GEFF file if it already exists.
        pixel_size: Physical size of a pixel along each spatial dimension (z, y, x or y, x),
            stored in the label image metadata. Defaults to 1.0.
        pixel_unit: Unit of `pixel_size`.
        time_scale: Physical time between frames. Defaults to 1.0.
        time_unit: Unit of `time_scale`.
        label_source: Path of the source image group, relative to the segmentation label image,
            stored as `image-label.source.image` (e.g. "../../" for a label in the `labels/`
            group of the image). If not provided, no source is recorded.
    """
    ctc_path = Path(ctc_path)
    geff_path = Path(geff_path).with_suffix(".geff")

    if not ctc_path.exists():
        raise FileNotFoundError(f"CTC file {ctc_path} does not exist")

    for tracks_file in ["man_track.txt", "res_track.txt"]:
        tracks_file_path = ctc_path / tracks_file
        if tracks_file_path.exists():
            break
    else:
        raise FileNotFoundError(
            f"Tracks file {ctc_path}/man_track.txt or {ctc_path}/res_track.txt does not exist"
        )

    # Check for existing geff
    if check_for_geff(geff_path):
        if overwrite:
            delete_geff(geff_path)
        else:
            raise FileExistsError(
                "Found an existing geff present in `geff_path`. "
                "Please use `overwrite=True` or provide an alternative "
                "`geff_path` to write to."
            )

    seg_path = _store_to_local_path(segmentation_store) if segmentation_store is not None else None

    tracks: dict[int, list[int]] = {}

    edges = []
    node_props: dict[str, list[int | float]] = {
        "id": [],
        "tracklet_id": [],
        "t": [],
        "x": [],
        "y": [],
    }

    segm_array = None
    node_id = 0

    sorted_files = sorted(ctc_path.glob("*.tif"))
    n_1_padding: tuple[int, ...] = ()
    expand_dims: tuple[None, ...] | slice = slice(None)

    for t, filepath in enumerate(sorted_files):
        frame = tifffile.imread(filepath)
        if t == 0 and pixel_size is not None and len(pixel_size) != frame.ndim:
            raise ValueError(
                f"`pixel_size` must have one entry per spatial dimension ({frame.ndim}), "
                f"got {len(pixel_size)}."
            )
        if frame.ndim == 3 and "z" not in node_props:
            node_props["z"] = []

        if seg_path is not None and segm_array is None:
            # created in first iteration
            if tczyx:
                n_1_padding = (1,) * (5 - frame.ndim - 1)  # forcing data to be (T, C, Z, Y, X)
                expand_dims = (np.newaxis,) * len(n_1_padding)

            if frame.dtype.kind not in "iu":
                raise ValueError(f"Label images must have an integer data type, got {frame.dtype}.")
            # Construct metadata model for ome zarr
            dims = _ome_dims(frame.ndim, tczyx, pixel_size, pixel_unit, time_scale, time_unit)
            image_label = ImageLabel(
                source=LabelSource(image=label_source) if label_source is not None else None
            )
            # (validated from a dict because the model's field is aliased to "image-label")
            label_image = LabelImage.model_validate(
                {"multiscales": [Multiscale.from_dims(dims)], "image-label": image_label}
            )

            segm_shape = (len(sorted_files), *n_1_padding, *frame.shape)
            chunks, shards = _chunks_and_shards(segm_shape, tczyx)
            _, arrays = prepare_image(
                seg_path,
                label_image,
                (segm_shape, frame.dtype),
                chunks=chunks,
                shards=shards,
                writer="zarr",
                overwrite=overwrite,
            )
            segm_array = arrays["0"]

        if segm_array is not None:
            segm_array[t] = frame[expand_dims]

        for obj in regionprops(frame):
            tracklet_id = obj.label
            node_props["id"].append(node_id)
            node_props["tracklet_id"].append(tracklet_id)
            node_props["t"].append(t)
            # using y,x for 2d and z,y,x for 3d
            for c, v in zip(("x", "y", "z"), obj.centroid[::-1], strict=False):
                node_props[c].append(v)

            if tracklet_id not in tracks:
                tracks[tracklet_id] = []

            tracks[tracklet_id].append(node_id)
            node_id += 1

    if len(node_props["id"]) == 0:
        raise ValueError(f"No nodes found in the CTC directory {ctc_path}")

    for _node_ids in tracks.values():
        # connect simple-paths of each track
        for i in range(len(_node_ids) - 1):
            # forward in time (parent -> child)
            edges.append((_node_ids[i], _node_ids[i + 1]))

    tracks_table = np.loadtxt(tracks_file_path, dtype=int)

    # removing orphan tracklets
    tracks_table = tracks_table[tracks_table[:, -1] > 0]

    for row in tracks_table:
        child_track_id = row[0]
        parent_track_id = row[-1]
        child_node_id = tracks[child_track_id][0]
        parent_node_id = tracks[parent_track_id][-1]
        # forward in time (parent -> child)
        edges.append((parent_node_id, child_node_id))

    # Node coordinates are in pixels / frames; `scale` converts them to physical units
    axis_names = [_scaled_axis("t", "time", "frame", time_scale, time_unit)]
    spatial_names = ("z", "y", "x") if "z" in node_props else ("y", "x")
    spatial_sizes = pixel_size if pixel_size is not None else (None,) * len(spatial_names)
    axis_names.extend(
        _scaled_axis(name, "space", "pixel", size, pixel_unit)
        for name, size in zip(spatial_names, spatial_sizes, strict=True)
    )

    node_ids = np.asarray(node_props.pop("id"), dtype="uint")

    rel_objs = None
    if seg_path is not None:
        # Record related object metadata for segmentation
        seg_path = None
        if isinstance(segmentation_store, (Path, str)):
            seg_path = segmentation_store  # type: ignore
        else:
            try:
                seg_path = segmentation_store.root  # type: ignore
            except AttributeError:
                warnings.warn(
                    "Cannot determine path to segmentation_store for related objects metadata",
                    stacklevel=2,
                )

        if seg_path is not None:
            rel_path = os.path.relpath(seg_path, geff_path)
            rel_objs = [RelatedObject(type="labels", path=rel_path, node_prop="tracklet_id")]

    write_arrays(
        geff_store=geff_path,
        node_ids=node_ids,
        node_props={
            name: {"values": np.asarray(values), "missing": None}
            for name, values in node_props.items()
        },
        edge_ids=np.asarray(edges, dtype=node_ids.dtype),
        edge_props={},
        metadata=GeffMetadata(
            geff_version=geff.__version__,
            axes=axis_names,
            directed=True,
            node_props_metadata={},
            edge_props_metadata={},
            track_node_props={"tracklet": "tracklet_id"},
            related_objects=rel_objs,
        ),
        zarr_format=3,
    )


def _register_label(image_path: Path, label_name: str) -> None:
    """Add `label_name` to the OME-Zarr `labels/` group of the image at `image_path`."""
    zarr_json_path = image_path / "labels" / "zarr.json"
    zarr_json: dict[str, Any] = {"zarr_format": 3, "node_type": "group"}
    labels: list[str] = []
    if zarr_json_path.exists():
        zarr_json = json.loads(zarr_json_path.read_text())
        labels = zarr_json.get("attributes", {}).get("ome", {}).get("labels", [])
    if label_name not in labels:
        labels.append(label_name)
    attributes = zarr_json.setdefault("attributes", {})
    attributes["ome"] = LabelsGroup(labels=labels).model_dump(mode="json", exclude_none=True)
    zarr_json_path.write_text(json.dumps(zarr_json, indent=2))


def convert_ctc(
    ctc_path: Path,
    image_dir: Path,
    zarr_path: StoreLike,
    label_name: str = "segmentation",
    tczyx: bool = False,
    overwrite: bool = False,
    pixel_size: list[float] | None = None,
    pixel_unit: SpaceUnits | None = None,
    time_scale: float | None = None,
    time_unit: TimeUnits | None = None,
) -> None:
    """
    Convert a CTC dataset (raw images, segmentation and tracks) to an OME-Zarr and a GEFF.

    The raw images are written to the OME-Zarr image at `zarr_path`, and the segmentation
    is written inside it as a label image following the OME-Zarr labels convention::

        zarr_path
        ├── zarr.json          # image metadata
        ├── 0/                 # image array
        ├── labels/
        │   ├── zarr.json      # lists the label images
        │   └── <label_name>/  # segmentation, with `image-label.source` pointing at the image
        └── tracks.geff        # the tracks, whose related objects point at the segmentation

    Lower-resolution scales (``1/``, ``2/``, ...) are generated for the image (block mean) and
    the segmentation (block mode) until each spatial dimension fits in a single chunk.

    Args:
        ctc_path: The path to the CTC directory with the tracks file and segmentation tiffs.
        image_dir: The path to the directory with the raw image tiffs.
        zarr_path: The path or local store of the OME-Zarr image to write. Stores without a
            local path (e.g. in-memory) are not supported.
        label_name: The name of the segmentation inside the OME-Zarr `labels/` group.
        tczyx: Expand data to make it (T, C, Z, Y, X) otherwise it's (T,) + Frame shape.
        overwrite: Whether to overwrite existing output (the OME-Zarr and the GEFF).
        pixel_size: Physical size of a pixel along each spatial dimension (z, y, x or y, x).
            Defaults to 1.0.
        pixel_unit: Unit of `pixel_size`.
        time_scale: Physical time between frames. Defaults to 1.0.
        time_unit: Unit of `time_scale`.
    """
    if not label_name or Path(label_name).name != label_name or label_name in (".", ".."):
        raise ValueError(f"`label_name` must be a plain name, not a path, got {label_name!r}.")
    image_path = _store_to_local_path(zarr_path)
    label_path = image_path / "labels" / label_name
    geff_path = image_path / "tracks.geff"

    # The image goes first: overwriting it removes everything nested inside, e.g. `labels/`
    ctc_tiffs_to_zarr(
        image_dir,
        image_path,
        ctzyx=tczyx,
        overwrite=overwrite,
        pixel_size=pixel_size,
        pixel_unit=pixel_unit,
        time_scale=time_scale,
        time_unit=time_unit,
    )
    from_ctc_to_geff(
        ctc_path,
        geff_path,
        segmentation_store=label_path,
        tczyx=tczyx,
        overwrite=overwrite,
        pixel_size=pixel_size,
        pixel_unit=pixel_unit,
        time_scale=time_scale,
        time_unit=time_unit,
        # `labels/<label_name>` -> `../../` is the image, per the OME-Zarr labels convention
        label_source="../../",
    )

    _register_label(image_path, label_name)

    generate_scale_pyramid(zarr.open_group(image_path, mode="r+"))
    generate_scale_pyramid(zarr.open_group(label_path, mode="r+"), is_label=True)
