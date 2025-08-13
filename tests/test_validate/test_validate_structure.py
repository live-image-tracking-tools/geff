from __future__ import annotations

import re
from typing import TYPE_CHECKING

import numpy as np
import pytest
import zarr

from geff import validate_structure

if TYPE_CHECKING:
    from pathlib import Path


def test_validate_structure(tmp_path: Path) -> None:
    # Does not exist
    with pytest.raises(FileNotFoundError, match=r"Path does not exist: does-not-exist"):
        validate_structure("does-not-exist")

    # remote zarr path does not raise existence error
    remote_path = "https://blah.com/test.zarr"
    with pytest.raises(ValueError, match=r"store must be a zarr StoreLike"):
        validate_structure(remote_path)

    # Path exists but is not a zarr store
    non_zarr_path = tmp_path / "not-a-zarr"
    non_zarr_path.mkdir()
    with pytest.raises(ValueError, match=r"store must be a zarr StoreLike"):
        validate_structure(non_zarr_path)

    zpath = tmp_path / "test.zarr"
    z = zarr.open_group(zpath)

    # Missing metadata
    with pytest.raises(ValueError, match="No geff key found in"):
        validate_structure(zpath)
    z.attrs["geff"] = {
        "geff_version": "0.0.1",
        "directed": True,
        "roi_min": [0, 0],
        "roi_max": [100, 100],
    }

    # No nodes
    with pytest.raises(ValueError, match="'graph' group must contain a group named 'nodes'"):
        validate_structure(zpath)
    nodes = z.create_group("nodes")

    # Nodes missing ids
    with pytest.raises(ValueError, match="'nodes' group must contain an 'ids' array"):
        validate_structure(zpath)
    n_node = 10
    z["nodes/ids"] = np.zeros(n_node)

    # Nodes must have a props group
    with pytest.raises(ValueError, match="'nodes' group must contain a group named 'props'"):
        validate_structure(zpath)
    nodes.create_group("props")

    # Subgroups in props must have values
    nodes.create_group("props/score")
    with pytest.raises(ValueError, match="Node property group 'score' must have a 'values' array"):
        validate_structure(zpath)
    z["nodes/props/score/values"] = np.zeros(n_node)
    validate_structure(zpath)

    # Property shape mismatch
    z["nodes/props/badshape/values"] = np.zeros(n_node * 2)
    with pytest.raises(
        ValueError,
        match=(
            f"Node property 'badshape' values has length {n_node * 2}, "
            f"which does not match id length {n_node}"
        ),
    ):
        validate_structure(zpath)

    del z["nodes/props"]["badshape"]
    # Property missing shape mismatch
    z["nodes/props/badshape/values"] = np.zeros(shape=(n_node))
    z["nodes/props/badshape/missing"] = np.zeros(shape=(n_node * 2))
    with pytest.raises(
        ValueError,
        match=(
            f"Node property 'badshape' missing mask has length {n_node * 2}, "
            f"which does not match id length {n_node}"
        ),
    ):
        validate_structure(zpath)
    del z["nodes/props"]["badshape"]

    # No edge group is okay, if the graph has no edges
    z.create_group("edges")

    # Missing edge ids
    with pytest.raises(ValueError, match="'edges' group must contain an 'ids' array"):
        validate_structure(zpath)

    # ids array must have last dim size 2
    n_edges = 5
    badshape = (n_edges, 3)
    z["edges/ids"] = np.zeros(badshape)
    with pytest.raises(
        ValueError,
        match=re.escape(
            f"edges ids must have a last dimension of size 2, received shape {badshape}"
        ),
    ):
        validate_structure(zpath)
    del z["edges"]["ids"]
    z["edges/ids"] = np.zeros((n_edges, 2))

    # Property values shape mismatch
    z["edges/props/badshape/values"] = np.zeros((n_edges * 2, 2))
    with pytest.raises(
        ValueError,
        match=(
            f"Edge property 'badshape' values has length {n_edges * 2}, "
            f"which does not match id length {n_edges}"
        ),
    ):
        validate_structure(zpath)
    del z["edges/props/badshape"]["values"]

    # Property missing shape mismatch
    z["edges/props/badshape/values"] = np.zeros((n_edges, 2))
    z["edges/props/badshape/missing"] = np.zeros((n_edges * 2, 2))
    with pytest.raises(
        ValueError,
        match=(
            f"Edge property 'badshape' missing mask has length {n_edges * 2}, "
            f"which does not match id length {n_edges}"
        ),
    ):
        validate_structure(zpath)
    del z["edges/props/badshape"]["missing"]

    # Nodes: property metadata has no matching data
    geff_attrs = z.attrs["geff"]
    geff_attrs["node_props_metadata"] = {
        "prop1": {"identifier": "prop1", "dtype": "float32"},
        "prop2": {"identifier": "prop2", "dtype": "int"},
    }
    z.attrs["geff"] = geff_attrs
    with pytest.raises(
        ValueError,
        match="Node property prop1 described in metadata is not present in props arrays",
    ):
        validate_structure(zpath)

    # Nodes: inconsistent property metadata dtype
    z["nodes/props/prop1/values"] = np.zeros(n_node, dtype=np.float32)
    z["nodes/props/prop2/values"] = np.zeros(n_node, dtype=np.float32)
    with pytest.raises(
        ValueError,
        match=(
            "Node property prop2 with dtype float32 does not match "
            "metadata dtype <class 'numpy.int64'>"
        ),
    ):
        validate_structure(zpath)
    # Another type of dtype mismatch
    z["nodes/props/prop2/values"] = np.zeros(n_node, dtype="int16")
    with pytest.raises(
        ValueError,
        match=(
            "Node property prop2 with dtype int16 does not match "
            "metadata dtype <class 'numpy.int64'>"
        ),
    ):
        validate_structure(zpath)
    z["nodes/props/prop2/values"] = np.zeros(n_node, dtype="int")  # clean up

    # Edges: property metadata has no matching data
    geff_attrs["edge_props_metadata"] = {
        "prop3": {"identifier": "prop3", "dtype": "bool"},
    }
    z.attrs["geff"] = geff_attrs
    with pytest.raises(
        ValueError,
        match="Edge property prop3 described in metadata is not present in props arrays",
    ):
        validate_structure(zpath)

    # Edges: inconsistent property metadata dtype
    z["edges/props/prop3/values"] = np.zeros(n_edges, dtype=np.float32)
    with pytest.raises(
        ValueError,
        match=(
            r"Edge property prop3 with dtype float32 does not match "
            r"metadata dtype <class 'numpy.bool_*'>"
        ),
    ):
        validate_structure(zpath)
    z["edges/props/prop3/values"] = np.zeros(n_edges, dtype="bool")  # clean up

    # No error raised when property with no matching prop metadata
    z["nodes/props/prop4/values"] = np.zeros(n_node, dtype="bool")
    z["edges/props/prop4/values"] = np.zeros(n_edges, dtype="uint8")

    # No error when identical property identifiers across node and edge props
    geff_attrs["node_props_metadata"] = {"prop4": {"identifier": "prop4", "dtype": "bool"}}
    geff_attrs["edge_props_metadata"] = {"prop4": {"identifier": "prop4", "dtype": "uint8"}}
    z.attrs["geff"] = geff_attrs

    # Everything passes
    validate_structure(zpath)
