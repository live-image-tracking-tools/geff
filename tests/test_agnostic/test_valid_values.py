import numpy as np

from geff.metadata._valid_values import validate_data_type


def test_validate_data_type():
    assert validate_data_type("varlength")
    assert validate_data_type("int")
    assert validate_data_type(np.uint16)
    assert validate_data_type(int)
    assert validate_data_type(str)

    assert not validate_data_type("abc")
    assert not validate_data_type(np.float16)
