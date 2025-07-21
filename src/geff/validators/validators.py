import zarr

def validate_geff_edges(group):
    '''
    Validate edges in a GEFF group.
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