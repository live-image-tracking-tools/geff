from typing import Any

import numpy as np
import pytest

from geff_spec import PropMetadata


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
        "str",
    ],
)
def test_validate_data_type_allowed(dtype_in: Any) -> None:
    """All allowed dtypes should work fine"""
    PropMetadata._convert_dtype(dtype_in)


@pytest.mark.parametrize(
    "dtype_in",
    ["float16", np.float16, "complex64", np.dtype("complex128"), ">f2", "varlength"],
)
def test_validate_data_type_disallowed(dtype_in) -> None:
    """All disallowed dtypes should raise error"""
    with pytest.raises(ValueError, match="Provided dtype "):
        PropMetadata._convert_dtype(dtype_in)
