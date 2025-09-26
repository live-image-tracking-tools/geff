from __future__ import annotations

import copy

import numpy as np
import pytest
import zarr
import zarr.storage

from geff import _path, validate_structure
from geff.core_io._base_write import write_arrays
from geff.core_io._utils import expect_group, open_storelike
from geff.testing._utils import check_equiv_geff
from geff.testing.data import (
    create_mock_geff,
    create_simple_2d_geff,
)
from geff.validate.structure import (
    _validate_axes_structure,
    _validate_edges_group,
    _validate_nodes_group,
    _validate_props_group,
)
from geff_spec import GeffMetadata, PropMetadata


@pytest.fixture
def z() -> zarr.Group:
    store, _ = create_mock_geff(
        node_id_dtype="uint",
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
        include_varlength=True,
    )
    return zarr.open_group(store)


@pytest.fixture
def meta(z) -> GeffMetadata:
    return GeffMetadata.read(z.store)


@pytest.fixture
def node_group(z) -> zarr.Group:
    return expect_group(z, _path.NODES)


@pytest.fixture
def edge_group(z) -> zarr.Group:
    return expect_group(z, _path.EDGES)


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

    # other cases are tested in validate_nodes_group and validate_edges_group


class Test_validate_nodes_group:
    def test_no_node_ids(self, node_group, meta):
        del node_group[_path.IDS]
        with pytest.raises(
            ValueError, match=f"'{_path.NODES}' group must contain an '{_path.IDS}' array"
        ):
            _validate_nodes_group(node_group, meta)

    def test_no_node_props_group(self, node_group, meta):
        del node_group[_path.PROPS]
        # Nodes must have a props group
        with pytest.raises(
            ValueError, match=f"'{_path.NODES}' group must contain a group named '{_path.PROPS}'"
        ):
            _validate_nodes_group(node_group, meta)

    def test_ids_not_int(self, node_group, meta):
        node_group[_path.IDS] = node_group[_path.IDS][:].astype("float")
        with pytest.raises(ValueError, match="Node ids must have an integer dtype"):
            _validate_nodes_group(node_group, meta)

    # Other cases are caught in tests for _validate_props_group


class Test_validate_edges_group:
    def test_no_edge_ids(self, edge_group, meta):
        del edge_group[_path.IDS]
        with pytest.raises(
            ValueError, match=f"'{_path.EDGES}' group must contain an '{_path.IDS}' array"
        ):
            _validate_edges_group(edge_group, meta)

    def test_edge_ids_bad_second_dim(self, edge_group, meta):
        edge_group[_path.IDS] = np.zeros((3, 3))
        with pytest.raises(
            ValueError,
            match="edges ids must be 2d with last dimension of size 2, received shape .*",
        ):
            _validate_edges_group(edge_group, meta)

    def test_edge_ids_wrong_ndim(self, edge_group, meta):
        edge_group[_path.IDS] = np.zeros((3, 1))
        with pytest.raises(
            ValueError,
            match="edges ids must be 2d with last dimension of size 2, received shape .*",
        ):
            _validate_edges_group(edge_group, meta)

    def test_edge_ids_not_int(self, edge_group, meta):
        edge_group[_path.IDS] = edge_group[_path.IDS][:].astype("float")
        with pytest.raises(
            ValueError,
            match="Edge ids must have an integer dtype",
        ):
            _validate_edges_group(edge_group, meta)

        # int and uint are now both ok
        edge_group[_path.IDS] = edge_group[_path.IDS][:].astype("int")
        _validate_edges_group(edge_group, meta)

    # Other cases are caught in tests for _validate_props_group


class Test_validate_props_group:
    def test_node_prop_no_values(self, node_group, meta):
        # Subgroups in props must have values
        key = "t"
        del node_group[_path.PROPS][key][_path.VALUES]
        id_len = node_group[_path.IDS].shape[0]
        with pytest.raises(
            ValueError, match=f"Node property group '{key}' must have a '{_path.VALUES}' array"
        ):
            _validate_props_group(node_group[_path.PROPS], id_len, "Node", meta.node_props_metadata)

    def test_node_prop_shape_mismatch(self, node_group, meta):
        # Property shape mismatch
        key = "x"
        node_group[f"{_path.PROPS}/{key}/{_path.VALUES}"] = np.zeros(1)
        id_len = node_group[_path.IDS].shape[0]
        with pytest.raises(
            ValueError,
            match=(
                f"Node property '{key}' values has length {1}, which does not match id length .*"
            ),
        ):
            _validate_props_group(node_group[_path.PROPS], id_len, "Node", meta.node_props_metadata)

    def test_node_prop_missing_mismatch(self, node_group, meta):
        # Property missing shape mismatch
        key = "t"
        node_group[f"{_path.PROPS}/{key}/{_path.MISSING}"] = np.zeros(shape=(1))
        id_len = node_group[_path.IDS].shape[0]
        with pytest.raises(
            ValueError,
            match=(
                f"Node property '{key}' missing mask has length 1, "
                "which does not match id length .*"
            ),
        ):
            _validate_props_group(node_group[_path.PROPS], id_len, "Node", meta.node_props_metadata)

    def test_missing_dtype(self, node_group, meta):
        # missing arrays must be boolean
        key = "score"
        node_group[f"{_path.PROPS}/{key}/{_path.MISSING}"] = np.zeros(
            node_group[f"{_path.PROPS}/{key}/{_path.VALUES}"].shape, dtype="float"
        )
        id_len = node_group[_path.IDS].shape[0]

        with pytest.raises(ValueError, match=f"Node property '{key}' missing must be boolean"):
            _validate_props_group(node_group[_path.PROPS], id_len, "Node", meta.node_props_metadata)

    def test_missing_prop_metadata(self, node_group):
        id_len = node_group[_path.IDS].shape[0]
        with pytest.raises(ValueError, match="Property .* is missing from the property metadata"):
            _validate_props_group(node_group[_path.PROPS], id_len, "Node", {})

    def test_extra_prop_metadata(self, node_group, meta):
        meta.node_props_metadata["extra"] = PropMetadata(identifier="extra", dtype="int")
        id_len = node_group[_path.IDS].shape[0]
        with pytest.raises(
            ValueError, match="Property .* is in the metadata but missing from the property group"
        ):
            _validate_props_group(node_group[_path.PROPS], id_len, "Node", meta.node_props_metadata)

    def test_mismatched_dtype_prop_metadata(self, node_group, meta):
        id_len = node_group[_path.IDS].shape[0]
        x_meta = meta.node_props_metadata["x"]
        x_meta.dtype = "uint64"
        meta.node_props_metadata["x"] = x_meta

        with pytest.raises(ValueError, match="Property .* has stated dtype .* but actual dtype .*"):
            _validate_props_group(node_group[_path.PROPS], id_len, "Node", meta.node_props_metadata)

    def test_varlen_value_dtype(self, node_group, meta):
        id_len = node_group[_path.IDS].shape[0]
        x_meta = meta.node_props_metadata["var_length"]
        x_meta.dtype = "float"
        meta.node_props_metadata["var_length"] = x_meta

        with pytest.raises(ValueError, match="Property .* has stated dtype .* but actual dtype .*"):
            _validate_props_group(node_group[_path.PROPS], id_len, "Node", meta.node_props_metadata)

    def test_varlen_data_dtype(self, node_group, meta):
        id_len = node_group[_path.IDS].shape[0]
        node_group[_path.PROPS]["var_length"][_path.VALUES] = np.zeros(
            shape=(id_len, 2), dtype="float"
        )

        with pytest.raises(
            ValueError, match="Varlength property .* values array does not have type uint64"
        ):
            _validate_props_group(node_group[_path.PROPS], id_len, "Node", meta.node_props_metadata)

    def test_data_wo_varlen(self, node_group, meta):
        id_len = node_group[_path.IDS].shape[0]
        node_group[_path.PROPS]["x"][_path.DATA] = np.zeros(10)

        with pytest.raises(
            ValueError, match="Found data array for property .* which is not a varlength property"
        ):
            _validate_props_group(node_group[_path.PROPS], id_len, "Node", meta.node_props_metadata)


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


class Test_check_equiv_geff:
    store, attrs = create_simple_2d_geff(num_nodes=10, num_edges=15)
    in_mem = attrs

    def _write_new_store(self, in_mem):
        store = zarr.storage.MemoryStore()
        write_arrays(store, **in_mem)
        return store

    def test_same_geff(self):
        # Check that two exactly same geffs pass
        check_equiv_geff(self.store, self.store)

    def test_id_shape_mismatch(self):
        # Id shape mismatch
        bad_store, attrs = create_simple_2d_geff(num_nodes=5)
        with pytest.raises(ValueError, match=r".* ids shape: .* does not match .*"):
            check_equiv_geff(self.store, bad_store)

    def test_props_mismatch(self):
        bad_mem = copy.deepcopy(self.in_mem)
        bad_mem["node_props"]["new prop"] = bad_mem["node_props"]["t"]
        bad_mem["metadata"].node_props_metadata["new prop"] = PropMetadata(
            identifier="new prop", dtype="uint64"
        )
        bad_store = self._write_new_store(bad_mem)
        with pytest.raises(ValueError, match=".* properties: a .* does not match b .*"):
            check_equiv_geff(self.store, bad_store)

    def test_only_one_with_missing(self):
        bad_mem = copy.deepcopy(self.in_mem)
        bad_mem["edge_props"]["score"]["missing"] = np.zeros(
            bad_mem["edge_props"]["score"]["values"].shape, dtype=np.bool_
        )
        bad_store = self._write_new_store(bad_mem)
        with pytest.raises(UserWarning, match=".* contains missing but the other does not"):
            check_equiv_geff(bad_store, self.store)

    def test_value_shape_mismatch(self):
        bad_mem = copy.deepcopy(self.in_mem)
        # Add extra dimension to an edge prop
        bad_mem["edge_props"]["score"]["values"] = bad_mem["edge_props"]["score"]["values"][
            ..., np.newaxis
        ]
        bad_store = self._write_new_store(bad_mem)
        with pytest.raises(ValueError, match=r".* shape: .* does not match b .*"):
            check_equiv_geff(self.store, bad_store)

    def test_value_dtype_mismatch(self):
        # Values dtype mismatch
        bad_mem = copy.deepcopy(self.in_mem)
        # Change dtype
        bad_mem["edge_props"]["score"]["values"] = (
            bad_mem["edge_props"]["score"]["values"].astype("int").squeeze()
        )
        bad_store = self._write_new_store(bad_mem)
        with pytest.raises(ValueError, match=r".* dtype: .* does not match b .*"):
            check_equiv_geff(self.store, bad_store)


class Test_validate_axes_structure:
    def test_missing_axes_prop(self, z, meta):
        key = "x"
        del z[_path.NODE_PROPS][key]
        del meta.node_props_metadata["x"]
        with pytest.raises(ValueError, match=f"Axis {key} data is missing"):
            _validate_axes_structure(z, meta)

    def test_must_be_1d(self, z, meta):
        z[f"{_path.NODE_PROPS}/x/{_path.VALUES}"] = np.zeros((10, 2))
        with pytest.raises(ValueError, match="Axis property x has 2 dimensions, must be 1D"):
            _validate_axes_structure(z, meta)

    def test_no_missing_values(self, z, meta):
        z[f"{_path.NODE_PROPS}/x/{_path.VALUES}"] = np.zeros((10,))
        z[f"{_path.NODE_PROPS}/x/{_path.MISSING}"] = np.zeros((10,))
        with pytest.raises(ValueError, match="Axis x has missing values which are not allowed"):
            _validate_axes_structure(z, meta)
