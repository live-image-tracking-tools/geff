import zarr
import numpy as np

def validate_geff_edges(group: zarr.Group) -> tuple[bool, list[tuple[int, int]]]:
    '''
    Validates that all edge source and target node IDs exist in the node list of a GEFF group.

    Args:
        group: Geff group with 'nodes' and 'edges' datasets. 

    Returns:
        Tuple[bool, List[Tuple[int, int]]]:
            - all_edges_valid: True if every edge references only existing node IDs, otherwise False.
            - invalid_edges: List of (source_id, target_id) tuples for edges that reference missing node IDs.

    '''
    node_ids = group['nodes']['ids'][:] 
    edges_ids = group['edges']['ids'][:]

    all_edges_valid = True
    invalid_edges = []

    for src, tgt in edges_ids:
        if src not in node_ids or tgt not in node_ids:
            all_edges_valid = False
            invalid_edges.append((src, tgt))

    return all_edges_valid, invalid_edges

def validate_no_self_edges(group: zarr.Group) -> tuple[bool, np.ndarray]:
    """
    Validates that there are no self-edges in the array of edges in geff.

    Args:
        edges (np.ndarray): An array of shape (N, 2) where each row represents an edge as [source, target].

    Returns:
        tuple: A tuple (is_valid, problematic_nodes) where:
            - is_valid (bool): True if no node has an edge to itself, False otherwise.
            - problematic_nodes (np.ndarray): An array of node IDs that have self-edges. Empty if valid.
    """
    edges = group['edges']['ids'][:]
    
    mask = edges[:, 0] == edges[:, 1]
    problematic_nodes = np.unique(edges[mask, 0])
    return (len(problematic_nodes) == 0, problematic_nodes)

def validate_no_repeated_edges(group: zarr.Group) -> tuple[bool, np.ndarray]:
    """
    Validates that there are no repeated edges in the array.

    Args:
        edges (np.ndarray): An array of shape (N, 2) where each row represents an edge as [source, target].

    Returns:
        tuple: A tuple (is_valid, repeated_edges) where:
            - is_valid (bool): True if there are no repeated edges, False otherwise.
            - repeated_edges (np.ndarray): An array of duplicated edges, each as [source, target]. Empty if valid.

    """
    
    edges = group['edges']['ids'][:]
    edges_view = np.ascontiguousarray(edges).view([('', edges.dtype)] * edges.shape[1])
    _, idx, counts = np.unique(edges_view, return_index=True, return_counts=True)
    repeated_mask = counts > 1
    repeated_edges = edges[idx[repeated_mask]]
    return (len(repeated_edges) == 0, repeated_edges)

def validate_tracklets(node_ids, edge_ids, tracklet_ids):
    """
    Validates that nodes with the same tracklet_id form a simple directed path,
    allowing for incoming and outgoing connections to/from nodes outside the tracklet.

    Args:
        node_ids (list): List of node ids
        edge_ids (np.ndarray): Array of [source, target] edges
        tracklet_ids (list): List of tracklet ids per node

    Returns:
        (is_valid, errors): bool, list of error messages
    """

    errors = []

    # Map node to its tracklet
    node_to_tracklet = {node: t_id for node, t_id in zip(node_ids, tracklet_ids)}

    # Map tracklet_id to [nodes]
    tracklet_to_nodes = {}
    for node, t_id in zip(node_ids, tracklet_ids):
        tracklet_to_nodes.setdefault(t_id, []).append(node)

    # Build adjacency and reverse adjacency
    adj = {node: [] for node in node_ids}
    rev_adj = {node: [] for node in node_ids}
    for src, tgt in edge_ids:
        adj.setdefault(src, []).append(tgt)
        rev_adj.setdefault(tgt, []).append(src)

    for t_id, t_nodes in tracklet_to_nodes.items():
        node_set = set(t_nodes)
        # Subgraph connections within tracklet
        sub_adj = {n: [m for m in adj.get(n, []) if m in node_set] for n in node_set}
        sub_rev_adj = {n: [m for m in rev_adj.get(n, []) if m in node_set] for n in node_set}

        # For each node, count incoming and outgoing edges from/to *within the tracklet*
        in_deg = {n: len(sub_rev_adj[n]) for n in node_set}
        out_deg = {n: len(sub_adj[n]) for n in node_set}

        # Start: in_deg==0 (within tracklet), End: out_deg==0 (within tracklet), all others ==1
        starts = [n for n in node_set if in_deg[n] == 0]
        ends = [n for n in node_set if out_deg[n] == 0]

        if len(starts) != 1 or len(ends) != 1:
            errors.append(f"Tracklet {t_id}: not a single path (starts: {starts}, ends: {ends})")
            continue

        # Traverse within the tracklet
        visited = set()
        queue = [starts[0]]
        while queue:
            n = queue.pop(0)
            if n in visited:
                errors.append(f"Tracklet {t_id}: cycle or repeated node detected")
                break
            visited.add(n)
            queue.extend(sub_adj[n])
        if len(visited) != len(node_set):
            errors.append(f"Tracklet {t_id}: not fully connected (visited {len(visited)}/{len(node_set)})")

    is_valid = (len(errors) == 0)
    return is_valid, errors

def validate_seg_id(group):
    pass
