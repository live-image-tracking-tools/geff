import networkx as nx
import numpy as np
import pytest

import geff

node_id_dtypes = ["int8", "uint8", "int16", "uint16", "str"]
node_prop_dtypes = [
    {"position": "double", "time": "double"},
    {"position": "int", "time": "int"},
]
edge_prop_dtypes = [
    {"score": "float64", "color": "uint8"},
    {"score": "float32", "color": "int16"},
]

# TODO: mixed dtypes?


@pytest.mark.parametrize("node_id_dtype", node_id_dtypes)
@pytest.mark.parametrize("node_prop_dtypes", node_prop_dtypes)
@pytest.mark.parametrize("edge_prop_dtypes", edge_prop_dtypes)
@pytest.mark.parametrize("directed", [True, False])
@pytest.mark.parametrize("include_t", [True, False])
@pytest.mark.parametrize("include_z", [True, False])
def test_read_write_consistency(
    path_w_expected_graph_props,
    node_id_dtype,
    node_prop_dtypes,
    edge_prop_dtypes,
    directed,
    include_t,
    include_z,
):
    path, graph_props = path_w_expected_graph_props(
        node_id_dtype,
        node_prop_dtypes,
        edge_prop_dtypes,
        directed,
        include_t=include_t,
        include_z=include_z,
    )

    graph = geff.read_nx(path)

    assert set(graph.nodes) == {*graph_props["nodes"].tolist()}
    assert set(graph.edges) == {*[tuple(edges) for edges in graph_props["edges"].tolist()]}
    for idx, node in enumerate(graph_props["nodes"]):
        if include_t and len(graph_props["t"]) > 0:
            np.testing.assert_array_equal(graph.nodes[node.item()]["t"], graph_props["t"][idx])
        if include_z and len(graph_props["z"]) > 0:
            np.testing.assert_array_equal(graph.nodes[node.item()]["z"], graph_props["z"][idx])
        # TODO: test other dimensions

    for idx, edge in enumerate(graph_props["edges"]):
        for name, values in graph_props["edge_props"].items():
            assert graph.edges[edge.tolist()][name] == values[idx].item()

    # TODO: test metadata
    # assert graph.graph["axis_names"] == graph_props["axis_names"]
    # assert graph.graph["axis_units"] == graph_props["axis_units"]


@pytest.mark.parametrize("node_id_dtype", node_id_dtypes)
@pytest.mark.parametrize("node_prop_dtypes", node_prop_dtypes)
@pytest.mark.parametrize("edge_prop_dtypes", edge_prop_dtypes)
@pytest.mark.parametrize("directed", [True, False])
def test_read_write_no_spatial(
    tmp_path, node_id_dtype, node_prop_dtypes, edge_prop_dtypes, directed
):
    graph = nx.DiGraph() if directed else nx.Graph()

    nodes = np.array([10, 2, 127, 4, 5], dtype=node_id_dtype)
    props = np.array([4, 9, 10, 2, 8], dtype=node_prop_dtypes["position"])
    for node, pos in zip(nodes, props):
        graph.add_node(node.item(), attr=pos)

    edges = np.array(
        [
            [10, 2],
            [2, 127],
            [2, 4],
            [4, 5],
        ],
        dtype=node_id_dtype,
    )
    scores = np.array([0.1, 0.2, 0.3, 0.4], dtype=edge_prop_dtypes["score"])
    colors = np.array([1, 2, 3, 4], dtype=edge_prop_dtypes["color"])
    for edge, score, color in zip(edges, scores, colors):
        graph.add_edge(*edge.tolist(), score=score.item(), color=color.item())

    path = tmp_path / "rw_consistency.zarr/graph"

    geff.write_nx(graph, path, axis_names=[])

    compare = geff.read_nx(path)

    assert set(graph.nodes) == set(compare.nodes)
    assert set(graph.edges) == set(compare.edges)
    for node in nodes:
        assert graph.nodes[node.item()]["attr"] == compare.nodes[node.item()]["attr"]

    for edge in edges:
        assert graph.edges[edge.tolist()]["score"] == compare.edges[edge.tolist()]["score"]
        assert graph.edges[edge.tolist()]["color"] == compare.edges[edge.tolist()]["color"]


def test_write_empty_graph(tmp_path):
    graph = nx.DiGraph()
    geff.write_nx(graph, axis_names=["t", "y", "x"], path=tmp_path / "empty.zarr")
