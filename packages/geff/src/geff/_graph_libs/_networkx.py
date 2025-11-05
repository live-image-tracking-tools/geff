from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

import networkx as nx
import numpy as np

from geff.core_io import write_dicts
from geff_spec.utils import create_or_update_metadata, update_metadata_axes

from ._backend_protocol import Backend
from ._graph_adapter import GraphAdapter

if TYPE_CHECKING:
    from collections.abc import Sequence

    from numpy.typing import NDArray
    from zarr.storage import StoreLike

    from geff._typing import PropDictNpArray
    from geff_spec import AxisType, GeffMetadata

import logging

logger = logging.getLogger(__name__)


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
    values = prop_dict["values"]
    varlength = np.issubdtype(values.dtype, np.object_)
    for idx in range(len(ids)):
        _id = ids[idx]
        val = prop_dict["values"][idx]
        # If property is sparse and missing for this node, skip setting property
        ignore = prop_dict["missing"][idx] if prop_dict["missing"] is not None else False
        if not ignore:
            # if varlength, store numpy arrays on graph. Otherwise,
            # Get either individual item or list instead of setting with np.array
            value = val if varlength else val.tolist()
            if nodes:
                graph.nodes[_id.item()][name] = value
            else:
                source, target = _id.tolist()
                graph.edges[source, target][name] = value


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
        axis_types: list[AxisType | None] | None = None,
        axis_scales: list[float | None] | None = None,
        scaled_units: list[str | None] | None = None,
        axis_offset: list[float | None] | None = None,
        zarr_format: Literal[2, 3] = 2,
        structure_validation: bool = True,
    ) -> None:
        directed = isinstance(graph, nx.DiGraph)
        metadata = create_or_update_metadata(metadata=metadata, is_directed=directed)
        if axis_names is not None:
            metadata = update_metadata_axes(
                metadata, axis_names, axis_units, axis_types, axis_scales, scaled_units, axis_offset
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
            metadata,
            zarr_format=zarr_format,
            structure_validation=structure_validation,
        )

    @staticmethod
    def graph_adapter(graph: Any) -> NxGraphAdapter:
        return NxGraphAdapter(graph)


class NxGraphAdapter(GraphAdapter):
    def __init__(self, graph: nx.Graph | nx.DiGraph) -> None:
        self.graph = graph

    def get_node_ids(self) -> Sequence[int]:
        return list(self.graph.nodes)

    def get_edge_ids(self) -> Sequence[tuple[int, int]]:
        return list(self.graph.edges)

    def has_node_prop(self, name: str, node: int, metadata: GeffMetadata) -> bool:
        return name in self.graph.nodes[node]

    def get_node_prop(
        self,
        name: str,
        node: int,
        metadata: GeffMetadata,
    ) -> Any:
        return self.graph.nodes[node][name]

    def has_edge_prop(self, name: str, edge: tuple[int, int], metadata: GeffMetadata) -> bool:
        return name in self.graph.edges[edge]

    def get_edge_prop(
        self,
        name: str,
        edge: tuple[int, int],
        metadata: GeffMetadata,
    ) -> Any:
        return self.graph.edges[edge][name]
