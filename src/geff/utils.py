from __future__ import annotations

import os
import warnings
from pathlib import Path
from typing import TYPE_CHECKING

import networkx as nx
import networkx.algorithms.isomorphism as iso
import numpy as np
import zarr

if TYPE_CHECKING:
    from zarr.storage import StoreLike

    from geff.typing import PropDictNpArray, VarLenPropDictNpArray

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


def encode_string_data(data: PropDictNpArray, encoding: str = "utf-8") -> VarLenPropDictNpArray:
    """Encode a string array into a data array, values array, and missing array


    Args:
        data (PropDictNpArray): A 2d numpy array representing a list of strings, one per
            node or edge, potentially with empty strings appended at the end to make it
            non-ragged, along with a 1D missing array.
        encoding (str, optional): The encoding to use to encode the string to bytes.
            Defaults to "utf-8". Other options are: https://docs.python.org/3/library/codecs.html#standard-encodings
    TODO: Check which ones are supported in java

    Raises:
        TypeError: If the input values are not a string array

    Returns:
        VarLenPropDictNpArray: new data, values, and missing array to write to the props group
    """
    str_values = data["values"]
    missing = data["missing"]
    if not str_values.dtype.kind == "U":
        raise TypeError("Cannot encode non-string array")

    warnings.warn(
        f"Property '{data}' is a string array. Automatically casting it to bytes",
        stacklevel=2,
    )
    data = np.array([str(row).encode(encoding) for row in data], dtype="S")
    shapes = np.asarray(tuple(len(s) for s in str_values), dtype=np.int64)
    offsets = np.concatenate(([0], np.cumsum(shapes[:-1])))
    new_values = np.vstack((offsets, shapes)).T
    return {"values": new_values, "missing": missing, "data": data}


def decode_string_data(data: VarLenPropDictNpArray, encoding: str = "utf-8") -> PropDictNpArray:
    """Turns encoded string values back into a native python string array of values

    Args:
        data (VarLenPropDictNpArray): The values, data, and missing arrays read from disk
            containing encoded string values of varying lengths
        encoding (str, optional): The encoding used to encode the strings.
            Defaults to "utf-8". Supports TODO

    Raises:
        TypeError: If the data array is not a byte array

    Returns:
        PropDictNpArray: The values and missing arrays representing the string values
            for each node/edge as native python strings in a numpy string array
    """
    encoded_data = data["data"]
    if not encoded_data.dtype.kind == "S":
        raise TypeError("Cannot decode non-bytes array")
    decoded_data = encoded_data.tobytes().decode(encoding)
    offset_shape = data["values"]
    missing = data["missing"]
    str_values = []
    for i in range(offset_shape):
        offset = offset_shape[i][0]
        shape = offset_shape[i][1:]
        size = shape.prod()
        str_val = decoded_data[offset : offset + size]
        str_values.append(str_val)
    new_values = np.array(str_values)
    return {"values": new_values, "missing": missing}


def validate(store: StoreLike):
    """Check that the structure of the zarr conforms to geff specification

    Args:
        store (str | Path | zarr store): Check the geff zarr, either str/Path/store

    Raises:
        AssertionError: If geff specs are violated
        ValueError: If store is not a valid zarr store or path doesn't exist
    """

    # Check if path exists for string/Path inputs
    if isinstance(store, str | Path):
        store_path = Path(store)
        if not is_remote_url(str(store_path)) and not store_path.exists():
            raise ValueError(f"Path does not exist: {store}")

    # Open the zarr group from the store
    try:
        graph = zarr.open_group(store, mode="r")
    except Exception as e:
        raise ValueError("store must be a zarr StoreLike") from e

    # graph attrs validation
    # Raises pydantic.ValidationError or ValueError
    GeffMetadata.read(store)

    assert "nodes" in graph, "graph group must contain a nodes group"
    nodes = graph["nodes"]

    # ids and props are required and should be same length
    assert "ids" in nodes.array_keys(), "nodes group must contain an ids array"
    assert "props" in nodes.group_keys(), "nodes group must contain a props group"

    # Property array length should match id length
    id_len = nodes["ids"].shape[0]
    for prop in nodes["props"].keys():
        prop_group = nodes["props"][prop]
        assert "values" in prop_group.array_keys(), (
            f"node property group {prop} must have values group"
        )
        prop_len = prop_group["values"].shape[0]
        assert prop_len == id_len, (
            f"Node property {prop} values has length {prop_len}, which does not match "
            f"id length {id_len}"
        )
        if "missing" in prop_group.array_keys():
            missing_len = prop_group["missing"].shape[0]
            assert missing_len == id_len, (
                f"Node property {prop} missing mask has length {missing_len}, which "
                f"does not match id length {id_len}"
            )

    # TODO: Do we want to prevent missing values on spatialtemporal properties

    if "edges" in graph.group_keys():
        edges = graph["edges"]

        # Edges only require ids which contain nodes for each edge
        assert "ids" in edges, "edge group must contain ids array"
        id_shape = edges["ids"].shape
        assert id_shape[-1] == 2, (
            f"edges ids must have a last dimension of size 2, received shape {id_shape}"
        )

        # Edge property array length should match edge id length
        edge_id_len = edges["ids"].shape[0]
        if "props" in edges:
            for prop in edges["props"].keys():
                prop_group = edges["props"][prop]
                assert "values" in prop_group.array_keys(), (
                    f"Edge property group {prop} must have values group"
                )
                prop_len = prop_group["values"].shape[0]
                assert prop_len == edge_id_len, (
                    f"Edge property {prop} values has length {prop_len}, which does not "
                    f"match id length {edge_id_len}"
                )
                if "missing" in prop_group.array_keys():
                    missing_len = prop_group["missing"].shape[0]
                    assert missing_len == edge_id_len, (
                        f"Edge property {prop} missing mask has length {missing_len}, "
                        f"which does not match id length {edge_id_len}"
                    )


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
