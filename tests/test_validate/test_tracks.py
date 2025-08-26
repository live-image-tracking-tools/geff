import numpy as np
import pytest

from geff.validate.tracks import validate_lineages, validate_tracklets


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
