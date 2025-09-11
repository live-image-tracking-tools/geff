from typing import Any

import numpy as np
import pytest

from geff_spec import validate_data_type


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
def test_validate_data_type_allowed(dtype_in: Any) -> None:
    """All allowed dtypes should return *True*."""
    assert validate_data_type(dtype_in) is True


@pytest.mark.parametrize(
    "dtype_in",
    ["float16", np.float16, "complex64", np.dtype("complex128"), ">f2"],
)
def test_validate_data_type_disallowed(dtype_in) -> None:
    """All disallowed dtypes should return *False*."""
    assert validate_data_type(dtype_in) is False


def test_validate_data_type():
    assert validate_data_type("varlength")
    assert validate_data_type("int")
    assert validate_data_type(np.uint16)
    assert validate_data_type(int)
    assert validate_data_type(str)

    assert not validate_data_type("abc")
    assert not validate_data_type(np.float16)
