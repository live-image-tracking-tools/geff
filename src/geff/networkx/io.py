from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

import networkx as nx
import numpy as np

from geff.geff_reader import read_to_memory
from geff.io_utils import (
    calculate_roi_from_nodes,
    create_or_update_metadata,
    get_graph_existing_metadata,
)
from geff.metadata_schema import GeffMetadata, axes_from_lists
from geff.write_dicts import write_dicts

if TYPE_CHECKING:
    from collections.abc import Sequence

    from numpy.typing import NDArray
    from zarr.storage import StoreLike

    from geff.typing import PropDictNpArray

import logging

logger = logging.getLogger(__name__)


class NxBackend:
    @property
    def type(self) -> tuple[type[nx.Graph | nx.DiGraph], ...]:
        """The networkx graph type. Useful for isinstance checks."""
        return nx.Graph, nx.DiGraph

    @staticmethod
    def construct(
        metadata: GeffMetadata,
        node_ids: NDArray[Any],
        edge_ids: NDArray[Any],
        node_props: dict[str, PropDictNpArray],
        edge_props: dict[str, PropDictNpArray],
    ) -> nx.Graph | nx.DiGraph:
        """
        Construct a `networkx` graph instance from GEFF data.

        Args:
            metadata (GeffMetadata): The metadata of the graph.
            node_ids (NDArray[Any]): An array containing the node ids. Must have same dtype as
                edge_ids.
            edge_ids (NDArray[Any]y): An array containing the edge ids. Must have same dtype
                as node_ids.
            node_props (dict[str, PropDictNpArray]): A dictionary
                from node property names to (values, missing) arrays, which should have same
                length as node_ids. Spatial graph does not support missing attributes, so the
                missing arrays should be None or all False. If present, the missing arrays are
                ignored with warning
            edge_props (dict[str, PropDictNpArray]): A dictionary
                from edge property names to (values, missing) arrays, which should have same
                length as edge_ids. Spatial graph does not support missing attributes, so the
                missing arrays should be None or all False. If present, the missing array is ignored
                with warning.

        Returns:
            (nx.Graph | nx.DiGraph): A `networkx` graph object.
        """
        graph = nx.DiGraph() if metadata.directed else nx.Graph()

        graph.add_nodes_from(node_ids.tolist())
        for name, prop_dict in node_props.items():
            _set_property_values(graph, node_ids, name, prop_dict, nodes=True)

        graph.add_edges_from(edge_ids.tolist())
        for name, prop_dict in edge_props.items():
            _set_property_values(graph, edge_ids, name, prop_dict, nodes=False)

        return graph

    @staticmethod
    def get_node_ids(graph: nx.Graph | nx.DiGraph) -> Sequence[Any]:
        """
        Get the node ids of the graph.

        Args:
            graph (nx.Graph | nx.DiGraph): The graph object.

        Returns:
            node_ids (Sequence[Any]): The node ids.
        """
        return list(graph.nodes)

    @staticmethod
    def get_edge_ids(graph: nx.Graph | nx.DiGraph) -> Sequence[tuple[Any, Any]]:
        """
        Get the edges of the graph.

        Args:
            graph (nx.Graph | nx.DiGraph): The graph object.

        Returns:
            edge_ids (Sequence[tuple[Any, Any]]): Pairs of node ids that represent edges..
        """
        return list(graph.edges)

    @staticmethod
    def get_node_prop(
        graph: nx.Graph | nx.DiGraph,
        name: str,
        nodes: Sequence[Any],
        metadata: GeffMetadata,
    ) -> NDArray[Any]:
        """
        Get a property of the nodes as a numpy array.

        Args:
            graph (nx.Graph | nx.DiGraph): The graph object.
            name (str): The name of the node property.
            nodes (Sequence[Any]): A sequence of node ids; this determines the order of the property
                array.
            metadata (GeffMetadata): The GEFF metadata.

        Returns:
            numpy.ndarray: The values of the selected property as a numpy array.
        """
        prop = [graph.nodes[node][name] for node in nodes]
        return np.array(prop)

    @staticmethod
    def get_edge_prop(
        graph: nx.Graph | nx.DiGraph,
        name: str,
        edges: Sequence[tuple[Any, Any]],
        metadata: GeffMetadata,
    ) -> NDArray[Any]:
        """
        Get a property of the edges as a numpy array.

        Args:
            graph (nx.Graph | nx.DiGraph): The graph object.
            name (str): The name of the edge property.
            edges (Sequence[Any]): A sequence of tuples of node ids, representing the edges; this
                determines the order of the property array.
            metadata (GeffMetadata): The GEFF metadata.

        Returns:
            numpy.ndarray: The values of the selected property as a numpy array.
        """
        prop = [graph.edges[edge][name] for edge in edges]
        return np.array(prop)


def get_roi(graph: nx.Graph, axis_names: list[str]) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Get the roi of a networkx graph.

    Args:
        graph (nx.Graph): A non-empty networkx graph
        axis_names (str): All nodes on graph have these property holding their position

    Returns:
        tuple[tuple[float, ...], tuple[float, ...]]: A tuple with the min values in each
            spatial dim, and a tuple with the max values in each spatial dim
    """
    return calculate_roi_from_nodes(
        graph.nodes(data=True),
        axis_names,
        lambda node_tuple: node_tuple[1],  # Extract data from (node_id, data) tuple
    )


def write_nx(
    graph: nx.Graph,
    store: StoreLike,
    metadata: GeffMetadata | None = None,
    axis_names: list[str] | None = None,
    axis_units: list[str | None] | None = None,
    axis_types: list[str | None] | None = None,
    zarr_format: Literal[2, 3] = 2,
) -> None:
    """Write a networkx graph to the geff file format

    Args:
        graph (nx.Graph): A networkx graph
        store (str | Path | zarr store): The path/str to the output zarr, or the store
            itself. Opens in append mode, so will only overwrite geff-controlled groups.
        metadata (GeffMetadata, optional): The original metadata of the graph.
            Defaults to None. If provided, will override the graph properties.
        axis_names (Optional[list[str]], optional): The names of the spatial dims
            represented in position property. Defaults to None. Will override
            both value in graph properties and metadata if provided.
        axis_units (Optional[list[str]], optional): The units of the spatial dims
            represented in position property. Defaults to None. Will override value
            both value in graph properties and metadata if provided.
        axis_types (Optional[list[str]], optional): The types of the spatial dims
            represented in position property. Usually one of "time", "space", or "channel".
            Defaults to None. Will override both value in graph properties and metadata
            if provided.
        zarr_format (Literal[2, 3], optional): The version of zarr to write.
            Defaults to 2.
    """

    axis_names, axis_units, axis_types = get_graph_existing_metadata(
        metadata, axis_names, axis_units, axis_types
    )

    node_props = list({k for _, data in graph.nodes(data=True) for k in data})

    edge_data = [((u, v), data) for u, v, data in graph.edges(data=True)]
    edge_props = list({k for _, _, data in graph.edges(data=True) for k in data})
    write_dicts(
        store,
        graph.nodes(data=True),
        edge_data,
        node_props,
        edge_props,
        axis_names,
        zarr_format=zarr_format,
    )

    # write metadata
    roi_min: tuple[float, ...] | None
    roi_max: tuple[float, ...] | None
    if axis_names is not None and graph.number_of_nodes() > 0:
        roi_min, roi_max = get_roi(graph, axis_names)
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
        isinstance(graph, nx.DiGraph),
        axes,
    )
    metadata.write(store)


def _set_property_values(
    graph: nx.Graph,
    ids: NDArray[Any],
    name: str,
    prop_dict: PropDictNpArray,
    nodes: bool = True,
) -> None:
    """Add properties in-place to a networkx graph's
    nodes or edges by creating attributes on the nodes/edges

    Args:
        graph (nx.DiGraph): The networkx graph, already populated with nodes or edges,
            that needs properties added
        ids (np.ndarray): Node or edge ids from Geff. If nodes, 1D. If edges, 2D.
        name (str): The name of the property.
        prop_dict (PropDict[np.ndarray]): A dictionary containing a "values" key with
            an array of values and an optional "missing" key for missing values.
        nodes (bool, optional): If True, extract and set node properties.  If False,
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
            if nodes:
                graph.nodes[_id.item()][name] = val.tolist()
            else:
                source, target = _id.tolist()
                graph.edges[source, target][name] = val.tolist()


def read_nx(
    store: StoreLike,
    validate: bool = True,
    node_props: list[str] | None = None,
    edge_props: list[str] | None = None,
) -> tuple[nx.Graph, GeffMetadata]:
    """Read a geff file into a networkx graph. Metadata properties will be stored in
    the graph properties, accessed via `G.graph[key]` where G is a networkx graph.

    Args:
        store (str | Path | zarr store): The path/str to the geff zarr, or the store
            itself. Opens in append mode, so will only overwrite geff-controlled groups.
        validate (bool, optional): Flag indicating whether to perform validation on the
            geff file before loading into memory. If set to False and there are
            format issues, will likely fail with a cryptic error. Defaults to True.
        node_props (list of str, optional): The names of the node properties to load,
            if None all properties will be loaded, defaults to None.
        edge_props (list of str, optional): The names of the edge properties to load,
            if None all properties will be loaded, defaults to None.

    Returns:
        A networkx graph containing the graph that was stored in the geff file format
    """
    in_memory_geff = read_to_memory(store, validate, node_props, edge_props)
    graph = NxBackend.construct(**in_memory_geff)

    return graph, in_memory_geff["metadata"]
