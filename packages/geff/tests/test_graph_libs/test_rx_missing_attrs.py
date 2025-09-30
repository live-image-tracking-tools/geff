from pathlib import Path

import numpy as np
import pytest
import zarr

import geff

rx = pytest.importorskip("rustworkx")
from geff._graph_libs._rustworkx import RxBackend  # noqa: E402


def create_rx_graph_sparse_node_props():
    """Create a rustworkx graph with sparse node properties."""
    graph = rx.PyGraph()

    # Node data with some missing score properties
    node_data = [
        {"t": 0, "y": 1, "x": 2, "score": 0.5},  # node 0
        {"t": 0, "y": 0, "x": 0, "score": 0.2},  # node 1
        {"t": 1, "y": 1, "x": 3},  # node 2 - missing score
        {"t": 1, "y": 5, "x": 2},  # node 3 - missing score
        {"t": 1, "y": 7, "x": 6, "score": 0.1},  # node 4
    ]

    node_indices = graph.add_nodes_from(node_data)
    positions = [[0, 1, 2], [0, 0, 0], [1, 1, 3], [1, 5, 2], [1, 7, 6]]

    return graph, node_indices, positions


def create_rx_graph_sparse_edge_props():
    """Create a rustworkx graph with sparse edge properties."""
    graph, node_indices, positions = create_rx_graph_sparse_node_props()

    # Add edges with some missing score properties
    edges = [
        (node_indices[0], node_indices[2], {"score": 0.1}),  # has score
        (node_indices[0], node_indices[3], {}),  # missing score
        (node_indices[1], node_indices[4], {"score": 0.5}),  # has score
    ]

    graph.add_edges_from(edges)
    return graph, node_indices


def test_sparse_node_props_rx(tmp_path) -> None:
    """Test rustworkx graphs with sparse node properties."""
    zarr_path = Path(tmp_path) / "test.zarr"
    graph, node_indices, positions = create_rx_graph_sparse_node_props()

    # Create node_id_dict to map rx indices to specific ids [1,2,3,4,5]
    node_id_dict = {idx: idx + 1 for idx in node_indices}

    RxBackend.write(graph, store=zarr_path, node_id_dict=node_id_dict, axis_names=["t", "y", "x"])

    # Check that the written file is valid
    assert Path(zarr_path).exists()
    geff.validate_structure(zarr_path)

    # Check the written data
    zroot = zarr.open_group(zarr_path, mode="r")
    node_props = zroot["nodes"]["props"]

    # Check time values
    t = node_props["t"]["values"][:]
    np.testing.assert_array_almost_equal(np.array(positions)[:, 0], t)

    # Check scores and missing mask
    scores = node_props["score"]["values"][:]
    assert scores[0] == 0.5  # node 1
    assert scores[1] == 0.2  # node 2
    assert scores[4] == 0.1  # node 5

    score_mask = node_props["score"]["missing"][:]
    np.testing.assert_array_almost_equal(score_mask, np.array([0, 0, 1, 1, 0]))

    # Read it back and verify consistency
    read_graph, metadata = RxBackend.read(zarr_path)

    # Check that we have the right number of nodes and structure
    assert read_graph.num_nodes() == graph.num_nodes()
    assert read_graph.num_edges() == graph.num_edges()


def test_sparse_edge_props_rx(tmp_path) -> None:
    """Test rustworkx graphs with sparse edge properties."""
    zarr_path = Path(tmp_path) / "test.zarr"
    graph, node_indices = create_rx_graph_sparse_edge_props()

    # Create node_id_dict to map rx indices to specific ids [1,2,3,4,5]
    node_id_dict = {idx: idx + 1 for idx in node_indices}

    RxBackend.write(graph, store=zarr_path, node_id_dict=node_id_dict, axis_names=["t", "y", "x"])

    # Check that the written file is valid
    assert Path(zarr_path).exists()
    geff.validate_structure(zarr_path)

    # Check the written data
    zroot = zarr.open_group(zarr_path, mode="r")
    edge_props = zroot["edges"]["props"]

    # Check edge scores
    scores = edge_props["score"]["values"][:]
    assert scores[0] == 0.1  # first edge
    assert scores[2] == 0.5  # third edge

    score_mask = edge_props["score"]["missing"][:]
    np.testing.assert_array_almost_equal(score_mask, np.array([0, 1, 0]))

    # Read it back and verify consistency
    read_graph, metadata = RxBackend.read(zarr_path)

    # Check basic structure
    assert read_graph.num_nodes() == graph.num_nodes()
    assert read_graph.num_edges() == graph.num_edges()


def test_missing_pos_prop_rx(tmp_path) -> None:
    """Test rustworkx graphs with missing positional properties."""
    graph, node_indices, positions = create_rx_graph_sparse_node_props()

    # Test with wrong property name (z instead of x)
    zarr_path = Path(tmp_path) / "test1.zarr"
    with pytest.raises(ValueError, match=r"Spatiotemporal property .* not found"):
        RxBackend.write(graph, store=zarr_path, axis_names=["t", "y", "z"])
