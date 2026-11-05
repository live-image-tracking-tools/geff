"""Generate lower-resolution scales for an existing single-scale OME-Zarr.

Downsampling is anisotropy-aware: a spatial axis is only downsampled (factor 2) if its voxel size is
within 2x of the finest spatial axis. Non-spatial axes are never downsampled.
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


def _downsampled_shape(shape: Sequence[int], factors: Sequence[int]) -> tuple[int, ...]:
    """Shape after downsampling: ``ceil(s / f)`` per dimension."""
    return tuple((s + f - 1) // f for s, f in zip(shape, factors, strict=True))


def _compute_downsample_factors(
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


def _compute_num_levels(
    shape: Sequence[int],
    voxel_size: Sequence[float],
    spatial_axes: Sequence[int],
    chunk_size: int = DEFAULT_SPATIAL_CHUNK_SIZE,
) -> int:
    """Compute how many pyramid levels are needed for the coarsest level to fit in one chunk.

    Simulates the downsampling that `_plan_pyramid` performs, level by level, until every
    spatial axis is at most `chunk_size` voxels long. Because downsampling is anisotropy-aware,
    an axis with much coarser voxels (e.g. z) is skipped until the finer axes catch up, so it
    can take more levels than ``ceil(log2(max(shape) / chunk_size))``.

    Args:
        shape: Shape of the full resolution array, with one entry per axis.
        voxel_size: Voxel size (scale) of the full resolution array, with one entry per axis.
        spatial_axes: Indices of the spatial axes. Other axes are never downsampled and do not
            count towards the chunk size limit.
        chunk_size: Maximum length of a spatial axis in the coarsest level. Defaults to
            `DEFAULT_SPATIAL_CHUNK_SIZE`.

    Returns:
        The number of levels, including the full resolution level. This is 1 if every spatial
        axis already fits in one chunk.
    """
    shape = list(shape)
    voxel = list(voxel_size)
    levels = 1
    while any(shape[i] > chunk_size for i in spatial_axes):
        factors = _compute_downsample_factors(voxel, spatial_axes)
        shape = list(_downsampled_shape(shape, factors))
        voxel = [v * f for v, f in zip(voxel, factors, strict=True)]
        levels += 1
    return levels


class _LevelPlan(NamedTuple):
    shape: tuple[int, ...]
    scale: tuple[float, ...]
    translation: tuple[float, ...]
    factors: tuple[int, ...]  # relative to the previous level; all 1s for level 0


def _plan_pyramid(
    shape: Sequence[int],
    scale: Sequence[float],
    translation: Sequence[float],
    spatial_axes: Sequence[int],
    num_levels: int | None = None,
    chunk_size: int = DEFAULT_SPATIAL_CHUNK_SIZE,
) -> list[_LevelPlan]:
    """Plan the levels of a scale pyramid without reading or writing any data.

    Each level is downsampled from the previous one, using the factors from the
    anisotropy-aware rule: a spatial axis is only halved if its voxel size is within 2x of the
    finest spatial axis, and non-spatial axes are never downsampled. See `_LevelPlan` for what is
    planned per level.

    Block downsampling by factor ``f`` places each output voxel center at the middle of ``f``
    input voxels, so the origin shifts by ``(f - 1) / 2`` voxels of the previous level. These
    shifts accumulate in the translation, so each level stays aligned with the full resolution
    one.

    Args:
        shape: Shape of the full resolution array, with one entry per axis.
        scale: Voxel size of the full resolution array, with one entry per axis.
        translation: Offset of the full resolution array, with one entry per axis.
        spatial_axes: Indices of the spatial axes.
        num_levels: Total number of levels, including the full resolution one. If None, it is
            computed with `_compute_num_levels` so the coarsest level fits in one chunk.
        chunk_size: Maximum spatial axis length of the coarsest level, used when `num_levels`
            is None. Defaults to `DEFAULT_SPATIAL_CHUNK_SIZE`.

    Returns:
        One `_LevelPlan` per level, ordered from full resolution (level 0, with factors of all
        1s) to the coarsest level.
    """
    if num_levels is None:
        num_levels = _compute_num_levels(shape, scale, spatial_axes, chunk_size)

    current = _LevelPlan(
        tuple(shape),
        tuple(float(s) for s in scale),
        tuple(float(t) for t in translation),
        (1,) * len(shape),
    )
    plan = [current]
    for _ in range(1, num_levels):
        factors = _compute_downsample_factors(current.scale, spatial_axes)
        shift = [(f - 1) / 2 * s for f, s in zip(factors, current.scale, strict=True)]
        current = _LevelPlan(
            _downsampled_shape(current.shape, factors),
            tuple(s * f for s, f in zip(current.scale, factors, strict=True)),
            tuple(t + d for t, d in zip(current.translation, shift, strict=True)),
            factors,
        )
        plan.append(current)
    return plan


# --------------------------------------------------------------------------- #
# Array kernels (numpy / dask, no zarr)
# --------------------------------------------------------------------------- #


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


def _downsample(
    data: np.ndarray | da.Array,
    factors: Sequence[int],
) -> np.ndarray | da.Array:
    """Downsample by per-axis factors, with output shape ``ceil(s / f)``.

    Uses block mean, rounded for integer dtypes so values are not biased low by
    truncation. Accepts numpy or dask arrays.
    """
    original_dtype = data.dtype
    data = _pad_to_multiple(data, factors)

    if isinstance(data, da.Array):
        return da.coarsen(_block_mean, data, dict(enumerate(factors)), trim_excess=False).astype(
            original_dtype
        )

    new_shape = []
    axes_to_reduce = []
    for i, (s, f) in enumerate(zip(data.shape, factors, strict=True)):
        new_shape.extend([s // f, f])
        axes_to_reduce.append(2 * i + 1)
    return _block_mean(data.reshape(new_shape), axis=tuple(axes_to_reduce)).astype(original_dtype)


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


def _spatial_axes(coordinate_system: v06.CoordinateSystem) -> list[int]:
    """Indices of the spatial axes."""
    return [i for i, ax in enumerate(coordinate_system.axes) if ax.type == "space"]


def _base_scale_and_translation(dataset: v06.Dataset, ndim: int) -> tuple[list[float], list[float]]:
    """Scale and translation of a dataset, defaulting to 1s and 0s if absent."""
    scale_transform = dataset.scale_transform
    translation_transform = dataset.translation_transform
    scale = list(scale_transform.scale) if scale_transform else [1.0] * ndim
    translation = list(translation_transform.translation) if translation_transform else [0.0] * ndim
    return scale, translation


def _make_dataset(path: str, level_plan: _LevelPlan, coordinate_system: str) -> v06.Dataset:
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
    level_plan: _LevelPlan,
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

    Raises:
        ValueError: If the group already has more than one scale.
    """
    multiscale = _read_multiscale(zarr_group)
    if len(multiscale.datasets) != 1:
        raise ValueError(
            f"Expected a single-scale OME-Zarr but found {len(multiscale.datasets)} scales: "
            "a scale pyramid already exists."
        )
    coordinate_system = multiscale.intrinsic_coordinate_system
    spatial_axes = _spatial_axes(coordinate_system)

    base_dataset = multiscale.datasets[0]
    base = zarr_group[base_dataset.path]
    if not isinstance(base, zarr.Array):
        raise TypeError(f"Expected {base_dataset.path!r} to be an array")

    base_scale, base_translation = _base_scale_and_translation(base_dataset, base.ndim)
    plan = _plan_pyramid(
        base.shape, base_scale, base_translation, spatial_axes, num_levels, chunk_size
    )

    datasets = [base_dataset]
    level_data = da.from_zarr(base)
    for level, level_plan in enumerate(plan[1:], start=1):
        logger.debug("Level %d: shape=%s factors=%s", level, level_plan.shape, level_plan.factors)
        level_data = cast("da.Array", _downsample(level_data, level_plan.factors))
        array = _write_level(
            zarr_group, str(level), level_data, base, level_plan, spatial_axes, chunk_size
        )
        # Re-read so the next level's graph starts from disk, not from level 0.
        level_data = da.from_zarr(array)
        datasets.append(_make_dataset(str(level), level_plan, coordinate_system.name))

    # validate_assignment re-checks the new datasets against the axes
    multiscale.datasets = datasets
    _write_multiscale(zarr_group, multiscale)
