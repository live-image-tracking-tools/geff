import numpy as np

from geff.validate.graph import (
    validate_no_repeated_edges,
    validate_no_self_edges,
    validate_nodes_for_edges,
    validate_unique_node_ids,
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


def test_validate_unique_node_ids() -> None:
    node_ids = np.array([0, 0, 1, 2, 3])
    valid, nonunique = validate_unique_node_ids(node_ids)
    assert not valid
    assert nonunique == np.array([0])
