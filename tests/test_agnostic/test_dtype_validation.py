import numpy as np
import pytest

from geff.metadata_schema import GeffMetadata
from geff.valid_values import validate_data_type
from geff.write_arrays import write_arrays


# -----------------------------------------------------------------------------
# Unit-tests for `validate_data_type`
# -----------------------------------------------------------------------------
@pytest.mark.parametrize(
    "dtype_in",
    [
        "int8",
        np.int16,
        np.dtype("uint32"),
        np.float32,
        np.dtype("float64"),
        np.bool_,
    ],
)
def test_validate_data_type_allowed(dtype_in):
    """All allowed dtypes should return *True*."""
    assert validate_data_type(dtype_in) is True


@pytest.mark.parametrize(
    "dtype_in",
    ["float16", np.float16, "complex64", np.dtype("complex128"), ">f2"],
)
def test_validate_data_type_disallowed(dtype_in):
    """All disallowed dtypes should return *False*."""
    assert validate_data_type(dtype_in) is False


# -----------------------------------------------------------------------------
# Integration tests for write_arrays
# -----------------------------------------------------------------------------


def _tmp_metadata():
    """Return minimal valid GeffMetadata object for tests."""
    return GeffMetadata(geff_version="0.0.1", directed=True)


def test_write_arrays_rejects_disallowed_id_dtype(tmp_path):
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


def test_write_arrays_rejects_disallowed_property_dtype(tmp_path):
    """write_arrays must fail fast if any property array has an unsupported dtype."""
    geff_path = tmp_path / "invalid_prop.geff"

    # ids are fine (int32)
    node_ids = np.array([1, 2, 3], dtype=np.int32)
    edge_ids = np.array([[1, 2], [2, 3]], dtype=np.int32)

    # property with disallowed dtype (float16)
    bad_prop_values = np.array([0.1, 0.2, 0.3], dtype=np.float16)
    node_props = {"score": (bad_prop_values, None)}

    with pytest.warns(UserWarning):
        write_arrays(
            geff_store=geff_path,
            node_ids=node_ids,
            node_props=node_props,
            edge_ids=edge_ids,
            edge_props=None,
            metadata=_tmp_metadata(),
        )
