import os
from pathlib import Path
from typing import Literal

from yaozarrs import DimSpec
from yaozarrs.v06 import ImageLabel, LabelImage, Multiscale
from yaozarrs.write.v06 import prepare_image

from geff.core_io._utils import check_for_geff, delete_geff
from geff_spec._valid_values import SpaceUnits, TimeUnits

try:
    import tifffile

    # TODO: would be nice to remove dask dependency just to create Zarr from Tiff
    # tifffile directly supports creating Zarr stores from sequences of Tiff files
    # The only convenience added is the ability to easily expand the data to (T, C, Z, Y, X)
    # in the case of images that cannot fit into memory.
    from dask.array.image import imread
    from skimage.measure import regionprops
except ImportError as e:
    raise ImportError("Please install with geff[ctc] to use this module.") from e

import warnings

import numpy as np
import zarr
from zarr.storage import StoreLike

import geff
from geff.core_io import write_arrays
from geff_spec import Axis, GeffMetadata, RelatedObject


def _scaling_kwargs(scale: float | None, unit: str | None) -> dict[str, float | str | None]:
    """Axis kwargs converting pixel/frame values to physical `scale` and `unit`."""
    if scale is None and unit is None:
        return {}
    return {"scale": 1.0 if scale is None else scale, "scaled_unit": unit}


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
            "Writing the segmentation as an OME-Zarr label image requires a path or a store "
            f"backed by a local directory, got {type(store).__name__}."
        )
    return Path(path)


def ctc_tiffs_to_zarr(
    ctc_path: Path,
    output_store: StoreLike,
    ctzyx: bool = False,
    overwrite: bool = False,
    zarr_format: Literal[2, 3] = 2,
) -> None:
    """
    Convert a CTC file to a Zarr file.

    Args:
        ctc_path (Path): The path to the CTC file.
        output_store (StoreLike): The path to the Zarr file.
        ctzyx (optional, bool): Expand data to make it (T, C, Z, Y, X)
            otherwise it's (T,) + Frame shape. Defaults to False.
        overwrite (optional, bool): Whether to overwrite the Zarr file if it already exists.
            Defaults to False.
        zarr_format (optional, Literal[2, 3]): The zarr specification to use when writing the zarr.
            Defaults to 2.
    """
    array = imread(str(ctc_path / "*.tif"))
    if ctzyx:
        n_missing_dims = 5 - array.ndim  # (T, C, Z, Y, X)
        expand_dims = (slice(None),) + (np.newaxis,) * n_missing_dims
        array = array[expand_dims]
    # Suppress warnings from dask/zarr compatibility layer
    # Note: dask 2025.12.0+ deprecated passing storage args via **kwargs in favor of
    # zarr_array_kwargs/zarr_read_kwargs parameters. When the deprecated API is removed,
    # we'll need to update to use the new parameters and handle version compatibility.
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore", message=r".*ignoring keyword argument.*zarr_format.*", category=UserWarning
        )
        warnings.filterwarnings(
            "ignore",
            message=r".*Passing storage-related arguments via \*\*kwargs is deprecated.*",
            category=FutureWarning,
        )
        array.to_zarr(url=output_store, overwrite=overwrite, zarr_format=zarr_format)


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
            delete_geff(geff_path, zarr_format=3)
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
            spatial_names = ("z", "y", "x")[-frame.ndim :]
            spatial_scales = pixel_size if pixel_size is not None else (1.0,) * frame.ndim
            dims = [DimSpec(name="t", scale=time_scale or 1.0, unit=time_unit)]
            if tczyx:
                dims.append(DimSpec(name="c"))
                if frame.ndim == 2:
                    dims.append(DimSpec(name="z"))
            dims.extend(
                DimSpec(name=name, scale=scale, unit=pixel_unit)
                for name, scale in zip(spatial_names, spatial_scales, strict=True)
            )
            label_image = LabelImage(
                multiscales=[Multiscale.from_dims(dims)],
                image_label=ImageLabel(),  # Add in source later if we write the raw images
            )

            _, arrays = prepare_image(
                seg_path,
                label_image,
                ((len(sorted_files), *n_1_padding, *frame.shape), frame.dtype),
                chunks=(1, *n_1_padding, *frame.shape),
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
    axis_names = [
        Axis(name="t", type="time", unit="frame", **_scaling_kwargs(time_scale, time_unit))
    ]
    spatial_names = ("z", "y", "x") if "z" in node_props else ("y", "x")
    spatial_sizes = pixel_size if pixel_size is not None else (None,) * len(spatial_names)
    axis_names.extend(
        Axis(name=name, type="space", unit="pixel", **_scaling_kwargs(size, pixel_unit))
        for name, size in zip(spatial_names, spatial_sizes, strict=True)
    )

    node_ids = np.asarray(node_props.pop("id"), dtype="uint")

    rel_objs = None
    if seg_path is not None:
        # Record related object metadata for segmentation
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
