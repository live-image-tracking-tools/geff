from collections.abc import Sequence
from typing import Any

import numpy as np
import zarr

import geff
from geff.metadata_schema import GeffMetadata, axes_from_lists


def geff_from_min_data(
    node_ids: np.ndarray | Sequence[Any],
    edge_ids: np.ndarray | Sequence[Any],
    t: np.ndarray | Sequence[float],
    axes_names: Sequence[str],
) -> zarr.Group:
    """
    Create an in-memory GEFF graph in Zarr format from minimal input data.

    This function initializes a Zarr group containing nodes, edges, and associated properties
    based on the provided node IDs, edge IDs, time values, and axes names. It assigns random
    properties for each axis except for 't', which uses the supplied time values. Metadata
    about the GEFF graph is also added to the Zarr group.

    Args:
        node_ids (np.ndarray or Sequence[Any]): 1D array or list of node identifiers.
            Can be integers, strings, or other hashable types.
        edge_ids (np.ndarray or Sequence[Any]): 1D array or list of edge identifiers.
            Can be integers, strings, or other types.
        t (np.ndarray or Sequence[float]): 1D array of time values corresponding to nodes.
        axes_names (Sequence[str]): List of axis names (e.g., ["t", "x", "y"]).

    Returns:
        zarr.Group: A Zarr group in memory containing the nodes, edges, properties, and
            metadata for the constructed GEFF graph.
    """
    # calculate the number of nodes
    num_nodes = len(node_ids)

    # get axes from names
    axes = axes_from_lists(axes_names)

    # Create an in-memory store
    store = zarr.storage.MemoryStore()

    # Create a root group using Zarr format version 2
    # It will be updated to zarr 3 when the geff package is updated
    root = zarr.group(store=store, overwrite=True, zarr_format=2)

    # add nodes to geff
    nodes = root.create_group("nodes")
    nodes.create_array("ids", data=node_ids)

    # add properties for nodes
    props = nodes.create_group("props")
    for ax in axes_names:
        if ax == "t":
            data = t
        else:
            data = np.random.rand(num_nodes)
        props.create_group(ax).create_array("values", data=data)

    # add edges
    edges = root.create_group("edges")
    edges.create_array("ids", data=edge_ids)

    # add metadata
    metadata = GeffMetadata(
        geff_version=geff.__version__,
        directed=True,
        axes=axes,
    )

    metadata.write(root)

    return root


def create_geff_correct() -> zarr.Group:
    """
    Create a minimal GEFF group with nodes and edges.
    """

    node_ids = np.array([0, 1, 2], dtype=np.int8)
    edge_ids = np.array([[0, 1], [1, 2]], dtype=np.int8)
    t = np.array([0, 1, 2])
    axes_names = ["t", "y", "x"]

    root = geff_from_min_data(node_ids=node_ids, edge_ids=edge_ids, t=t, axes_names=axes_names)

    return root


def create_geff_edge_error() -> zarr.Group:
    """
    Create a minimal GEFF group with nodes and edges.
    """

    node_ids = np.array([0, 1, 2], dtype=np.int8)
    edge_ids = np.array([[0, 1], [1, 2], [2, 3], [0, 0], [0, 1]], dtype=np.int8)
    t = np.array([0, 1, 2])
    axes_names = ["t", "y", "x"]

    root = geff_from_min_data(node_ids=node_ids, edge_ids=edge_ids, t=t, axes_names=axes_names)

    return root
