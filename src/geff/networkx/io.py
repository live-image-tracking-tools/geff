from __future__ import annotations

import copy
import warnings
from typing import TYPE_CHECKING, Any, Literal

import networkx as nx
import numpy as np
import zarr

import geff
from geff.geff_reader import read_to_dict
from geff.metadata_schema import GeffMetadata, axes_from_lists
from geff.write_dicts import write_dicts

if TYPE_CHECKING:
    from pathlib import Path

    from numpy.typing import NDArray

    from geff.dict_representation import GraphDict, PropDictNpArray

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
    _min = None
    _max = None
    for node, data in graph.nodes(data=True):
        try:
            pos = np.array([data[name] for name in axis_names])
        except KeyError as e:
            missing_names = {name for name in axis_names if name not in data}
            raise ValueError(
                f"Spatiotemporal properties {missing_names} not found in node {node}"
            ) from e
        if _min is None or _max is None:
            _min = pos
            _max = pos
        else:
            _min = np.min([_min, pos], axis=0)
            _max = np.max([_max, pos], axis=0)

    return tuple(_min.tolist()), tuple(_max.tolist())  # type: ignore


def _get_graph_existing_metadata(
    graph: nx.Graph,
    metadata: GeffMetadata | None = None,
    axis_names: list[str] | None = None,
    axis_units: list[str | None] | None = None,
    axis_types: list[str | None] | None = None,
) -> tuple[list[str] | None, list[str | None] | None, list[str | None] | None]:
    """Get the existing metadata from a graph.

    If axis lists are provided, they will override the graph properties and metadata.
    If metadata is provided, it will override the graph properties.
    If neither are provided, the graph properties will be used.

    Args:
        graph (nx.Graph): A networkx graph
        metadata (GeffMetadata, optional): The metadata of the graph. Defaults to None.
        axis_names (list[str | None], optional): The names of the spatial dims. Defaults to None.
        axis_units (list[str | None], optional): The units of the spatial dims. Defaults to None.
        axis_types (list[str | None], optional): The types of the spatial dims. Defaults to None.

    Returns:
        tuple[list[str] | None, list[str | None] | None, list[str | None] | None]:
            A tuple with the names of the spatial dims, the units of the spatial dims,
            and the types of the spatial dims. None if not provided.
    """
    lists_provided = any(x is not None for x in [axis_names, axis_units, axis_types])
    metadata_provided = metadata is not None

    if lists_provided and metadata_provided:
        warnings.warn(
            "Both axis lists and metadata provided. Overriding metadata with axis lists.",
            stacklevel=2,
        )

    # If any axis lists is not provided, fallback to metadata if provided
    if metadata is not None and metadata.axes is not None:
        # the x = x or y is a python idiom for setting x to y if x is None, otherwise x
        axis_names = axis_names or [axis.name for axis in metadata.axes]
        axis_units = axis_units or [axis.unit for axis in metadata.axes]
        axis_types = axis_types or [axis.type for axis in metadata.axes]

    return axis_names, axis_units, axis_types


def write_nx(
    graph: nx.Graph,
    path: str | Path,
    metadata: GeffMetadata | None = None,
    axis_names: list[str] | None = None,
    axis_units: list[str | None] | None = None,
    axis_types: list[str | None] | None = None,
    zarr_format: Literal[2, 3] | None = 2,
):
    """Write a networkx graph to the geff file format

    Args:
        graph (nx.Graph): A networkx graph
        path (str | Path): The path to the output zarr. Opens in append mode,
            so will only overwrite geff-controlled groups.
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
        zarr_format (int, optional): The version of zarr to write.
            Defaults to 2.
    """
    # open/create zarr container
    if zarr.__version__.startswith("3"):
        group = zarr.open_group(path, mode="a", zarr_format=zarr_format)
    else:
        group = zarr.open_group(path, mode="a")

    axis_names, axis_units, axis_types = _get_graph_existing_metadata(
        graph, metadata, axis_names, axis_units, axis_types
    )

    node_props = list({k for _, data in graph.nodes(data=True) for k in data})

    edge_data = [((u, v), data) for u, v, data in graph.edges(data=True)]
    edge_props = list({k for _, _, data in graph.edges(data=True) for k in data})
    write_dicts(
        path,
        graph.nodes(data=True),
        edge_data,
        node_props,
        edge_props,
        axis_names,
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

    # Conditionally update metadata with new axes, version, and directedness
    # If metadata is provided, extra properties are preserved; otherwise, a new GeffMetadata object
    # is created
    if metadata is not None:
        metadata = copy.deepcopy(metadata)
        metadata.geff_version = geff.__version__
        metadata.directed = isinstance(graph, nx.DiGraph)
        metadata.axes = axes
    else:
        metadata = GeffMetadata(
            geff_version=geff.__version__,
            directed=isinstance(graph, nx.DiGraph),
            axes=axes,
        )
    metadata.write(group)


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

    return graph, metadata


def read_nx(
    path: Path | str,
    validate: bool = True,
    node_props: list[str] | None = None,
    edge_props: list[str] | None = None,
) -> tuple[nx.Graph, GeffMetadata]:
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
    graph_dict = read_to_dict(path, validate, node_props, edge_props)
    graph, metadata = _ingest_dict_nx(graph_dict)

    return graph, metadata
