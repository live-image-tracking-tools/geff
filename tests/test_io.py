from typing import Any

import networkx as nx
import numpy as np
import pytest
from numpy.typing import NDArray

from geff.io import SupportedBackend, read

node_dtypes = ["int8", "uint8", "int16", "uint16", "str"]
node_prop_dtypes = [
    {"position": "double"},
    {"position": "int"},
]
edge_prop_dtypes = [
    {"score": "float64", "color": "uint8"},
    {"score": "float32", "color": "int16"},
]


def get_nodes(graph) -> set[Any]:
    if isinstance(graph, (nx.Graph | nx.DiGraph)):
        return set(graph.nodes)
    else:
        raise TypeError(f"No `get_nodes` code path has been defined for type '{type(graph)}'.")


def get_edges(graph) -> set[tuple[Any, Any]]:
    if isinstance(graph, (nx.Graph | nx.DiGraph)):
        return set(graph.edges)
    else:
        raise TypeError(f"No `get_edges` code path has been defined for type '{type(graph)}'.")


def get_node_prop(graph, name: str, nodes: list[Any]) -> NDArray[Any]:
    if isinstance(graph, (nx.Graph | nx.DiGraph)):
        prop = [graph.nodes[node][name] for node in nodes]
        return np.array(prop)
    else:
        raise TypeError(f"No `get_node_prop` code path has been defined for type '{type(graph)}'.")


def get_edge_prop(graph, name: str, edges: list[Any]) -> NDArray[Any]:
    if isinstance(graph, (nx.Graph | nx.DiGraph)):
        prop = [graph.edges[edge][name] for edge in edges]
        return np.array(prop)
    else:
        raise TypeError(f"No `get_edge_prop` code path has been defined for type '{type(graph)}'.")


def is_expected_type(graph, backend: SupportedBackend):
    match backend:
        case SupportedBackend.NETWORKX:
            return isinstance(graph, nx.Graph | nx.DiGraph)
        case _:
            raise TypeError(
                f"No `is_expected_type` code path has been defined for backend '{backend.value}'."
            )


@pytest.mark.parametrize("node_dtype", node_dtypes)
@pytest.mark.parametrize("node_prop_dtypes", node_prop_dtypes)
@pytest.mark.parametrize("edge_prop_dtypes", edge_prop_dtypes)
@pytest.mark.parametrize("directed", [True, False])
# Add new backends to this parametrization
@pytest.mark.parametrize("backend", [SupportedBackend.NETWORKX])
def test_read(
    path_w_expected_graph_props,
    node_dtype,
    node_prop_dtypes,
    edge_prop_dtypes,
    directed,
    backend,
):
    path, graph_props = path_w_expected_graph_props(
        node_dtype, node_prop_dtypes, edge_prop_dtypes, directed
    )
    graph, metadata = read(path, backend=backend)

    assert is_expected_type(graph, backend)

    # nodes and edges correct
    assert get_nodes(graph) == {*graph_props["nodes"].tolist()}
    assert get_edges(graph) == {*[tuple(edges) for edges in graph_props["edges"].tolist()]}

    # check node properties are correct
    spatial_node_properties = ["t", "z", "y", "x"]
    for name in spatial_node_properties:
        np.testing.assert_array_equal(
            get_node_prop(graph, name, graph_props["nodes"].tolist()), graph_props[name]
        )
    for name, values in graph_props["extra_node_props"].items():
        np.testing.assert_array_equal(
            get_node_prop(graph, name, graph_props["nodes"].tolist()), values
        )
    # check edge properties are correct
    for name, values in graph_props["edge_props"].items():
        np.testing.assert_array_equal(
            get_edge_prop(graph, name, graph_props["edges"].tolist()), values
        )

    # TODO: metadata? Or will it be tested elsewhere
