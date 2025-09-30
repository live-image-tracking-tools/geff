from pathlib import Path

import networkx as nx
import numpy as np
import pytest
import zarr

import geff
from geff._graph_libs._networkx import NxBackend


def graph_sparse_node_props():
    graph = nx.Graph()
    nodes = [1, 2, 3, 4, 5]
    positions = [
        [0, 1, 2],
        [0, 0, 0],
        [1, 1, 3],
        [1, 5, 2],
        [1, 7, 6],
    ]
    node_scores = [0.5, 0.2, None, None, 0.1]
    for node, pos, score in zip(nodes, positions, node_scores, strict=False):
        t, y, x = pos
        if score is not None:
            graph.add_node(node, t=t, y=y, x=x, score=score)
        else:
            graph.add_node(node, t=t, y=y, x=x)
    return graph, positions


def graph_sparse_edge_props():
    graph, _ = graph_sparse_node_props()
    edges = [
        [1, 3],
        [1, 4],
        [2, 5],
    ]
    edge_scores = [0.1, None, 0.5]
    for edge, score in zip(edges, edge_scores, strict=False):
        if score is not None:
            graph.add_edge(edge[0], edge[1], score=score)
        else:
            graph.add_edge(edge[0], edge[1])
    return graph


def test_sparse_node_props(tmp_path) -> None:
    zarr_path = Path(tmp_path) / "test.zarr"
    graph, positions = graph_sparse_node_props()
    NxBackend.write(graph, axis_names=["t", "y", "x"], store=zarr_path)
    # check that the written thing is valid
    assert Path(zarr_path).exists()
    geff.validate_structure(zarr_path)

    zroot = zarr.open_group(zarr_path, mode="r")
    node_props = zroot["nodes"]["props"]
    t = node_props["t"]["values"][:]
    # TODO: test other dimensions
    np.testing.assert_array_almost_equal(np.array(positions)[:, 0], t)
    scores = node_props["score"]["values"][:]
    assert scores[0] == 0.5
    assert scores[1] == 0.2
    assert scores[4] == 0.1
    score_mask = node_props["score"]["missing"][:]
    np.testing.assert_array_almost_equal(score_mask, np.array([0, 0, 1, 1, 0]))

    # read it back in and check for consistency
    read_graph, metadata = NxBackend.read(zarr_path)
    for node, data in graph.nodes(data=True):
        assert read_graph.nodes[node] == data


def test_sparse_edge_props(tmp_path) -> None:
    zarr_path = Path(tmp_path) / "test.zarr"
    graph = graph_sparse_edge_props()
    NxBackend.write(graph, axis_names=["t", "y", "x"], store=zarr_path)
    # check that the written thing is valid
    assert Path(zarr_path).exists()
    geff.validate_structure(zarr_path)

    zroot = zarr.open_group(zarr_path, mode="r")
    edge_props = zroot["edges"]["props"]
    scores = edge_props["score"]["values"][:]
    assert scores[0] == 0.1
    assert scores[2] == 0.5

    score_mask = edge_props["score"]["missing"][:]
    np.testing.assert_array_almost_equal(score_mask, np.array([0, 1, 0]))

    # read it back in and check for consistency
    read_graph, metadata = NxBackend.read(zarr_path)
    for u, v, data in graph.edges(data=True):
        assert read_graph.edges[u, v] == data


def test_missing_pos_prop(tmp_path) -> None:
    # Test graph has t, y, x
    # Some nodes have score
    graph, _ = graph_sparse_node_props()
    # axis name that does not exist as property on graph
    zarr_path = Path(tmp_path) / "test1.zarr"
    with pytest.raises(ValueError, match=r"Spatiotemporal property .* not found"):
        NxBackend.write(graph, axis_names=["t", "y", "z"], store=zarr_path)
