import numpy as np
import pytest

from geff.testing.data import create_mock_geff, create_simple_2d_geff
from geff.validate.segmentation import (
    axes_match_seg_dims,
    graph_is_in_seg_bounds,
    has_seg_ids_at_coords,
    has_seg_ids_at_time_points,
    has_valid_seg_id,
)


@pytest.fixture
def valid_store_and_attrs():
    store, memory_geff = create_mock_geff(
        node_id_dtype="uint",
        node_axis_dtypes={"position": "float64", "time": "float64"},
        directed=True,
        num_nodes=5,
        num_edges=2,
        include_t=True,
        include_z=False,
        include_y=True,
        include_x=True,
        extra_node_props={"seg_id": "int"},
    )
    return store, memory_geff


@pytest.fixture
def invalid_store_and_attrs():
    store, memory_geff = create_mock_geff(
        node_id_dtype="uint8",
        node_axis_dtypes={"position": "float64", "time": "float64"},
        directed=True,
        num_nodes=5,
        num_edges=2,
        include_t=True,
        include_z=False,
        include_y=True,
        include_x=True,
        extra_node_props={"seg_id": "float32"},  # floats should not be allowed for seg_id
    )
    return store, memory_geff


@pytest.fixture
def valid_segmentation():
    shape = (6, 600, 200)  # (t, y, x)
    seg = np.zeros(shape, dtype=int)

    x_float = [1.0, 0.775, 0.55, 0.325, 0.1]
    y_vals = [100, 200, 300, 400, 500]
    scale = [1, 1, 100]

    for t, y, x_f, seg_id in zip(range(5), y_vals, x_float, range(5), strict=False):
        x = int(x_f * scale[2])
        seg[t, y, x] = seg_id
    return seg


def test_has_valid_seg_id(valid_store_and_attrs, invalid_store_and_attrs) -> None:
    _, mem_geff = valid_store_and_attrs  # valid seg id
    assert has_valid_seg_id(mem_geff)[0] is True

    _, mem_geff = invalid_store_and_attrs  # seg_id is of type float32
    assert has_valid_seg_id(mem_geff)[0] is False

    _, mem_geff = create_simple_2d_geff()  # no seg_id
    assert has_valid_seg_id(mem_geff)[0] is False

    # Add missing array with no missing values
    _, mem_geff = valid_store_and_attrs
    n_nodes = mem_geff["node_ids"].shape[0]
    mem_geff["node_props"]["seg_id"]["missing"] = np.array([False] * n_nodes)
    assert has_valid_seg_id(mem_geff)[0] is True

    # Add in missing values
    mem_geff["node_props"]["seg_id"]["missing"][0] = True
    assert has_valid_seg_id(mem_geff)[0] is False


def test_axes_match_seg_dims(valid_store_and_attrs, valid_segmentation) -> None:
    _, mem_geff = valid_store_and_attrs
    assert axes_match_seg_dims(mem_geff, valid_segmentation)[0] is True

    seg_invalid = np.zeros((600, 200))  # invalid, 2D instead of 3D
    assert axes_match_seg_dims(mem_geff, seg_invalid)[0] is False


def test_graph_is_in_seg_bounds(valid_store_and_attrs, valid_segmentation) -> None:
    _, memory_geff = valid_store_and_attrs
    scale = (1, 1, 100)
    assert graph_is_in_seg_bounds(memory_geff, valid_segmentation, scale=scale)[0] is True

    # Invalid scale → graph exceeds segmentation shape
    bad_scale = (1, 1, 0.001)
    assert graph_is_in_seg_bounds(memory_geff, valid_segmentation, scale=bad_scale)[0] is False

    # Mismatched scale length
    bad_scale_len = (1, 1)
    assert graph_is_in_seg_bounds(memory_geff, valid_segmentation, scale=bad_scale_len)[0] is False


@pytest.mark.parametrize(
    "time_points, seg_ids, expected",
    [
        ([0, 1, 2, 3, 4], [0, 1, 2, 3, 4], True),
        ([0, 1, 2], [0, 99, 2], False),  # one bad seg_id
        ([10], [1], False),  # out-of-bounds time
    ],
)
def test_has_seg_ids_at_time_points(
    valid_store_and_attrs: tuple,
    valid_segmentation: np.ndarray,
    time_points: list[int],
    seg_ids: list[int],
    expected: bool,
) -> None:
    _, mem_geff = valid_store_and_attrs
    assert (
        has_seg_ids_at_time_points(
            valid_segmentation, time_points, seg_ids, metadata=mem_geff["metadata"]
        )[0]
        == expected
    )


@pytest.mark.parametrize(
    "coords, seg_ids, expected",
    [
        # Coords are in world units, scaling will map them to pixel space
        (
            [(0, 100, 1.0), (1, 200, 0.775), (2, 300, 0.55), (3, 400, 0.325), (4, 500, 0.1)],
            [0, 1, 2, 3, 4],
            True,
        ),
        ([(0, 100, 1.0)], [99], False),  # Wrong seg_id
        ([(10, 100, 1.0)], [1], False),  # Out-of-bounds time
        ([(0, 100, 1.0)], [0, 1], False),  # Mismatched lengths
    ],
)
def test_has_seg_ids_at_coords(
    valid_segmentation: np.ndarray,
    coords: list[tuple[int, int, float]],
    seg_ids: list[int],
    expected: bool,
) -> None:
    scale = (1, 1, 100)
    if len(coords) != len(seg_ids):
        assert has_seg_ids_at_coords(valid_segmentation, coords, seg_ids, scale=scale)[0] is False
    else:
        assert (
            has_seg_ids_at_coords(valid_segmentation, coords, seg_ids, scale=scale)[0] == expected
        )
