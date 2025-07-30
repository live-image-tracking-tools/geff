from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, cast

import networkx as nx
import networkx.algorithms.isomorphism as iso
import numpy as np
import zarr

from . import _path

if TYPE_CHECKING:
    from collections.abc import Mapping

    from zarr.storage import StoreLike

from urllib.parse import urlparse

from .metadata_schema import GeffMetadata


def is_remote_url(path: str) -> bool:
    """Returns True if the path is a remote URL (http, https, ftp, sftp), otherwise False.

    Parameters
    ----------
    path : str
        path to a local or remote resource

    Returns
    -------
    bool
        True if the path is a remote URL, False otherwise
    """
    parsed = urlparse(path)
    return parsed.scheme in ("http", "https", "ftp", "sftp")


def remove_tilde(store: StoreLike) -> StoreLike:
    """
    Remove tilde from a store path/str, because zarr (3?) will not recognize
        the tilde and write the zarr in the wrong directory.

    Args:
        store (str | Path | zarr store): The store to remove the tilde from

    Returns:
        StoreLike: The store with the tilde removed
    """
    if isinstance(store, str | Path):
        store_str = str(store)
        if "~" in store_str:
            store = os.path.expanduser(store_str)
    return store


def _validate_props_metadata(
    props_metadata_dict: Mapping, props_group: zarr.Group, component_type: str
) -> None:
    """Validate that properties described in metadata are compatible with the data in zarr arrays.

    Args:
        props_metadata_dict (dict): Dictionary of property metadata with identifier keys
            and PropMetadata values
        props_group (zarr.Group): Zarr group containing the component properties (nodes or edges)
        component_type (str): Component type for error messages ("Node" or "Edge")

    Raises:
        AssertionError: If properties in metadata don't match zarr arrays
    """
    id_dtype_map = {
        prop.identifier: np.dtype(prop.dtype).type for prop in props_metadata_dict.values()
    }
    for prop_id, prop_dtype in id_dtype_map.items():
        # Properties described in metadata should be present in zarr arrays
        assert prop_id in props_group.keys(), (
            f"{component_type} property {prop_id} described in metadata is not present "
            f"in props arrays"
        )
        # dtype in metadata should match dtype in zarr arrays
        array_dtype = props_group[prop_id][_path.VALUES].dtype  # type: ignore
        assert array_dtype == prop_dtype, (
            f"{component_type} property {prop_id} with dtype {array_dtype} does not match "
            f"metadata dtype {prop_dtype}"
        )


def validate(store: StoreLike) -> None:
    """Ensure that the structure of the zarr conforms to geff specification

    Args:
        store (str | Path | zarr store): Check the geff zarr, either str/Path/store

    Raises:
        ValueError: If geff specs are violated
        FileNotFoundError: If store is not a valid zarr store or path doesn't exist
    """

    # Check if path exists for string/Path inputs
    if isinstance(store, str | Path):
        store_path = Path(store)
        if not is_remote_url(str(store_path)) and not store_path.exists():
            raise FileNotFoundError(f"Path does not exist: {store}")

    # Open the zarr group from the store
    try:
        graph_group = zarr.open_group(store, mode="r")
    except Exception as e:
        raise ValueError(f"store must be a zarr StoreLike: {e}") from e

    # graph attrs validation
    # Raises pydantic.ValidationError or ValueError
    metadata = GeffMetadata.read(store)

    nodes_group = expect_group(graph_group, _path.NODES)
    _validate_nodes_group(nodes_group, metadata)

    # TODO: Do we want to prevent missing values on spatialtemporal properties
    if _path.EDGES in graph_group.keys():
        edges_group = expect_group(graph_group, _path.EDGES)
        _validate_edges_group(edges_group, metadata)


# -----------------------------------------------------------------------------#
# helpers
# -----------------------------------------------------------------------------#


def expect_array(parent: zarr.Group, key: str, parent_name: str) -> zarr.Array:
    """Return an array in the parent group with the given key, or raise ValueError."""
    arr = parent.get(key)
    if not isinstance(arr, zarr.Array):
        raise ValueError(f"{parent_name!r} group must contain an {key!r} array")
    return arr


def expect_group(parent: zarr.Group, key: str, parent_name: str = "graph") -> zarr.Group:
    """Return a group in the parent group with the given key, or raise ValueError."""
    grp = parent.get(key)
    if not isinstance(grp, zarr.Group):
        raise ValueError(f"{parent_name!r} group must contain a group named {key!r}")
    return grp


# -----------------------------------------------------------------------------#
# node / edge / props validators
# -----------------------------------------------------------------------------#


def _validate_props_group(
    props_group: zarr.Group,
    expected_len: int,
    parent_key: str,
) -> None:
    """Validate every property subgroup under `props_group`."""
    for prop_name in props_group.keys():
        prop_group = props_group[prop_name]
        if not isinstance(prop_group, zarr.Group):
            raise ValueError(
                f"{_path.PROPS!r} group '{prop_name}' under {parent_key!r} "
                f"must be a zarr group. Got {type(prop_group)}"
            )

        arrays = set(prop_group.array_keys())
        if _path.VALUES not in arrays:
            raise ValueError(
                f"{parent_key} property group {prop_name!r} must have a {_path.VALUES!r} array"
            )

        val_len = cast("zarr.Array", prop_group[_path.VALUES]).shape[0]
        if val_len != expected_len:
            raise ValueError(
                f"{parent_key} property {prop_name!r} {_path.VALUES} has length {val_len}, "
                f"which does not match id length {expected_len}"
            )

        if _path.MISSING in arrays:
            miss_len = cast("zarr.Array", prop_group[_path.MISSING]).shape[0]
            if miss_len != expected_len:
                raise ValueError(
                    f"{parent_key} property {prop_name!r} {_path.MISSING} mask has length "
                    f"{miss_len}, which does not match id length {expected_len}"
                )


def _validate_nodes_group(nodes_group: zarr.Group, metadata: GeffMetadata) -> None:
    """Validate the structure of a nodes group in a GEFF zarr store."""
    node_ids = expect_array(nodes_group, _path.IDS, _path.NODES)
    id_len = node_ids.shape[0]
    node_props = expect_group(nodes_group, _path.PROPS, _path.NODES)
    _validate_props_group(node_props, id_len, "Node")

    # Node properties metadata validation
    if metadata.node_props_metadata is not None:
        _validate_props_metadata(metadata.node_props_metadata, node_props, "Node")


def _validate_edges_group(edges_group: zarr.Group, metadata: GeffMetadata) -> None:
    """Validate the structure of an edges group in a GEFF zarr store."""
    # Edges only require ids which contain nodes for each edge
    edges_ids = expect_array(edges_group, _path.IDS, _path.EDGES)
    if edges_ids.shape[-1] != 2:
        raise ValueError(
            f"edges ids must have a last dimension of size 2, received shape {edges_ids.shape}"
        )

    # Edge property array length should match edge id length
    edge_id_len = edges_ids.shape[0]
    edge_props = edges_group.get(_path.PROPS)
    if edge_props is None:
        return
    if not isinstance(edge_props, zarr.Group):
        raise ValueError(
            f"{_path.EDGES!r} group must contain a {_path.PROPS!r} group. Got {type(edge_props)}"
        )
    _validate_props_group(edge_props, edge_id_len, "Edge")
    # Edge properties metadata validation
    if metadata.edge_props_metadata is not None:
        _validate_props_metadata(metadata.edge_props_metadata, edge_props, "Edge")


def nx_is_equal(g1: nx.Graph, g2: nx.Graph) -> bool:
    """Utility function to check that two Network graphs are perfectly identical.

    It checks that the graphs are isomorphic, and that their graph,
    nodes and edges attributes are all identical.

    Args:
        g1 (nx.Graph): The first graph to compare.
        g2 (nx.Graph): The second graph to compare.

    Returns:
        bool: True if the graphs are identical, False otherwise.
    """
    edges_attr = list({k for (n1, n2, d) in g2.edges.data() for k in d})
    edges_default = len(edges_attr) * [0]
    em = iso.categorical_edge_match(edges_attr, edges_default)
    nodes_attr = list({k for (n, d) in g2.nodes.data() for k in d})
    nodes_default = len(nodes_attr) * [0]
    nm = iso.categorical_node_match(nodes_attr, nodes_default)

    same_nodes = same_edges = False
    if not g1.nodes.data() and not g2.nodes.data():
        same_nodes = True
    elif len(g1.nodes.data()) != len(g2.nodes.data()):
        same_nodes = False
    else:
        for data1, data2 in zip(sorted(g1.nodes.data()), sorted(g2.nodes.data()), strict=False):
            n1, attr1 = data1
            n2, attr2 = data2
            if sorted(attr1) == sorted(attr2) and n1 == n2:
                same_nodes = True
            else:
                same_nodes = False

    if not g1.edges.data() and not g2.edges.data():
        same_edges = True
    elif len(g1.edges.data()) != len(g2.edges.data()):
        same_edges = False
    else:
        for data1, data2 in zip(sorted(g1.edges.data()), sorted(g2.edges.data()), strict=False):
            n11, n12, attr1 = data1
            n21, n22, attr2 = data2
            if sorted(attr1) == sorted(attr2) and sorted((n11, n12)) == sorted((n21, n22)):
                same_edges = True
            else:
                same_edges = False

    if (
        nx.is_isomorphic(g1, g2, edge_match=em, node_match=nm)
        and g1.graph == g2.graph
        and same_nodes
        and same_edges
    ):
        return True
    else:
        return False
