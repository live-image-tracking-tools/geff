from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

import networkx as nx
import numpy as np
import zarr

import geff
import geff.utils
from geff.metadata_schema import GeffMetadata

if TYPE_CHECKING:
    from pathlib import Path


def get_roi(graph: nx.Graph, position_prop: str) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Get the roi of a networkx graph.

    Args:
        graph (nx.Graph): A non-empty networkx graph
        position_prop (str): All nodes on graph have this property holding their position

    Returns:
        tuple[tuple[float, ...], tuple[float, ...]]: A tuple with the min values in each
            spatial dim, and a tuple with the max values in each spatial dim
    """
    _min = None
    _max = None
    for _, data in graph.nodes(data=True):
        pos = np.array(data[position_prop])
        if _min is None:
            _min = pos
            _max = pos
        else:
            _min = np.min([_min, pos], axis=0)
            _max = np.max([_max, pos], axis=0)

    return tuple(_min.tolist()), tuple(_max.tolist())  # type: ignore


def get_node_props(graph: nx.Graph) -> list[str]:
    """Get the property keys present on any node in the networkx graph. Does not imply
    that the properties are present on all nodes.

    Args:
        graph (nx.Graph): A networkx graph

    Returns:
        list[str]: A list of all unique node property keys
    """
    return list({k for n in graph.nodes for k in graph.nodes[n]})


def get_edge_props(graph: nx.Graph) -> list[str]:
    """Get the property keys present on any edge in the networkx graph. Does not imply
    that the properties are present on all edges.

    Args:
        graph (nx.Graph): A networkx graph

    Returns:
        list[str]: A list of all unique edge property keys
    """
    return list({k for e in graph.edges for k in graph.edges[e]})


def write_nx(
    graph: nx.Graph,
    path: str | Path,
    position_prop: str | None = None,
    axis_names: list[str] | None = None,
    axis_units: list[str] | None = None,
    zarr_format: int = 2,
    validate: bool = True,
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
        zarr_format (int, optional): The version of zarr to write.
            Defaults to 2.
        validate (bool, optional): Flag indicating whether to perform validation on the
            networkx graph before writing anything to disk. If set to False and there are
            missing properties, will likely fail with a KeyError, leading to an incomplete
            graph written to disk. Defaults to True.
    """
    if graph.number_of_nodes() == 0:
        warnings.warn(f"Graph is empty - not writing anything to {path}", stacklevel=2)
        return

    # open/create zarr container
    if zarr.__version__.startswith("3"):
        group = zarr.open(path, mode="a", zarr_format=zarr_format)
    else:
        group = zarr.open(path, mode="a")

    node_props = get_node_props(graph)
    if validate:
        if position_prop is not None:
            if position_prop not in node_props:
                raise ValueError(f"Position property {position_prop} not found in graph")
            for node, data in graph.nodes(data=True):
                if position_prop not in data:
                    raise ValueError(f"Node {node} does not have position property {position_prop}")

    # write metadata
    roi_min: tuple[float, ...] | None
    roi_max: tuple[float, ...] | None
    if position_prop is not None:
        roi_min, roi_max = get_roi(graph, position_prop=position_prop)
    else:
        roi_min, roi_max = None, None
    metadata = GeffMetadata(
        geff_version=geff.__version__,
        directed=isinstance(graph, nx.DiGraph),
        roi_min=roi_min,
        roi_max=roi_max,
        position_prop=position_prop,
        axis_names=axis_names if axis_names is not None else graph.graph.get("axis_names", None),
        axis_units=axis_units if axis_units is not None else graph.graph.get("axis_units", None),
    )
    metadata.write(group)

    # get node and edge IDs
    nodes_list = list(graph.nodes())
    nodes_arr = np.array(nodes_list)
    edges_list = list(graph.edges())
    edges_arr = np.array(edges_list)

    # write nodes
    group["nodes/ids"] = nodes_arr

    # write node properties
    for name in node_props:
        values = []
        missing = []
        for node in nodes_list:
            if name in graph.nodes[node]:
                value = graph.nodes[node][name]
                mask = 0
            else:
                value = 0
                mask = 1
            values.append(value)
            missing.append(mask)
        # Missing value are only allowed for non-position property
        if name != position_prop:
            # Always store missing array even if all values are present
            group[f"nodes/props/{name}/missing"] = np.array(missing, dtype=bool)
        group[f"nodes/props/{name}/values"] = np.array(values)

    # write edges
    # Edge group is only created if edges are present on graph
    if len(edges_list) > 0:
        group["edges/ids"] = edges_arr

        # write edge properties
        for name in get_edge_props(graph):
            values = []
            missing = []
            for edge in edges_list:
                if name in graph.edges[edge]:
                    value = graph.edges[edge][name]
                    mask = 0
                else:
                    value = 0
                    mask = 1
                values.append(value)
                missing.append(mask)
            group[f"edges/props/{name}/missing"] = np.array(missing, dtype=bool)
            group[f"edges/props/{name}/values"] = np.array(values)


def _set_property_values(
    graph: nx.DiGraph, ids: np.ndarray, graph_group: zarr.Group, name: str, nodes: bool = True
) -> None:
    """Add properties in-place to a networkx graph's nodes or edges.

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

    # open zarr container
    if validate:
        geff.utils.validate(path)

    group = zarr.open(path, mode="r")
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
