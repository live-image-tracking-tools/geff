import numpy as np
import pytest
import spatial_graph as sg

import geff
from geff.testing.data import create_memory_mock_geff

node_dtypes = ["int8", "uint8", "int16", "uint16"]
node_attr_dtypes = [
    {"position": "double", "time": "double"},
    {"position": "int", "time": "int"},
]
extra_edge_props = [
    {"score": "float64", "color": "uint8"},
    {"score": "float32", "color": "int16"},
]


@pytest.mark.parametrize("node_dtype", node_dtypes)
@pytest.mark.parametrize("node_attr_dtypes", node_attr_dtypes)
@pytest.mark.parametrize("extra_edge_props", extra_edge_props)
@pytest.mark.parametrize("directed", [True, False])
def test_read_write_consistency(
    node_dtype,
    node_attr_dtypes,
    extra_edge_props,
    directed,
):
    store, graph_attrs = create_memory_mock_geff(
        node_id_dtype=node_dtype,
        node_axis_dtypes=node_attr_dtypes,
        extra_edge_props=extra_edge_props,
        directed=directed,
    )
    # with pytest.warns(UserWarning, match="Potential missing values for attr"):
    # TODO: make sure test data has missing values, otherwise this warning will
    # not be triggered
    graph, _ = geff.read_sg(store, position_attr="pos")

    np.testing.assert_array_equal(np.sort(graph.nodes), np.sort(graph_attrs["nodes"]))
    np.testing.assert_array_equal(np.sort(graph.edges), np.sort(graph_attrs["edges"]))

    for idx, node in enumerate(graph_attrs["nodes"]):
        np.testing.assert_array_equal(
            graph.node_attrs[node].pos,
            np.array([graph_attrs[d][idx] for d in ["t", "z", "y", "x"]]),
        )

    for idx, edge in enumerate(graph_attrs["edges"]):
        for name, values in graph_attrs["extra_edge_props"].items():
            assert getattr(graph.edge_attrs[edge], name) == values[idx].item()


def test_write_empty_graph():
    create_graph = getattr(sg, "create_graph", sg.SpatialGraph)
    graph = create_graph(
        ndims=3,
        node_dtype="uint64",
        node_attr_dtypes={"pos": "float32[3]"},
        edge_attr_dtypes={},
        position_attr="pos",
    )
    with pytest.warns(match="Graph is empty - not writing anything "):
        geff.write_sg(graph, store=".")
