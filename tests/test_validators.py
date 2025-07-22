import numpy as np
import zarr
from geff.validators.validators import validate_geff_edges, validate_no_self_edges, validate_no_repeated_edges, validate_tracklets
from geff.testing.data import create_geff_correct, create_geff_edge_error
import pytest


def test_no_self_edges():
    """
    Test that no node has an edge to itself.
    """    
    geff = create_geff_correct()
    is_valid, problematic_nodes = validate_no_self_edges(geff)
    assert is_valid, "There should be no self-edges in the GEFF group."
    assert len(problematic_nodes) == 0, "There should be no problematic nodes with self-edges."

def test_detects_self_edges():
    """
    Test that validator detects nodes with self-edges.
    """
    geff = create_geff_edge_error()
    is_valid, problematic_nodes = validate_no_self_edges(geff)
    assert not is_valid, "Validator should detect self-edges."
    assert len(problematic_nodes) > 0, "There should be problematic nodes with self-edges."
    assert np.array_equal(problematic_nodes, np.array([0])), "Node 0 should be the problematic node with a self-edge."

def test_all_edges_valid():
    """
    Test that all edges reference existing node IDs.
    """
    geff = create_geff_correct()
    is_valid, invalid_edges = validate_geff_edges(geff)
    assert is_valid, "All edges should reference valid node IDs."
    assert len(invalid_edges) == 0, "There should be no invalid edges."

def test_detects_invalid_edges():
    """
    Test that invalid edges (edges with missing node IDs) are detected.
    """
    geff = create_geff_edge_error()
    is_valid, invalid_edges = validate_geff_edges(geff)
    assert not is_valid, "Validator should detect edges referencing missing node IDs."
    assert (2, 3) in invalid_edges, "Edge (2, 3) should be flagged as invalid."
    assert len(invalid_edges) == 1, "There should be exactly one invalid edge."

def test_no_repeated_edges():
    """
    Test that validator passes when all edges are unique.
    """
    geff = create_geff_correct()
    is_valid, repeated_edges = validate_no_repeated_edges(geff)
    assert is_valid, "There should be no repeated edges."
    assert len(repeated_edges) == 0, "No edges should be reported as repeated."

def test_detects_repeated_edges():
    """
    Test that validator detects repeated edges.
    """
    geff = create_geff_edge_error()
    is_valid, repeated_edges = validate_no_repeated_edges(geff)
    assert not is_valid, "Validator should detect repeated edges."
    assert [0, 1] in repeated_edges.tolist(), "Edge [0, 1] should be reported as repeated."
    assert len(repeated_edges) == 1, "There should be exactly one unique repeated edge."

@pytest.mark.parametrize(
    "node_ids, edge_ids, tracklet_ids, expected_valid, description", [
        # Single, simple, valid tracklet (1→2→3)
        ([1, 2, 3], np.array([[1, 2], [2, 3]]), [10, 10, 10], True, "Valid simple path"),
        # Tracklet with missing edge
        ([1, 2, 3], np.array([[1, 2]]), [10, 10, 10], False, "Missing edge in path"),
        # Tracklet with a cycle
        ([1, 2, 3], np.array([[1, 2], [2, 3], [3, 1]]), [10, 10, 10], False, "Cycle in tracklet"),
        # Multiple valid tracklets
        ([1, 2, 3, 4, 5, 6], np.array([[1, 2], [2, 3], [4, 5], [5, 6]]), [10, 10, 10, 20, 20, 20], True, "Two valid tracklets"),
        # Branching in tracklet
        ([1, 2, 3], np.array([[1, 2], [1, 3]]), [10, 10, 10], False, "Branch in tracklet"),
        # Valid path with in/out edges to/from outside tracklet
        ([1, 2, 3, 4, 5], np.array([[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]]), [10, 10, 10, 10, 10], True, "Edges to/from outside"),
        # Not fully connected
        ([1, 2, 3], np.array([[1, 2]]), [10, 10, 10], False, "Not fully connected"),
        # Two nodes, valid path
        ([1, 2], np.array([[1, 2]]), [10, 10], True, "Two nodes, valid path"),
        # Tracklet with all nodes, but disconnected
        ([1, 2, 3, 4], np.array([[1, 2], [3, 4]]), [10, 10, 10, 10], False, "Disconnected tracklet"),
        # Multiple tracklets, one valid, one invalid
        ([1, 2, 3, 4, 5, 6], np.array([[1, 2], [2, 3], [4, 5]]), [10, 10, 10, 20, 20, 20], False, "One valid, one invalid"),
    ]
)
def test_validate_tracklets(node_ids, edge_ids, tracklet_ids, expected_valid, description):
    is_valid, errors = validate_tracklets(node_ids, edge_ids, tracklet_ids)
    assert is_valid == expected_valid, f"{description} failed: {errors}"