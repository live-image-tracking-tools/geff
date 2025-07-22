"""Test data generation utilities for geff graphs.

This module provides functions to create mock geff graphs for testing and development.
It includes both simple convenience functions and a comprehensive function for advanced use cases.

Examples:
    # Simple 2D graph with defaults
    >>> store, props = create_simple_2d_geff()
    >>> # Creates: 10 nodes, 15 edges, undirected, 2D (x, y, t)

    # Simple 3D graph with custom size
    >>> store, props = create_simple_3d_geff(num_nodes=20, num_edges=30)
    >>> # Creates: 20 nodes, 30 edges, undirected, 3D (x, y, z, t)

    # Advanced usage with full control
    >>> store, props = create_memory_mock_geff(
    ...     node_id_dtype="str",
    ...     node_axis_dtypes={"position": "float64", "time": "float32"},
    ...     directed=True,
    ...     num_nodes=5,
    ...     num_edges=8,
    ...     extra_node_props={"label": "str", "confidence": "float64"},
    ...     extra_edge_props={"score": "float64", "color": "uint8",
    ...           "weight": "float64", "type": "str"},
    ...     include_t=True,
    ...     include_z=False,  # 2D only
    ...     include_y=True,
    ...     include_x=True,
    ... )

    # Using with GeffReader
    >>> from geff import GeffReader
    >>> store, props = create_simple_2d_geff()
    >>> reader = GeffReader(store)
    >>> graph = reader.read_nx()
    >>> # graph is a networkx Graph ready for analysis
"""

from typing import Any, Literal, TypedDict, cast

import networkx as nx
import numpy as np
import zarr
import zarr.storage
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
    extra_edge_props: dict[str, NDArray[Any]]
    directed: bool
    axis_names: tuple[Axes, ...]
    axis_units: tuple[str, ...]


class ExampleNodeAxisPropsDtypes(TypedDict):
    position: DTypeStr
    time: DTypeStr


def create_dummy_graph_props(
    node_id_dtype: DTypeStr,
    node_axis_dtypes: ExampleNodeAxisPropsDtypes,
    directed: bool,
    num_nodes: int = 5,
    num_edges: int = 4,
    extra_node_props: dict[str, DTypeStr] | None = None,
    extra_edge_props: dict[str, DTypeStr] | None = None,
    include_t: bool = True,
    include_z: bool = True,
    include_y: bool = True,
    include_x: bool = True,
) -> GraphAttrs:
    """Create dummy graph properties for testing.

    Args:
        node_id_dtype: Data type for node IDs
        node_axis_dtypes: Dictionary specifying dtypes for node axis properties (space and time)
        directed: Whether the graph is directed
        num_nodes: Number of nodes to generate
        num_edges: Number of edges to generate
        extra_node_props: Dict mapping property names to dtypes for extra node properties
        extra_edge_props: Dict mapping property names to dtypes for extra edge properties
        include_t: Whether to include time dimension
        include_z: Whether to include z dimension
        include_y: Whether to include y dimension
        include_x: Whether to include x dimension

    Returns:
        Dictionary containing all graph properties
    """
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
        np.array(
            [(i // max(1, num_nodes // 5)) + 1 for i in range(num_nodes)],
            dtype=node_axis_dtypes["time"],
        )
        if include_t
        else np.array([], dtype="float64")  # Default dtype when time not included
    )
    z = (
        np.linspace(0.5, 0.1, num_nodes, dtype=node_axis_dtypes["position"])
        if include_z
        else np.array([], dtype="float64")  # Default dtype when position not included
    )
    y = (
        np.linspace(100.0, 500.0, num_nodes, dtype=node_axis_dtypes["position"])
        if include_y
        else np.array([], dtype="float64")  # Default dtype when position not included
    )
    x = (
        np.linspace(1.0, 0.1, num_nodes, dtype=node_axis_dtypes["position"])
        if include_x
        else np.array([], dtype="float64")  # Default dtype when position not included
    )

    # Generate edges with flexible count (ensure we don't exceed possible edges)
    max_possible_edges = (
        num_nodes * (num_nodes - 1) // 2 if not directed else num_nodes * (num_nodes - 1)
    )
    actual_num_edges = min(num_edges, max_possible_edges)

    # Create edges ensuring we don't create duplicates
    edges: list[list[Any]] = []
    edge_count = 0

    # For undirected graphs, we need to be more careful about duplicates
    if not directed:
        # Create a simple chain first, then add cross edges
        for i in range(min(actual_num_edges, num_nodes - 1)):
            source_idx = i
            target_idx = i + 1
            if node_id_dtype == "str":
                edges.append([f"node_{source_idx}", f"node_{target_idx}"])
            else:
                edges.append([int(source_idx), int(target_idx)])
            edge_count += 1

        # Add remaining edges as cross connections
        remaining_edges = actual_num_edges - edge_count
        for i in range(remaining_edges):
            source_idx = i % (num_nodes - 2)
            target_idx = (i + 2) % (num_nodes - 1) + 1
            if source_idx != target_idx:
                if node_id_dtype == "str":
                    edges.append([f"node_{source_idx}", f"node_{target_idx}"])
                else:
                    edges.append([int(source_idx), int(target_idx)])
                edge_count += 1
    else:
        # For directed graphs, we can create more edges
        edge_count = 0
        for i in range(actual_num_edges):
            source_idx = i % num_nodes
            target_idx = (i + 1) % num_nodes
            if source_idx != target_idx:  # Avoid self-loops
                if node_id_dtype == "str":
                    edges.append([f"node_{source_idx}", f"node_{target_idx}"])
                else:
                    edges.append([int(source_idx), int(target_idx)])
                edge_count += 1

        # Add more edges if we haven't reached the target
        if edge_count < actual_num_edges:
            for i in range(actual_num_edges - edge_count):
                source_idx = (i + 2) % num_nodes
                target_idx = (i + 3) % num_nodes
                if source_idx != target_idx:
                    if node_id_dtype == "str":
                        edges.append([f"node_{source_idx}", f"node_{target_idx}"])
                    else:
                        edges.append([int(source_idx), int(target_idx)])

    edges = np.array(edges, dtype=object if node_id_dtype == "str" else node_id_dtype)
    # Generate extra node properties
    extra_node_props_dict = {}
    if extra_node_props is not None:
        # Validate input is a dict
        if not isinstance(extra_node_props, dict):
            raise ValueError(f"extra_node_props must be a dict, got {type(extra_node_props)}")

        # Validate dict contains only string keys and valid dtype values
        for prop_name, prop_dtype in extra_node_props.items():
            if not isinstance(prop_name, str):
                raise ValueError(f"extra_node_props keys must be strings, got {type(prop_name)}")

            if not isinstance(prop_dtype, str):
                raise ValueError(
                    f"extra_node_props[{prop_name}] must be a string dtype, got {type(prop_dtype)}"
                )

            # Validate dtype is supported using DTypeStr
            from typing import get_args

            valid_dtypes = get_args(DTypeStr)
            if prop_dtype not in valid_dtypes:
                raise ValueError(
                    f"extra_node_props[{prop_name}] dtype '{prop_dtype}' not supported. "
                    f"Valid dtypes: {valid_dtypes}"
                )

            # Generate different patterns for different property types
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
    edge_props_dict = {}

    # Generate edge properties from extra_edge_props
    if extra_edge_props is not None:
        # Validate input is a dict
        if not isinstance(extra_edge_props, dict):
            raise ValueError(f"extra_edge_props must be a dict, got {type(extra_edge_props)}")

        # Validate dict contains only string keys and valid dtype values
        for prop_name, prop_dtype in extra_edge_props.items():
            if not isinstance(prop_name, str):
                raise ValueError(f"extra_edge_props keys must be strings, got {type(prop_name)}")

            if not isinstance(prop_dtype, str):
                raise ValueError(
                    f"extra_edge_props[{prop_name}] must be a string dtype, got {type(prop_dtype)}"
                )

            # Validate dtype is supported using DTypeStr
            from typing import get_args

            valid_dtypes = get_args(DTypeStr)
            if prop_dtype not in valid_dtypes:
                raise ValueError(
                    f"extra_edge_props[{prop_name}] dtype '{prop_dtype}' not supported. "
                    f"Valid dtypes: {valid_dtypes}"
                )

            # Generate different patterns for different property types
            if prop_dtype == "str":
                edge_props_dict[prop_name] = np.array(
                    [f"{prop_name}_{i}" for i in range(len(edges))], dtype=prop_dtype
                )
            elif prop_dtype in ["int", "int8", "uint8", "int16", "uint16"]:
                edge_props_dict[prop_name] = np.arange(len(edges), dtype=prop_dtype)
            else:  # float types
                edge_props_dict[prop_name] = np.linspace(0.1, 1.0, len(edges), dtype=prop_dtype)

    return {
        "nodes": nodes,
        "edges": edges,
        "t": t,
        "z": z,
        "y": y,
        "x": x,
        "extra_node_props": extra_node_props_dict,
        "extra_edge_props": edge_props_dict,
        "directed": directed,
        "axis_names": axis_names,
        "axis_units": axis_units,
    }


def create_memory_mock_geff(
    node_id_dtype: DTypeStr,
    node_axis_dtypes: ExampleNodeAxisPropsDtypes,
    directed: bool,
    num_nodes: int = 5,
    num_edges: int = 4,
    extra_node_props: dict[str, DTypeStr] | None = None,
    extra_edge_props: dict[str, DTypeStr] | None = None,
    include_t: bool = True,
    include_z: bool = True,
    include_y: bool = True,
    include_x: bool = True,
) -> tuple[zarr.storage.MemoryStore, GraphAttrs]:
    """Create a mock geff graph in memory and return the zarr store and graph properties.

    Args:
        node_id_dtype: Data type for node IDs
        node_axis_dtypes: Dictionary specifying dtypes for node axis properties (space and time)
        directed: Whether the graph is directed
        num_nodes: Number of nodes to generate
        num_edges: Number of edges to generate
        extra_node_props: Dict mapping property names to dtypes for extra node properties
        extra_edge_props: Dict mapping property names to dtypes for extra edge properties
        include_t: Whether to include time dimension
        include_z: Whether to include z dimension
        include_y: Whether to include y dimension
        include_x: Whether to include x dimension

    Returns:
        Tuple of (zarr store in memory, graph properties dictionary)
    """
    graph_props = create_dummy_graph_props(
        node_id_dtype=node_id_dtype,
        node_axis_dtypes=node_axis_dtypes,
        directed=directed,
        num_nodes=num_nodes,
        num_edges=num_edges,
        extra_node_props=extra_node_props,
        extra_edge_props=extra_edge_props,
        include_t=include_t,
        include_z=include_z,
        include_y=include_y,
        include_x=include_x,
    )

    # write graph with networkx api
    graph = nx.DiGraph() if directed else nx.Graph()

    for idx, node in enumerate(graph_props["nodes"]):
        props = {
            name: prop_array[idx] for name, prop_array in graph_props["extra_node_props"].items()
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
            name: prop_array[idx] for name, prop_array in graph_props["extra_edge_props"].items()
        }
        graph.add_edge(*edge.tolist(), **props)

    # Create memory store and write graph to it
    store = zarr.storage.MemoryStore()

    geff.write_nx(
        graph,
        store,
        axis_names=list(graph_props["axis_names"]),
        axis_units=list(graph_props["axis_units"]),
    )

    return store, graph_props


def create_simple_2d_geff(
    num_nodes: int = 10,
    num_edges: int = 15,
    directed: bool = False,
) -> tuple[zarr.storage.MemoryStore, GraphAttrs]:
    """Create a simple 2D geff graph with default settings.

    This is a convenience function for creating basic 2D graphs without having to
    specify all the detailed parameters. Uses sensible defaults for common use cases.

    Args:
        num_nodes: Number of nodes to generate (default: 10)
        num_edges: Number of edges to generate (default: 15)
        directed: Whether the graph is directed (default: False)

    Returns:
        Tuple of (zarr store in memory, graph properties dictionary)

    Examples:
        Basic usage with defaults:
            >>> store, props = create_simple_2d_geff()
            >>> # store is a zarr.MemoryStore with 10 nodes, 15 edges

        Custom graph size:
            >>> store, props = create_simple_2d_geff(num_nodes=5, num_edges=8)
            >>> # store has 5 nodes, 8 edges

        Directed graph:
            >>> store, props = create_simple_2d_geff(directed=True)
            >>> # Creates a directed graph

        Using with GeffReader:
            >>> store, props = create_simple_2d_geff()
            >>> reader = GeffReader(store)
            >>> graph = reader.read_nx()
            >>> # graph is a networkx Graph with 2D spatial data (x, y, t)
    """
    return create_memory_mock_geff(
        node_id_dtype="int",
        node_axis_dtypes={"position": "float64", "time": "float64"},
        directed=directed,
        num_nodes=num_nodes,
        num_edges=num_edges,
        extra_edge_props={"score": "float64", "color": "int"},
        include_t=True,
        include_z=False,  # 2D only
        include_y=True,
        include_x=True,
    )


def create_simple_3d_geff(
    num_nodes: int = 10,
    num_edges: int = 15,
    directed: bool = False,
) -> tuple[zarr.storage.MemoryStore, GraphAttrs]:
    """Create a simple 3D geff graph with default settings.

    This is a convenience function for creating basic 3D graphs without having to
    specify all the detailed parameters. Uses sensible defaults for common use cases.

    Args:
        num_nodes: Number of nodes to generate (default: 10)
        num_edges: Number of edges to generate (default: 15)
        directed: Whether the graph is directed (default: False)

    Returns:
        Tuple of (zarr store in memory, graph properties dictionary)

    Examples:
        Basic usage with defaults:
            >>> store, props = create_simple_3d_geff()
            >>> # store is a zarr.MemoryStore with 10 nodes, 15 edges

        Custom graph size:
            >>> store, props = create_simple_3d_geff(num_nodes=5, num_edges=8)
            >>> # store has 5 nodes, 8 edges

        Directed graph:
            >>> store, props = create_simple_3d_geff(directed=True)
            >>> # Creates a directed graph

        Using with GeffReader:
            >>> store, props = create_simple_3d_geff()
            >>> reader = GeffReader(store)
            >>> graph = reader.read_nx()
            >>> # graph is a networkx Graph with 3D spatial data (x, y, z, t)

        Accessing spatial coordinates:
            >>> store, props = create_simple_3d_geff()
            >>> reader = GeffReader(store)
            >>> graph = reader.read_nx()
            >>> # Each node has x, y, z, t coordinates
            >>> node_data = graph.nodes[0]
            >>> x, y, z, t = node_data['x'], node_data['y'], node_data['z'], node_data['t']
    """
    return create_memory_mock_geff(
        node_id_dtype="int",
        node_axis_dtypes={"position": "float64", "time": "float64"},
        directed=directed,
        num_nodes=num_nodes,
        num_edges=num_edges,
        extra_edge_props={"score": "float64", "color": "int"},
        include_t=True,
        include_z=True,  # 3D includes z
        include_y=True,
        include_x=True,
    )
