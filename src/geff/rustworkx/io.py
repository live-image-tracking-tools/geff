from __future__ import annotations

import copy
import warnings
from typing import TYPE_CHECKING, Any, Literal

import numpy as np
import zarr

import geff
from geff.geff_reader import read_to_dict
from geff.metadata_schema import GeffMetadata, axes_from_lists
from geff.utils import remove_tilde
from geff.write_dicts import write_dicts

if TYPE_CHECKING:
    import rustworkx as rx
    from zarr.storage import StoreLike

    from geff.dict_representation import GraphDict, PropDictNpArray


def get_roi_rx(
    graph: rx.PyGraph, axis_names: list[str]
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Get the roi of a rustworkx graph.

    Args:
        graph: A non-empty rustworkx graph
        axis_names: All nodes on graph have these property holding their position

    Returns:
        tuple[tuple[float, ...], tuple[float, ...]]: A tuple with the min values in each
            spatial dim, and a tuple with the max values in each spatial dim
    """
    _min = None
    _max = None
    for node_data in graph.nodes():
        try:
            pos = np.array([node_data[name] for name in axis_names])
        except KeyError as e:
            missing_names = {name for name in axis_names if name not in node_data}
            raise ValueError(f"Spatiotemporal properties {missing_names} not found in node") from e
        if _min is None or _max is None:
            _min = pos
            _max = pos
        else:
            _min = np.min([_min, pos], axis=0)
            _max = np.max([_max, pos], axis=0)

    return tuple(_min.tolist()), tuple(_max.tolist())  # type: ignore


def _get_graph_existing_metadata_rx(
    graph: rx.PyGraph,
    metadata: GeffMetadata | None = None,
    axis_names: list[str] | None = None,
    axis_units: list[str | None] | None = None,
    axis_types: list[str | None] | None = None,
) -> tuple[list[str] | None, list[str | None] | None, list[str | None] | None]:
    """Get the existing metadata from a rustworkx graph.

    If axis lists are provided, they will override the graph properties and metadata.
    If metadata is provided, it will override the graph properties.
    If neither are provided, the graph properties will be used.

    Args:
        graph: A rustworkx graph
        metadata: The metadata of the graph. Defaults to None.
        axis_names: The names of the spatial dims. Defaults to None.
        axis_units: The units of the spatial dims. Defaults to None.
        axis_types: The types of the spatial dims. Defaults to None.

    Returns:
        tuple[list[str] | None, list[str | None] | None, list[str | None] | None]:
            A tuple with the names of the spatial dims, the units of the spatial dims,
            and the types of the spatial dims. None if not provided.
    """
    lists_provided = any(x is not None for x in [axis_names, axis_units, axis_types])
    metadata_provided = metadata is not None

    if lists_provided and metadata_provided:
        warnings.warn(
            "Both axis lists and metadata provided. Overriding metadata with axis lists.",
            stacklevel=2,
        )

    # If any axis lists is not provided, fallback to metadata if provided
    if metadata is not None and metadata.axes is not None:
        # the x = x or y is a python idiom for setting x to y if x is None, otherwise x
        axis_names = axis_names or [axis.name for axis in metadata.axes]
        axis_units = axis_units or [axis.unit for axis in metadata.axes]
        axis_types = axis_types or [axis.type for axis in metadata.axes]

    return axis_names, axis_units, axis_types


def write_rx(
    graph: rx.PyGraph,
    store: StoreLike,
    metadata: GeffMetadata | None = None,
    node_id_dict: dict[int, int] | None = None,
    axis_names: list[str] | None = None,
    axis_units: list[str | None] | None = None,
    axis_types: list[str | None] | None = None,
    zarr_format: Literal[2, 3] = 2,
) -> None:
    """Write a rustworkx graph to the geff file format

    Args:
        graph: The rustworkx graph to write.
        store: The store to write the geff file to.
        metadata: The original metadata of the graph. Defaults to None.
        node_id_dict: A dictionary mapping rx node indices to arbitrary indices.
        axis_names: The names of the axes.
        axis_units: The units of the axes.
        axis_types: The types of the axes.
        zarr_format: The zarr format to use.
    """
    try:
        import rustworkx as rx
    except ImportError as e:
        raise ImportError(
            "rustworkx is not installed. Please install it with `pip install geff[rx]`."
        ) from e

    store = remove_tilde(store)

    # open/create zarr container
    if zarr.__version__.startswith("3"):
        group = zarr.open_group(store, mode="a", zarr_format=zarr_format)
    else:
        group = zarr.open_group(store, mode="a")

    axis_names, axis_units, axis_types = _get_graph_existing_metadata_rx(
        graph, metadata, axis_names, axis_units, axis_types
    )

    if graph.num_nodes() == 0:
        # Handle empty graph case - still need to write empty structure
        node_data: list[tuple[int, dict[str, Any]]] = []
        edge_data: list[tuple[tuple[int, int], dict[str, Any]]] = []
        node_props: list[str] = []
        edge_props: list[str] = []

        write_dicts(
            geff_store=store,
            node_data=node_data,
            edge_data=edge_data,
            node_prop_names=node_props,
            edge_prop_names=edge_props,
            axis_names=axis_names,
            zarr_format=zarr_format,
        )

        # Write metadata for empty graph
        axes = axes_from_lists(
            axis_names,
            axis_units=axis_units,
            axis_types=axis_types,
            roi_min=None,
            roi_max=None,
        )

        if metadata is not None:
            metadata = copy.deepcopy(metadata)
            metadata.geff_version = geff.__version__
            metadata.directed = isinstance(graph, rx.PyDiGraph)
            metadata.axes = axes
        else:
            metadata = GeffMetadata(
                geff_version=geff.__version__,
                directed=isinstance(graph, rx.PyDiGraph),
                axes=axes,
            )
        metadata.write(group)
        warnings.warn(f"Graph is empty - only writing metadata to {store}", stacklevel=2)
        return

    # Prepare node data
    if node_id_dict is None:
        node_data = [
            (i, data) for i, data in zip(graph.node_indices(), graph.nodes(), strict=False)
        ]
    else:
        node_data = [
            (node_id_dict[i], data)
            for i, data in zip(graph.node_indices(), graph.nodes(), strict=False)
        ]

    # Prepare edge data
    if node_id_dict is None:
        edge_data = [((u, v), data) for u, v, data in graph.weighted_edge_list()]
    else:
        edge_data = [
            ((node_id_dict[u], node_id_dict[v]), data) for u, v, data in graph.weighted_edge_list()
        ]

    node_props = list({k for _, data in node_data for k in data})
    edge_props = list({k for _, data in edge_data for k in data})

    write_dicts(
        geff_store=store,
        node_data=node_data,
        edge_data=edge_data,
        node_prop_names=node_props,
        edge_prop_names=edge_props,
        axis_names=axis_names,
        zarr_format=zarr_format,
    )

    # write metadata
    roi_min: tuple[float, ...] | None
    roi_max: tuple[float, ...] | None
    if axis_names is not None and graph.num_nodes() > 0:
        roi_min, roi_max = get_roi_rx(graph, axis_names)
    else:
        roi_min, roi_max = None, None

    axes = axes_from_lists(
        axis_names,
        axis_units=axis_units,
        axis_types=axis_types,
        roi_min=roi_min,
        roi_max=roi_max,
    )

    # Conditionally update metadata with new axes, version, and directedness
    if metadata is not None:
        metadata = copy.deepcopy(metadata)
        metadata.geff_version = geff.__version__
        metadata.directed = isinstance(graph, rx.PyDiGraph)
        metadata.axes = axes
    else:
        metadata = GeffMetadata(
            geff_version=geff.__version__,
            directed=isinstance(graph, rx.PyDiGraph),
            axes=axes,
        )
    metadata.write(group)


def _set_property_values_rx(
    graph: rx.PyGraph,
    ids: list[int],
    name: str,
    prop_dict: PropDictNpArray,
    nodes: bool = True,
) -> None:
    """Add properties in-place to a rustworkx graph's
    nodes or edges by creating attributes on the nodes/edges

    Args:
        graph: The rustworkx graph, already populated with nodes or edges,
            that needs properties added
        ids: Node or edge ids from Geff. If nodes, list of node ids. If edges, list of edge tuples.
        name: The name of the property.
        prop_dict: A dictionary containing a "values" key with
            an array of values and an optional "missing" key for missing values.
        nodes: If True, extract and set node properties. If False,
            extract and set edge properties. Defaults to True.
    """
    sparse = "missing" in prop_dict

    for idx in range(len(ids)):
        _id = ids[idx]
        val = prop_dict["values"][idx]
        # If property is sparse and missing for this node, skip setting property
        ignore = prop_dict["missing"][idx] if sparse else False
        if not ignore:
            # Get either individual item or list instead of setting with np.array
            val = (
                val.tolist()
                if hasattr(val, "size") and val.size > 1
                else (val.item() if hasattr(val, "item") else val)
            )
            if nodes:
                # For rustworkx, we need to update the node data in place
                node_data = graph[_id]
                if isinstance(node_data, dict):
                    node_data[name] = val
                else:
                    # If node data is not a dict, we can't add properties
                    pass
            else:
                # For edges, we need to find the edge and update its data
                # This is more complex in rustworkx as we need to find the edge index
                source, target = _id[0], _id[1]  # type: ignore
                edge_indices = graph.edge_indices_from_endpoints(source, target)
                if edge_indices:
                    edge_index = edge_indices[0]
                    # Get current edge data
                    current_edge_data = graph.get_edge_data_by_index(edge_index)
                    if isinstance(current_edge_data, dict):
                        current_edge_data[name] = val
                    else:
                        # If edge data is not a dict, we can't easily add properties
                        # This is a limitation of the current implementation
                        pass


def _ingest_dict_rx(graph_dict: GraphDict) -> tuple[rx.PyGraph, dict[int, int]]:
    """Convert a GraphDict to a rustworkx graph."""
    try:
        import rustworkx as rx
    except ImportError as e:
        raise ImportError(
            "rustworkx is not installed. Please install it with `pip install geff[rx]`."
        ) from e

    metadata = graph_dict["metadata"]

    graph = rx.PyDiGraph() if metadata.directed else rx.PyGraph()
    graph.attrs = metadata.model_dump()

    # Add nodes with populated properties
    node_ids = graph_dict["nodes"].tolist()
    node_props: list[dict[str, Any]] = [{} for _ in node_ids]

    # Populate node properties first
    for name, prop_dict in graph_dict["node_props"].items():
        sparse = "missing" in prop_dict
        for idx in range(len(node_ids)):
            val = prop_dict["values"][idx]
            ignore = prop_dict["missing"][idx] if sparse else False
            if not ignore:
                val = (
                    val.tolist()
                    if hasattr(val, "size") and val.size > 1
                    else (val.item() if hasattr(val, "item") else val)
                )
                node_props[idx][name] = val

    # Add nodes with their properties
    rx_node_ids = graph.add_nodes_from(node_props)

    # Create mapping from geff node id to rustworkx node index
    to_rx_id_map = dict(zip(node_ids, rx_node_ids, strict=False))

    # Add edges if they exist
    if len(graph_dict["edges"]) > 0:
        edge_ids = graph_dict["edges"].tolist()

        # Prepare edge data with properties
        edges_with_data = []
        for idx, edge_pair in enumerate(edge_ids):
            source_id, target_id = edge_pair
            rx_source = to_rx_id_map[source_id]
            rx_target = to_rx_id_map[target_id]

            # Create edge data dict with properties
            edge_data = {}
            for name, prop_dict in graph_dict["edge_props"].items():
                sparse = "missing" in prop_dict
                val = prop_dict["values"][idx]
                ignore = prop_dict["missing"][idx] if sparse else False
                if not ignore:
                    val = (
                        val.tolist()
                        if hasattr(val, "size") and val.size > 1
                        else (val.item() if hasattr(val, "item") else val)
                    )
                    edge_data[name] = val

            edges_with_data.append((rx_source, rx_target, edge_data))

        # Add edges with their properties
        graph.add_edges_from(edges_with_data)

    return graph, to_rx_id_map


def read_rx(
    store: StoreLike,
    validate: bool = True,
    node_props: list[str] | None = None,
    edge_props: list[str] | None = None,
) -> tuple[rx.PyGraph, GeffMetadata]:
    """Read a geff file into a rustworkx graph.
    Metadata properties will be stored in the graph.attrs dict
    and can be accessed via `G.attrs[key]` where G is a rustworkx graph.

    Args:
        store: The path/str to the geff zarr, or the store itself.
        validate: Whether to validate the geff file.
        node_props: The names of the node properties to load,
            if None all properties will be loaded, defaults to None.
        edge_props: The names of the edge properties to load,
            if None all properties will be loaded, defaults to None.

    Returns:
        A tuple containing the rustworkx graph and the metadata.
    """
    graph_dict = read_to_dict(store, validate, node_props, edge_props)
    graph, _ = _ingest_dict_rx(graph_dict)

    return graph, graph_dict["metadata"]
