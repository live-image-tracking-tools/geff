from typing import cast

import networkx as nx
import numpy as np
from numpy.typing import ArrayLike


def validate_nodes_for_edges(
    node_ids: ArrayLike, edge_ids: ArrayLike
) -> tuple[bool, list[tuple[int, int]]]:
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
        tuple[bool, list[tuple[int, int]]]:
            - all_edges_valid (bool): True if all edges reference valid node IDs.
            - invalid_edges (list of tuple[int, int]): List of (source, target) pairs for
              invalid edges.
    """

    node_ids = np.asarray(node_ids)
    edge_ids = np.asarray(edge_ids)

    # Build a boolean mask: True for valid edges
    valid_src = np.isin(edge_ids[:, 0], node_ids)
    valid_tgt = np.isin(edge_ids[:, 1], node_ids)
    mask = valid_src & valid_tgt

    # Find invalid edges
    invalid_edges = [tuple(edge) for edge in edge_ids[~mask]]
    all_edges_valid = not invalid_edges
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


def validate_tracklets(
    node_ids: ArrayLike, edge_ids: ArrayLike, tracklet_ids: ArrayLike
) -> tuple[bool, list[str]]:
    """
    Validates if each tracklet forms a single, cycle-free path using NetworkX
    for improved performance.

    Args:
        node_ids (ArrayLike): Sequence of node identifiers.
        edge_ids (ArrayLike): Sequence of edges as (source, target) node ID pairs.
            Edges must be between nodes in `node_ids`.
        tracklet_ids (ArrayLike): Sequence of tracklet IDs corresponding to each node.

    Returns:
        tuple[bool, list[str]]:
            - is_valid (bool): True if all tracklets are valid, otherwise False.
            - errors (list[str]): List of error messages for invalid tracklets.
    """
    errors = []

    nodes = np.asarray(node_ids, dtype=np.int64)
    edges = np.asarray(edge_ids, dtype=np.int64)
    tracklets = np.asarray(tracklet_ids, dtype=np.int64)

    # Group nodes by tracklet ID.
    tracklet_to_nodes: dict[int, list[int]] = {}
    for node, t_id in zip(nodes, tracklets, strict=False):
        tracklet_to_nodes.setdefault(t_id, []).append(node)

    # Build the graph.
    G: nx.DiGraph[int] = nx.DiGraph(tuple(edge) for edge in edges)
    # Ensure all nodes from node_ids are in the graph, even if isolated.
    G.add_nodes_from(nodes)

    # Validate each tracklet.
    for t_id, t_nodes in tracklet_to_nodes.items():
        # by definition, a tracklet
        if len(t_nodes) < 2:
            continue

        # Gets a subgraph for the current tracklet.
        S = cast("nx.DiGraph[int]", G.subgraph(t_nodes))

        # Check - no branches or merges (junctions).
        breakpoint()
        max_in_degree = max((d for _, d in S.in_degree), default=0)
        max_out_degree = max((d for _, d in S.out_degree), default=0)

        if max_in_degree > 1 or max_out_degree > 1:
            errors.append(f"Tracklet {t_id}: Invalid path structure (branch or merge detected).")
            continue

        # Check - No cycles.
        if not nx.is_directed_acyclic_graph(S):
            errors.append(f"Tracklet {t_id}: Cycle detected.")
            continue

        # Check - Fully connected.
        if not nx.is_weakly_connected(S):
            errors.append(f"Tracklet {t_id}: Not fully connected.")
            continue

        # Check - Tracklet is maximal linear segment.
        start_node = next(n for n, d in S.in_degree if d == 0)
        end_node = next(n for n, d in S.out_degree if d == 0)

        # Check if the path could be extended backward
        preds_in_G = list(G.predecessors(start_node))
        if len(preds_in_G) == 1:
            predecessor = preds_in_G[0]
            # If the predecessor is also part of a linear segment...
            if G.out_degree(predecessor) == 1:
                errors.append(
                    f"Tracklet {t_id}: Not maximal. Path can extend backward to node {predecessor}."
                )
                continue

        # Check if the path could be extended forward
        succs_in_G = list(G.successors(end_node))
        if len(succs_in_G) == 1:
            successor = succs_in_G[0]
            # If the successor is also part of a linear segment...
            if G.in_degree(successor) == 1:
                errors.append(
                    f"Tracklet {t_id}: Not maximal. Path can extend forward to node {successor}."
                )
                continue

    return not errors, errors


def validate_lineages(
    node_ids: ArrayLike, edge_ids: ArrayLike, lineage_ids: ArrayLike
) -> tuple[bool, list[str]]:
    """Validates if each lineage is a valid, isolated connected component.

    A lineage is considered valid if and only if the set of nodes belonging
    to it is identical to one of the graph's weakly connected components.
    This efficiently ensures both internal connectivity and external isolation.

    Args:
        node_ids: A sequence of unique node identifiers in the graph.
        edge_ids: A sequence of (source, target) pairs representing directed
            edges.
        lineage_ids: A sequence of lineage identifiers corresponding to each
            node in `node_ids`.

    Returns:
        A tuple containing:
            - is_valid (bool): True if all lineages are valid connected
              components, False otherwise.
            - errors (list[str]): A list of error messages for each invalid
              lineage.
    """
    ID_DTYPE = np.int64
    # Ensure consistent dtypes.
    nodes = np.asarray(node_ids, dtype=ID_DTYPE)
    edges = np.asarray(edge_ids, dtype=ID_DTYPE)
    lineages = np.asarray(lineage_ids, dtype=ID_DTYPE)

    errors: list[str] = []
    lineage_to_nodes: dict[np.int64, list[np.int64]] = {}

    for node, l_id in zip(nodes, lineages, strict=False):
        lineage_to_nodes.setdefault(l_id, []).append(node)

    # Build the graph.
    G = nx.DiGraph(tuple(edge) for edge in edges)
    G.add_nodes_from(nodes)

    # Find all weakly connected components.
    valid_components = {frozenset(component) for component in nx.weakly_connected_components(G)}

    # Check if each lineage's node set matches a valid component.
    for l_id, l_nodes in lineage_to_nodes.items():
        if not l_nodes:
            continue

        l_nodes_set = frozenset(l_nodes)

        if l_nodes_set not in valid_components:
            errors.append(f"Lineage {l_id}: Does not form a valid, isolated connected component.")

    return not errors, errors
