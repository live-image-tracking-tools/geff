from pathlib import Path

import networkx as nx
import numpy as np
import pytest
import zarr

import geff


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


def test_sparse_node_props(tmp_path):
    zarr_path = Path(tmp_path) / "test.zarr"
    graph, positions = graph_sparse_node_props()
    geff.write_nx(graph, axis_names=["t", "y", "x"], path=zarr_path)
    # check that the written thing is valid
    assert Path(zarr_path).exists()
    geff.validate(zarr_path)

    zroot = zarr.open(zarr_path, mode="r")
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
    read_graph, metadata = geff.read_nx(zarr_path)
    for node, data in graph.nodes(data=True):
        assert read_graph.nodes[node] == data


def test_sparse_edge_props(tmp_path):
    zarr_path = Path(tmp_path) / "test.zarr"
    graph = graph_sparse_edge_props()
    geff.write_nx(graph, axis_names=["t", "y", "x"], path=zarr_path)
    # check that the written thing is valid
    assert Path(zarr_path).exists()
    geff.validate(zarr_path)

    zroot = zarr.open(zarr_path, mode="r")
    edge_props = zroot["edges"]["props"]
    scores = edge_props["score"]["values"][:]
    assert scores[0] == 0.1
    assert scores[2] == 0.5

    score_mask = edge_props["score"]["missing"][:]
    np.testing.assert_array_almost_equal(score_mask, np.array([0, 1, 0]))

    # read it back in and check for consistency
    read_graph, metadata = geff.read_nx(zarr_path)
    for u, v, data in graph.edges(data=True):
        assert read_graph.edges[u, v] == data


def test_missing_pos_prop(tmp_path):
    zarr_path = Path(tmp_path) / "test1.zarr"
    graph, _ = graph_sparse_node_props()
    # wrong property name
    with pytest.raises(UserWarning, match="Property .* is not present on any graph elements"):
        with pytest.raises(ValueError, match=r"Spatiotemporal property .* not found"):
            geff.write_nx(graph, axis_names=["t", "y", "z"], path=zarr_path)
    # missing property
    del graph.nodes[1]["t"]
    print(graph.nodes[1])
    with pytest.raises(ValueError, match=r"Spatiotemporal property 't' not found in : \[1\]"):
        geff.write_nx(graph, axis_names=["t", "y", "x"], path=zarr_path)
