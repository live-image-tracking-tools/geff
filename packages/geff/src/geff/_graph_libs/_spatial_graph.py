from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Any, Literal, cast

from ._errors import MissingDependencyError

try:
    import spatial_graph as sg
except ImportError as e:
    raise MissingDependencyError(
        "This module requires spatial-graph to be installed. "
        "Please install it with `pip install 'geff[spatial-graph]'`."
    ) from e

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from numpy.typing import NDArray
    from zarr.storage import StoreLike

    from geff._typing import PropDictNpArray
    from geff_spec import AxisType, GeffMetadata

from geff.core_io import write_arrays
from geff.core_io._utils import remove_tilde
from geff_spec.utils import axes_from_lists, create_or_update_metadata

from ._backend_protocol import Backend
from ._graph_adapter import GraphAdapter

GRAPH_TYPES = (sg.SpatialGraph, sg.SpatialDiGraph)


# NOTE: see _api_wrapper.py read/write/construct for docs
class SgBackend(Backend):
    @property
    def GRAPH_TYPES(self) -> tuple[type[sg.SpatialGraph], type[sg.SpatialDiGraph]]:
        return sg.SpatialGraph, sg.SpatialDiGraph

    @staticmethod
    def construct(
        metadata: GeffMetadata,
        node_ids: NDArray[Any],
        edge_ids: NDArray[Any],
        node_props: dict[str, PropDictNpArray],
        edge_props: dict[str, PropDictNpArray],
        position_attr: str = "position",
    ) -> sg.SpatialGraph | sg.SpatialDiGraph:
        # Cast empty list to None for consistency
        if metadata.axes == []:
            metadata.axes = None
        if metadata.axes is None:
            if len(node_ids) != 0:
                raise ValueError(
                    "Cannot construct a non-empty SpatialGraph from a geff without axes"
                )
            else:
                position_attrs = []
        else:
            position_attrs = [axis.name for axis in metadata.axes]
        ndims = len(position_attrs)

        def get_dtype_str(dataset: np.ndarray) -> str:
            dtype = dataset.dtype
            shape = dataset.shape
            if len(shape) > 1:
                size = shape[1]
                return f"{dtype}[{size}]"
            else:
                return str(dtype)

        # read nodes/edges
        node_dtype = get_dtype_str(node_ids)

        # collect node and edge attributes
        node_attr_dtypes = {
            name: get_dtype_str(node_props[name]["values"]) for name in node_props.keys()
        }
        for name in node_props.keys():
            if node_props[name]["missing"] is not None:
                warnings.warn(
                    f"Potential missing values for attr {name} are being ignored",
                    stacklevel=2,
                )
        edge_attr_dtypes = {
            name: get_dtype_str(edge_props[name]["values"]) for name in edge_props.keys()
        }
        for name in edge_props.keys():
            if edge_props[name]["missing"] is not None:
                warnings.warn(
                    f"Potential missing values for attr {name} are being ignored",
                    stacklevel=2,
                )

        node_attrs = {name: node_props[name]["values"] for name in node_props.keys()}
        edge_attrs = {name: edge_props[name]["values"] for name in edge_props.keys()}

        # squish position attributes together into one position attribute
        position: np.ndarray[tuple[int, ...], np.dtype[Any]]
        if len(node_ids) == 0:
            # Need to include a singleton spatial dimension in the shape to be
            # valid for spatial graph
            position = np.zeros(shape=(0, 1), dtype="float64")
            ndims = 1
        else:
            position = np.stack([node_attrs[name] for name in position_attrs], axis=1)
        for name in position_attrs:
            del node_attrs[name]
            del node_attr_dtypes[name]
        node_attrs[position_attr] = position
        node_attr_dtypes[position_attr] = get_dtype_str(position)

        # create graph
        create_graph: Callable[..., sg.SpatialGraph | sg.SpatialDiGraph] = getattr(
            sg, "create_graph", sg.SpatialGraph
        )
        graph = create_graph(
            ndims=ndims,
            node_dtype=node_dtype,
            node_attr_dtypes=node_attr_dtypes,
            edge_attr_dtypes=edge_attr_dtypes,
            position_attr=position_attr,
            directed=metadata.directed,
        )

        if len(node_ids) > 0:
            graph.add_nodes(node_ids, **node_attrs)
            graph.add_edges(edge_ids, **edge_attrs)

        return graph

    @staticmethod
    def write(
        graph: sg.SpatialGraph | sg.SpatialDiGraph,
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
        store = remove_tilde(store)

        if (axis_names is None) and (metadata is not None) and (metadata.axes is not None):
            axis_names = [axis.name for axis in metadata.axes]
        elif axis_names is not None:
            pass
        else:
            # It's ok if there are no axes names if the graph is empty
            if len(list(graph.nodes)) != 0:
                raise ValueError(
                    "Axis names must be specified either using the `axis_names` argument "
                    "or within the geff metadata."
                )
            else:
                axis_names = []

        # create or update metadata
        roi_min, roi_max = graph.roi
        axes = axes_from_lists(
            axis_names,
            axis_units=axis_units,
            axis_types=axis_types,
            axis_scales=axis_scales,
            scaled_units=scaled_units,
            roi_min=roi_min,
            roi_max=roi_max,
            axis_offset=axis_offset,
        )
        metadata = create_or_update_metadata(metadata, graph.directed, axes)

        if graph.ndims != len(axes) and len(list(graph.nodes)) != 0:
            raise ValueError(
                f"Cannot write a SpatialGraph with ndims {graph.ndims} and "
                f"a different number of axes ({axis_names})"
            )

        # write to geff
        write_arrays(
            geff_store=store,
            node_ids=graph.nodes,
            node_props={
                name: {"values": getattr(graph.node_attrs[graph.nodes], name), "missing": None}
                for name in graph.node_attr_dtypes.keys()
            },
            node_props_unsquish={graph.position_attr: axis_names},
            edge_ids=graph.edges,
            edge_props={
                name: {"values": getattr(graph.edge_attrs[graph.edges], name), "missing": None}
                for name in graph.edge_attr_dtypes.keys()
            },
            metadata=metadata,
            zarr_format=zarr_format,
            structure_validation=structure_validation,
        )

    @staticmethod
    def graph_adapter(graph: sg.SpatialGraph | sg.SpatialDiGraph) -> SgGraphAdapter:
        return SgGraphAdapter(graph)


class SgGraphAdapter(GraphAdapter):
    def __init__(self, graph: sg.SpatialGraph | sg.SpatialDiGraph) -> None:
        self.graph = graph

    def get_node_ids(self) -> Sequence[int]:
        return list(self.graph.nodes)

    def get_edge_ids(self) -> Sequence[tuple[int, int]]:
        return [tuple(edge.tolist()) for edge in self.graph.edges]

    def has_node_prop(self, name: str, node: int, metadata: GeffMetadata) -> bool:
        # doesn't support missing node properties
        return True

    def get_node_prop(
        self,
        name: str,
        node: int,
        metadata: GeffMetadata,
    ) -> Any:
        axes = metadata.axes
        if axes is None:
            raise ValueError("No axes found for spatial props")
        axes_names = [ax.name for ax in axes]
        if name in axes_names:
            return self._get_node_spatial_props(name, node, axes_names)
        else:
            return getattr(self.graph.node_attrs[node], name)

    # This is not the most elegant solution but the idea is:
    #   spatial-graph combines the spatial properties into a single position attr
    #   so to compare with the results we need to index each position separately
    def _get_node_spatial_props(
        self,
        name: str,
        node: int,
        axes_names: list[str],
    ) -> Any:
        if name not in axes_names:
            raise ValueError(f"Node property '{name}' not found in axes names {axes_names}")
        idx = axes_names.index(name)
        position = getattr(self.graph.node_attrs[node], self.graph.position_attr)
        position = cast("NDArray[Any]", position)  # cast because getattr call
        return position[idx]

    def has_edge_prop(self, name: str, edge: tuple[int, int], metadata: GeffMetadata) -> bool:
        # doesn't support missing edge properties
        return True

    def get_edge_prop(
        self,
        name: str,
        edge: tuple[int, int],
        metadata: GeffMetadata,
    ) -> Any:
        return getattr(self.graph.edge_attrs[edge], name)
