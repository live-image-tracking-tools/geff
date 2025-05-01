import re

import pydantic
import pytest
import zarr

from geff.utils import validate


def test_validate(tmpdir):
    # Does not exist
    with pytest.raises(AssertionError, match=r"Directory .* does not exist"):
        validate("does-not-exist")

    zpath = str(tmpdir / "test.zarr")
    z = zarr.open(zpath)

    # Missing metadata
    with pytest.raises(pydantic.ValidationError):
        validate(zpath)
    z.attrs["geff_version"] = "v0.0.1"
    z.attrs["directed"] = True
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
    z["nodes"].create_dataset("ids", shape=(n_node), dtype='int')

    # Nodes missing position attrs
    with pytest.raises(AssertionError, match="nodes group must contain an attrs/position array"):
        validate(zpath)
    z["nodes"].create_dataset("attrs/position", shape=(n_node), dtype='float')

    # Attr shape mismatch
    z["nodes"].create_dataset("attrs/badshape", shape=(n_node * 2), dtype='float')
    with pytest.raises(
        AssertionError,
        match=(
            f"Node attribute badshape has length {n_node * 2}, "
            f"which does not match id length {n_node}"
        ),
    ):
        validate(zpath)
    del z["nodes/attrs"]["badshape"]

    # Edges missing
    with pytest.raises(AssertionError, match="graph group must contain an edge group"):
        validate(zpath)
    z.create_group("edges")

    # Missing edge ids
    with pytest.raises(AssertionError, match="edge group must contain ids array"):
        validate(zpath)

    # ids array must have last dim size 2
    badshape = (5, 3)
    z["edges"].create_dataset("ids", shape=(5, 3), dtype='int')
    with pytest.raises(
        AssertionError,
        match=re.escape(
            f"edges ids must have a last dimension of size 2, received shape {badshape}"
        ),
    ):
        validate(zpath)
    del z["edges"]["ids"]
    z["edges"].create_dataset("ids", shape=(5, 2), dtype='int')

    # everything passes
    validate(zpath)
