from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

import numpy as np

from ._errors import MissingDependencyError

try:
    import rustworkx as rx
except ImportError as e:
    raise MissingDependencyError(
        "This module requires rustworkx to be installed. "
        "Please install it with `pip install 'geff[rx]'`."
    ) from e


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


# NOTE: see _api_wrapper.py read/write/construct for docs
class RxBackend(Backend):
    @property
    def GRAPH_TYPES(self) -> tuple[type[rx.PyGraph], type[rx.PyDiGraph]]:
        return rx.PyGraph, rx.PyDiGraph

    @staticmethod
    def construct(
        metadata: GeffMetadata,
        node_ids: NDArray[Any],
        edge_ids: NDArray[Any],
        node_props: dict[str, PropDictNpArray],
        edge_props: dict[str, PropDictNpArray],
    ) -> rx.PyGraph | rx.PyDiGraph:
        metadata = metadata

        graph = rx.PyDiGraph() if metadata.directed else rx.PyGraph()
        graph.attrs = metadata.model_dump()

        # Add nodes with populated properties
        node_ids = node_ids.tolist()
        props_per_node: list[dict[str, Any]] = [{} for _ in node_ids]

        # Populate node properties first
        indices = np.arange(len(node_ids))

        for name, prop_dict in node_props.items():
            values = prop_dict["values"]
            if prop_dict["missing"] is not None:
                current_indices = indices[~prop_dict["missing"]]
                values = values[current_indices]
            else:
                current_indices = indices

            values = values.tolist()
            current_indices = current_indices.tolist()

            for idx, val in zip(current_indices, values, strict=True):
                props_per_node[idx][name] = val

        # Add nodes with their properties
        rx_node_ids = graph.add_nodes_from(props_per_node)

        # Create mapping from geff node id to rustworkx node index
        to_rx_id_map = dict(zip(node_ids, rx_node_ids, strict=False))

        # Add edges if they exist
        if len(edge_ids) > 0:
            # converting to local rx ids
            edge_ids = np.vectorize(to_rx_id_map.__getitem__)(edge_ids)
            # Prepare edge data with properties
            edges_data: list[dict[str, Any]] = [{} for _ in edge_ids]
            indices = np.arange(len(edge_ids))

            for name, prop_dict in edge_props.items():
                values = prop_dict["values"]
                if prop_dict["missing"] is not None:
                    current_indices = indices[~prop_dict["missing"]]
                    values = values[current_indices]
                else:
                    current_indices = indices

                values = values.tolist()
                current_indices = current_indices.tolist()

                for idx, val in zip(current_indices, values, strict=True):
                    edges_data[idx][name] = val

            # Add edges with their properties
            graph.add_edges_from(
                [(e[0], e[1], d) for e, d in zip(edge_ids, edges_data, strict=True)]
            )

        graph.attrs["to_rx_id_map"] = to_rx_id_map

        return graph

    @staticmethod
    def write(
        graph: rx.PyGraph | rx.PyDiGraph,
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
        node_id_dict: dict[int, int] | None = None,
    ) -> None:
        directed = isinstance(graph, rx.PyDiGraph)
        metadata = create_or_update_metadata(metadata=metadata, is_directed=directed)
        if axis_names is not None:
            metadata = update_metadata_axes(
                metadata, axis_names, axis_units, axis_types, axis_scales, scaled_units, axis_offset
            )

        if graph.num_nodes() == 0:
            # Handle empty graph case - still need to write empty structure
            node_data: list[tuple[int, dict[str, Any]]] = []
            edge_data: list[tuple[tuple[int, int], dict[str, Any]]] = []
            node_props: list[str] = []
            edge_props: list[str] = []

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
            metadata=metadata,
            zarr_format=zarr_format,
            structure_validation=structure_validation,
        )

    @staticmethod
    def graph_adapter(graph: rx.PyGraph | rx.PyDiGraph) -> RxGraphAdapter:
        return RxGraphAdapter(graph)


class RxGraphAdapter(GraphAdapter):
    def __init__(self, graph: rx.PyGraph | rx.PyDiGraph) -> None:
        self.graph = graph

    def get_node_ids(self) -> Sequence[int]:
        return list(self.graph.node_indices())

    def get_edge_ids(self) -> Sequence[tuple[int, int]]:
        return list(self.graph.edge_list())

    def has_node_prop(self, name: str, node: int, metadata: GeffMetadata) -> bool:
        return name in self.graph[node]

    def get_node_prop(
        self,
        name: str,
        node: int,
        metadata: GeffMetadata,
    ) -> Any:
        return self.graph[node][name]

    def has_edge_prop(self, name: str, edge: tuple[int, int], metadata: GeffMetadata) -> bool:
        return name in self.graph.get_edge_data(*edge)

    def get_edge_prop(
        self,
        name: str,
        edge: tuple[int, int],
        metadata: GeffMetadata,
    ) -> Any:
        return self.graph.get_edge_data(*edge)[name]
