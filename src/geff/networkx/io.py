from __future__ import annotations

import os
from typing import TYPE_CHECKING, Literal

import networkx as nx
import numpy as np
import zarr

import geff
import geff.utils
from geff.metadata_schema import GeffMetadata, axes_from_lists
from geff.writer_helper import write_props

if TYPE_CHECKING:
    from pathlib import Path


def get_roi(graph: nx.Graph, axis_names: list[str]) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Get the roi of a networkx graph.

    Args:
        graph (nx.Graph): A non-empty networkx graph
        axis_names (str): All nodes on graph have these property holding their position

    Returns:
        tuple[tuple[float, ...], tuple[float, ...]]: A tuple with the min values in each
            spatial dim, and a tuple with the max values in each spatial dim
    """
    _min = None
    _max = None
    for _, data in graph.nodes(data=True):
        pos = np.array([data[name] for name in axis_names])
        if _min is None or _max is None:
            _min = pos
            _max = pos
        else:
            _min = np.min([_min, pos], axis=0)
            _max = np.max([_max, pos], axis=0)

    return tuple(_min.tolist()), tuple(_max.tolist())  # type: ignore


def write_nx(
    graph: nx.Graph,
    path: str | Path,
    axis_names: list[str] | None = None,
    axis_units: list[str] | None = None,
    axis_types: list[str] | None = None,
    zarr_format: Literal[2, 3] | None = 2,
):
    """Write a networkx graph to the geff file format

    Args:
        graph (nx.Graph): A networkx graph
        path (str | Path): The path to the output zarr. Opens in append mode,
            so will only overwrite geff-controlled groups.
        position_prop (Optional[str]): The name of the position property present on every node,
            if present. Defaults to None.
        axis_names (Optional[list[str]], optional): The names of the spatial dims
            represented in position property. Defaults to None. Will override
            value in graph properties if provided.
        axis_units (Optional[list[str]], optional): The units of the spatial dims
            represented in position property. Defaults to None. Will override value
            in graph properties if provided.
        axis_types (Optional[list[str]], optional): The types of the spatial dims
            represented in position property. Usually one of "time", "space", or "channel".
            Defaults to None. Will override value in graph properties if provided.
        zarr_format (int, optional): The version of zarr to write.
            Defaults to 2.
    """
    # open/create zarr container
    if zarr.__version__.startswith("3"):
        group = zarr.open_group(path, mode="a", zarr_format=zarr_format)
    else:
        group = zarr.open_group(path, mode="a")
    # TODO: update this once we have changed/standardized how we are handling pre-existing metadata
    axis_names = axis_names if axis_names is not None else graph.graph.get("axis_names", None)
    axis_units = axis_units if axis_units is not None else graph.graph.get("axis_units", None)
    axis_types = axis_types if axis_types is not None else graph.graph.get("axis_types", None)

    node_data = list(graph.nodes(data=True))
    write_props(
        group=group.require_group("nodes"),
        data=node_data,
        prop_names=list({k for _, data in node_data for k in data}),
        axis_names=axis_names,
    )
    del node_data

    edge_data = [((u, v), data) for u, v, data in graph.edges(data=True)]
    write_props(
        group=group.require_group("edges"),
        data=edge_data,
        prop_names=list({k for _, data in edge_data for k in data}),
    )
    del edge_data

    # write metadata
    roi_min: tuple[float, ...] | None
    roi_max: tuple[float, ...] | None
    if axis_names is not None and graph.number_of_nodes() > 0:
        roi_min, roi_max = get_roi(graph, axis_names)
    else:
        roi_min, roi_max = None, None
    axes = axes_from_lists(
        axis_names, axis_units=axis_units, axis_types=axis_types, roi_min=roi_min, roi_max=roi_max
    )
    metadata = GeffMetadata(
        geff_version=geff.__version__,
        directed=isinstance(graph, nx.DiGraph),
        axes=axes,
    )
    metadata.write(group)


def _set_property_values(
    graph: nx.DiGraph, ids: np.ndarray, graph_group: zarr.Group, name: str, nodes: bool = True
) -> None:
    """Add properties in-place to a networkx graph's
    nodes or edges by creating attributes on the nodes/edges

    Args:
        graph (nx.DiGraph): The networkx graph, already populated with nodes or edges,
            that needs properties added
        ids (np.ndarray): Node or edge ids from Geff. If nodes, 1D. If edges, 2D.
        graph_group (zarr.Group): A zarr group holding the geff graph.
        name (str): The name of the property
        nodes (bool, optional): If True, extract and set node properties.  If False,
            extract and set edge properties. Defaults to True.
    """
    element = "nodes" if nodes else "edges"
    prop_group = graph_group[f"{element}/props/{name}"]
    values = prop_group["values"][:]
    sparse = "missing" in prop_group.array_keys()
    if sparse:
        missing = prop_group["missing"][:]
    for idx in range(len(ids)):
        _id = ids[idx]
        val = values[idx]
        # If property is sparse and missing for this node, skip setting property
        ignore = missing[idx] if sparse else False
        if not ignore:
            # Get either individual item or list instead of setting with np.array
            val = val.tolist() if val.size > 1 else val.item()
            if nodes:
                graph.nodes[_id.item()][name] = val
            else:
                source, target = _id.tolist()
                graph.edges[source, target][name] = val


def read_nx(path: Path | str, validate: bool = True) -> nx.Graph:
    """Read a geff file into a networkx graph. Metadata properties will be stored in
    the graph properties, accessed via `G.graph[key]` where G is a networkx graph.

    Args:
        path (Path | str): The path to the root of the geff zarr, where the .attrs contains
            the geff  metadata
        validate (bool, optional): Flag indicating whether to perform validation on the
            geff file before loading into memory. If set to False and there are
            format issues, will likely fail with a cryptic error. Defaults to True.

    Returns:
        A networkx graph containing the graph that was stored in the geff file format
    """
    # zarr python 3 doesn't support Path
    path = str(path)
    path = os.path.expanduser(path)

    # open zarr container
    if validate:
        geff.utils.validate(path)

    group = zarr.open_group(path, mode="r")
    metadata = GeffMetadata.read(group)

    # read meta-data
    graph = nx.DiGraph() if metadata.directed else nx.Graph()
    for key, val in metadata:
        graph.graph[key] = val

    nodes = group["nodes/ids"][:]
    graph.add_nodes_from(nodes.tolist())

    # collect node properties
    for name in group["nodes/props"]:
        _set_property_values(graph, nodes, group, name, nodes=True)

    if "edges" in group.group_keys():
        edges = group["edges/ids"][:]
        graph.add_edges_from(edges.tolist())

        # collect edge properties if they exist
        if "edges/props" in group:
            for name in group["edges/props"]:
                _set_property_values(graph, edges, group, name, nodes=False)

    return graph
