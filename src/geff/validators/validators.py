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



