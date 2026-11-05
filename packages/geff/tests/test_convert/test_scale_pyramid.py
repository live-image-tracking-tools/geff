import pytest

pytest.importorskip("dask")
pytest.importorskip("yaozarrs")

import dask.array as da
import numpy as np
import zarr
import zarr.storage
from yaozarrs import DimSpec, v06

from geff.convert._scale_pyramid import (
    _base_scale_and_translation,
    _compute_downsample_factors,
    _compute_num_levels,
    _downsample,
    _downsampled_shape,
    _level_chunks,
    _LevelPlan,
    _make_dataset,
    _pad_to_multiple,
    _plan_pyramid,
    _read_multiscale,
    _shard_shape,
    _spatial_axes,
    _write_level,
    _write_multiscale,
    default_chunks_and_shards,
    generate_scale_pyramid,
)

SPATIAL = [1, 2, 3]


def make_group(
    shape: tuple[int, ...] = (2, 40, 300, 301),
    scale: tuple[float, ...] = (1.0, 3.0, 1.0, 1.0),
    translation: tuple[float, ...] | None = None,
    chunks: tuple[int, ...] = (1, 40, 128, 128),
    names: tuple[str, ...] = ("t", "z", "y", "x"),
) -> tuple[zarr.Group, np.ndarray]:
    """Single-scale OME-Zarr 0.6 image in an in-memory zarr v3 group."""
    group = zarr.open_group(zarr.storage.MemoryStore(), mode="w", zarr_format=3)
    rng = np.random.default_rng(0)
    data = rng.integers(0, 255, shape).astype(np.uint16)
    group.create_array("0", data=data, chunks=chunks, dimension_names=list(names))

    translations = translation or (0.0,) * len(names)
    dims = [
        DimSpec(name=n, scale=s, translation=t)
        for n, s, t in zip(names, scale, translations, strict=True)
    ]
    multiscale = v06.Multiscale.from_dims(dims)
    group.attrs["ome"] = {
        "version": "0.6",
        "multiscales": [multiscale.model_dump(mode="json", exclude_none=True)],
    }
    return group, data


# ----------------------------------------------------------------------------
# Planning
# ----------------------------------------------------------------------------


def test_downsampled_shape_uses_ceil():
    assert _downsampled_shape((5, 7, 8), (2, 2, 1)) == (3, 4, 8)


def test_downsample_factors_isotropic():
    assert _compute_downsample_factors([1, 1, 1, 1], SPATIAL) == (1, 2, 2, 2)


def test_downsample_factors_skip_coarse_axis():
    assert _compute_downsample_factors([1, 4, 1, 1], SPATIAL) == (1, 1, 2, 2)


def test_downsample_factors_ignore_non_spatial_axis_voxel_size():
    # A tiny time scale must not be treated as the "finest" axis.
    assert _compute_downsample_factors([0.01, 1, 1, 1], SPATIAL) == (1, 2, 2, 2)


def test_compute_num_levels():
    assert _compute_num_levels((40, 100, 100), [1, 1, 1], [0, 1, 2], chunk_size=128) == 1
    assert _compute_num_levels((40, 300, 301), [3, 1, 1], [0, 1, 2], chunk_size=128) == 3


def test_plan_pyramid_shapes_scales_translations():
    plan = _plan_pyramid((2, 40, 300, 301), (1, 3, 1, 1), (0, 0, 0, 0), SPATIAL, chunk_size=128)
    assert [p.shape for p in plan] == [(2, 40, 300, 301), (2, 40, 150, 151), (2, 20, 75, 76)]
    assert [p.scale for p in plan] == [(1, 3, 1, 1), (1, 3, 2, 2), (1, 6, 4, 4)]
    assert [p.factors for p in plan] == [(1, 1, 1, 1), (1, 1, 2, 2), (1, 2, 2, 2)]
    # shift is (f - 1) / 2 voxels of the *previous* level's scale
    assert plan[0].translation == (0, 0, 0, 0)
    assert plan[1].translation == (0, 0, 0.5, 0.5)
    assert plan[2].translation == (0, 1.5, 1.5, 1.5)


def test_plan_pyramid_keeps_base_translation():
    plan = _plan_pyramid((10, 10), (1, 1), (5.0, -2.0), [0, 1], num_levels=2)
    assert plan[1].translation == (5.5, -1.5)


def test_plan_pyramid_explicit_num_levels():
    assert len(_plan_pyramid((300, 300), (1, 1), (0, 0), [0, 1], num_levels=2)) == 2
    assert len(_plan_pyramid((300, 300), (1, 1), (0, 0), [0, 1], num_levels=1)) == 1


# ----------------------------------------------------------------------------
# Array kernels
# ----------------------------------------------------------------------------


@pytest.mark.parametrize("use_dask", [False, True])
def test_pad_to_multiple_edge_pads_end(use_dask):
    data = np.arange(15).reshape(3, 5)
    padded = _pad_to_multiple(da.from_array(data) if use_dask else data, (2, 2))
    padded = np.asarray(padded)
    assert padded.shape == (4, 6)
    np.testing.assert_array_equal(padded[3], padded[2])
    np.testing.assert_array_equal(padded[:, 5], padded[:, 4])


def test_pad_to_multiple_noop_when_divisible():
    data = np.zeros((4, 6))
    assert _pad_to_multiple(data, (2, 3)) is data


@pytest.mark.parametrize("use_dask", [False, True])
def test_downsample_mean_hand_computed(use_dask):
    base = np.kron(np.array([[1, 2], [3, 4]]), np.ones((2, 2))).astype(np.uint16)
    data = da.from_array(base, chunks=2) if use_dask else base
    out = np.asarray(_downsample(data, (2, 2)))
    np.testing.assert_array_equal(out, [[1, 2], [3, 4]])
    assert out.dtype == np.uint16


def test_downsample_numpy_matches_dask_and_shape():
    rng = np.random.default_rng(1)
    data = rng.integers(0, 4, (5, 7, 9)).astype(np.uint16)
    expected = _downsample(data, (2, 2, 2))
    actual = _downsample(da.from_array(data, chunks=(2, 4, 4)), (2, 2, 2)).compute()
    assert expected.shape == (3, 4, 5)
    np.testing.assert_array_equal(expected, actual)


def test_downsample_factor_one_axes_untouched():
    data = np.arange(12, dtype=np.uint16).reshape(3, 4)
    out = _downsample(data, (1, 2))
    assert out.shape == (3, 2)


@pytest.mark.parametrize("use_dask", [False, True])
def test_downsample_mean_rounds_integers_instead_of_truncating(use_dask):
    # block means: 0.75 -> 1, 0.25 -> 0, 2.75 -> 3 (truncation would give 0, 0, 2)
    base = np.array([[0, 1, 0, 0], [1, 1, 0, 1], [2, 3, 3, 3], [3, 3, 3, 3]], dtype=np.uint16)
    data = da.from_array(base, chunks=2) if use_dask else base
    out = np.asarray(_downsample(data, (2, 2)))
    np.testing.assert_array_equal(out, [[1, 0], [3, 3]])
    assert out.dtype == np.uint16


def test_downsample_mean_does_not_round_floats():
    data = np.array([[0.0, 1.0], [1.0, 1.0]], dtype=np.float32)
    out = _downsample(data, (2, 2))
    np.testing.assert_allclose(out, [[0.75]])
    assert out.dtype == np.float32


# ----------------------------------------------------------------------------
# Metadata
# ----------------------------------------------------------------------------


def test_spatial_axes():
    group, _ = make_group()
    cs = _read_multiscale(group).intrinsic_coordinate_system
    assert _spatial_axes(cs) == SPATIAL


def test_spatial_axes_other_layout():
    group, _ = make_group(
        shape=(2, 3, 300, 301), scale=(1.0, 1.0, 1.0, 1.0), chunks=(1, 1, 128, 128),
        names=("t", "c", "y", "x"),
    )  # fmt: skip
    cs = _read_multiscale(group).intrinsic_coordinate_system
    assert _spatial_axes(cs) == [2, 3]


@pytest.mark.parametrize("translation", [None, (0.0, 1.0, 2.0, 3.0)])
def test_base_scale_and_translation(translation):
    group, _ = make_group(scale=(1.0, 2.0, 3.0, 4.0), translation=translation)
    multiscale = _read_multiscale(group)
    scale, trans = _base_scale_and_translation(multiscale.datasets[0], 4)
    assert scale == [1.0, 2.0, 3.0, 4.0]
    assert trans == list(translation or (0.0,) * 4)


def test_make_dataset_omits_zero_translation():
    plan = _LevelPlan((1, 2), (1.0, 2.0), (0.0, 0.0), (1, 1))
    ds = _make_dataset("3", plan, "intrinsic")
    assert ds.path == "3"
    (transform,) = ds.coordinateTransformations
    assert transform.type == "scale"
    assert transform.input.path == "3"
    assert transform.output.name == "intrinsic"


def test_make_dataset_nonzero_translation_is_scale_then_translation_sequence():
    plan = _LevelPlan((1, 2), (1.0, 2.0), (0.0, 0.5), (1, 1))
    ds = _make_dataset("1", plan, "intrinsic")
    (transform,) = ds.coordinateTransformations
    assert transform.type == "sequence"
    assert [t.type for t in transform.transformations] == ["scale", "translation"]
    assert transform.transformations[1].translation == [0.0, 0.5]


def test_read_write_multiscale_roundtrip_preserves_other_attrs():
    group, _ = make_group()
    group.attrs["custom"] = {"keep": "me"}
    multiscale = _read_multiscale(group)

    # Add an extra multiscale so we can check only the first is replaced.
    ome = dict(group.attrs["ome"])
    ome["multiscales"] = [*ome["multiscales"], {"name": "other"}]
    group.attrs["ome"] = ome

    multiscale.datasets.append(
        _make_dataset(
            "1",
            _LevelPlan((2, 40, 150, 151), (1, 3, 2, 2), (0, 0, 0.5, 0.5), (1, 1, 2, 2)),
            "intrinsic",
        )
    )
    _write_multiscale(group, multiscale)

    reread = _read_multiscale(group)
    assert [d.path for d in reread.datasets] == ["0", "1"]
    assert group.attrs["custom"] == {"keep": "me"}
    assert group.attrs["ome"]["version"] == "0.6"
    assert group.attrs["ome"]["multiscales"][1] == {"name": "other"}


def test_read_multiscale_missing_raises():
    group = zarr.open_group(zarr.storage.MemoryStore(), mode="w", zarr_format=3)
    with pytest.raises(ValueError, match="No multiscales"):
        _read_multiscale(group)


# ----------------------------------------------------------------------------
# Level writing
# ----------------------------------------------------------------------------


def test_level_chunks_spatial_chunk_size_clipped_and_others_one():
    assert _level_chunks((2, 20, 75, 76), SPATIAL, 128) == (1, 20, 75, 76)
    assert _level_chunks((2, 40, 300, 301), SPATIAL, 128) == (1, 40, 128, 128)
    assert _level_chunks((2, 3, 300, 301), [2, 3], 64) == (1, 1, 64, 64)


def test_default_chunks_and_shards():
    chunks, shards = default_chunks_and_shards((3, 1, 1, 300, 200), [2, 3, 4])
    assert chunks == (1, 1, 1, 128, 128)
    assert shards == (1, 1, 1, 384, 256)


def test_shard_shape_rounds_spatial_up_to_chunks_and_keeps_others():
    assert _shard_shape((2, 40, 150, 151), (1, 40, 128, 128), SPATIAL) == (1, 40, 256, 256)
    assert _shard_shape((2, 20, 75, 76), (1, 20, 75, 76), SPATIAL) == (1, 20, 75, 76)


def test_write_level_creates_sharded_array_with_data():
    group, base_data = make_group()
    base = group["0"]
    plan = _LevelPlan((2, 40, 150, 151), (1.0, 3.0, 2.0, 2.0), (0, 0, 0.5, 0.5), (1, 1, 2, 2))
    data = _downsample(da.from_array(base_data, chunks=(1, 40, 64, 64)), plan.factors)

    array = _write_level(group, "1", data, base, plan, SPATIAL, 128)

    assert array.shape == plan.shape
    assert array.chunks == (1, 40, 128, 128)
    assert array.shards == (1, 40, 256, 256)
    assert array.dtype == base.dtype
    assert array.metadata.dimension_names == ("t", "z", "y", "x")
    np.testing.assert_array_equal(array[:], data.compute())


# ----------------------------------------------------------------------------
# End to end
# ----------------------------------------------------------------------------


def test_generate_scale_pyramid():
    group, base_data = make_group()
    generate_scale_pyramid(group)

    multiscale = _read_multiscale(group)
    assert [d.path for d in multiscale.datasets] == ["0", "1", "2"]

    shapes = [group[d.path].shape for d in multiscale.datasets]
    assert shapes == [(2, 40, 300, 301), (2, 40, 150, 151), (2, 20, 75, 76)]

    scales, translations = zip(
        *(_base_scale_and_translation(d, 4) for d in multiscale.datasets), strict=True
    )
    assert scales == ([1, 3, 1, 1], [1, 3, 2, 2], [1, 6, 4, 4])
    assert translations == ([0] * 4, [0, 0, 0.5, 0.5], [0, 1.5, 1.5, 1.5])

    # scale 0 untouched, level 1 equals one downsampling step of scale 0
    np.testing.assert_array_equal(group["0"][:], base_data)
    np.testing.assert_array_equal(group["1"][:], _downsample(base_data, (1, 1, 2, 2)))
    np.testing.assert_array_equal(group["2"][:], _downsample(group["1"][:], (1, 2, 2, 2)))
    assert group["2"].shards == (1, 20, 75, 76)


def test_generate_scale_pyramid_respects_base_translation():
    group, _ = make_group(translation=(10.0, 0.0, 100.0, 200.0))
    generate_scale_pyramid(group, num_levels=2)
    multiscale = _read_multiscale(group)
    _, translation = _base_scale_and_translation(multiscale.datasets[1], 4)
    assert translation == [10.0, 0.0, 100.5, 200.5]


def test_generate_scale_pyramid_single_level_is_noop():
    group, _ = make_group()
    generate_scale_pyramid(group, num_levels=1)
    multiscale = _read_multiscale(group)
    assert [d.path for d in multiscale.datasets] == ["0"]
    assert "1" not in group


def test_generate_scale_pyramid_existing_pyramid_raises():
    group, _ = make_group()
    generate_scale_pyramid(group)
    with pytest.raises(ValueError, match="already exists"):
        generate_scale_pyramid(group)


def test_generate_scale_pyramid_small_image_needs_no_levels():
    group, _ = make_group(shape=(2, 10, 64, 64), chunks=(1, 10, 64, 64))
    generate_scale_pyramid(group)
    assert len(_read_multiscale(group).datasets) == 1


def test_generate_scale_pyramid_rechunks_levels_from_whole_frame_base():
    group, _ = make_group(chunks=(1, 40, 300, 301))
    generate_scale_pyramid(group)
    assert group["0"].chunks == (1, 40, 300, 301)  # scale 0 is left as written
    assert group["1"].chunks == (1, 40, 128, 128)
    assert group["1"].shards == (1, 40, 256, 256)


def test_generate_scale_pyramid_chunk_size_sets_new_level_chunks():
    group, _ = make_group()
    generate_scale_pyramid(group, chunk_size=64)
    assert group["1"].chunks == (1, 40, 64, 64)
    assert group["1"].shards == (1, 40, 192, 192)


def test_generate_scale_pyramid_with_channel_axis():
    group, base_data = make_group(
        shape=(2, 3, 20, 300, 301), scale=(1.0, 1.0, 2.0, 1.0, 1.0), chunks=(1, 1, 20, 128, 128),
        names=("t", "c", "z", "y", "x"),
    )  # fmt: skip
    generate_scale_pyramid(group)

    assert group["1"].shape == (2, 3, 20, 150, 151)
    assert group["1"].shards == (1, 1, 20, 256, 256)
    np.testing.assert_array_equal(group["1"][:], _downsample(base_data, (1, 1, 1, 2, 2)))
    scale, translation = _base_scale_and_translation(_read_multiscale(group).datasets[1], 5)
    assert scale == [1.0, 1.0, 2.0, 2.0, 2.0]
    assert translation == [0.0, 0.0, 0.0, 0.5, 0.5]


def test_generate_scale_pyramid_requires_ome_metadata():
    group = zarr.open_group(zarr.storage.MemoryStore(), mode="w", zarr_format=3)
    group.create_array("0", shape=(2, 300, 300), chunks=(1, 128, 128), dtype="uint16")
    with pytest.raises(ValueError, match="No multiscales"):
        generate_scale_pyramid(group)
