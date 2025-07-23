from typing import Any

import networkx as nx
import numpy as np
import pytest
from numpy.typing import NDArray

from geff.io import SupportedBackend, read
from geff.testing.data import create_memory_mock_geff

node_id_dtypes = ["int8", "uint8", "int16", "uint16"]
node_axis_dtypes = [
    {"position": "double", "time": "double"},
    {"position": "int", "time": "int"},
]
extra_edge_props = [
    {"score": "float64", "color": "uint8"},
    {"score": "float32", "color": "int16"},
]

# NOTE: new backends have to add cases to the utility functions below


def is_expected_type(graph, backend: SupportedBackend):
    match backend:
        case SupportedBackend.NETWORKX:
            return isinstance(graph, nx.Graph | nx.DiGraph)
        case _:
            raise TypeError(
                f"No `is_expected_type` code path has been defined for backend '{backend.value}'."
            )


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


@pytest.mark.parametrize("node_id_dtype", node_id_dtypes)
@pytest.mark.parametrize("node_axis_dtypes", node_axis_dtypes)
@pytest.mark.parametrize("extra_edge_props", extra_edge_props)
@pytest.mark.parametrize("directed", [True, False])
@pytest.mark.parametrize("include_t", [True, False])
@pytest.mark.parametrize("include_z", [True, False])
def test_read(
    node_id_dtype,
    node_axis_dtypes,
    extra_edge_props,
    directed,
    include_t,
    include_z,
):
    store, graph_props = create_memory_mock_geff(
        node_id_dtype,
        node_axis_dtypes,
        extra_edge_props=extra_edge_props,
        directed=directed,
        include_t=include_t,
        include_z=include_z,
    )
    for backend in SupportedBackend:
        # temporarily skip dummy example case until it is removed
        if backend == SupportedBackend.GRAPH_DICT:
            continue

        graph, metadata = read(store, backend=backend)

        assert is_expected_type(graph, backend)

        # nodes and edges correct
        assert get_nodes(graph) == {*graph_props["nodes"].tolist()}
        assert get_edges(graph) == {*[tuple(edges) for edges in graph_props["edges"].tolist()]}

        # check node properties are correct
        spatial_node_properties = ["y", "x"]
        if include_t:
            spatial_node_properties.append("t")
        if include_z:
            spatial_node_properties.append("z")
        for name in spatial_node_properties:
            np.testing.assert_array_equal(
                get_node_prop(graph, name, graph_props["nodes"].tolist()), graph_props[name]
            )
        for name, values in graph_props["extra_node_props"].items():
            np.testing.assert_array_equal(
                get_node_prop(graph, name, graph_props["nodes"].tolist()), values
            )
        # check edge properties are correct
        for name, values in graph_props["extra_edge_props"].items():
            np.testing.assert_array_equal(
                get_edge_prop(graph, name, graph_props["edges"].tolist()), values
            )

    # TODO: metadata? Or will it be tested elsewhere
