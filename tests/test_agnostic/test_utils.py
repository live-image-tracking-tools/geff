from __future__ import annotations

import re
from typing import TYPE_CHECKING

import numpy as np
import pytest
import zarr

from geff.utils import validate

if TYPE_CHECKING:
    from pathlib import Path


def test_validate(tmp_path: Path) -> None:
    # Does not exist
    with pytest.raises(FileNotFoundError, match=r"Path does not exist: does-not-exist"):
        validate("does-not-exist")

    # remote zarr path does not raise existence error
    remote_path = "https://blah.com/test.zarr"
    with pytest.raises(ValueError, match=r"store must be a zarr StoreLike"):
        validate(remote_path)

    # Path exists but is not a zarr store
    non_zarr_path = tmp_path / "not-a-zarr"
    non_zarr_path.mkdir()
    with pytest.raises(ValueError, match=r"store must be a zarr StoreLike"):
        validate(non_zarr_path)

    zpath = tmp_path / "test.zarr"
    z = zarr.open_group(zpath)

    # Missing metadata
    with pytest.raises(ValueError, match="No geff key found in"):
        validate(zpath)
    z.attrs["geff"] = {
        "geff_version": "0.0.1",
        "directed": True,
        "roi_min": [0, 0],
        "roi_max": [100, 100],
    }
    # No nodes
    with pytest.raises(ValueError, match="'graph' group must contain a group named 'nodes'"):
        validate(zpath)
    nodes = z.create_group("nodes")

    # Nodes missing ids
    with pytest.raises(ValueError, match="'nodes' group must contain an 'ids' array"):
        validate(zpath)
    n_node = 10
    z["nodes/ids"] = np.zeros(n_node)

    # Nodes must have a props group
    with pytest.raises(ValueError, match="'nodes' group must contain a group named 'props'"):
        validate(zpath)
    nodes.create_group("props")

    # Subgroups in props must have values
    nodes.create_group("props/score")
    with pytest.raises(ValueError, match="Node property group 'score' must have a 'values' array"):
        validate(zpath)
    z["nodes/props/score/values"] = np.zeros(n_node)
    validate(zpath)

    # Property shape mismatch
    z["nodes/props/badshape/values"] = np.zeros(n_node * 2)
    with pytest.raises(
        ValueError,
        match=(
            f"Node property 'badshape' values has length {n_node * 2}, "
            f"which does not match id length {n_node}"
        ),
    ):
        validate(zpath)

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
        validate(zpath)
    del z["nodes/props"]["badshape"]

    # No edge group is okay, if the graph has no edges
    z.create_group("edges")

    # Missing edge ids
    with pytest.raises(ValueError, match="'edges' group must contain an 'ids' array"):
        validate(zpath)

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
        validate(zpath)
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
        validate(zpath)
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
        validate(zpath)
    del z["edges/props/badshape"]["missing"]

    # everything passes
    validate(zpath)
