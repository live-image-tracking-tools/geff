import numpy as np
import zarr
from src.geff.validators.validators import validate_geff_edges, validate_no_self_edges
from src.geff.testing.data import create_geff_correct, create_geff_edge_error


def test_no_self_edges():
    """
    Test that no node has an edge to itself.
    """    
    geff = create_geff_correct()
    is_valid, problematic_nodes = validate_no_self_edges(geff)
    assert is_valid, "There should be no self-edges in the GEFF group."
    assert len(problematic_nodes) == 0, "There should be no problematic nodes with self-edges."