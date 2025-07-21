import zarr

def validate_geff_edges(group):
    '''
    Validates that all edge source and target node IDs exist in the node list of a GEFF group.

    Args:
        group: An object with 'nodes' and 'edges' datasets. 

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

def validate_seg_id(group):
    pass
