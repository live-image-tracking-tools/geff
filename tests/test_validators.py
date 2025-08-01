import numpy as np
import pytest

from geff.validators.validators import (
    validate_lineages,
    validate_no_repeated_edges,
    validate_no_self_edges,
    validate_nodes_for_edges,
    validate_tracklets,
)


def test_no_self_edges() -> None:
    """
    Test that no node has an edge to itself.
    """
    edge_ids = np.array([[0, 1], [1, 2], [2, 3]])
    is_valid, problematic_nodes = validate_no_self_edges(edge_ids)
    assert is_valid, "There should be no self-edges in the GEFF group."
    assert len(problematic_nodes) == 0, "There should be no problematic nodes with self-edges."


def test_detects_self_edges() -> None:
    """
    Test that validator detects nodes with self-edges.
    """
    edge_ids = np.array([[0, 1], [1, 2], [2, 3], [0, 0]])  # Node 0 has a self-edge
    is_valid, problematic_nodes = validate_no_self_edges(edge_ids)
    assert not is_valid, "Validator should detect self-edges."
    assert len(problematic_nodes) > 0, "There should be problematic nodes with self-edges."
    assert np.array_equal(problematic_nodes, np.array([0])), (
        "Node 0 should be the problematic node with a self-edge."
    )


def test_all_edges_valid() -> None:
    """
    Test that all edges reference existing node IDs.
    """
    node_ids = np.array([0, 1, 2, 3])
    edge_ids = np.array([[0, 1], [1, 2], [2, 3]])
    is_valid, invalid_edges = validate_nodes_for_edges(node_ids, edge_ids)
    assert is_valid, "All edges should reference valid node IDs."
    assert len(invalid_edges) == 0, "There should be no invalid edges."


def test_detects_invalid_edges() -> None:
    """
    Test that invalid edges (edges with missing node IDs) are detected.
    """
    node_ids = np.array([0, 1, 2])
    edge_ids = np.array([[0, 1], [1, 2], [2, 3]])
    is_valid, invalid_edges = validate_nodes_for_edges(node_ids, edge_ids)
    assert not is_valid, "Validator should detect edges referencing missing node IDs."
    assert (2, 3) in invalid_edges, "Edge (2, 3) should be flagged as invalid."
    assert len(invalid_edges) == 1, "There should be exactly one invalid edge."


def test_no_repeated_edges() -> None:
    """
    Test that validator passes when all edges are unique.
    """
    edge_ids = np.array([[0, 1], [1, 2], [2, 3]])
    is_valid, repeated_edges = validate_no_repeated_edges(edge_ids)
    assert is_valid, "There should be no repeated edges."
    assert len(repeated_edges) == 0, "No edges should be reported as repeated."


def test_detects_repeated_edges() -> None:
    """
    Test that validator detects repeated edges.
    """
    edge_ids = np.array([[0, 1], [1, 2], [2, 3], [0, 1]])  # Edge (0, 1) is repeated
    is_valid, repeated_edges = validate_no_repeated_edges(edge_ids)
    assert not is_valid, "Validator should detect repeated edges."
    assert [0, 1] in repeated_edges.tolist(), "Edge [0, 1] should be reported as repeated."
    assert len(repeated_edges) == 1, "There should be exactly one unique repeated edge."


@pytest.mark.parametrize(
    "node_ids, edge_ids, tracklet_ids, expected_valid, description",
    [
        # Single, simple, valid tracklet (1→2→3)
        (
            np.array([1, 2, 3]),
            np.array([[1, 2], [2, 3]]),
            np.array([10, 10, 10]),
            True,
            "Valid simple path",
        ),
        # Tracklet with missing edge
        (
            np.array([1, 2, 3]),
            np.array([[1, 2]]),
            np.array([10, 10, 10]),
            False,
            "Missing edge in path",
        ),
        # Tracklet with a cycle
        (
            np.array([1, 2, 3]),
            np.array([[1, 2], [2, 3], [3, 1]]),
            np.array([10, 10, 10]),
            False,
            "Cycle in tracklet",
        ),
        # Multiple valid tracklets
        (
            np.array([1, 2, 3, 4, 5, 6]),
            np.array([[1, 2], [2, 3], [4, 5], [5, 6]]),
            np.array([10, 10, 10, 20, 20, 20]),
            True,
            "Two valid tracklets",
        ),
        # Branching in tracklet
        (
            np.array([1, 2, 3]),
            np.array([[1, 2], [1, 3]]),
            np.array([10, 10, 10]),
            False,
            "Branch in tracklet",
        ),
        # Not fully connected
        (
            np.array([1, 2, 3]),
            np.array([[1, 2]]),
            np.array([10, 10, 10]),
            False,
            "Not fully connected",
        ),
        # Two nodes, valid path
        (np.array([1, 2]), np.array([[1, 2]]), np.array([10, 10]), True, "Two nodes, valid path"),
        # Tracklet with all nodes, but disconnected
        (
            np.array([1, 2, 3, 4]),
            np.array([[1, 2], [3, 4]]),
            np.array([10, 10, 10, 10]),
            False,
            "Disconnected tracklet",
        ),
        # Multiple tracklets, one valid, one invalid
        (
            np.array([1, 2, 3, 4, 5, 6]),
            np.array([[1, 2], [2, 3], [4, 5]]),
            np.array([10, 10, 10, 20, 20, 20]),
            False,
            "One valid, one invalid",
        ),
        # Not maximal length tracklet
        (
            np.array([1, 2, 3, 4, 5]),
            np.array([[1, 2], [2, 3], [3, 4], [4, 5]]),
            np.array([10, 10, 10, 20, 20]),
            False,
            "Tracklet not maximal length",
        ),
    ],
)
def test_validate_tracklets(node_ids, edge_ids, tracklet_ids, expected_valid, description) -> None:
    is_valid, errors = validate_tracklets(node_ids, edge_ids, tracklet_ids)
    assert is_valid == expected_valid, f"{description} failed: {errors}"


@pytest.mark.parametrize(
    "node_ids, edge_ids, lineage_ids, expected_valid, description",
    [
        # --- Valid Cases (Lineage is a connected component) ---
        (
            np.array([1, 2, 3]),
            np.array([[1, 2], [2, 3]]),
            np.array([10, 10, 10]),
            True,
            "Valid: Simple connected lineage",
        ),
        (
            np.array([1, 2, 3]),
            np.array([[1, 2], [2, 3], [3, 1]]),
            np.array([10, 10, 10]),
            True,
            "Valid: A cycle connects all nodes",
        ),
        (
            np.array([1, 2, 3]),
            np.array([[1, 2], [1, 3]]),
            np.array([10, 10, 10]),
            True,
            "Valid: A branch connects all nodes",
        ),
        (
            np.array([1, 2, 3, 4, 5, 6]),
            np.array([[1, 2], [2, 3], [4, 5], [5, 6]]),
            np.array([10, 10, 10, 20, 20, 20]),
            True,
            "Valid: Two separate, fully-connected lineages",
        ),
        (
            np.array([1]),
            np.array([]),
            np.array([10]),
            True,
            "Valid: A single-node lineage is always a connected component",
        ),
        # --- Invalid Cases (Lineage is NOT a connected component) ---
        (
            np.array([1, 2, 3, 4]),
            np.array([[0, 1], [1, 2], [2, 3], [3, 4]]),
            np.array([10, 10, 10, 10]),
            False,
            "Invalid: Lineage is not isolated (part of a larger component)",
        ),
        (
            np.array([1, 2, 3]),
            np.array([[1, 2]]),
            np.array([10, 10, 10]),
            False,
            "Invalid: Lineage is not internally connected (node 3 is separate)",
        ),
        (
            np.array([1, 2, 3, 4]),
            np.array([[1, 2], [3, 4]]),
            np.array([10, 10, 10, 10]),
            False,
            "Invalid: Lineage contains two separate components",
        ),
        (
            np.array([1, 2, 3, 4, 5, 6]),
            np.array([[1, 2], [2, 3], [4, 5]]),
            np.array([10, 10, 10, 20, 20, 20]),
            False,
            "Invalid: One valid lineage, one invalid (disconnected) lineage",
        ),
        (
            np.array([1, 2, 3]),
            np.array([]),
            np.array([10, 10, 10]),
            False,
            "Invalid: Lineage contains three separate single-node components",
        ),
        (
            np.array([1, 2, 3]),
            np.array([[1, 2], [2, 3], [3, 4]]),
            np.array([10, 10, 10]),
            False,
            "Invalid: Lineage contains outside edges (node 4 not in lineage)",
        ),
    ],
)
def test_validate_lineages(node_ids, edge_ids, lineage_ids, expected_valid, description) -> None:
    """
    Tests the validate_lineages function for various connectivity scenarios.
    """
    is_valid, errors = validate_lineages(node_ids, edge_ids, lineage_ids)
    assert is_valid == expected_valid, f"Test '{description}' failed: {errors}"
