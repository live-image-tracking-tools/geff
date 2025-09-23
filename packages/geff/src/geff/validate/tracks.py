from __future__ import annotations

from typing import TYPE_CHECKING, cast

import networkx as nx
import numpy as np

if TYPE_CHECKING:
    from numpy.typing import ArrayLike


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
            # TODO: remove ignore, see issue 314
            if G.out_degree(predecessor) == 1:  # pyright: ignore
                errors.append(
                    f"Tracklet {t_id}: Not maximal. Path can extend backward to node {predecessor}."
                )
                continue

        # Check if the path could be extended forward
        succs_in_G = list(G.successors(end_node))
        if len(succs_in_G) == 1:
            successor = succs_in_G[0]
            # If the successor is also part of a linear segment...
            # TODO: remove ignore, see issue 314
            if G.in_degree(successor) == 1:  # pyright: ignore
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
