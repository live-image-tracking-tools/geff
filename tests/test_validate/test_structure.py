from __future__ import annotations

import copy

import numpy as np
import pytest
import zarr
import zarr.storage

from geff import _path, validate_structure
from geff.core_io._base_read import read_to_memory
from geff.core_io._base_write import write_arrays
from geff.core_io._utils import open_storelike
from geff.metadata._schema import GeffMetadata
from geff.testing._utils import check_equiv_geff
from geff.testing.data import (
    create_2d_geff_with_invalid_shapes,
    create_memory_mock_geff,
    create_simple_2d_geff,
)
from geff.validate.data import ValidationConfig, validate_optional_data, validate_zarr_data
from geff.validate.structure import _validate_axes_structure


@pytest.fixture
def z() -> zarr.Group:
    store, attrs = create_memory_mock_geff(
        node_id_dtype="int",
        node_axis_dtypes={"position": "float64", "time": "float64"},
        directed=False,
        num_nodes=10,
        num_edges=15,
        extra_node_props={"score": "float64"},
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

    def test_missing_metadata(self, z):
        del z.attrs["geff"]

        # Missing metadata
        with pytest.raises(ValueError, match="No geff key found in"):
            validate_structure(z.store)

    def test_no_nodes_group(self, z):
        del z[_path.NODES]
        with pytest.raises(
            ValueError, match=f"'graph' group must contain a group named '{_path.NODES}'"
        ):
            validate_structure(z.store)

    def test_no_edges(self, z):
        del z["edges"]
        with pytest.raises(
            ValueError, match=f"'graph' group must contain a group named '{_path.EDGES}'"
        ):
            validate_structure(z.store)


class Test_validate_nodes_group:
    def test_no_node_ids(self, z):
        del z[_path.NODE_IDS]
        with pytest.raises(
            ValueError, match=f"'{_path.NODES}' group must contain an '{_path.IDS}' array"
        ):
            validate_structure(z.store)

    def test_no_node_props_group(self, z):
        del z[_path.NODE_PROPS]
        # Nodes must have a props group
        with pytest.raises(
            ValueError, match=f"'{_path.NODES}' group must contain a group named '{_path.PROPS}'"
        ):
            validate_structure(z.store)

    def test_node_prop_no_values(self, z):
        # Subgroups in props must have values
        key = "t"
        del z[_path.NODE_PROPS][key][_path.VALUES]
        with pytest.raises(
            ValueError, match=f"Node property group '{key}' must have a '{_path.VALUES}' array"
        ):
            validate_structure(z.store)

    def test_node_prop_shape_mismatch(self, z):
        # Property shape mismatch
        key = "badshape"
        z[f"{_path.NODE_PROPS}/{key}/{_path.VALUES}"] = np.zeros(1)
        with pytest.raises(
            ValueError,
            match=(
                f"Node property '{key}' values has length {1}, which does not match id length .*"
            ),
        ):
            validate_structure(z.store)

    def test_node_prop_missing_mismatch(self, z):
        # Property missing shape mismatch
        key = "t"
        z[f"{_path.NODE_PROPS}/{key}/{_path.MISSING}"] = np.zeros(shape=(1))
        with pytest.raises(
            ValueError,
            match=(
                f"Node property '{key}' missing mask has length 1, "
                "which does not match id length .*"
            ),
        ):
            validate_structure(z.store)


class Test_validate_edges_group:
    def test_no_edge_ids(self, z):
        del z[_path.EDGE_IDS]
        with pytest.raises(
            ValueError, match=f"'{_path.EDGES}' group must contain an '{_path.IDS}' array"
        ):
            validate_structure(z.store)

    def test_edge_ids_bad_shape(self, z):
        z[_path.EDGE_IDS] = np.zeros((3, 3))
        with pytest.raises(
            ValueError,
            match="edges ids must have a last dimension of size 2, received shape .*",
        ):
            validate_structure(z.store)

    def test_edge_values_bad_shape(self, z):
        key = "score"
        z[f"{_path.EDGE_PROPS}/{key}/{_path.VALUES}"] = np.zeros((1, 2))
        with pytest.raises(
            ValueError,
            match=(f"Edge property '{key}' values has length 1, which does not match id length .*"),
        ):
            validate_structure(z.store)

    def test_edge_missing_bad_shape(self, z):
        key = "score"
        z[f"{_path.EDGE_PROPS}/{key}/{_path.MISSING}"] = np.zeros((1, 2))
        with pytest.raises(
            ValueError,
            match=(
                f"Edge property '{key}' missing mask has length 1, "
                "which does not match id length .*"
            ),
        ):
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

    # Props mismatch
    bad_mem = copy.deepcopy(in_mem)
    bad_mem["node_props"]["new prop"] = bad_mem["node_props"]["t"]
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


def test_validate_axes_structure(tmp_path):
    meta = GeffMetadata(geff_version="0.1.0", directed=True, axes=[{"name": "x"}])

    zpath = tmp_path / "test.zarr"
    z = zarr.open_group(zpath)
    z.create_group(_path.NODE_PROPS)

    with pytest.raises(AssertionError, match="Axis x data is missing"):
        _validate_axes_structure(z, meta)
    z.create_group(f"{_path.NODE_PROPS}/x")

    # Values must be 1d
    z[f"{_path.NODE_PROPS}/x/{_path.VALUES}"] = np.zeros((10, 2))
    with pytest.raises(AssertionError, match="Axis property x has 2 dimensions, must be 1D"):
        _validate_axes_structure(z, meta)
    del z[f"{_path.NODE_PROPS}/x/{_path.VALUES}"]

    # No missing values
    z[f"{_path.NODE_PROPS}/x/{_path.VALUES}"] = np.zeros((10,))
    z[f"{_path.NODE_PROPS}/x/{_path.MISSING}"] = np.zeros((10,))
    with pytest.raises(AssertionError, match="Axis x has missing values which are not allowed"):
        _validate_axes_structure(z, meta)


def test_validate_zarr_data():
    # We're not currently going to test/raise all of the ValueErrors
    # because each of the sub functions is tested independently

    store, _ = create_simple_2d_geff()
    graph_dict = read_to_memory(store, validate=False)

    validate_zarr_data(graph_dict)


@pytest.mark.xfail(reason="Bad shapes. TODO separate out into multiple tests")
def test_optional_data():
    # config = ValidationConfig(lineage=True)
    # graph_dict = ...  # TODO need a test graph with lineage data
    # validate_optional_data(config, graph_dict)

    # config = ValidationConfig(tracklet=True)
    # graph_dict = ...  # TODO need a test graph with tracklet data
    # validate_optional_data(config, graph_dict)

    graph_dict = create_2d_geff_with_invalid_shapes()

    config = ValidationConfig(sphere=True)
    validate_optional_data(config, graph_dict)

    config = ValidationConfig(ellipsoid=True)
    validate_optional_data(config, graph_dict)
