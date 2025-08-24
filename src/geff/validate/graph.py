from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import ArrayLike


def validate_unique_node_ids(node_ids: ArrayLike) -> tuple[bool, np.ndarray]:
    """Validates that all node ids are unique

    Args:
        node_ids (ArrayLike): 1D arraylike of node ids

    Returns:
        tuple[bool, np.ndarray]:
            - valid (bool): True if all node ids are unique
            - errors (list[ints]): List of any non-unique node ids
    """
    node_ids = np.asarray(node_ids)

    unique_ids, counts = np.unique(node_ids, return_counts=True)
    if any(counts > 1):
        return False, unique_ids[counts > 1]
    return True, np.array([])


def validate_nodes_for_edges(node_ids: ArrayLike, edge_ids: ArrayLike) -> tuple[bool, np.ndarray]:
    """
    Validates that all edges in `edge_ids` reference node IDs present in `node_ids`.

    This function checks whether each edge in `edge_ids` consists of node IDs that exist in
    `node_ids`. It returns a boolean indicating whether all edges are valid, and a list of
    invalid edges.

    Args:
        node_ids (ArrayLike): 1D array-like of valid node IDs (integers).
        edge_ids (ArrayLike): 2D array-like of edges with shape (M, 2), where each row is
            (source, target).

    Returns:
        tuple[bool, np.ndarray]:
            - all_edges_valid (bool): True if all edges reference valid node IDs.
            - invalid_edges (np.ndarray): Array of (source, target) pairs for
              invalid edges.
    """

    node_ids = np.asarray(node_ids)
    edge_ids = np.asarray(edge_ids)

    # Build a boolean mask: True for valid edges
    valid_src = np.isin(edge_ids[:, 0], node_ids)
    valid_tgt = np.isin(edge_ids[:, 1], node_ids)
    mask = valid_src & valid_tgt

    # Find invalid edges
    invalid_edges = edge_ids[~mask]
    all_edges_valid = len(invalid_edges) == 0
    return all_edges_valid, invalid_edges


def validate_no_self_edges(edge_ids: ArrayLike) -> tuple[bool, np.ndarray]:
    """
    Validates that there are no self-edges in the provided array of edges.

    Args:
        edge_ids (ArrayLike): 2D array-like of edges with shape (M, 2). Each row is
            (source, target).

    Returns:
        tuple[bool, np.ndarray]: A tuple (is_valid, problematic_nodes) where:
            - is_valid (bool): True if no node has an edge to itself, False otherwise.
            - problematic_nodes (np.ndarray): Array of node IDs that have self-edges.
              Empty if valid.
    """
    edge_ids = np.asarray(edge_ids)
    mask = edge_ids[:, 0] == edge_ids[:, 1]
    problematic_nodes = np.unique(edge_ids[mask, 0])
    return (len(problematic_nodes) == 0, problematic_nodes)


def validate_no_repeated_edges(edge_ids: ArrayLike) -> tuple[bool, np.ndarray]:
    """
    Validates that there are no repeated edges in the array.

    Args:
        edge_ids (ArrayLike): 2D array-like of edges with shape (M, 2). Each row is
            (source, target).

    Returns:
        tuple: A tuple (is_valid, repeated_edges) where:
            - is_valid (bool): True if there are no repeated edges, False otherwise.
            - repeated_edges (np.ndarray): An array of duplicated edges. Empty if valid.

    """
    edge_ids = np.asarray(edge_ids)
    edges_view = np.ascontiguousarray(edge_ids).view([("", edge_ids.dtype)] * edge_ids.shape[1])
    _, idx, counts = np.unique(edges_view, return_index=True, return_counts=True)
    repeated_mask = counts > 1
    repeated_edges = edge_ids[idx[repeated_mask]]
    return (len(repeated_edges) == 0, repeated_edges)
