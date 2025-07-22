import re

import numpy as np
import pytest
import zarr

from geff.metadata_schema import GeffMetadata
from geff.utils import validate, validate_axes_structure, validate_zarr_structure


def test_validate(tmp_path):
    # Does not exist
    with pytest.raises(AssertionError, match=r"Directory .* does not exist"):
        validate("does-not-exist")

    zpath = tmp_path / "test.zarr"
    z = zarr.open(zpath)

    # Missing metadata
    with pytest.raises(ValueError, match="No geff key found in"):
        validate(zpath)
    z.attrs["geff"] = {
        "geff_version": "0.0.1",
        "directed": True,
        "roi_min": [0, 0],
        "roi_max": [100, 100],
    }


def test_validate_zarr_structure(tmp_path):
    zpath = tmp_path / "test.zarr"
    z = zarr.open_group(zpath)
    meta = GeffMetadata(**{"geff_version": "0.0.1", "directed": True})

    # No nodes
    with pytest.raises(AssertionError, match="graph group must contain a nodes group"):
        validate_zarr_structure(z, meta)
    z.create_group("nodes")

    # Nodes missing ids
    with pytest.raises(AssertionError, match="nodes group must contain an ids array"):
        validate_zarr_structure(z, meta)
    n_node = 10
    z["nodes/ids"] = np.zeros(n_node)

    # Node dtype must be integer like
    with pytest.raises(AssertionError, match="node ids must have an integer dtype"):
        validate_zarr_structure(z, meta)
    z["nodes/ids"] = np.ones(n_node, dtype="int32")

    # Subgroups in props must have values
    z["nodes"].create_group("props")
    z["nodes"].create_group("props/score")
    with pytest.raises(AssertionError, match="node property group score must have values group"):
        validate_zarr_structure(z, meta)
    z["nodes/props/score/values"] = np.zeros(n_node)
    validate_zarr_structure(z, meta)

    # Property shape mismatch
    z["nodes/props/badshape/values"] = np.zeros(n_node * 2)
    with pytest.raises(
        AssertionError,
        match=(
            f"node property badshape values has length {n_node * 2}, "
            f"which does not match id length {n_node}"
        ),
    ):
        validate_zarr_structure(z, meta)

    del z["nodes/props"]["badshape"]
    # Property missing shape mismatch
    z["nodes/props/badshape/values"] = np.zeros(shape=(n_node))
    z["nodes/props/badshape/missing"] = np.zeros(shape=(n_node * 2))
    with pytest.raises(
        AssertionError,
        match=(
            f"node property badshape missing mask has length {n_node * 2}, "
            f"which does not match id length {n_node}"
        ),
    ):
        validate_zarr_structure(z, meta)
    del z["nodes/props"]["badshape"]

    # Missing array must be boolean
    z["nodes/props/missing_dtype/values"] = np.zeros(shape=(n_node))
    z["nodes/props/missing_dtype/missing"] = np.zeros(shape=(n_node))
    with pytest.raises(
        AssertionError, match="Missing array for property missing_dtype must be boolean"
    ):
        validate_zarr_structure(z, meta)
    del z["nodes/props"]["missing_dtype"]

    # No edge group is okay, if the graph has no edges
    z.create_group("edges")

    # Missing edge ids
    with pytest.raises(AssertionError, match="edge group must contain ids array"):
        validate_zarr_structure(z, meta)

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
        validate_zarr_structure(z, meta)
    del z["edges"]["ids"]
    z["edges/ids"] = np.zeros((n_edges, 2))

    # Property values shape mismatch
    z["edges/props/badshape/values"] = np.zeros((n_edges * 2, 2))
    with pytest.raises(
        AssertionError,
        match=(
            f"edge property badshape values has length {n_edges * 2}, "
            f"which does not match id length {n_edges}"
        ),
    ):
        validate_zarr_structure(z, meta)
    del z["edges/props/badshape"]["values"]

    # Property missing shape mismatch
    z["edges/props/badshape/values"] = np.zeros((n_edges, 2))
    z["edges/props/badshape/missing"] = np.zeros((n_edges * 2, 2))
    with pytest.raises(
        AssertionError,
        match=(
            f"edge property badshape missing mask has length {n_edges * 2}, "
            f"which does not match id length {n_edges}"
        ),
    ):
        validate_zarr_structure(z, meta)
    del z["edges/props/badshape"]["missing"]

    # everything passes
    validate_zarr_structure(z, meta)


def test_validate_axes_structure(tmp_path):
    meta = GeffMetadata(geff_version="0.1.0", directed=True, axes=[{"name": "x"}])

    zpath = tmp_path / "test.zarr"
    z = zarr.open_group(zpath)
    z.create_group("nodes/props")

    with pytest.raises(AssertionError, match="Axis x data is missing"):
        validate_axes_structure(z, meta)
    z.create_group("nodes/props/x")

    # Values must be 1d
    z["nodes/props/x/values"] = np.zeros((10, 2))
    with pytest.raises(AssertionError, match="Axis property x has 2 dimensions, must be 1D"):
        validate_axes_structure(z, meta)
    del z["nodes/props/x/values"]

    # No missing values
    z["nodes/props/x/values"] = np.zeros((10,))
    z["nodes/props/x/missing"] = np.zeros((10,))
    with pytest.raises(AssertionError, match="Axis x has missing values which are not allowed"):
        validate_axes_structure(z, meta)
