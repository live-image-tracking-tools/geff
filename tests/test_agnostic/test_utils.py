import re

import numpy as np
import pytest
import zarr

from geff.utils import validate


def test_validate(tmp_path):
    # Does not exist
    with pytest.raises(AssertionError, match=r"Directory .* does not exist"):
        validate("does-not-exist")

    zpath = tmp_path / "test.zarr"
    z = zarr.open(zpath)

    # Missing metadata
    with pytest.raises(ValueError, match="No geff_version found in"):
        validate(zpath)
    z.attrs["geff_version"] = "v0.0.1"
    z.attrs["directed"] = True
    z.attrs["position_prop"] = "position"
    z.attrs["roi_min"] = [0, 0]
    z.attrs["roi_max"] = [100, 100]

    # No nodes
    with pytest.raises(AssertionError, match="graph group must contain a nodes group"):
        validate(zpath)
    z.create_group("nodes")

    # Nodes missing ids
    with pytest.raises(AssertionError, match="nodes group must contain an ids array"):
        validate(zpath)
    n_node = 10
    z["nodes/ids"] = np.zeros(n_node)

    # Nodes missing position props
    with pytest.raises(AssertionError, match="nodes group must contain a props group"):
        validate(zpath)
    z["nodes"].create_group("props")
    with pytest.raises(AssertionError, match="nodes group must contain a props/position group"):
        validate(zpath)
    z["nodes"].create_group("props/position")
    with pytest.raises(AssertionError, match="node property group position must have values group"):
        validate(zpath)
    z["nodes/props/position/values"] = np.zeros(n_node)
    validate(zpath)

    # valid and invalid "missing" arrays for position property
    z["nodes/props/position/missing"] = np.zeros((n_node), dtype=bool)
    with pytest.raises(AssertionError, match="position group cannot have missing values"):
        validate(zpath)
    del z["nodes/props/position"]["missing"]

    # Property shape mismatch
    z["nodes/props/badshape/values"] = np.zeros(n_node * 2)
    with pytest.raises(
        AssertionError,
        match=(
            f"Node property badshape values has length {n_node * 2}, "
            f"which does not match id length {n_node}"
        ),
    ):
        validate(zpath)

    del z["nodes/props"]["badshape"]
    # Property missing shape mismatch
    z["nodes/props/badshape/values"] = np.zeros(shape=(n_node))
    z["nodes/props/badshape/missing"] = np.zeros(shape=(n_node * 2))
    with pytest.raises(
        AssertionError,
        match=(
            f"Node property badshape missing mask has length {n_node * 2}, "
            f"which does not match id length {n_node}"
        ),
    ):
        validate(zpath)
    del z["nodes/props"]["badshape"]

    # No edge group is okay, if the graph has no edges
    z.create_group("edges")

    # Missing edge ids
    with pytest.raises(AssertionError, match="edge group must contain ids array"):
        validate(zpath)

    # ids array must have last dim size 2
    n_edges = 5
    badshape = (n_edges, 3)
    z["edges/ids"] = np.zeros(badshape)
    with pytest.raises(
        AssertionError,
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
        AssertionError,
        match=(
            f"Edge property badshape values has length {n_edges * 2}, "
            f"which does not match id length {n_edges}"
        ),
    ):
        validate(zpath)
    del z["edges/props/badshape"]["values"]

    # Property missing shape mismatch
    z["edges/props/badshape/values"] = np.zeros((n_edges, 2))
    z["edges/props/badshape/missing"] = np.zeros((n_edges * 2, 2))
    with pytest.raises(
        AssertionError,
        match=(
            f"Edge property badshape missing mask has length {n_edges * 2}, "
            f"which does not match id length {n_edges}"
        ),
    ):
        validate(zpath)
    del z["edges/props/badshape"]["missing"]

    # everything passes
    validate(zpath)
