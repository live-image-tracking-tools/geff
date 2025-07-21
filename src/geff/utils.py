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
    GeffMetadata.read(graph)

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


def check_equiv_geff(path_a, path_b):
    """This function compares two geffs, typically a starting fixture geff with
    the output of an implementation.

    This tests focuses on maintaining shape and dtype consistency. It does not
    assert element wise equality. path_a is assumed to be the "correct" geff.

    Args:
        path_a (str): Path to first zarr geff group
        path_b (str): Path to second zarr geff group
    """

    za = zarr.open(path_a)
    zb = zarr.open(path_b)

    for graph_group in ["nodes", "edges"]:
        ga = za[graph_group]
        gb = zb[graph_group]

        # Check ids
        assert ga["ids"].shape == gb["ids"].shape
        assert ga["ids"].dtype == gb["ids"].dtype

        ga_has_props = "props" in ga
        gb_has_props = "props" in gb

        assert ga_has_props == gb_has_props

        if ga_has_props:
            # Check that properties in each geff are the same
            assert set(ga["props"]) == set(gb["props"])

            # Check shape and dtype of each prop
            for prop in ga["props"]:
                if "missing" in ga[f"props/{prop}"]:
                    assert ga[f"props/{prop}/missing"].shape == gb[f"props/{prop}/missing"].shape
                    assert ga[f"props/{prop}/missing"].dtype == gb[f"props/{prop}/missing"].dtype
                assert ga[f"props/{prop}/values"].shape == gb[f"props/{prop}/values"].shape
                assert ga[f"props/{prop}/values"].dtype == gb[f"props/{prop}/values"].dtype
