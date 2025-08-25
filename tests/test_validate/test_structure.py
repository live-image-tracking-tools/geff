from __future__ import annotations

import copy
import re
from typing import TYPE_CHECKING

import numpy as np
import pytest
import zarr
import zarr.storage

from geff import validate_structure
from geff.core_io._base_read import read_to_memory
from geff.core_io._base_write import write_arrays
from geff.core_io._utils import open_storelike
from geff.testing._utils import check_equiv_geff
from geff.testing.data import create_simple_2d_geff

from geff.testing.data import (
    create_dummy_graph_props,
    create_memory_mock_geff,
    create_simple_2d_geff,
    create_simple_3d_geff,
    create_simple_temporal_geff,
)

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def z() -> zarr.Group:
    store, attrs = create_memory_mock_geff(
        node_id_dtype="int",
        node_axis_dtypes={"position": "float64", "time": "float64"},
        directed=False,
        num_nodes=10,
        num_edges=15,
        extra_node_props={"score": "float64"}
        extra_edge_props={"score": "float64", "color": "int"},
        include_t=True,
        include_z=True,  # 3D includes z
        include_y=True,
        include_x=True,
    )
    store, attrs = create_simple_2d_geff()
    return zarr.open_group(store)

class TestValidateStructure:

    def test_valid_geff(self, z):
        validate_structure(z.store)

    def test_input_path(self, tmp_path: Path, z) -> None:
        # Does not exist
        with pytest.raises(FileNotFoundError, match=r"Path does not exist: does-not-exist"):
            validate_structure("does-not-exist")

        # remote zarr path does not raise existence error
        # (if we had a real remote geff we could update this to pass)
        remote_path = "https://blah.com/test.zarr"
        with pytest.raises(ValueError, match=r"store must be a zarr StoreLike"):
            validate_structure(remote_path)

        # Path exists but is not a zarr store
        non_zarr_path = tmp_path / "not-a-zarr"
        non_zarr_path.mkdir()
        with pytest.raises(ValueError, match=r"store must be a zarr StoreLike"):
            validate_structure(non_zarr_path)
        
    def test_missing_metadata(self, z):
        del z.attrs["geff"]

        # Missing metadata
        with pytest.raises(ValueError, match="No geff key found in"):
            validate_structure(z.store)

    def test_no_nodes_group(self, z):
        del z["nodes"]
        with pytest.raises(ValueError, match="'graph' group must contain a group named 'nodes'"):
            validate_structure(z.store)

    def test_no_node_ids(self, z):
        del z["nodes"]["ids"]
        with pytest.raises(ValueError, match="'nodes' group must contain an 'ids' array"):
            validate_structure(z.store)

    def test_no_node_props_group(self, z):
        del z["nodes"]["props"]
        # Nodes must have a props group
        with pytest.raises(ValueError, match="'nodes' group must contain a group named 'props'"):
            validate_structure(z.store)

    def test_node_prop_no_values(self, z):
        # Subgroups in props must have values
        del z["nodes"]["props"]["t"]["values"]
        with pytest.raises(ValueError, match="Node property group 't' must have a 'values' array"):
            validate_structure(z.store)

    def test_node_prop_shape_mismatch(self, z):
        # Property shape mismatch
        z["nodes/props/badshape/values"] = np.zeros(1)
        with pytest.raises(
            ValueError,
            match=(
                f"Node property 'badshape' values has length {1}, "
                f"which does not match id length .*"
            ),
        ):
            validate_structure(z.store)

    def test_node_prop_missing_mismatch(self, z):
        # Property missing shape mismatch
        z["nodes/props/t/missing"] = np.zeros(shape=(1))
        with pytest.raises(
            ValueError,
            match=(
                f"Node property 't' missing mask has length 1, "
                f"which does not match id length .*"
            ),
        ):
            validate_structure(z.store)

    def test_no_edges(self, z):
        del z["edges"]
        with pytest.raises(ValueError, match="'graph' group must contain a group named 'edges'"):
            validate_structure(z.store)

    def test_no_edge_ids(self, z):
        del z["edges"]["ids"]
        with pytest.raises(ValueError, match="'edges' group must contain an 'ids' array"):
            validate_structure(z.store)

    def test_edge_ids_bad_shape(self, z):
        z["edges/ids"] = np.zeros((3, 3))
        with pytest.raises(
            ValueError,
            match=f"edges ids must have a last dimension of size 2, received shape .*",
        ):
            validate_structure(z.store)
    
    def test_edge_values_bad_shape(self, z):
        z["edges/props/score/values"] = np.zeros((1, 2))
        with pytest.raises(
            ValueError,
            match=(
                f"Edge property 'score' values has length 1, "
                f"which does not match id length .*"
            ),
        ):
            validate_structure(z.store)

    def test_edge_missing_bad_shape(self, z):
        z["edges/props/score/missing"] = np.zeros((1, 2))
        with pytest.raises(
            ValueError,
            match=(
                f"Edge property 'score' missing mask has length 1, "
                f"which does not match id length .*"
            ),
        ):
            validate_structure(z.store)

    def test_metadata_missing_data(self, z):
    # Nodes: property metadata has no matching data
        geff_attrs = z.attrs["geff"]
        geff_attrs["node_props_metadata"] = {
            "prop1": {"identifier": "prop1", "dtype": "float32"},
        }
        z.attrs["geff"] = geff_attrs
        with pytest.raises(
            ValueError,
            match="Node property prop1 described in metadata is not present in props arrays",
        ):
            validate_structure(z.store)

    def test_metadata_dtype_data_mismatch(self, z):
        geff_attrs = z.attrs["geff"]
        geff_attrs["node_props_metadata"] = {
            "t": {"identifier": "t", "dtype": "str"},
        }
        z.attrs["geff"] = geff_attrs
        with pytest.raises(
            ValueError,
            match=(
                "Node property t with dtype float64 does not match "
                "metadata dtype <class 'numpy.str_'>"
            ),
        ):
            validate_structure(z.store)

        geff_attrs["node_props_metadata"]["t"] ={
            "identifier": "t", "dtype": "float64"
        }
        geff_attrs["node_props_metadata"]["x"] ={
            "identifier": "x", "dtype": "int64"
        }
        z.attrs["geff"] = geff_attrs
        # Another type of dtype mismatch
        n_node = 10
        z["nodes/props/x/values"] = np.zeros(n_node, dtype="int16")
        with pytest.raises(
            ValueError,
            match=(
                "Node property x with dtype int16 does not match "
                "metadata dtype <class 'numpy.int64'>"
            ),
        ):
            validate_structure(z.store)

    def test_edge_metadata_missing_data(self, z):
        del z["edges/props/score"]
        with pytest.raises(
            ValueError,
            match="Edge property score described in metadata is not present in props arrays",
        ):
            validate_structure(z.store)
    
    def test_node_metadata_missing_data(self, z):
        del z["nodes/props/score"]
        with pytest.raises(
            ValueError,
            match="Edge property score described in metadata is not present in props arrays",
        ):
            validate_structure(z.store)

    def test_edge_metadata_wrong_dtype(self, z):
        geff_attrs = z.attrs["geff"]
        geff_attrs["edge_props_metadata"] = {
            "score": {"identifier": "score", "dtype": "int32"},
        }
        z.attrs["geff"] = geff_attrs
        with pytest.raises(
            ValueError,
            match="Edge property score with dtype float64 does not match metadata dtype .*",
        ):
            validate_structure(z.store)
    
    # # No error raised when property with no matching prop metadata
    # z["nodes/props/prop4/values"] = np.zeros(n_node, dtype="bool")
    # z["edges/props/prop4/values"] = np.zeros(n_edges, dtype="uint8")

    def test_repeated_prop_name_node_edge(self, z):
        geff_attrs = z.attrs["geff"]
        geff_attrs["edge_props_metadata"] = {
            "score": {"identifier": "score", "dtype": "int32"},
        }
        geff_attrs["node_props_metadata"]["score"] = geff_attrs["edge_props_metadata"]["score"]
        zarr.create_array(z.store, path="edges/props/score", )
        z["edges/props/score"] = z["nodes/props/score"][:]
        validate_structure(z.store)


def test_open_storelike(tmp_path):
    # Open from a path
    valid_zarr = f"{tmp_path}/test.zarr"
    _ = zarr.open(valid_zarr)
    group = open_storelike(valid_zarr)
    assert isinstance(group, zarr.Group)

    # Open from a store
    store = zarr.storage.MemoryStore()
    zarr.open_group(store, path="group")
    group = open_storelike(store)
    assert isinstance(group, zarr.Group)

    # Bad path
    with pytest.raises(FileNotFoundError, match="Path does not exist"):
        open_storelike(f"{tmp_path}/bad.zarr")

    # Not a store
    with pytest.raises(ValueError, match="store must be a zarr StoreLike"):
        open_storelike(group)


def test_check_equiv_geff():
    def _write_new_store(in_mem):
        store = zarr.storage.MemoryStore()
        write_arrays(store, **in_mem)
        return store

    store, attrs = create_simple_2d_geff(num_nodes=10, num_edges=15)

    # Check that two exactly same geffs pass
    check_equiv_geff(store, store)

    # Create in memory version to mess with
    in_mem = read_to_memory(store)

    # Id shape mismatch
    bad_store, attrs = create_simple_2d_geff(num_nodes=5)
    with pytest.raises(ValueError, match=r".* ids shape: .* does not match .*"):
        check_equiv_geff(store, bad_store)

    # Missing props
    bad_mem = copy.deepcopy(in_mem)
    bad_mem["node_props"] = {}
    bad_store = _write_new_store(bad_mem)
    with pytest.raises(ValueError, match=".* properties: a .* does not match b .*"):
        check_equiv_geff(store, bad_store)

    # Warn if one has missing but other doesn't
    bad_mem = copy.deepcopy(in_mem)
    bad_mem["edge_props"]["score"]["missing"] = np.zeros(
        bad_mem["edge_props"]["score"]["values"].shape, dtype=np.bool_
    )
    bad_store = _write_new_store(bad_mem)
    with pytest.raises(UserWarning, match=".* contains missing but the other does not"):
        check_equiv_geff(bad_store, store)

    # Values shape mismatch
    bad_mem = copy.deepcopy(in_mem)
    # Add extra dimension to an edge prop
    bad_mem["edge_props"]["score"]["values"] = bad_mem["edge_props"]["score"]["values"][
        ..., np.newaxis
    ]
    bad_store = _write_new_store(bad_mem)
    with pytest.raises(ValueError, match=r".* shape: .* does not match b .*"):
        check_equiv_geff(store, bad_store)

    # Values dtype mismatch
    bad_mem = copy.deepcopy(in_mem)
    # Change dtype
    bad_mem["edge_props"]["score"]["values"] = (
        bad_mem["edge_props"]["score"]["values"].astype("int").squeeze()
    )
    bad_store = _write_new_store(bad_mem)
    with pytest.raises(ValueError, match=r".* dtype: .* does not match b .*"):
        check_equiv_geff(store, bad_store)
