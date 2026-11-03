"""Generate lower-resolution scales for an existing single-scale OME-Zarr.

Ported from ``sgro_lab_utils/pyramid.py``. Downsampling is anisotropy-aware:
a spatial axis is only downsampled (factor 2) if its voxel size is within 2x
of the finest spatial axis. Non-spatial axes are never downsampled.
"""

import logging
from collections.abc import Sequence
from typing import Any, NamedTuple, cast

import dask.array as da
import numpy as np
import zarr
from yaozarrs import v06

logger = logging.getLogger(__name__)

# Target ~3M voxels per spatial chunk based on Caroline's benchmarking
# 128^3 -> 2M, but is a power of 2
DEFAULT_SPATIAL_CHUNK_SIZE = 128


# --------------------------------------------------------------------------- #
# Planning (pure python)
# --------------------------------------------------------------------------- #


def downsampled_shape(shape: Sequence[int], factors: Sequence[int]) -> tuple[int, ...]:
    """Shape after downsampling: ``ceil(s / f)`` per dimension."""
    return tuple((s + f - 1) // f for s, f in zip(shape, factors, strict=True))


def compute_downsample_factors(
    voxel_size: Sequence[float], spatial_axes: Sequence[int]
) -> tuple[int, ...]:
    """Anisotropy-aware downsample factors (1 or 2 per axis).

    Args:
        voxel_size: Current voxel size for every axis.
        spatial_axes: Indices of the spatial axes in ``voxel_size``.

    Returns:
        One factor per axis. Non-spatial axes always get 1.
    """
    finest = min(voxel_size[i] for i in spatial_axes)
    factors = [1] * len(voxel_size)
    for i in spatial_axes:
        if voxel_size[i] < finest * 2:
            factors[i] = 2
    return tuple(factors)


def compute_num_levels(
    shape: Sequence[int],
    voxel_size: Sequence[float],
    spatial_axes: Sequence[int],
    chunk_size: int = DEFAULT_SPATIAL_CHUNK_SIZE,
) -> int:
    """Number of levels (including the base) until every spatial dim fits in one chunk."""
    shape = list(shape)
    voxel = list(voxel_size)
    levels = 1
    while any(shape[i] > chunk_size for i in spatial_axes):
        factors = compute_downsample_factors(voxel, spatial_axes)
        shape = list(downsampled_shape(shape, factors))
        voxel = [v * f for v, f in zip(voxel, factors, strict=True)]
        levels += 1
    return levels


class LevelPlan(NamedTuple):
    shape: tuple[int, ...]
    scale: tuple[float, ...]
    translation: tuple[float, ...]
    factors: tuple[int, ...]  # relative to the previous level; all 1s for level 0


def plan_pyramid(
    shape: Sequence[int],
    scale: Sequence[float],
    translation: Sequence[float],
    spatial_axes: Sequence[int],
    num_levels: int | None = None,
    chunk_size: int = DEFAULT_SPATIAL_CHUNK_SIZE,
) -> list[LevelPlan]:
    """Compute shape, scale, translation and factors for every level.

    Block downsampling by factor ``f`` places each output voxel center at the
    middle of ``f`` input voxels, shifting the origin by ``(f - 1) / 2`` input
    voxels.
    """
    if num_levels is None:
        num_levels = compute_num_levels(shape, scale, spatial_axes, chunk_size)

    current = LevelPlan(
        tuple(shape),
        tuple(float(s) for s in scale),
        tuple(float(t) for t in translation),
        (1,) * len(shape),
    )
    plan = [current]
    for _ in range(1, num_levels):
        factors = compute_downsample_factors(current.scale, spatial_axes)
        shift = [(f - 1) / 2 * s for f, s in zip(factors, current.scale, strict=True)]
        current = LevelPlan(
            downsampled_shape(current.shape, factors),
            tuple(s * f for s, f in zip(current.scale, factors, strict=True)),
            tuple(t + d for t, d in zip(current.translation, shift, strict=True)),
            factors,
        )
        plan.append(current)
    return plan


# --------------------------------------------------------------------------- #
# Array kernels (numpy / dask, no zarr)
# --------------------------------------------------------------------------- #


def _vote(flat: np.ndarray) -> np.ndarray:
    """Most frequent value along the last axis; ties go to nonzero values, then the lowest."""
    flat = np.sort(flat, axis=-1)
    counts = (flat[..., :, None] == flat[..., None, :]).sum(axis=-1)
    score = counts * 2 + (flat != 0)
    best = np.argmax(score, axis=-1)  # first max -> lowest value on equal scores
    return np.take_along_axis(flat, best[..., None], axis=-1)[..., 0]


def _block_mode(block: np.ndarray, axis: int | tuple[int, ...] | None = None) -> np.ndarray:
    """Most frequent value over ``axis``; ties go to nonzero values, then the lowest value.

    Blocks with a single value (most of a label image is background) skip the vote, which
    compares every pair of values in a block and is much more expensive.
    """
    if axis is None:
        axes = tuple(range(block.ndim))
    else:
        axes = (axis,) if isinstance(axis, int) else tuple(axis)
    axes = tuple(a % block.ndim for a in axes)
    kept = [i for i in range(block.ndim) if i not in axes]
    kept_shape = tuple(block.shape[i] for i in kept)
    if block.size == 0:
        return np.empty(kept_shape, dtype=block.dtype)

    flat = np.transpose(block, kept + list(axes)).reshape(*kept_shape, -1)
    result = np.asarray(flat.min(axis=-1))
    mixed = result != flat.max(axis=-1)
    if mixed.any():
        result = result.copy()  # own the data, and keep 0-d results indexable
        result[mixed] = _vote(flat[mixed])
    return result


def _pad_to_multiple(data: np.ndarray | da.Array, factors: Sequence[int]) -> np.ndarray | da.Array:
    """Edge-pad the end of each axis so its length is divisible by its factor."""
    pad_width = [(0, int(-s % f)) for s, f in zip(data.shape, factors, strict=True)]
    if not any(after for _, after in pad_width):
        return data
    if isinstance(data, da.Array):
        return da.pad(data, pad_width, mode="edge")
    return np.pad(data, pad_width, mode="edge")


def _block_mean(block: np.ndarray, axis: int | tuple[int, ...] | None = None) -> np.ndarray:
    """Mean over ``axis``, rounded to the nearest integer (half to even) for integer dtypes."""
    mean = np.asarray(np.mean(block, axis=axis))
    return np.rint(mean) if np.issubdtype(block.dtype, np.integer) else mean


def downsample(
    data: np.ndarray | da.Array,
    factors: Sequence[int],
    is_label: bool,
) -> np.ndarray | da.Array:
    """Downsample by per-axis factors, with output shape ``ceil(s / f)``.

    Uses block mean for images (rounded for integer dtypes, so values are not biased
    low by truncation) and block mode (majority vote, preferring nonzero ids on ties)
    for labels. Both are centered on the block, so they share the same translation
    shift. Accepts numpy or dask arrays.
    """
    original_dtype = data.dtype
    reducer = _block_mode if is_label else _block_mean
    data = _pad_to_multiple(data, factors)

    if isinstance(data, da.Array):
        return da.coarsen(reducer, data, dict(enumerate(factors)), trim_excess=False).astype(
            original_dtype
        )

    new_shape = []
    axes_to_reduce = []
    for i, (s, f) in enumerate(zip(data.shape, factors, strict=True)):
        new_shape.extend([s // f, f])
        axes_to_reduce.append(2 * i + 1)
    return reducer(data.reshape(new_shape), axis=tuple(axes_to_reduce)).astype(original_dtype)


# --------------------------------------------------------------------------- #
# OME-NGFF metadata
# --------------------------------------------------------------------------- #


def _read_multiscale(group: zarr.Group) -> v06.Multiscale:
    """Read the first OME-Zarr 0.6 multiscale from ``attrs["ome"]``."""
    ome = group.attrs.get("ome")
    multiscales = ome.get("multiscales") if isinstance(ome, dict) else None
    if not isinstance(multiscales, list) or not multiscales:
        raise ValueError(f"No multiscales metadata found in group {group.path!r}")
    return v06.Multiscale.model_validate(multiscales[0])


def _write_multiscale(group: zarr.Group, multiscale: v06.Multiscale) -> None:
    """Replace the first multiscale of a group, preserving all other attributes."""
    ome = cast("dict[str, Any]", dict(group.attrs["ome"]))  # type: ignore[arg-type]
    dumped = multiscale.model_dump(mode="json", exclude_none=True)
    ome["multiscales"] = [dumped, *ome["multiscales"][1:]]
    group.attrs["ome"] = ome


def _output_coordinate_system(multiscale: v06.Multiscale) -> v06.CoordinateSystem:
    """The coordinate system that the datasets' transformations map into."""
    output = multiscale.datasets[0].coordinateTransformations[0].output
    systems = multiscale.coordinateSystems
    if output is None or output.name is None:
        if len(systems) != 1:
            raise ValueError("Cannot tell which coordinate system the datasets map into")
        return systems[0]
    return next(cs for cs in systems if cs.name == output.name)


def _spatial_axes(coordinate_system: v06.CoordinateSystem) -> list[int]:
    """Indices of the spatial axes."""
    return [i for i, ax in enumerate(coordinate_system.axes) if ax.type == "space"]


def _base_scale_and_translation(dataset: v06.Dataset, ndim: int) -> tuple[list[float], list[float]]:
    """Scale and translation of a dataset, defaulting to 1s and 0s if absent.

    Handles a lone ``scale``, ``identity``, or a ``sequence`` of scale/translation.
    """
    (transform,) = dataset.coordinateTransformations
    steps = transform.transformations if transform.type == "sequence" else [transform]
    scale = [1.0] * ndim
    translation = [0.0] * ndim
    for step in steps:
        if step.type == "scale":
            scale = list(step.scale)
        elif step.type == "translation":
            translation = list(step.translation)
        elif step.type != "identity":
            raise ValueError(f"Unsupported dataset transformation type {step.type!r}")
    return scale, translation


def _make_dataset(path: str, level_plan: LevelPlan, coordinate_system: str) -> v06.Dataset:
    """Dataset entry for a level. A translation is only included if nonzero."""
    transform: dict = {"type": "scale", "scale": list(level_plan.scale)}
    if any(level_plan.translation):
        # a scale and a translation must be a sequence, scale first
        transform = {
            "type": "sequence",
            "transformations": [
                transform,
                {"type": "translation", "translation": list(level_plan.translation)},
            ],
        }
    transform["input"] = {"path": path}
    transform["output"] = {"name": coordinate_system}
    return v06.Dataset.model_validate({"path": path, "coordinateTransformations": [transform]})


# --------------------------------------------------------------------------- #
# Writing levels (zarr)
# --------------------------------------------------------------------------- #


def _level_chunks(
    shape: Sequence[int], spatial_axes: Sequence[int], chunk_size: int
) -> tuple[int, ...]:
    """Chunks of ``chunk_size`` along spatial axes (clipped to the shape), 1 elsewhere."""
    return tuple(min(chunk_size, s) if i in spatial_axes else 1 for i, s in enumerate(shape))


def _shard_shape(
    shape: Sequence[int], chunks: Sequence[int], spatial_axes: Sequence[int]
) -> tuple[int, ...]:
    """One shard per non-spatial index, spanning the full spatial extent of the level.

    Spatial dims are rounded up to a whole number of chunks, as zarr requires
    shard shapes to be a multiple of the chunk shape.
    """
    return tuple(
        ((s + c - 1) // c) * c if i in spatial_axes else c
        for i, (s, c) in enumerate(zip(shape, chunks, strict=True))
    )


def default_chunks_and_shards(
    shape: Sequence[int],
    spatial_axes: Sequence[int],
    chunk_size: int = DEFAULT_SPATIAL_CHUNK_SIZE,
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Chunk and shard shapes used for every pyramid level, including scale 0.

    Spatial chunks are ``chunk_size`` (clipped to the shape) and all other axes
    have chunk size 1. There is one shard per non-spatial index, so each frame
    (or channel of a frame) is a single shard.
    """
    chunks = _level_chunks(shape, spatial_axes, chunk_size)
    return chunks, _shard_shape(shape, chunks, spatial_axes)


def _write_level(
    group: zarr.Group,
    name: str,
    data: da.Array,
    like: zarr.Array,
    level_plan: LevelPlan,
    spatial_axes: Sequence[int],
    chunk_size: int,
) -> zarr.Array:
    """Create a sharded array for a level, write ``data`` into it, and return it.

    dtype, fill value and dimension names are taken from ``like``.
    """
    chunks, shards = default_chunks_and_shards(level_plan.shape, spatial_axes, chunk_size)
    array = group.create_array(
        name,
        shape=level_plan.shape,
        chunks=chunks,
        shards=shards,
        dtype=like.dtype,
        fill_value=like.fill_value,
        dimension_names=getattr(like.metadata, "dimension_names", None),
    )
    # Rechunk to whole shards so no two dask tasks write to the same shard.
    da.store(data.rechunk(cast("Any", shards)), array, lock=False)
    return array


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #


def generate_scale_pyramid(
    zarr_group: zarr.Group,
    num_levels: int | None = None,
    chunk_size: int = DEFAULT_SPATIAL_CHUNK_SIZE,
    is_label: bool = False,
) -> None:
    """Generate lower-resolution scales for a single-scale OME-Zarr, in place.

    Reads scale ``"0"`` and its OME-Zarr 0.6 metadata from ``zarr_group``, writes
    downsampled arrays ``"1"``, ``"2"``, ... into the same group, and updates
    the ``multiscales`` metadata. Each level is written to disk before the next
    is computed, which keeps the dask graph shallow.

    Args:
        zarr_group: Group with a valid single-scale OME-Zarr layout.
        num_levels: Total number of levels including the base. If None, chosen
            so the coarsest level fits in a single ``chunk_size`` spatial chunk.
        chunk_size: Spatial chunk size of the new levels, also used when auto-computing
            the number of levels. Scale 0 is left as written, so it should have been
            written with :func:`default_chunks_and_shards` to match.
        is_label: Downsample by block mode (majority vote) instead of block mean.
    """
    multiscale = _read_multiscale(zarr_group)
    coordinate_system = _output_coordinate_system(multiscale)
    spatial_axes = _spatial_axes(coordinate_system)

    base_dataset = multiscale.datasets[0]
    base = zarr_group[base_dataset.path]
    if not isinstance(base, zarr.Array):
        raise TypeError(f"Expected {base_dataset.path!r} to be an array")

    base_scale, base_translation = _base_scale_and_translation(base_dataset, base.ndim)
    plan = plan_pyramid(
        base.shape, base_scale, base_translation, spatial_axes, num_levels, chunk_size
    )

    datasets = [base_dataset]
    level_data = da.from_zarr(base)
    for level, level_plan in enumerate(plan[1:], start=1):
        logger.debug("Level %d: shape=%s factors=%s", level, level_plan.shape, level_plan.factors)
        level_data = cast("da.Array", downsample(level_data, level_plan.factors, is_label))
        array = _write_level(
            zarr_group, str(level), level_data, base, level_plan, spatial_axes, chunk_size
        )
        # Re-read so the next level's graph starts from disk, not from level 0.
        level_data = da.from_zarr(array)
        datasets.append(_make_dataset(str(level), level_plan, coordinate_system.name))

    # validate_assignment re-checks the new datasets against the axes
    multiscale.datasets = datasets
    _write_multiscale(zarr_group, multiscale)
