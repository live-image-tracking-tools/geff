import numpy as np
import pytest
from numpy.testing import assert_array_equal

from geff.utils import decode_string_data, encode_string_data


@pytest.mark.parametrize(
    ("values", "missing"),
    [
        (
            np.array(["hi", "my", "name", "is"], dtype=str),
            np.array([False, True, True, True], dtype=bool),
        )
    ],
)
def test_encode_decode(values, missing):
    orig_props = {"values": values, "missing": missing}
    new_props = encode_string_data(orig_props)

    expected_encoding = np.array(b"himynameis")
    assert isinstance(new_props["data"], np.ndarray)
    assert_array_equal(expected_encoding, new_props["data"])
    expected_values = [[0, 2], [2, 2], [4, 4], [8, 2]]
    assert_array_equal(expected_values, new_props["values"])
    assert_array_equal(orig_props["missing"], new_props["missing"])
    re_decoded = decode_string_data(new_props)
    assert_array_equal(re_decoded["values"], values)
    assert_array_equal(re_decoded["missing"], missing)
