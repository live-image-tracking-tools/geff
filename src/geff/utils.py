from __future__ import annotations

import os
from typing import TYPE_CHECKING, Literal

import numpy as np
import zarr

from .metadata_schema import GeffMetadata

if TYPE_CHECKING:
    from pathlib import Path


def validate(path: str | Path):
    """Check that the structure of the zarr conforms to geff specification

    Args:
        path (str | Path): Path to geff zarr

    Raises:
        AssertionError: If geff specs are violated
    """
    # Check that directory exists
    assert os.path.exists(path), f"Directory {path} does not exist"

    # zarr python 3 doesn't support Path
    path = str(path)
    path = os.path.expanduser(path)
    graph = zarr.open(path, mode="r")

    # graph attrs validation
    # Raises pydantic.ValidationError or ValueError
    meta = GeffMetadata.read(graph)

    validate_zarr_structure(graph, meta)


def validate_zarr_structure(graph: zarr.Group, meta: GeffMetadata):
    """Check that the structure of the zarr conforms to geff specification

    Also checks that any special properties match their spec

    Args:
        graph (zarr.Group): The zarr group containing the geff metadata
        meta (GeffMetadata): Metadata from geff
    """

    assert "nodes" in graph, "graph group must contain a nodes group"
    nodes = graph["nodes"]

    # ids and required and must by int type
    assert "ids" in nodes.array_keys(), "nodes group must contain an ids array"
    assert np.issubdtype(nodes["ids"].dtype, np.integer), "node ids must have an integer dtype"

    # Properties on nodes are optional
    if "props" in nodes.group_keys():
        validate_graph_group(nodes, "node")

    if "edges" in graph.group_keys():
        edges = graph["edges"]

        # Edges only require ids which contain nodes for each edge
        assert "ids" in edges, "edge group must contain ids array"
        id_shape = edges["ids"].shape
        assert id_shape[-1] == 2, (
            f"edges ids must have a last dimension of size 2, received shape {id_shape}"
        )

        if "props" in edges:
            validate_graph_group(edges, "edge")
def validate_graph_group(group: zarr.Group, type: Literal["node", "edge"]):
    """Verify that either a group of nodes or edges has basic correct structure

    - First dimension size must match the number of ids
    - Missing arrays must be boolean

    Args:
        group (zarr.Group): The zarr group containing the geff metadata
        type (Literal[str]): Type of group being evaluated. Either edge or node
    """
    # Property array length should match id length
    id_len = group["ids"].shape[0]
    for prop in group["props"].keys():
        prop_group = group["props"][prop]
        assert "values" in prop_group.array_keys(), (
            f"{type} property group {prop} must have values group"
        )
        prop_len = prop_group["values"].shape[0]
        assert prop_len == id_len, (
            f"{type} property {prop} values has length {prop_len}, which does not match "
            f"id length {id_len}"
        )
        if "missing" in prop_group.array_keys():
            missing_len = prop_group["missing"].shape[0]
            assert missing_len == id_len, (
                f"{type} property {prop} missing mask has length {missing_len}, which "
                f"does not match id length {id_len}"
            )
            missing_dtype = prop_group["missing"].dtype
            assert np.issubdtype(missing_dtype, np.bool_), f"Missing array for property {prop} must be boolean"
