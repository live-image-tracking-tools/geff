from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

import networkx as nx
import numpy as np

from geff.core_io import write_dicts
from geff.core_io._utils import calculate_roi_from_nodes
from geff.metadata._schema import GeffMetadata, _axes_from_lists
from geff.metadata.utils import (
    create_or_update_metadata,
    get_graph_existing_metadata,
)

from ._backend_protocol import Backend
from ._graph_adapter import GraphAdapter

if TYPE_CHECKING:
    from collections.abc import Sequence

    from numpy.typing import NDArray
    from zarr.storage import StoreLike

    from geff._typing import PropDictNpArray

import logging

logger = logging.getLogger(__name__)


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
    for idx in range(len(ids)):
        _id = ids[idx]
        val = prop_dict["values"][idx]
        # If property is sparse and missing for this node, skip setting property
        ignore = prop_dict["missing"][idx] if prop_dict["missing"] is not None else False
        if not ignore:
            # Get either individual item or list instead of setting with np.array
            if nodes:
                graph.nodes[_id.item()][name] = val.tolist()
            else:
                source, target = _id.tolist()
                graph.edges[source, target][name] = val.tolist()


# NOTE: see _api_wrapper.py read/write/construct for docs
class NxBackend(Backend):
    @property
    def GRAPH_TYPES(self) -> tuple[type[nx.Graph], type[nx.DiGraph]]:
        return nx.Graph, nx.DiGraph

    @staticmethod
    def construct(
        metadata: GeffMetadata,
        node_ids: NDArray[Any],
        edge_ids: NDArray[Any],
        node_props: dict[str, PropDictNpArray],
        edge_props: dict[str, PropDictNpArray],
    ) -> nx.Graph | nx.DiGraph:
        graph = nx.DiGraph() if metadata.directed else nx.Graph()

        graph.add_nodes_from(node_ids.tolist())
        for name, prop_dict in node_props.items():
            _set_property_values(graph, node_ids, name, prop_dict, nodes=True)

        graph.add_edges_from(edge_ids.tolist())
        for name, prop_dict in edge_props.items():
            _set_property_values(graph, edge_ids, name, prop_dict, nodes=False)

        return graph

    @staticmethod
    def write(
        graph: nx.Graph | nx.DiGraph,
        store: StoreLike,
        metadata: GeffMetadata | None = None,
        axis_names: list[str] | None = None,
        axis_units: list[str | None] | None = None,
        axis_types: list[str | None] | None = None,
        zarr_format: Literal[2, 3] = 2,
    ) -> None:
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

        axes = _axes_from_lists(
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

    @staticmethod
    def graph_adapter(graph: Any) -> NxGraphAdapter:
        return NxGraphAdapter(graph)


class NxGraphAdapter(GraphAdapter):
    def __init__(self, graph: nx.Graph | nx.DiGraph) -> None:
        self.graph = graph

    def get_node_ids(self) -> Sequence[Any]:
        return list(self.graph.nodes)

    def get_edge_ids(self) -> Sequence[tuple[Any, Any]]:
        return list(self.graph.edges)

    def get_node_prop(
        self,
        name: str,
        nodes: Sequence[Any],
        metadata: GeffMetadata,
    ) -> NDArray[Any]:
        prop = [self.graph.nodes[node][name] for node in nodes]
        return np.array(prop)

    def get_edge_prop(
        self,
        name: str,
        edges: Sequence[tuple[Any, Any]],
        metadata: GeffMetadata,
    ) -> NDArray[Any]:
        prop = [self.graph.edges[edge][name] for edge in edges]
        return np.array(prop)
