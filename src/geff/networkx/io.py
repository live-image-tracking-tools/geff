from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Any, Sequence

import networkx as nx
import numpy as np
import zarr

import geff
import geff.utils
from geff.metadata_schema import GeffMetadata
from geff.writer_helper import BaseWriterHelper

if TYPE_CHECKING:
    from pathlib import Path


def get_roi(graph: nx.Graph, position_attr: str) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Get the roi of a networkx graph.

    Args:
        graph (nx.Graph): A non-empty networkx graph
        position_attr (str): All nodes on graph have this attribute holding their position

    Returns:
        tuple[tuple[float, ...], tuple[float, ...]]: A tuple with the min values in each
            spatial dim, and a tuple with the max values in each spatial dim
    """
    _min = None
    _max = None
    for _, data in graph.nodes(data=True):
        pos = np.array(data[position_attr])
        if _min is None:
            _min = pos
            _max = pos
        else:
            _min = np.min([_min, pos], axis=0)
            _max = np.max([_max, pos], axis=0)

    return tuple(_min.tolist()), tuple(_max.tolist())  # type: ignore


class NXWriterHelper(BaseWriterHelper):
    """
    Helper class for writing node or edge attributes to a zarr group.

    Args:
        group: The zarr group to write the attribute to.
        iterator: a sequence of (id, data) pairs. For example, graph.nodes(data=True)
        position_attr: The name of the position attribute. If None, no position attribute
    """

    def __init__(
        self,
        group: zarr.Group,
        data_sequence: Sequence[tuple[Any, dict[str, Any]]],
        position_attr: str | None = None,
    ):
        super().__init__(group, position_attr)
        self._data = data_sequence
        ids = [idx for idx, _ in data_sequence]
        if len(ids) > 0:
            self._group["ids"] = np.asarray(ids)
        elif self._group.name == "/nodes":
            self._group["ids"] = np.empty((0,), dtype=np.int64)
        elif self._group.name == "/edges":
            self._group["ids"] = np.empty((0, 2), dtype=np.int64)
        else:
            raise ValueError(f"Invalid group name: {self._group.name}")

    def _data_dict_iterator(self) -> Sequence[tuple[Any, dict[str, Any]]]:
        return self._data

    def _attr_names(self) -> list[str]:
        return list({k for _, data in self._data for k in data})


def write_nx(
    graph: nx.Graph,
    path: str | Path,
    position_attr: str | None = None,
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
        position_attr (Optional[str]): The name of the position attribute present on every node,
            if present. Defaults to None.
        axis_names (Optional[list[str]], optional): The names of the spatial dims
            represented in position attribute. Defaults to None. Will override
            value in graph attributes if provided.
        axis_units (Optional[list[str]], optional): The units of the spatial dims
            represented in position attribute. Defaults to None. Will override value
            in graph attributes if provided.
        zarr_format (int, optional): The version of zarr to write.
            Defaults to 2.
        validate (bool, optional): Flag indicating whether to perform validation on the
            networkx graph before writing anything to disk. If set to False and there are
            missing attributes, will likely fail with a KeyError, leading to an incomplete
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

    node_writer = NXWriterHelper(
        group.require_group("nodes"),
        list(graph.nodes(data=True)),
        position_attr=position_attr,
    )
    node_writer.write_attrs()

    edge_writer = NXWriterHelper(
        group.require_group("edges"),
        [((u, v), data) for u, v, data in graph.edges(data=True)],
    )
    edge_writer.write_attrs()

    # write metadata
    if position_attr is not None:
        roi_min, roi_max = get_roi(graph, position_attr=position_attr)
    else:
        roi_min, roi_max = None, None

    metadata = GeffMetadata(
        geff_version=geff.__version__,
        directed=isinstance(graph, nx.DiGraph),
        roi_min=roi_min,
        roi_max=roi_max,
        position_attr=position_attr,
        axis_names=axis_names if axis_names is not None else graph.graph.get("axis_names", None),
        axis_units=axis_units if axis_units is not None else graph.graph.get("axis_units", None),
    )
    metadata.write(group)


def _set_attribute_values(
    graph: nx.DiGraph, ids: np.ndarray, graph_group: zarr.Group, name: str, nodes: bool = True
) -> None:
    """Add attributes in-place to a networkx graph's nodes or edges.

    Args:
        graph (nx.DiGraph): The networkx graph, already populated with nodes or edges,
            that needs attributes added
        ids (np.ndarray): Node or edge ids from Geff. If nodes, 1D. If edges, 2D.
        graph_group (zarr.Group): A zarr group holding the geff graph.
        name (str): The name of the attribute
        nodes (bool, optional): If True, extract and set node attributes.  If False,
            extract and set edge attributes. Defaults to True.
    """
    element = "nodes" if nodes else "edges"
    attr_group = graph_group[f"{element}/attrs/{name}"]
    values = attr_group["values"][:]
    sparse = "missing" in attr_group.array_keys()
    if sparse:
        missing = attr_group["missing"][:]
    for idx in range(len(ids)):
        _id = ids[idx]
        val = values[idx]
        # If attribute is sparse and missing for this node, skip setting attribute
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
    """Read a geff file into a networkx graph. Metadata attributes will be stored in
    the graph attributes, accessed via `G.graph[key]` where G is a networkx graph.

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

    # collect node attributes
    for name in group["nodes/attrs"]:
        _set_attribute_values(graph, nodes, group, name, nodes=True)

    if "edges" in group.group_keys():
        edges = group["edges/ids"][:]
        graph.add_edges_from(edges.tolist())

        # collect edge attributes if they exist
        if "edges/attrs" in group:
            for name in group["edges/attrs"]:
                _set_attribute_values(graph, edges, group, name, nodes=False)

    return graph
