from __future__ import annotations

import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Any

import networkx as nx
import numpy as np
import zarr

import geff
from geff.file_reader import FileReader
from geff.metadata_schema import GeffMetadata
from geff.writer_helper import write_props

if TYPE_CHECKING:
    from numpy.typing import NDArray

    from geff.dict_representation import GraphDict, PropDict


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

    node_data = list(graph.nodes(data=True))
    write_props(
        group=group.require_group("nodes"),
        data=node_data,
        prop_names=list({k for _, data in node_data for k in data}),
        position_prop=position_prop,
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
        axis_names=(axis_names if axis_names is not None else graph.graph.get("axis_names", None)),
        axis_units=(axis_units if axis_units is not None else graph.graph.get("axis_units", None)),
    )
    metadata.write(group)


def _set_property_values(
    graph: nx.Graph,
    ids: NDArray[Any],
    name: str,
    prop_dict: PropDict[NDArray],
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
            val = val.tolist() if val.size > 1 else val.item()
            if nodes:
                graph.nodes[_id.item()][name] = val
            else:
                source, target = _id.tolist()
                graph.edges[source, target][name] = val


def _ingest_dict_nx(graph_dict: GraphDict):
    metadata = graph_dict["metadata"]

    graph = nx.DiGraph() if metadata.directed else nx.Graph()
    for key, val in metadata:
        graph.graph[key] = val

    graph.add_nodes_from(graph_dict["nodes"].tolist())
    for name, prop_dict in graph_dict["node_props"].items():
        _set_property_values(graph, graph_dict["nodes"], name, prop_dict, nodes=True)

    graph.add_edges_from(graph_dict["edges"].tolist())
    for name, prop_dict in graph_dict["edge_props"].items():
        _set_property_values(graph, graph_dict["edges"], name, prop_dict, nodes=False)

    return graph


def read_nx(
    path: Path | str,
    validate: bool = True,
    node_props: list[str] | None = None,
    edge_props: list[str] | None = None,
) -> nx.Graph:
    """Read a geff file into a networkx graph. Metadata properties will be stored in
    the graph properties, accessed via `G.graph[key]` where G is a networkx graph.

    Args:
        path (Path | str): The path to the root of the geff zarr, where the .attrs contains
            the geff  metadata
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
    if isinstance(path, str):
        path = Path(path)
    path = path.expanduser()
    file_reader = FileReader(path, validate)

    if node_props is None:
        node_props = file_reader.node_prop_names
    if edge_props is None:
        edge_props = file_reader.edge_prop_names

    for node_prop_name in node_props:
        file_reader.read_node_props(node_prop_name)
    for edge_prop_name in edge_props:
        file_reader.read_edge_props(edge_prop_name)

    graph_dict = file_reader.build()
    graph = _ingest_dict_nx(graph_dict)

    return graph
