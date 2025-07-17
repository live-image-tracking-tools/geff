import networkx as nx
import numpy as np
import pytest

import geff

node_dtypes = ["int8", "uint8", "int16", "uint16", "str"]
node_attr_dtypes = [
    {"position": "double"},
    {"position": "int"},
]
edge_attr_dtypes = [
    {"score": "float64", "color": "uint8"},
    {"score": "float32", "color": "int16"},
]

# TODO: mixed dtypes?


@pytest.mark.parametrize("node_dtype", node_dtypes)
@pytest.mark.parametrize("node_attr_dtypes", node_attr_dtypes)
@pytest.mark.parametrize("edge_attr_dtypes", edge_attr_dtypes)
@pytest.mark.parametrize("directed", [True, False])
def test_read_write_consistency(
    path_w_expected_graph_attrs,
    node_dtype,
    node_attr_dtypes,
    edge_attr_dtypes,
    directed,
):
    path, graph_attrs = path_w_expected_graph_attrs(
        node_dtype, node_attr_dtypes, edge_attr_dtypes, directed
    )

    graph = geff.read_nx(path)

    assert set(graph.nodes) == {*graph_attrs["nodes"].tolist()}
    assert set(graph.edges) == {
        *[tuple(edges) for edges in graph_attrs["edges"].tolist()]
    }
    for idx, node in enumerate(graph_attrs["nodes"]):
        np.testing.assert_array_equal(
            graph.nodes[node.item()]["pos"], graph_attrs["node_positions"][idx]
        )

    for idx, edge in enumerate(graph_attrs["edges"]):
        for name, values in graph_attrs["edge_attrs"].items():
            assert graph.edges[edge.tolist()][name] == values[idx].item()

    assert graph.graph["axis_names"] == graph_attrs["axis_names"]
    assert graph.graph["axis_units"] == graph_attrs["axis_units"]


@pytest.mark.parametrize("node_dtype", node_dtypes)
@pytest.mark.parametrize("node_attr_dtypes", node_attr_dtypes)
@pytest.mark.parametrize("edge_attr_dtypes", edge_attr_dtypes)
@pytest.mark.parametrize("directed", [True, False])
def test_read_write_no_spatial(
    tmp_path, node_dtype, node_attr_dtypes, edge_attr_dtypes, directed
):
    graph = nx.DiGraph() if directed else nx.Graph()

    nodes = np.array([10, 2, 127, 4, 5], dtype=node_dtype)
    attrs = np.array([4, 9, 10, 2, 8], dtype=node_attr_dtypes["position"])
    for node, pos in zip(nodes, attrs):
        graph.add_node(node.item(), attr=pos.tolist())

    edges = np.array(
        [
            [10, 2],
            [2, 127],
            [2, 4],
            [4, 5],
        ],
        dtype=node_dtype,
    )
    scores = np.array([0.1, 0.2, 0.3, 0.4], dtype=edge_attr_dtypes["score"])
    colors = np.array([1, 2, 3, 4], dtype=edge_attr_dtypes["color"])
    for edge, score, color in zip(edges, scores, colors):
        graph.add_edge(*edge.tolist(), score=score.item(), color=color.item())

    path = tmp_path / "rw_consistency.zarr/graph"

    geff.write_nx(graph, path)

    compare = geff.read_nx(path)

    assert set(graph.nodes) == set(compare.nodes)
    assert set(graph.edges) == set(compare.edges)
    for node in nodes:
        assert graph.nodes[node.item()]["attr"] == compare.nodes[node.item()]["attr"]

    for edge in edges:
        assert (
            graph.edges[edge.tolist()]["score"] == compare.edges[edge.tolist()]["score"]
        )
        assert (
            graph.edges[edge.tolist()]["color"] == compare.edges[edge.tolist()]["color"]
        )


def test_write_empty_graph():
    graph = nx.DiGraph()
    with pytest.warns(match="Graph is empty - not writing anything "):
        geff.write_nx(graph, position_attr="pos", path=".")
