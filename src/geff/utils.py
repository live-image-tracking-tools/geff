from __future__ import annotations

import os
from typing import TYPE_CHECKING

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

    # ids and props are required and should be same length
    assert "ids" in nodes.array_keys(), "nodes group must contain an ids array"
    assert "props" in nodes.group_keys(), "nodes group must contain a props group"

    # Property array length should match id length
    id_len = nodes["ids"].shape[0]
    for prop in nodes["props"].keys():
        prop_group = nodes["props"][prop]
        assert "values" in prop_group.array_keys(), (
            f"node property group {prop} must have values group"
        )
        prop_len = prop_group["values"].shape[0]
        assert prop_len == id_len, (
            f"Node property {prop} values has length {prop_len}, which does not match "
            f"id length {id_len}"
        )
        if "missing" in prop_group.array_keys():
            missing_len = prop_group["missing"].shape[0]
            assert missing_len == id_len, (
                f"Node property {prop} missing mask has length {missing_len}, which "
                f"does not match id length {id_len}"
            )

    # TODO: Do we want to prevent missing values on spatialtemporal properties

    if "edges" in graph.group_keys():
        edges = graph["edges"]

        # Edges only require ids which contain nodes for each edge
        assert "ids" in edges, "edge group must contain ids array"
        id_shape = edges["ids"].shape
        assert id_shape[-1] == 2, (
            f"edges ids must have a last dimension of size 2, received shape {id_shape}"
        )

        # Edge property array length should match edge id length
        edge_id_len = edges["ids"].shape[0]
        if "props" in edges:
            for prop in edges["props"].keys():
                prop_group = edges["props"][prop]
                assert "values" in prop_group.array_keys(), (
                    f"Edge property group {prop} must have values group"
                )
                prop_len = prop_group["values"].shape[0]
                assert prop_len == edge_id_len, (
                    f"Edge property {prop} values has length {prop_len}, which does not "
                    f"match id length {edge_id_len}"
                )
                if "missing" in prop_group.array_keys():
                    missing_len = prop_group["missing"].shape[0]
                    assert missing_len == edge_id_len, (
                        f"Edge property {prop} missing mask has length {missing_len}, "
                        f"which does not match id length {edge_id_len}"
                    )
