from pathlib import Path
from typing import Any, Callable, Literal, Optional, TypedDict, cast

import networkx as nx
import numpy as np
import pytest
from numpy.typing import NDArray

import geff

DTypeStr = Literal["double", "int", "int8", "uint8", "int16", "uint16", "float32", "float64", "str"]
Axes = Literal["t", "z", "y", "x"]


class GraphAttrs(TypedDict):
    nodes: NDArray[Any]
    edges: NDArray[Any]
    t: NDArray[Any]
    z: NDArray[Any]
    y: NDArray[Any]
    x: NDArray[Any]
    extra_node_props: dict[str, NDArray[Any]]
    edge_props: dict[str, NDArray[Any]]
    directed: bool
    axis_names: tuple[Axes, ...]
    axis_units: tuple[str, ...]


class ExampleNodePropsDtypes(TypedDict):
    position: DTypeStr
    time: DTypeStr
    extra: DTypeStr


class ExampleEdgePropsDtypes(TypedDict):
    score: DTypeStr
    color: DTypeStr


def create_dummy_graph_props(
    node_id_dtype: DTypeStr,
    node_prop_dtypes: ExampleNodePropsDtypes,
    edge_prop_dtypes: ExampleEdgePropsDtypes,
    directed: bool,
    num_nodes: int = 5,
    num_edges: int = 4,
    extra_node_props: Optional[list[dict[str, DTypeStr]]] = None,
    include_t: bool = True,
    include_z: bool = True,
    include_y: bool = True,
    include_x: bool = True,
) -> GraphAttrs:
    # Build axis_names and axis_units based on which dimensions to include
    axis_names_list = []
    axis_units_list = []

    if include_t:
        axis_names_list.append("t")
        axis_units_list.append("s")
    if include_z:
        axis_names_list.append("z")
        axis_units_list.append("nm")
    if include_y:
        axis_names_list.append("y")
        axis_units_list.append("nm")
    if include_x:
        axis_names_list.append("x")
        axis_units_list.append("nm")

    axis_names: tuple[Axes, ...] = cast("tuple[Axes, ...]", tuple(axis_names_list))
    axis_units = tuple(axis_units_list)

    # Generate nodes with flexible count
    if node_id_dtype == "str":
        # For string dtype, create string representations of numbers
        nodes = np.array([f"node_{i}" for i in range(num_nodes)], dtype=node_id_dtype)
    else:
        # For numeric dtypes, use arange
        nodes = np.arange(num_nodes, dtype=node_id_dtype)

    # Generate spatiotemporal coordinates with flexible dimensions
    t = (
        np.linspace(0.1, 0.5, num_nodes, dtype=node_prop_dtypes["time"])
        if include_t
        else np.array(
            [], dtype="float64"
        )  # Default dtype when time not included, type doesn't matter
        # because node properties are not written to nodes when length is 0
    )
    z = (
        np.linspace(0.5, 0.1, num_nodes, dtype=node_prop_dtypes["position"])
        if include_z
        else np.array(
            [], dtype="float64"
        )  # Default dtype when position not included, type doesn't matter
        # because node properties are not written to nodes when length is 0
    )
    y = (
        np.linspace(100.0, 500.0, num_nodes, dtype=node_prop_dtypes["position"])
        if include_y
        else np.array(
            [], dtype="float64"
        )  # Default dtype when position not included, type doesn't matter
        # because node properties are not written to nodes when length is 0
    )
    x = (
        np.linspace(1.0, 0.1, num_nodes, dtype=node_prop_dtypes["position"])
        if include_x
        else np.array(
            [], dtype="float64"
        )  # Default dtype when position not included, type doesn't matter
        # because node properties are not written to nodes when length is 0
    )

    # Generate edges with flexible count (ensure we don't exceed possible edges)
    max_possible_edges = (
        num_nodes * (num_nodes - 1) // 2 if not directed else num_nodes * (num_nodes - 1)
    )
    actual_num_edges = min(num_edges, max_possible_edges)

    # Create a simple edge pattern (0->1, 1->2, etc.)
    edges: list[list[Any]] = []
    for i in range(actual_num_edges):
        source_idx = i % num_nodes
        target_idx = (i + 1) % num_nodes
        if source_idx != target_idx:  # Avoid self-loops
            # Create edge based on dtype
            if node_id_dtype == "str":
                edges.append([f"node_{source_idx}", f"node_{target_idx}"])
            else:
                edges.append([int(source_idx), int(target_idx)])

    edges = np.array(edges, dtype=object if node_id_dtype == "str" else node_id_dtype)

    # Generate extra node properties
    extra_node_props_dict = {}
    if extra_node_props is not None:
        for i, prop_spec in enumerate(extra_node_props):
            for prop_name, prop_dtype in prop_spec.items():
                if prop_dtype == "str":
                    extra_node_props_dict[prop_name] = np.array(
                        [f"{prop_name}_{i}" for i in range(num_nodes)], dtype=prop_dtype
                    )
                elif prop_dtype in ["int", "int8", "uint8", "int16", "uint16"]:
                    extra_node_props_dict[prop_name] = np.arange(num_nodes, dtype=prop_dtype)
                else:  # float types
                    extra_node_props_dict[prop_name] = np.linspace(
                        0.1, 1.0, num_nodes, dtype=prop_dtype
                    )

    # Generate edge properties
    scores = np.linspace(0.1, 0.4, len(edges), dtype=edge_prop_dtypes["score"])
    colors = np.arange(len(edges), dtype=edge_prop_dtypes["color"])

    return {
        "nodes": nodes,
        "edges": edges,
        "t": t,
        "z": z,
        "y": y,
        "x": x,
        "extra_node_props": extra_node_props_dict,
        "edge_props": {"score": scores, "color": colors},
        "directed": directed,
        "axis_names": axis_names,
        "axis_units": axis_units,
    }


# Using a fixture instead of a function so the tmp_path fixture is automatically passed
# Implemented as a closure where tmp_path is the bound variable
@pytest.fixture
def path_w_expected_graph_props(
    tmp_path,
) -> Callable[
    [
        DTypeStr,
        ExampleNodePropsDtypes,
        ExampleEdgePropsDtypes,
        bool,
        int,
        int,
        list[dict[str, DTypeStr]],
        bool,
        bool,
        bool,
        bool,
    ],
    tuple[Path, GraphAttrs],
]:
    def func(
        node_id_dtype: DTypeStr,
        node_prop_dtypes: ExampleNodePropsDtypes,
        edge_prop_dtypes: ExampleEdgePropsDtypes,
        directed: bool,
        num_nodes: int = 5,
        num_edges: int = 4,
        extra_node_props: Optional[list[dict[str, DTypeStr]]] = None,
        include_t: bool = True,
        include_z: bool = True,
        include_y: bool = True,
        include_x: bool = True,
    ) -> tuple[Path, GraphAttrs]:
        """
        Fixture to a geff graph path saved on disk with the expected graph properties.

        Returns:
        Path
            Path to the example graph.
        GraphAttrs
            The expected graph properties in a dictionary.
        """

        graph_props = create_dummy_graph_props(
            node_id_dtype=node_id_dtype,
            node_prop_dtypes=node_prop_dtypes,
            edge_prop_dtypes=edge_prop_dtypes,
            directed=directed,
            num_nodes=num_nodes,
            num_edges=num_edges,
            extra_node_props=extra_node_props,
            include_t=include_t,
            include_z=include_z,
            include_y=include_y,
            include_x=include_x,
        )

        # write graph with networkx api
        graph = nx.DiGraph() if directed else nx.Graph()

        for idx, node in enumerate(graph_props["nodes"]):
            props = {
                name: prop_array[idx]
                for name, prop_array in graph_props["extra_node_props"].items()
            }
            node_attrs = {}

            # Only add spatial dimensions that are included
            if include_t and len(graph_props["t"]) > 0:
                node_attrs["t"] = graph_props["t"][idx]
            if include_z and len(graph_props["z"]) > 0:
                node_attrs["z"] = graph_props["z"][idx]
            if include_y and len(graph_props["y"]) > 0:
                node_attrs["y"] = graph_props["y"][idx]
            if include_x and len(graph_props["x"]) > 0:
                node_attrs["x"] = graph_props["x"][idx]

            graph.add_node(node, **node_attrs, **props)

        for idx, edge in enumerate(graph_props["edges"]):
            props = {
                name: prop_array[idx] for name, prop_array in graph_props["edge_props"].items()
            }
            graph.add_edge(*edge.tolist(), **props)

        path = tmp_path / "rw_consistency.zarr/graph"

        geff.write_nx(
            graph,
            path,
            axis_names=list(graph_props["axis_names"]),
            axis_units=list(graph_props["axis_units"]),
        )

        return path, graph_props

    return func
