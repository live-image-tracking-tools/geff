import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import numpy as np
import pytest
import zarr
import zarr.storage

from geff.core_io import write_arrays
from geff.core_io._base_read import read_to_memory
from geff.metadata._schema import GeffMetadata
from geff.testing.data import create_simple_3d_geff
from geff.validate.structure import validate_structure

if TYPE_CHECKING:
    from geff._typing import PropDictNpArray


from geff.core_io._base_write import dict_props_to_arr


def _tmp_metadata():
    """Return minimal valid GeffMetadata object for tests."""
    return GeffMetadata(geff_version="0.0.1", directed=True)


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
        node_ids = np.array([1, 2, 3], dtype=np.int32)
        edge_ids = np.array([[1, 2], [2, 3]], dtype=np.int32)
        metadata = GeffMetadata(geff_version="0.0.1", directed=True)

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
                node_props=None,
                edge_ids=edge_ids,
                edge_props=None,
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

    # TODO: test properties helper. It's covered by networkx tests now, so I'm okay merging,
    # but we should do it when we have time.

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

        # float16 is currently not allowed by Java Zarr
        node_ids = np.array([1, 2, 3], dtype=np.float16)
        edge_ids = np.array([[1, 2], [2, 3]], dtype=np.float16)

        with pytest.warns(UserWarning):
            write_arrays(
                geff_store=geff_path,
                node_ids=node_ids,
                node_props=None,
                edge_ids=edge_ids,
                edge_props=None,
                metadata=_tmp_metadata(),
            )

    def test_write_arrays_rejects_disallowed_property_dtype(self, tmp_path) -> None:
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

        with pytest.warns(UserWarning):
            write_arrays(
                geff_store=geff_path,
                node_ids=node_ids,
                node_props=node_props,
                edge_ids=edge_ids,
                edge_props=None,
                metadata=_tmp_metadata(),
            )


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
    print(props_dict)
    values = props_dict[data_type]["values"]
    missing = props_dict[data_type]["missing"]
    ex_values, ex_missing = expected
    ex_values = np.array(ex_values)
    ex_missing = np.array(ex_missing, dtype=bool) if ex_missing is not None else None

    np.testing.assert_array_equal(missing, ex_missing)
    np.testing.assert_array_equal(values, ex_values)


# TODO: test write_dicts (it is pretty solidly covered by networkx and write_array tests,
# so I'm okay merging without, but we should do it when we have time)
