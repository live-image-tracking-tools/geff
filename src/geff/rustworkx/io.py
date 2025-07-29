from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Any, Literal

import numpy as np

try:
    import rustworkx as rx
except ImportError as e:
    raise ImportError(
        "This module requires rustworkx to be installed. "
        "Please install it with `pip install 'geff[rx]'`."
    ) from e


from geff.geff_reader import read_to_memory
from geff.io_utils import (
    calculate_roi_from_nodes,
    create_or_update_metadata,
    get_graph_existing_metadata,
)
from geff.metadata_schema import GeffMetadata, axes_from_lists
from geff.write_dicts import write_dicts

if TYPE_CHECKING:
    from zarr.storage import StoreLike

    from geff.typing import InMemoryGeff


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
    return calculate_roi_from_nodes(
        graph.nodes(),
        axis_names,
        lambda node_data: node_data,  # node_data is already the dict for rustworkx
    )


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

    Note on RustworkX Node ID Handling:
        RustworkX uses internal node indices that are not directly controllable by the user.
        These indices are typically sequential integers starting from 0, but may have gaps
        if nodes are removed. To maintain compatibility with geff's requirement for stable
        node identifiers, this function uses the following approach:

        1. If node_id_dict is None: Uses rustworkx's internal node indices directly
        2. If node_id_dict is provided: Maps rx node indices to custom identifiers

        When reading back with read_rx(), the mapping is reversed to restore the original
        rustworkx node indices, ensuring round-trip consistency.

    Args:
        graph: The rustworkx graph to write.
        store: The store to write the geff file to.
        metadata: The original metadata of the graph. Defaults to None.
        node_id_dict: A dictionary mapping rx node indices to arbitrary indices.
            This allows custom node identifiers to be used in the geff file instead
            of rustworkx's internal indices. If None, uses rx indices directly.
        axis_names: The names of the axes.
        axis_units: The units of the axes.
        axis_types: The types of the axes.
        zarr_format: The zarr format to use.
    """

    axis_names, axis_units, axis_types = get_graph_existing_metadata(
        metadata, axis_names, axis_units, axis_types
    )

    if graph.num_nodes() == 0:
        # Handle empty graph case - still need to write empty structure
        node_data: list[tuple[int, dict[str, Any]]] = []
        edge_data: list[tuple[tuple[int, int], dict[str, Any]]] = []
        node_props: list[str] = []
        edge_props: list[str] = []

        warnings.warn(f"Graph is empty - only writing metadata to {store}", stacklevel=2)

    else:
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
                ((node_id_dict[u], node_id_dict[v]), data)
                for u, v, data in graph.weighted_edge_list()
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

    metadata = create_or_update_metadata(
        metadata,
        isinstance(graph, rx.PyDiGraph),
        axes,
    )
    metadata.write(store)


def _ingest_dict_rx(graph_dict: InMemoryGeff) -> rx.PyDiGraph | rx.PyGraph:
    """
    Convert a InMemoryGeff to a rustworkx graph.
    The graph will have a `to_rx_id_map` attribute that maps geff node ids
    to rustworkx node indices.

    Args:
        graph_dict: The InMemoryGeff to convert to a rustworkx graph.

    Returns:
        rx.PyGraph: A rustworkx graph.
    """
    metadata = graph_dict["metadata"]

    graph = rx.PyDiGraph() if metadata.directed else rx.PyGraph()
    graph.attrs = metadata.model_dump()

    # Add nodes with populated properties
    node_ids = graph_dict["node_ids"].tolist()
    node_props: list[dict[str, Any]] = [{} for _ in node_ids]

    # Populate node properties first
    indices = np.arange(len(node_ids))

    for name, prop_dict in graph_dict["node_props"].items():
        values = prop_dict["values"]
        if "missing" in prop_dict:
            current_indices = indices[~prop_dict["missing"]]
            values = values[current_indices]
        else:
            current_indices = indices

        values = values.tolist()
        current_indices = current_indices.tolist()

        for idx, val in zip(current_indices, values, strict=True):
            node_props[idx][name] = val

    # Add nodes with their properties
    rx_node_ids = graph.add_nodes_from(node_props)

    # Create mapping from geff node id to rustworkx node index
    to_rx_id_map = dict(zip(node_ids, rx_node_ids, strict=False))

    # Add edges if they exist
    if len(graph_dict["edge_ids"]) > 0:
        # converting to local rx ids
        edge_ids = np.vectorize(to_rx_id_map.__getitem__)(graph_dict["edge_ids"])
        # Prepare edge data with properties
        edges_data: list[dict[str, Any]] = [{} for _ in edge_ids]
        indices = np.arange(len(edge_ids))

        for name, prop_dict in graph_dict["edge_props"].items():
            values = prop_dict["values"]
            if "missing" in prop_dict:
                current_indices = indices[~prop_dict["missing"]]
                values = values[current_indices]
            else:
                current_indices = indices

            values = values.tolist()
            current_indices = current_indices.tolist()

            for idx, val in zip(current_indices, values, strict=True):
                edges_data[idx][name] = val

        # Add edges with their properties
        graph.add_edges_from([(e[0], e[1], d) for e, d in zip(edge_ids, edges_data, strict=True)])

    graph.attrs["to_rx_id_map"] = to_rx_id_map

    return graph


def read_rx(
    store: StoreLike,
    validate: bool = True,
    node_props: list[str] | None = None,
    edge_props: list[str] | None = None,
) -> tuple[rx.PyGraph | rx.PyDiGraph, GeffMetadata]:
    """Read a geff file into a rustworkx graph.
    Metadata properties will be stored in the graph.attrs dict
    and can be accessed via `G.attrs[key]` where G is a rustworkx graph.

    The graph will have a `to_rx_id_map` attribute that maps geff node ids
    to rustworkx node indices.
    This can be used to map back to the original geff node ids.

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
    graph_dict = read_to_memory(store, validate, node_props, edge_props)
    graph = _ingest_dict_rx(graph_dict)

    return graph, graph_dict["metadata"]
