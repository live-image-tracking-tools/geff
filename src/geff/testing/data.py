from typing import Union, Sequence, Any
import zarr
import numpy as np
import geff
from geff.metadata_schema import GeffMetadata, axes_from_lists


def geff_from_min_data(
    node_ids: Union[np.ndarray, Sequence[Any]],
    edge_ids: Union[np.ndarray, Sequence[Any]],
    t: Union[np.ndarray, Sequence[float]],
    axes_names: Sequence[str]
) -> zarr.Group:
    """
    Creates a minimal in-memory GEFF Zarr group from node and edge identifiers and metadata.

    Args:
        node_ids (Union[np.ndarray, Sequence[Any]]): 1D list or array of node identifiers. Can be integers, strings, or other hashable types.
        edge_ids (Union[np.ndarray, Sequence[Any]]): 1D list or array of edge identifiers. Can be integers, strings, or other types.
        t (Union[np.ndarray, Sequence[float]]): 1D array of time values corresponding to nodes.
        axes_names (Sequence[str]): List of strings specifying axes names (e.g., ["t", "x", "y"]).

    Returns:
        zarr.Group: A Zarr group in memory following the GEFF format.

    Notes:
        This function uses Zarr format version 2 for compatibility. 
        GEFF metadata is included and assumes a directed graph structure.
        For non-temporal axes, node properties are filled with random values as placeholders.
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

    return root

def create_geff_correct() -> zarr.Group:
    """
    Create a minimal GEFF group with nodes and edges.
    """

    node_ids = np.array([0,1,2], dtype=np.int8)
    edge_ids = np.array([[0, 1], [1, 2]], dtype=np.int8)
    t = np.array([0,1,2])
    axes_names = ['t', 'y', 'x']

    root = geff_from_min_data(
        node_ids=node_ids,
        edge_ids=edge_ids,
        t=t,
        axes_names=axes_names
        )

    return root   

def create_geff_edge_error() -> zarr.Group:
    """
    Create a minimal GEFF group with nodes and edges.
    """

    node_ids = np.array([0,1,2], dtype=np.int8)
    edge_ids = np.array([[0, 1], [1, 2], [2, 3]], dtype=np.int8)
    t = np.array([0,1,2])
    axes_names = ['t', 'y', 'x']

    root = geff_from_min_data(
        node_ids=node_ids,
        edge_ids=edge_ids,
        t=t,
        axes_names=axes_names
        )

    return root