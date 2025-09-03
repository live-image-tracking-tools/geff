from typing import Any, get_args

import networkx as nx
import numpy as np
import pytest
from numpy.typing import NDArray

from geff import GeffMetadata
from geff._graph_libs._api_wrapper import SupportedBackend, read
from geff.testing.data import create_mock_geff

rx = pytest.importorskip("rustworkx")
sg = pytest.importorskip("spatial_graph")

node_id_dtypes = ["uint8", "uint16"]
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
        case "networkx":
            return isinstance(graph, nx.Graph | nx.DiGraph)
        case "rustworkx":
            return isinstance(graph, rx.PyGraph | rx.PyDiGraph)
        case "spatial-graph":
            return isinstance(graph, sg.SpatialGraph | sg.SpatialDiGraph)
        case _:
            raise TypeError(
                f"No `is_expected_type` code path has been defined for backend '{backend}'."
            )


def get_nodes(graph) -> set[Any]:
    if isinstance(graph, (nx.Graph | nx.DiGraph)):
        return set(graph.nodes)
    elif isinstance(graph, rx.PyGraph | rx.PyDiGraph):
        return set(graph.node_indices())
    elif isinstance(graph, sg.SpatialGraph | sg.SpatialDiGraph):
        return set(graph.nodes)
    else:
        raise TypeError(f"No `get_nodes` code path has been defined for type '{type(graph)}'.")


def get_edges(graph) -> set[tuple[Any, Any]]:
    if isinstance(graph, (nx.Graph | nx.DiGraph)):
        return set(graph.edges)
    elif isinstance(graph, rx.PyGraph | rx.PyDiGraph):
        return set(graph.edge_list())
    elif isinstance(graph, sg.SpatialGraph | sg.SpatialDiGraph):
        return {tuple(edge.tolist()) for edge in graph.edges}
    else:
        raise TypeError(f"No `get_edges` code path has been defined for type '{type(graph)}'.")


def get_node_prop(graph, name: str, nodes: list[Any], metadata: GeffMetadata) -> NDArray[Any]:
    if isinstance(graph, (nx.Graph | nx.DiGraph)):
        prop = [graph.nodes[node][name] for node in nodes]
        return np.array(prop)
    elif isinstance(graph, rx.PyGraph | rx.PyDiGraph):
        return np.array([graph[node][name] for node in nodes])
    elif isinstance(graph, sg.SpatialGraph | sg.SpatialDiGraph):
        axes = metadata.axes
        if axes is None:
            raise ValueError("No axes found for spatial props")
        axes_names = [ax.name for ax in axes]
        if name in axes_names:
            return sg_get_node_spatial_props(graph, name, nodes, axes_names)
        else:
            # TODO: is this the best way to access node attributes?
            return getattr(graph.node_attrs[nodes], name)
    else:
        raise TypeError(f"No `get_node_prop` code path has been defined for type '{type(graph)}'.")


def get_edge_prop(graph, name: str, edges: list[Any]) -> NDArray[Any]:
    if isinstance(graph, (nx.Graph | nx.DiGraph)):
        prop = [graph.edges[edge][name] for edge in edges]
        return np.array(prop)
    elif isinstance(graph, rx.PyGraph | rx.PyDiGraph):
        # return np.array([graph[edge][name] for edge in edges])
        return np.array([graph.get_edge_data(*edge)[name] for edge in edges])
    elif isinstance(graph, sg.SpatialGraph | sg.SpatialDiGraph):
        # TODO: is this the best way to access edge attributes?
        return getattr(graph.edge_attrs[edges], name)
    else:
        raise TypeError(f"No `get_edge_prop` code path has been defined for type '{type(graph)}'.")


# This is not the most elegant solution but the idea is:
#   spatial graph takes the spatial properties defined in axes and combines them into a single attr
#   so to compare with the results we need to index each position separately
def sg_get_node_spatial_props(
    graph: sg.SpatialGraph | sg.SpatialDiGraph, name: str, nodes: list[Any], axes_names: list[str]
):
    if name not in axes_names:
        raise ValueError(f"Node property '{name}' not found in axes names {axes_names}")
    idx = axes_names.index(name)
    position = getattr(graph.node_attrs[nodes], graph.position_attr)
    return position[:, idx]


@pytest.mark.parametrize("node_id_dtype", node_id_dtypes)
@pytest.mark.parametrize("node_axis_dtypes", node_axis_dtypes)
@pytest.mark.parametrize("extra_edge_props", extra_edge_props)
@pytest.mark.parametrize("directed", [True, False])
@pytest.mark.parametrize("include_t", [True, False])
@pytest.mark.parametrize("include_z", [True, False])
@pytest.mark.parametrize("backend", get_args(SupportedBackend))
def test_read(
    node_id_dtype,
    node_axis_dtypes,
    extra_edge_props,
    directed,
    include_t,
    include_z,
    backend,
) -> None:
    store, memory_geff = create_mock_geff(
        node_id_dtype,
        node_axis_dtypes,
        extra_edge_props=extra_edge_props,
        directed=directed,
        include_t=include_t,
        include_z=include_z,
    )

    graph, metadata = read(store, backend=backend)

    assert is_expected_type(graph, backend)

    # nodes and edges correct
    assert get_nodes(graph) == {*memory_geff["node_ids"].tolist()}
    assert get_edges(graph) == {*[tuple(edges) for edges in memory_geff["edge_ids"].tolist()]}

    # check node properties are correct
    spatial_node_properties = ["y", "x"]
    if include_t:
        spatial_node_properties.append("t")
    if include_z:
        spatial_node_properties.append("z")
    for name in spatial_node_properties:
        np.testing.assert_array_equal(
            get_node_prop(graph, name, memory_geff["node_ids"].tolist(), metadata=metadata),
            memory_geff["node_props"][name]["values"],
        )
    for name, data in memory_geff["node_props"].items():
        values = data["values"]
        np.testing.assert_array_equal(
            get_node_prop(graph, name, memory_geff["node_ids"].tolist(), metadata=metadata), values
        )
    # check edge properties are correct
    for name, data in memory_geff["edge_props"].items():
        values = data["values"]
        np.testing.assert_array_equal(
            get_edge_prop(graph, name, memory_geff["edge_ids"].tolist()), values
        )
