from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

import spatial_graph as sg
import zarr

import geff
from geff.metadata_schema import GeffMetadata

if TYPE_CHECKING:
    from pathlib import Path


def write_sg(
    graph: sg.SpatialGraph,
    path: str | Path,
    axis_names: list[str] | None = None,
    axis_units: list[str] | None = None,
    zarr_format: int = 2,
):
    """Write a SpatialGraph to the geff file format

    Args:
        graph (sg.SpatialGraph):

            The graph to write.

        path (str | Path):

            The path to the output zarr. Opens in append mode, so will only
            overwrite geff-controlled groups.

        axis_names (Optional[list[str]], optional):

            The names of the spatial dims represented in position attribute.
            Defaults to None. Will override value in graph attributes if
            provided.

        axis_units (Optional[list[str]], optional):

            The units of the spatial dims represented in position attribute.
            Defaults to None. Will override value in graph attributes if
            provided.

        zarr_format (int, optional):

            The version of zarr to write. Defaults to 2.
    """
    if len(graph) == 0:
        warnings.warn(f"Graph is empty - not writing anything to {path}", stacklevel=2)
        return

    # open/create zarr container
    if zarr.__version__.startswith("3"):
        group = zarr.open(path, mode="a", zarr_format=zarr_format)
    else:
        group = zarr.open(path, mode="a")

    # write node/edge IDs
    group["nodes/ids"] = graph.nodes
    group["edges/ids"] = graph.edges

    for name in graph.node_attr_dtypes.keys():
        group[f"nodes/attrs/{name}/values"] = getattr(graph.node_attrs, name)
    for name in graph.edge_attr_dtypes.keys():
        group[f"edges/attrs/{name}/values"] = getattr(graph.edge_attrs, name)

    # write metadata
    roi_min, roi_max = graph.roi
    metadata = GeffMetadata(
        geff_version=geff.__version__,
        directed=graph.directed,
        roi_min=roi_min,
        roi_max=roi_max,
        position_attr=graph.position_attr,
        axis_names=axis_names,
        axis_units=axis_units,
    )
    metadata.write(group)


def read_sg(path: Path | str, validate: bool = True) -> sg.SpatialGraph:
    """Read a geff file into a SpatialGraph.

    Args:

        path (Path | str):

            The path to the root of the geff zarr, where the .attrs contains
            the geff  metadata.

        validate (bool, optional):

            Flag indicating whether to perform validation on the geff file
            before loading into memory. If set to False and there are format
            issues, will likely fail with a cryptic error. Defaults to True.

    Returns:

        A SpatialGraph containing the graph that was stored in the geff file
        format.
    """
    # zarr python 3 doesn't support Path
    path = str(path)

    # open zarr container
    if validate:
        geff.utils.validate(path)

    group = zarr.open(path, mode="r")
    metadata = GeffMetadata.read(group)

    position_attr = metadata.position_attr
    ndims = group[f"nodes/attrs/{position_attr}/values"].shape[1]

    def get_dtype_str(dataset):
        dtype = dataset.dtype
        shape = dataset.shape
        if len(shape) > 1:
            size = shape[1]
            return f"{dtype}[{size}]"
        else:
            return str(dtype)

    # read nodes/edges
    nodes = group["nodes/ids"][:]
    edges = group["edges/ids"][:]
    node_dtype = get_dtype_str(group["nodes/ids"])

    # collect node attributes
    node_attr_dtypes = {
        name: get_dtype_str(group[f"nodes/attrs/{name}/values"]) for name in group["nodes/attrs"]
    }
    edge_attr_dtypes = {
        name: get_dtype_str(group[f"edges/attrs/{name}/values"]) for name in group["edges/attrs"]
    }
    node_attrs = {name: group[f"nodes/attrs/{name}/values"][:] for name in group["nodes/attrs"]}
    edge_attrs = {name: group[f"edges/attrs/{name}/values"][:] for name in group["edges/attrs"]}

    # create graph
    graph = sg.SpatialGraph(
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
