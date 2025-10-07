"""Test data generation utilities for geff graphs.

This module provides functions to create mock geff graphs for testing and development.
It includes both simple convenience functions and a comprehensive function for advanced use cases.


Examples:
    # Simple 2D graph with defaults
    >>> store, memory_geff = create_simple_2d_geff()
    >>> # Creates: 10 nodes, 15 edges, undirected, 2D (x, y, t)

    # Simple 3D graph with custom size
    >>> store, memory_geff = create_simple_3d_geff(num_nodes=20, num_edges=30)
    >>> # Creates: 20 nodes, 30 edges, undirected, 3D (x, y, z, t)

    # Advanced usage with full control
    >>> store, memory_geff = create_mock_geff(
    ...     node_id_dtype="int",
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

    # Advanced usage with custom arrays
    >>> import numpy as np
    >>> custom_labels = np.array(["A", "B", "C", "D", "E"])
    >>> custom_scores = np.array([0.1, 0.5, 0.8, 0.3, 0.9])
    >>> custom_edge_weights = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8])
    >>> store, memory_geff = create_mock_geff(
    ...     node_id_dtype="int",
    ...     node_axis_dtypes={"position": "float64", "time": "float64"},
    ...     directed=False,
    ...     num_nodes=5,
    ...     num_edges=8,
    ...     extra_node_props={"label": custom_labels, "score": custom_scores,
    ...         "confidence": "float64"},
    ...     extra_edge_props={"weight": custom_edge_weights, "type": "str"},
    ...     include_t=True,
    ...     include_z=False,
    ...     include_y=True,
    ...     include_x=True,
    ... )

    # To construct an graph with a backend graph lib
    >>> # Import construct function of your choice
    >>> store, memory_geff = create_simple_2d_geff()
    >>> graph = construct_nx(**memory_geff)
    >>> # graph is a networkx Graph ready for analysis
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, TypedDict, get_args

import numpy as np
import zarr
import zarr.storage

from geff.core_io import write_arrays
from geff_spec import Axis, PropMetadata
from geff_spec.utils import (
    add_or_update_props_metadata,
    create_or_update_metadata,
    create_props_metadata,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from numpy.typing import NDArray

    from geff._typing import InMemoryGeff, PropDictNpArray
    from geff_spec._valid_values import AxisType, SpaceUnits, TimeUnits


DTypeStr = Literal["double", "int", "int8", "uint8", "int16", "uint16", "float32", "float64", "str"]
NodeIdDTypeStr = Literal["uint", "uint8", "uint16", "uint32", "uint64"]
AxesOptions = Literal["t", "z", "y", "x"]


class ExampleNodeAxisPropsDtypes(TypedDict):
    position: DTypeStr
    time: DTypeStr


def create_dummy_in_mem_geff(
    node_id_dtype: NodeIdDTypeStr,
    node_axis_dtypes: ExampleNodeAxisPropsDtypes,
    directed: bool,
    num_nodes: int = 5,
    num_edges: int = 4,
    extra_node_props: Mapping[str, DTypeStr | NDArray[Any]] | None = None,
    extra_edge_props: Mapping[str, DTypeStr | NDArray[Any]] | None = None,
    include_t: bool = True,
    include_z: bool = True,
    include_y: bool = True,
    include_x: bool = True,
    include_varlength: bool = False,
    include_missing: bool = False,
) -> InMemoryGeff:
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
        include_varlength: Whether to include a variable length property. If true, will
            make a property on nodes called "var_length" that has 2d np arrays of various
            shapes
        include_missing: If true, creades a node and edge prop called "sparse_prop" where every
            other node/edge has a missing value

    Returns:
        InMemoryGeff containing all graph properties
    """
    # Generate nodes with flexible count
    nodes = np.arange(num_nodes, dtype=node_id_dtype)
    node_props: dict[str, PropDictNpArray] = {}
    node_prop_meta: list[PropMetadata] = []

    # Generate spatiotemporal coordinates with flexible dimensions
    def _add_axis(
        name: str,
        ax_type: Literal[AxisType],
        unit: str | Literal[SpaceUnits] | Literal[TimeUnits],
        values: np.ndarray,
    ) -> PropMetadata:
        node_props[name] = {"values": values, "missing": None}
        if num_nodes > 0:
            roimin, roimax = values.min(), values.max()
        else:
            roimin, roimax = None, None
        axes.append(Axis(name=name, type=ax_type, unit=unit, min=roimin, max=roimax))
        return create_props_metadata(identifier=name, prop_data=node_props[name], unit=unit)

    axes: list[Axis] = []
    if include_t:
        meta = _add_axis(
            name="t",
            ax_type="time",
            unit="second",
            values=np.array(
                [(i * 5 // num_nodes) + 1 for i in range(num_nodes)],
                dtype=node_axis_dtypes["time"],
            ),
        )
        node_prop_meta.append(meta)
    if include_z:
        meta = _add_axis(
            name="z",
            ax_type="space",
            unit="nanometer",
            values=np.linspace(0.5, 0.1, num_nodes, dtype=node_axis_dtypes["position"]),
        )
        node_prop_meta.append(meta)
    if include_y:
        meta = _add_axis(
            name="y",
            ax_type="space",
            unit="nanometer",
            values=np.linspace(100.0, 500.0, num_nodes, dtype=node_axis_dtypes["position"]),
        )
        node_prop_meta.append(meta)
    if include_x:
        meta = _add_axis(
            name="x",
            ax_type="space",
            unit="nanometer",
            values=np.linspace(1.0, 0.1, num_nodes, dtype=node_axis_dtypes["position"]),
        )
        node_prop_meta.append(meta)

    # Generate edges with flexible count (ensure we don't exceed possible edges)
    max_possible_edges = (
        num_nodes * (num_nodes - 1) // 2 if not directed else num_nodes * (num_nodes - 1)
    )
    actual_num_edges = min(num_edges, max_possible_edges)

    # Create edges ensuring we don't create duplicates
    edges_: list[list[Any]] = []
    edge_count = 0

    # For undirected graphs, we need to be more careful about duplicates
    if not directed:
        # Create a simple chain first, then add cross edges
        for i in range(min(actual_num_edges, num_nodes - 1)):
            source_idx = i
            target_idx = i + 1
            edges_.append([int(source_idx), int(target_idx)])
            edge_count += 1

        # Add remaining edges as cross connections
        remaining_edges = actual_num_edges - edge_count
        for i in range(remaining_edges):
            source_idx = i % (num_nodes - 2)
            target_idx = (i + 2) % (num_nodes - 1) + 1
            if source_idx != target_idx:
                edges_.append([int(source_idx), int(target_idx)])
                edge_count += 1
    else:
        # For directed graphs, we can create more edges efficiently
        edges_ = []
        edge_count = 0
        created_edges = set()  # Track created edges to avoid duplicates

        # First create a chain of edges
        for i in range(min(actual_num_edges, num_nodes - 1)):
            source_idx = i
            target_idx = i + 1
            edge_tuple = (int(source_idx), int(target_idx))
            if edge_tuple not in created_edges:
                edges_.append([int(source_idx), int(target_idx)])
                created_edges.add(edge_tuple)
                edge_count += 1

        # Add remaining edges using different patterns
        remaining_edges = actual_num_edges - edge_count
        if remaining_edges > 0:
            # Create edges with different offsets
            for i in range(remaining_edges * 2):  # Try more iterations to find unique edges
                source_idx = i % num_nodes
                target_idx = (i + 2) % num_nodes  # Skip one node
                if source_idx != target_idx:
                    edge_tuple = (int(source_idx), int(target_idx))
                    if edge_tuple not in created_edges:
                        edges_.append([int(source_idx), int(target_idx)])
                        created_edges.add(edge_tuple)
                        edge_count += 1

                        # Stop if we've reached the target
                        if edge_count >= actual_num_edges:
                            break

            # If we still need more edges, use another pattern
            if edge_count < actual_num_edges:
                for i in range(actual_num_edges * 2):  # Try more iterations to find unique edges
                    source_idx = i % num_nodes
                    target_idx = (i + 3) % num_nodes  # Skip two nodes
                    if source_idx != target_idx:
                        edge_tuple = (int(source_idx), int(target_idx))
                        if edge_tuple not in created_edges:
                            edges_.append([int(source_idx), int(target_idx)])
                            created_edges.add(edge_tuple)
                            edge_count += 1

                            # Stop if we've reached the target
                            if edge_count >= actual_num_edges:
                                break

    edges = np.array(edges_, dtype=node_id_dtype)
    if edges.shape[0] == 0:
        edges = edges.reshape((0, 2))

    # Generate extra node properties
    if extra_node_props is not None:
        # Validate input is a dict
        if not isinstance(extra_node_props, dict):
            raise ValueError(f"extra_node_props must be a dict, got {type(extra_node_props)}")

        # Validate dict contains only string keys and valid dtype values or numpy arrays
        for prop_name, prop_value in extra_node_props.items():
            if not isinstance(prop_name, str):
                raise ValueError(f"extra_node_props keys must be strings, got {type(prop_name)}")

            # Check if value is a string (dtype) or numpy array
            if isinstance(prop_value, str):
                # Auto-generate array with specified dtype
                prop_dtype = prop_value

                # Validate dtype is supported using DTypeStr
                valid_dtypes = get_args(DTypeStr)
                if prop_dtype not in valid_dtypes:
                    raise ValueError(
                        f"extra_node_props[{prop_name}] dtype '{prop_dtype}' not supported. "
                        f"Valid dtypes: {valid_dtypes}"
                    )

                # Generate different patterns for different property types
                if prop_dtype == "str":
                    values = np.array(
                        [f"{prop_name}_{i}" for i in range(num_nodes)], dtype=prop_dtype
                    )
                elif prop_dtype in ["int", "int8", "uint8", "int16", "uint16"]:
                    values = np.arange(num_nodes, dtype=prop_dtype)
                else:  # float types
                    values = np.linspace(0.1, 1.0, num_nodes, dtype=prop_dtype)
                prop_dict: PropDictNpArray = {"values": values, "missing": None}
                node_props[prop_name] = prop_dict
                node_prop_meta.append(create_props_metadata(prop_name, prop_dict))

            elif isinstance(prop_value, np.ndarray):
                # Use provided array directly
                # Validate array length matches num_nodes
                if len(prop_value) != num_nodes:
                    raise ValueError(
                        f"extra_node_props[{prop_name}] array length {len(prop_value)} "
                        f"does not match num_nodes {num_nodes}"
                    )

                node_props[prop_name] = {"values": prop_value, "missing": None}

            else:
                raise ValueError(
                    f"extra_node_props[{prop_name}] must be a string dtype or numpy array, "
                    f"got {type(prop_value)}"
                )

    # Generate edge properties
    edge_props_dict: dict[str, PropDictNpArray] = {}
    edge_prop_meta: list[PropMetadata] = []
    # Generate edge properties from extra_edge_props
    if extra_edge_props is not None:
        # Validate input is a dict
        if not isinstance(extra_edge_props, dict):
            raise ValueError(f"extra_edge_props must be a dict, got {type(extra_edge_props)}")

        # Validate dict contains only string keys and valid dtype values or numpy arrays
        for prop_name, prop_value in extra_edge_props.items():
            if not isinstance(prop_name, str):
                raise ValueError(f"extra_edge_props keys must be strings, got {type(prop_name)}")

            # Check if value is a string (dtype) or numpy array
            if isinstance(prop_value, str):
                # Auto-generate array with specified dtype
                prop_dtype = prop_value

                # Validate dtype is supported using DTypeStr
                valid_dtypes = get_args(DTypeStr)
                if prop_dtype not in valid_dtypes:
                    raise ValueError(
                        f"extra_edge_props[{prop_name}] dtype '{prop_dtype}' not supported. "
                        f"Valid dtypes: {valid_dtypes}"
                    )

                # Generate different patterns for different property types
                if prop_dtype == "str":
                    values = np.array(
                        [f"{prop_name}_{i}" for i in range(len(edges))], dtype=prop_dtype
                    )
                elif prop_dtype in ["int", "int8", "uint8", "int16", "uint16"]:
                    values = np.arange(len(edges), dtype=prop_dtype)
                else:  # float types
                    values = np.linspace(0.1, 1.0, len(edges), dtype=prop_dtype)

                edge_props_dict[prop_name] = {"values": values, "missing": None}
            elif isinstance(prop_value, np.ndarray):
                # Use provided array directly
                # Validate array length matches num_edges
                if len(prop_value) != len(edges):
                    raise ValueError(
                        f"extra_edge_props[{prop_name}] array length {len(prop_value)} "
                        f"does not match number of edges {len(edges)}"
                    )

                edge_props_dict[prop_name] = {"values": prop_value, "missing": None}

            else:
                raise ValueError(
                    f"extra_edge_props[{prop_name}] must be a string dtype or numpy array, "
                    f"got {type(prop_value)}"
                )

            edge_prop_meta.append(
                create_props_metadata(identifier=prop_name, prop_data=edge_props_dict[prop_name])
            )

    if include_varlength:
        prop_name = "var_length"
        ndim = 3
        _dtype = np.uint64
        values_list = []
        for node in range(num_nodes):
            shape = [
                node,
            ] * ndim
            arr = np.ones(shape=shape, dtype=_dtype) * node
            values_list.append(arr)

        values = np.array(values_list, dtype=np.object_)
        missing = np.zeros(shape=(num_nodes,), dtype=np.bool_)
        if num_nodes > 0:
            missing[0] = 1
        prop_dict = {"values": values, "missing": missing}
        node_props[prop_name] = prop_dict
        node_prop_meta.append(create_props_metadata(prop_name, prop_dict))

    if include_missing:
        prop_name = "sparse_prop"
        values = np.arange(num_nodes, dtype="float64")
        missing = np.zeros(num_nodes, dtype=np.bool_)
        if num_nodes > 0:
            missing[::2] = 1
        prop_dict = {"values": values, "missing": missing}
        prop_meta = create_props_metadata(prop_name, prop_dict)
        node_props[prop_name] = prop_dict
        node_prop_meta.append(prop_meta)
        edge_props_dict[prop_name] = prop_dict
        edge_prop_meta.append(prop_meta)

    metadata = create_or_update_metadata(metadata=None, is_directed=directed, axes=axes)
    metadata = add_or_update_props_metadata(metadata, node_prop_meta, "node")
    metadata = add_or_update_props_metadata(metadata, edge_prop_meta, "edge")

    return {
        "metadata": metadata,
        "node_ids": nodes,
        "edge_ids": edges,
        "node_props": node_props,
        "edge_props": edge_props_dict,
    }


def create_mock_geff(
    node_id_dtype: NodeIdDTypeStr,
    node_axis_dtypes: ExampleNodeAxisPropsDtypes,
    directed: bool,
    num_nodes: int = 5,
    num_edges: int = 4,
    extra_node_props: Mapping[str, DTypeStr | NDArray[Any]] | None = None,
    extra_edge_props: Mapping[str, DTypeStr | NDArray[Any]] | None = None,
    include_t: bool = True,
    include_z: bool = True,
    include_y: bool = True,
    include_x: bool = True,
    include_varlength: bool = False,
    include_missing: bool = False,
) -> tuple[zarr.storage.MemoryStore, InMemoryGeff]:
    """Create a mock geff in memory and return the zarr store and the in memory geff.

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
        include_varlength: Whether to include a variable length property. If true, will
            make a property on nodes called "var_length" that has 2d np arrays of various
            shapes
        include_missing: If true, creades a node prop called "sparse_prop" where every other
            node has a missing value

    Returns:
        Tuple of (zarr store in memory, InMemoryGeff)
    """
    memory_geff = create_dummy_in_mem_geff(
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
        include_varlength=include_varlength,
    )

    # Create memory store and write graph to it
    store = zarr.storage.MemoryStore()
    write_arrays(store, **memory_geff)

    return store, memory_geff


def create_simple_2d_geff(
    num_nodes: int = 10,
    num_edges: int = 15,
    directed: bool = False,
) -> tuple[zarr.storage.MemoryStore, InMemoryGeff]:
    """Create a simple 2D geff graph with default settings.

    This is a convenience function for creating basic 2D graphs without having to
    specify all the detailed parameters. Uses sensible defaults for common use cases.

    Args:
        num_nodes: Number of nodes to generate (default: 10)
        num_edges: Number of edges to generate (default: 15)
        directed: Whether the graph is directed (default: False)

    Returns:
        Tuple of (zarr store in memory, InMemoryGeff)
    """
    return create_mock_geff(
        node_id_dtype="uint",
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
) -> tuple[zarr.storage.MemoryStore, InMemoryGeff]:
    """Create a simple 3D geff graph with default settings.

    This is a convenience function for creating basic 3D graphs without having to
    specify all the detailed parameters. Uses sensible defaults for common use cases.

    Args:
        num_nodes: Number of nodes to generate (default: 10)
        num_edges: Number of edges to generate (default: 15)
        directed: Whether the graph is directed (default: False)

    Returns:
        Tuple of (zarr store in memory, InMemoryGeff)
    """
    return create_mock_geff(
        node_id_dtype="uint",
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


def create_simple_temporal_geff(
    num_nodes: int = 10,
    num_edges: int = 15,
    directed: bool = False,
) -> tuple[zarr.storage.MemoryStore, InMemoryGeff]:
    """Create a simple geff graph with only time dimension (no spatial dimensions).

    This function creates a graph with nodes, edges, and time coordinates,
    but no spatial dimensions (x, y, z). Useful for temporal-only analysis.

    Args:
        num_nodes: Number of nodes to generate (default: 10)
        num_edges: Number of edges to generate (default: 15)
        directed: Whether the graph is directed (default: False)

    Returns:
        Tuple of (zarr store in memory, InMemoryGeff)
    """
    return create_mock_geff(
        node_id_dtype="uint",
        node_axis_dtypes={"position": "float64", "time": "float64"},
        directed=directed,
        num_nodes=num_nodes,
        num_edges=num_edges,
        extra_edge_props={"score": "float64", "color": "int"},
        include_t=True,
        include_z=False,  # No spatial dimensions
        include_y=False,  # No spatial dimensions
        include_x=False,  # No spatial dimensions
    )


def create_empty_geff(directed: bool = False) -> tuple[zarr.storage.MemoryStore, InMemoryGeff]:
    """Creates a geff without any nodes or edges

    Args:
        directed (bool, optional): Whether to create a directed graph. Defaults to False.

    Returns:
        tuple[zarr.storage.MemoryStore, InMemoryGeff]
    """
    return create_mock_geff(
        node_id_dtype="uint",
        node_axis_dtypes={"position": "float64", "time": "float64"},
        directed=directed,
        num_nodes=0,
        num_edges=0,
        include_t=False,  # No time
        include_z=False,  # No spatial dimensions
        include_y=False,  # No spatial dimensions
        include_x=False,  # No spatial dimensions
    )
