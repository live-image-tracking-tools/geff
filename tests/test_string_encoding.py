from typing import TYPE_CHECKING

import numpy as np
import pytest
from numpy.testing import assert_array_equal

from geff.string_encoding import decode_string_data, encode_string_data

if TYPE_CHECKING:
    from geff._typing import PropDictNpArray


@pytest.mark.parametrize(
    ("values", "missing", "expected_encoding", "expected_values"),
    [
        (
            np.array(["hi", "my", "name", "is"], dtype=str),
            np.array([False, True, True, True], dtype=np.bool_),
            np.array(b"himynameis"),
            [[0, 2], [2, 2], [4, 4], [8, 2]],
        ),
        (
            np.array(["hi", "", "", ""], dtype=str),
            np.array([False, True, True, True], dtype=np.bool_),
            np.array(b"hi"),
            [[0, 2], [2, 0], [2, 0], [2, 0]],
        ),
    ],
)
def test_encode_decode(values, missing, expected_encoding, expected_values):
    orig_props: PropDictNpArray = {"values": values, "missing": missing}
    new_values, new_missing, new_data = encode_string_data(orig_props)
    assert isinstance(new_data, np.ndarray)
    assert_array_equal(expected_encoding, new_data)
    assert_array_equal(expected_values, new_values)
    if new_missing is None or orig_props["missing"] is None:
        assert orig_props["missing"] is None and new_missing is None
    else:
        assert_array_equal(orig_props["missing"], new_missing)
    re_decoded = decode_string_data(new_values, new_missing, new_data)
    assert_array_equal(re_decoded["values"], values)

    if new_missing is None or re_decoded["missing"] is None:
        assert re_decoded["missing"] is None and new_missing is None
    else:
        assert_array_equal(re_decoded["missing"], missing)
