import numpy as np
import pytest
import spatial_graph as sg

import geff

node_dtypes = ["int8", "uint8", "int16", "uint16"]
node_attr_dtypes = [
    {"position": "double"},
    {"position": "int"},
]
edge_attr_dtypes = [
    {"score": "float64", "color": "uint8"},
    {"score": "float32", "color": "int16"},
]


@pytest.mark.parametrize("node_dtype", node_dtypes)
@pytest.mark.parametrize("node_attr_dtypes", node_attr_dtypes)
@pytest.mark.parametrize("edge_attr_dtypes", edge_attr_dtypes)
@pytest.mark.parametrize("directed", [True, False])
def test_read_write_consistency(
    path_w_expected_graph_props,
    node_dtype,
    node_attr_dtypes,
    edge_attr_dtypes,
    directed,
):
    path, graph_attrs = path_w_expected_graph_props(
        node_dtype, node_attr_dtypes, edge_attr_dtypes, directed
    )
    # with pytest.warns(UserWarning, match="Potential missing values for attr"):
    # TODO: make sure test data has missing values, otherwise this warning will
    # not be triggered
    graph = geff.read_sg(path, position_attr="pos")

    np.testing.assert_array_equal(np.sort(graph.nodes), np.sort(graph_attrs["nodes"]))
    np.testing.assert_array_equal(np.sort(graph.edges), np.sort(graph_attrs["edges"]))

    for idx, node in enumerate(graph_attrs["nodes"]):
        np.testing.assert_array_equal(
            graph.node_attrs[node].pos,
            np.array([graph_attrs[d][idx] for d in ["t", "z", "y", "x"]]),
        )

    for idx, edge in enumerate(graph_attrs["edges"]):
        for name, values in graph_attrs["edge_props"].items():
            assert getattr(graph.edge_attrs[edge], name) == values[idx].item()


def test_write_empty_graph():
    graph = sg.SpatialGraph(
        ndims=3,
        node_dtype="uint64",
        node_attr_dtypes={"pos": "float32[3]"},
        edge_attr_dtypes={},
        position_attr="pos",
    )
    with pytest.warns(match="Graph is empty - not writing anything "):
        geff.write_sg(graph, path=".")
