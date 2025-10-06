import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import numpy as np
import pytest
import zarr
import zarr.storage

from geff import _path
from geff.core_io import construct_var_len_props, write_arrays
from geff.core_io._base_read import read_to_memory
from geff.testing._utils import check_equiv_geff
from geff.testing.data import (
    create_simple_2d_geff,
    create_simple_3d_geff,
    create_simple_temporal_geff,
)
from geff.validate.structure import validate_structure
from geff_spec import GeffMetadata

if TYPE_CHECKING:
    from geff._typing import InMemoryGeff, PropDictNpArray


from geff.core_io._base_write import (
    dict_props_to_arr,
    write_dicts,
    write_props_arrays,
)


def _tmp_metadata():
    """Return minimal valid GeffMetadata object for tests."""
    return GeffMetadata(
        geff_version="0.0.1", directed=True, node_props_metadata={}, edge_props_metadata={}
    )


@pytest.fixture
def dict_data():
    data = [
        (0, {"num": 1, "str": "category"}),
        (127, {"num": 5, "str_arr": ["test", "string"]}),
        (1, {"num": 6, "num_arr": [1, 2]}),
    ]
    return data


class TestWriteArrays:
    @pytest.mark.parametrize("zarr_format", [2, 3])
    def test_write_arrays_basic(self, tmp_path: Path, zarr_format: Literal[2, 3]) -> None:
        """Test basic functionality of write_arrays with minimal data."""
        # Create test data
        geff_path = tmp_path / "test.geff"
        node_ids = np.array([1, 2, 3], dtype=np.uint32)
        edge_ids = np.array([[1, 2], [2, 3]], dtype=np.uint32)
        metadata = _tmp_metadata()

        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                category=UserWarning,
                message="Requesting zarr spec v3 with zarr-python v2.*",
            )
            # Call write_arrays
            write_arrays(
                geff_store=geff_path,
                node_ids=node_ids,
                node_props={},
                edge_ids=edge_ids,
                edge_props={},
                metadata=metadata,
                zarr_format=zarr_format,
            )

        # Verify the zarr group was created
        assert geff_path.exists()

        # Verify node and edge IDs were written correctly
        root = zarr.open_group(str(geff_path))
        assert "nodes/ids" in root
        assert "edges/ids" in root

        # Check the data matches
        np.testing.assert_array_equal(root["nodes/ids"][:], node_ids)
        np.testing.assert_array_equal(root["edges/ids"][:], edge_ids)

        # Check the data types match
        assert root["nodes/ids"].dtype == node_ids.dtype
        assert root["edges/ids"].dtype == edge_ids.dtype

        # Verify metadata was written
        assert "geff" in root.attrs
        assert root.attrs["geff"]["geff_version"] == "0.0.1"
        assert root.attrs["geff"]["directed"] is True

        validate_structure(geff_path)

    def test_write_in_mem_geff(self):
        store, attrs = create_simple_3d_geff()
        in_mem_geff = read_to_memory(store)

        # Test writing
        new_store = zarr.storage.MemoryStore()
        write_arrays(new_store, **in_mem_geff)

        validate_structure(new_store)

    def test_write_arrays_rejects_disallowed_id_dtype(self, tmp_path) -> None:
        """write_arrays must fail fast for node/edge ids with unsupported dtype."""
        geff_path = tmp_path / "invalid_ids.geff"

        # float16 is currently not allowed by GEFF Spec
        node_ids = np.array([1, 2, 3], dtype=np.float16)
        edge_ids = np.array([[1, 2], [2, 3]], dtype=np.float16)

        with pytest.raises(TypeError, match="Node ids and edge ids must have int dtype"):
            write_arrays(
                geff_store=geff_path,
                node_ids=node_ids,
                node_props=None,
                edge_ids=edge_ids,
                edge_props=None,
                metadata=_tmp_metadata(),
            )

    def test_write_arrays_upcasts_disallowed_property_dtype(self, tmp_path) -> None:
        """write_arrays must fail fast if any property array has an unsupported dtype."""
        geff_path = tmp_path / "invalid_prop.geff"

        # ids are fine (int32)
        node_ids = np.array([1, 2, 3], dtype=np.int32)
        edge_ids = np.array([[1, 2], [2, 3]], dtype=np.int32)

        # property with disallowed dtype (float16)
        bad_prop_values = np.array([0.1, 0.2, 0.3], dtype=np.float16)
        node_props: dict[str, PropDictNpArray] = {
            "score": {"values": bad_prop_values, "missing": None}
        }

        with pytest.warns(
            UserWarning, match="Dtype float16 is being upcast to float32 for Java compatibility"
        ):
            write_arrays(
                geff_store=geff_path,
                node_ids=node_ids,
                node_props=node_props,
                edge_ids=edge_ids,
                edge_props=None,
                metadata=_tmp_metadata(),
            )

    @pytest.mark.parametrize(
        "data_func", [create_simple_2d_geff, create_simple_3d_geff, create_simple_temporal_geff]
    )
    @pytest.mark.parametrize("zarr_format", [2, 3])
    def test_simple_geffs(self, data_func, zarr_format, tmp_path):
        memory_geff: InMemoryGeff
        store, memory_geff = data_func()
        path = tmp_path / "test.geff"
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                category=UserWarning,
                message="Requesting zarr spec v3 with zarr-python v2.*",
            )
            write_arrays(path, **memory_geff, zarr_format=zarr_format)
            check_equiv_geff(store, path)

    def test_invalid_geff(self, tmp_path):
        _, memory_geff = create_simple_2d_geff()
        path = tmp_path / "test.geff"
        # Add array with wrong size
        memory_geff["node_props"]["bad_size"] = {"values": np.zeros((2, 10)), "missing": None}

        with pytest.raises(
            ValueError,
            match="Node property 'bad_size' values has length 2, which "
            "does not match id length 10\nCannot write invalid geff.",
        ):
            write_arrays(path, **memory_geff)


@pytest.mark.parametrize(
    ("data_type", "expected"),
    [
        ("num", ([1, 5, 6], None)),
        ("str", (["category", "", ""], [0, 1, 1])),
        ("num_arr", ([[1, 2], [1, 2], [1, 2]], [1, 1, 0])),
        ("str_arr", ([["test", "string"], ["test", "string"], ["test", "string"]], [1, 0, 1])),
    ],
)
def test_dict_prop_to_arr(dict_data, data_type, expected) -> None:
    props_dict = dict_props_to_arr(dict_data, [data_type])
    values = props_dict[data_type]["values"]
    missing = props_dict[data_type]["missing"]
    ex_values, ex_missing = expected
    ex_values = np.array(ex_values)
    ex_missing = np.array(ex_missing, dtype=bool) if ex_missing is not None else None

    np.testing.assert_array_equal(missing, ex_missing)
    np.testing.assert_array_equal(values, ex_values)


class Test_write_dicts:
    def test_node_ids_not_int(self):
        store = zarr.storage.MemoryStore()
        node_data = [(float(node), {}) for node in range(10)]
        meta = GeffMetadata(directed=False, node_props_metadata={}, edge_props_metadata={})
        with pytest.raises(UserWarning, match=r"Node ids with dtype .* are being cast to uint"):
            write_dicts(store, node_data, [], [], [], meta)

            z = zarr.open(store)
            assert np.issubdtype(z[_path.NODE_IDS].dtype, np.unsignedinteger)

    def test_node_int_to_uint(self):
        store = zarr.storage.MemoryStore()
        node_data = [(node, {}) for node in range(10)]
        meta = GeffMetadata(directed=False, node_props_metadata={}, edge_props_metadata={})
        write_dicts(store, node_data, [], [], [], metadata=meta)

        z = zarr.open(store)
        assert np.issubdtype(z[_path.NODE_IDS].dtype, np.unsignedinteger)

    def test_negative_ids(self):
        store = zarr.storage.MemoryStore()
        node_data = [(-node, {}) for node in range(10)]
        meta = GeffMetadata(directed=False, node_props_metadata={}, edge_props_metadata={})
        with pytest.raises(ValueError, match="Cannot write a geff with node ids that are negative"):
            write_dicts(store, node_data, [], [], [], metadata=meta)


@pytest.mark.parametrize("group", ["nodes", "edges"])
class TestWritePropsArrays:
    def _helper_for_testing_expected(
        self,
        store,
        props_metadata,
        group,
        prop_name,
        varlength,
        prop_dtype,
        expected_values,
        expected_missing,
        expected_data,
    ):
        prop_meta = None
        for prop_meta in props_metadata:
            if prop_meta.identifier == prop_name:
                break
        assert prop_meta is not None
        assert np.issubdtype(np.dtype(prop_meta.dtype), prop_dtype)
        assert prop_meta.varlength == varlength
        root = zarr.open(store)
        group_path = _path.NODES if group == "nodes" else _path.EDGES
        written_values = root[group_path][_path.PROPS][prop_name]["values"]
        np.testing.assert_array_equal(written_values[:], expected_values)

        if expected_missing is None:
            assert "missing" not in root[group_path][_path.PROPS][prop_name].keys()
        else:
            written_missing = root[group_path][_path.PROPS][prop_name]["missing"]
            np.testing.assert_array_equal(written_missing[:], expected_missing)
        if expected_data is None:
            assert "data" not in root[group_path][_path.PROPS][prop_name].keys()
        else:
            written_data = root[group_path][_path.PROPS][prop_name]["data"]
            np.testing.assert_array_equal(written_data[:], expected_data)

    def test_int_prop(self, group):
        store = zarr.storage.MemoryStore()
        prop_name = "ints"
        varlength = False
        prop_dtype = np.uint16
        prop = {
            "values": np.array([1, 2, 3, 4], dtype=np.uint16),
            "missing": np.array([0, 0, 0, 1], dtype=bool),
        }
        expected_values = prop["values"]
        expected_missing = prop["missing"]
        expected_data = None

        props_metadata = write_props_arrays(store, group, {prop_name: prop})
        self._helper_for_testing_expected(
            store,
            props_metadata,
            group,
            prop_name,
            varlength,
            prop_dtype,
            expected_values,
            expected_missing,
            expected_data,
        )

    def test_unsquish_prop(self, group):
        store = zarr.storage.MemoryStore()
        prop_name = "prop_to_unsqush"
        new_prop1 = "s1"
        new_prop2 = "s2"
        varlength = False
        prop_dtype = np.float32
        prop = {
            "values": np.array([[1, 2], [3, 4]], dtype=prop_dtype),
            "missing": np.array([0, 1], dtype=bool),
        }
        expected_values1 = np.array([1, 3], dtype=prop_dtype)
        expected_values2 = np.array([2, 4], dtype=prop_dtype)
        expected_missing = prop["missing"]
        expected_data = None
        props_unsquish = {prop_name: [new_prop1, new_prop2]}
        props_metadata = write_props_arrays(
            store, group, {prop_name: prop}, props_unsquish=props_unsquish
        )

        prop_name = new_prop1
        expected_values = expected_values1
        for prop_name, expected_values in zip(
            [new_prop1, new_prop2], [expected_values1, expected_values2], strict=True
        ):
            self._helper_for_testing_expected(
                store,
                props_metadata,
                group,
                prop_name,
                varlength,
                prop_dtype,
                expected_values,
                expected_missing,
                expected_data,
            )

    def test_str_prop(self, group):
        store = zarr.storage.MemoryStore()
        prop_name = "str"
        varlength = False
        prop_dtype = "str"
        prop = {
            "values": np.array(["", "test", "str"], dtype=prop_dtype),
            "missing": np.array([0, 1, 0], dtype=bool),
        }
        expected_values = prop["values"]
        expected_missing = prop["missing"]
        expected_data = None
        props_metadata = write_props_arrays(store, group, {prop_name: prop})
        self._helper_for_testing_expected(
            store,
            props_metadata,
            group,
            prop_name,
            varlength,
            prop_dtype,
            expected_values,
            expected_missing,
            expected_data,
        )

    def test_str_array_prop(self, group):
        store = zarr.storage.MemoryStore()
        prop_name = "str_arr"
        varlength = False
        prop_dtype = "str"
        prop = {
            "values": np.array(
                [
                    [
                        "",
                        "test",
                    ],
                    ["str", "array"],
                ],
                dtype=np.str_,
            ),
            "missing": np.array([0, 1], dtype=bool),
        }
        expected_values = prop["values"]
        expected_missing = prop["missing"]
        expected_data = None
        props_metadata = write_props_arrays(store, group, {prop_name: prop})
        self._helper_for_testing_expected(
            store,
            props_metadata,
            group,
            prop_name,
            varlength,
            prop_dtype,
            expected_values,
            expected_missing,
            expected_data,
        )

    def test_varlength_1d(self, group):
        store = zarr.storage.MemoryStore()
        prop_name = "varlength"
        varlength = True
        prop_dtype = "int"
        prop = construct_var_len_props(
            [
                [1, 2, 3],
                [4, 5],
                None,
            ]
        )
        expected_values = np.array(
            [
                [
                    0,
                    3,
                ],
                [3, 2],
                [5, 0],
            ]
        )
        expected_missing = prop["missing"]
        expected_data = np.array([1, 2, 3, 4, 5], dtype="int")
        props_metadata = write_props_arrays(store, group, {prop_name: prop})

        self._helper_for_testing_expected(
            store,
            props_metadata,
            group,
            prop_name,
            varlength,
            prop_dtype,
            expected_values,
            expected_missing,
            expected_data,
        )

    def test_varlength_3d(self, group):
        store = zarr.storage.MemoryStore()
        prop_name = "varlength"
        varlength = True
        prop_dtype = "int"
        prop = construct_var_len_props([[[[0], [1], [2]]], [[4, 5], [6, 7]]])

        expected_values = np.array(
            [
                [0, 1, 3, 1],
                [3, 1, 2, 2],
            ]
        )
        expected_missing = prop["missing"]
        expected_data = np.array([0, 1, 2, 4, 5, 6, 7], dtype="int")
        props_metadata = write_props_arrays(store, group, {prop_name: prop})

        self._helper_for_testing_expected(
            store,
            props_metadata,
            group,
            prop_name,
            varlength,
            prop_dtype,
            expected_values,
            expected_missing,
            expected_data,
        )
