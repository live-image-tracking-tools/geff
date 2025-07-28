from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Literal

try:
    import spatial_graph as sg
except ImportError as e:
    raise ImportError(
        "This module requires spatial-graph to be installed. "
        "Please install it with `pip install 'geff[spatial-graph]'`."
    ) from e

import numpy as np
from zarr.storage import StoreLike

if TYPE_CHECKING:
    from zarr.storage import StoreLike

import geff
from geff.geff_reader import read_to_memory
from geff.metadata_schema import GeffMetadata, axes_from_lists
from geff.utils import remove_tilde
from geff.write_arrays import write_arrays


def write_sg(
    graph: sg.SpatialGraph | sg.SpatialDiGraph,
    store: StoreLike,
    axis_names: list[str] | None = None,
    axis_units: list[str] | None = None,
    axis_types: list[str] | None = None,
    zarr_format: Literal[2, 3] = 2,
):
    """Write a SpatialGraph to the geff file format.

    Because SpatialGraph does not support ragged or missing node/edge attributes,
    the missing arrays will not be written.

    Args:
        graph (sg.SpatialGraph):

            The graph to write.

        store (str | Path | zarr store):

            The path to the output zarr. Opens in append mode, so will only
            overwrite geff-controlled groups.

        axis_names (Optional[list[str]], optional):

            The names of the spatial dims represented in position attribute.
            Defaults to None.

        axis_units (Optional[list[str]], optional):

            The units of the spatial dims represented in position attribute.
            Defaults to None.

        axis_types (Optional[list[str]], optional):

            The types of the spatial dims represented in position property.
            Usually one of "time", "space", or "channel". Defaults to None.

        zarr_format (Literal[2, 3], optional):

            The version of zarr to write. Defaults to 2.
    """

    store = remove_tilde(store)

    if len(graph) == 0:
        warnings.warn(f"Graph is empty - not writing anything to {store}", stacklevel=2)
        return

    if axis_names is None:
        assert graph.dims <= 4, (
            "For SpatialGraphs with more than 4 dimension, axis_names has to be provided."
        )
        axis_names = ["t", "z", "y", "x"][-graph.dims :]

    # create metadata
    roi_min, roi_max = graph.roi
    axes = axes_from_lists(
        axis_names, axis_units=axis_units, axis_types=axis_types, roi_min=roi_min, roi_max=roi_max
    )
    metadata = GeffMetadata(
        geff_version=geff.__version__,
        directed=graph.directed,
        axes=axes,
    )

    # write to geff
    write_arrays(
        geff_store=store,
        node_ids=graph.nodes,
        node_props={
            name: getattr(graph.node_attrs, name) for name in graph.node_attr_dtypes.keys()
        },
        node_props_unsquish={graph.position_attr: axis_names},
        edge_ids=graph.edges,
        edge_props={
            name: getattr(graph.edge_attrs, name) for name in graph.edge_attr_dtypes.keys()
        },
        metadata=metadata,
        zarr_format=zarr_format,
    )


def read_sg(
    store: StoreLike,
    validate: bool = True,
    position_attr: str = "position",
    node_props: list[str] | None = None,
    edge_props: list[str] | None = None,
) -> sg.SpatialGraph:
    """Read a geff file into a SpatialGraph.

    Because SpatialGraph does not support missing/ragged node/edge attributes,
    missing arrays will be ignored, with a warning raised.

    Args:

        store (Path | str | zarr store):

            The path to the root of the geff zarr, where the .attrs contains
            the geff  metadata.

        validate (bool, optional):

            Flag indicating whether to perform validation on the geff file
            before loading into memory. If set to False and there are format
            issues, will likely fail with a cryptic error. Defaults to True.

        position_attr (str, optional):

            How to call the position attribute in the returned SpatialGraph.
            Defaults to "position".

        node_props (list of str, optional):

            The names of the node properties to load, if None all properties
            will be loaded, defaults to None.

        edge_props (list of str, optional):

            The names of the edge properties to load, if None all properties
            will be loaded, defaults to None.

    Returns:

        A SpatialGraph containing the graph that was stored in the geff file
        format.
    """

    in_memory_geff = read_to_memory(store, validate, node_props, edge_props)

    metadata = in_memory_geff["metadata"]
    assert metadata.axes is not None, "Can not construct a SpatialGraph from a non-spatial geff"

    position_attrs = [axis.name for axis in metadata.axes]
    ndims = len(position_attrs)

    def get_dtype_str(dataset):
        dtype = dataset.dtype
        shape = dataset.shape
        if len(shape) > 1:
            size = shape[1]
            return f"{dtype}[{size}]"
        else:
            return str(dtype)

    # read nodes/edges
    nodes = in_memory_geff["node_ids"]
    edges = in_memory_geff["edge_ids"]
    node_dtype = get_dtype_str(nodes)

    # collect node and edge attributes
    node_attr_dtypes = {
        name: get_dtype_str(in_memory_geff["node_props"][name]["values"])
        for name in in_memory_geff["node_props"].keys()
    }
    for name in in_memory_geff["node_props"].keys():
        if "missing" in in_memory_geff["node_props"][name]:
            warnings.warn(
                f"Potential missing values for attr {name} are being ignored", stacklevel=2
            )
    edge_attr_dtypes = {
        name: get_dtype_str(in_memory_geff["edge_props"][name]["values"])
        for name in in_memory_geff["edge_props"].keys()
    }
    for name in in_memory_geff["edge_props"].keys():
        if "missing" in in_memory_geff["edge_props"][name]:
            warnings.warn(
                f"Potential missing values for attr {name} are being ignored", stacklevel=2
            )

    node_attrs = {
        name: in_memory_geff["node_props"][name]["values"]
        for name in in_memory_geff["node_props"].keys()
    }
    edge_attrs = {
        name: in_memory_geff["edge_props"][name]["values"]
        for name in in_memory_geff["edge_props"].keys()
    }

    # squish position attributes together into one position attribute
    position = np.stack([node_attrs[name] for name in position_attrs], axis=1)
    for name in position_attrs:
        del node_attrs[name]
        del node_attr_dtypes[name]
    node_attrs[position_attr] = position
    node_attr_dtypes[position_attr] = get_dtype_str(position)

    # create graph
    create_graph = getattr(sg, "create_graph", sg.SpatialGraph)
    graph = create_graph(
        ndims=ndims,
        node_dtype=node_dtype,
        node_attr_dtypes=node_attr_dtypes,
        edge_attr_dtypes=edge_attr_dtypes,
        position_attr=position_attr,
        directed=metadata.directed,
    )

    graph.add_nodes(nodes, **node_attrs)
    graph.add_edges(edges, **edge_attrs)

    return graph
