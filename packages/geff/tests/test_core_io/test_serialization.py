import numpy as np
import pytest

from geff.core_io import construct_var_len_props
from geff.core_io._serialization import (
    _deserialize_vlen_value,
    deserialize_vlen_property_data,
    serialize_vlen_property_data,
)


def basic_1d_data():
    """Basic 1D test data."""
    prop_dict = construct_var_len_props(
        [
            np.array([1, 2, 3]),
            np.array([4, 5]),
            np.array([6]),
        ]
    )
    offset_shapes = [
        [0, 3],
        [3, 2],
        [5, 1],
    ]
    serialized = np.array([1, 2, 3, 4, 5, 6])
    serialized_dict = {
        "values": np.array(offset_shapes, dtype=np.uint64),
        "missing": None,
        "data": serialized,
    }
    return prop_dict, serialized_dict


def data_with_missing():
    prop_dict = {
        "values": np.array(
            [
                np.array([1, 2, 3]),
                np.array([4, 5]),
                np.array([6]),
            ],
            dtype=np.object_,
        ),
        "missing": np.array([0, 1, 0], dtype=np.bool_),
    }
    offset_shapes = [
        [0, 3],
        [3, 2],
        [5, 1],
    ]
    serialized = np.array([1, 2, 3, 4, 5, 6])
    serialized_dict = {
        "values": np.array(offset_shapes, dtype=np.uint64),
        "missing": np.array([0, 1, 0], dtype=np.bool_),
        "data": serialized,
    }
    return prop_dict, serialized_dict


def basic_2d_data():
    """Basic 2D test data."""
    prop_dict = construct_var_len_props([[[1, 2], [3, 4]], [[5, 6, 7], [8, 9, 10]]])
    offset_shapes = [
        [0, 2, 2],
        [4, 2, 3],
    ]
    serialized = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    serialized_dict = {
        "values": np.array(offset_shapes, dtype=np.uint64),
        "missing": None,
        "data": serialized,
    }
    return prop_dict, serialized_dict


def complex_2d_data():
    """Complex 2D test data with different shapes."""
    prop_dict = construct_var_len_props(
        [
            [[1, 2], [3, 4]],  # 2x2
            None,
            np.array([[5, 6, 7]]),  # 1x3
            np.array([[8], [9], [10]]),  # 3x1
        ]
    )
    offset_shapes = [
        [0, 2, 2],
        [4, 0, 0],
        [4, 1, 3],
        [7, 3, 1],
    ]
    serialized = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    serialized_dict = {
        "values": np.array(offset_shapes, dtype=np.uint64),
        "missing": np.array([0, 1, 0, 0], dtype=np.bool_),
        "data": serialized,
    }
    return prop_dict, serialized_dict


def empty_and_data():
    """Test data with empty arrays."""
    prop_dict = {
        "values": np.array(
            [
                np.array([], dtype="int"),
                np.array([1, 2], dtype="int"),
                np.array([], dtype="int"),
            ],
            dtype=np.object_,
        ),
        "missing": None,
    }
    offset_shapes = [
        [
            0,
            0,
        ],
        [0, 2],
        [2, 0],
    ]
    serialized = np.array([1, 2])
    serialized_dict = {
        "values": np.array(offset_shapes, dtype=np.uint64),
        "missing": None,
        "data": serialized,
    }
    return prop_dict, serialized_dict


def all_missing_data():
    prop_dict = {
        "values": np.array(
            [
                np.array([], dtype="int"),
                np.array([1, 2], dtype="int"),
                np.array([], dtype="int"),
            ],
            dtype=np.object_,
        ),
        "missing": np.array(
            [
                1,
                1,
                1,
            ],
            dtype=np.bool_,
        ),
    }
    offset_shapes = [
        [
            0,
            0,
        ],
        [0, 2],
        [2, 0],
    ]
    serialized = np.array([1, 2])
    serialized_dict = {
        "values": np.array(offset_shapes, dtype=np.uint64),
        "missing": np.array(
            [
                1,
                1,
                1,
            ],
            dtype=np.bool_,
        ),
        "data": serialized,
    }
    return prop_dict, serialized_dict


def mixed_dimension_data():
    """Test data with mixed dimensions (should expand dims of the first array)."""
    prop_dict = construct_var_len_props([np.array([1, 2, 3]), np.array([[4, 5], [6, 7]])])

    offset_shapes = [
        [0, 1, 3],
        [3, 2, 2],
    ]
    serialized = np.array([1, 2, 3, 4, 5, 6, 7])
    serialized_dict = {
        "values": np.array(offset_shapes, dtype=np.uint64),
        "missing": None,
        "data": serialized,
    }
    return prop_dict, serialized_dict


def float_data():
    """Floating point test data."""
    prop_dict = construct_var_len_props(
        [
            np.array([1.1, 2.2, 3.3]),
            [],
            np.array([4.4]),
        ]
    )
    offset_shapes = [
        [
            0,
            3,
        ],
        [3, 0],
        [3, 1],
    ]
    serialized = np.array([1.1, 2.2, 3.3, 4.4])
    serialized_dict = {
        "values": np.array(offset_shapes, dtype=np.uint64),
        "missing": None,
        "data": serialized,
    }
    return prop_dict, serialized_dict


class TestSerializeVlenPropertyData:
    """Test suite for serialize_vlen_property_data function."""

    @pytest.mark.parametrize(
        "case",
        [
            basic_1d_data,
            data_with_missing,
            basic_2d_data,
            complex_2d_data,
            empty_and_data,
            all_missing_data,
            mixed_dimension_data,
            float_data,
        ],
    )
    def test_serialize_basic_data(self, case):
        """Test serialization of basic variable-length data."""
        prop_dict, ser_dict = case()
        values, missing, data = serialize_vlen_property_data(prop_dict)
        expected_values = ser_dict["values"]
        expected_missing = ser_dict["missing"]
        expected_data = ser_dict["data"]
        np.testing.assert_array_equal(values, expected_values)
        np.testing.assert_array_equal(missing, expected_missing)
        np.testing.assert_array_equal(data, expected_data)

    def test_serialize_nonarrays(self):
        with pytest.raises(
            ValueError,
            match="For variable length properties, each node/edge property must be a numpy array",
        ):
            serialize_vlen_property_data(
                {
                    "values": [[1, 2]],
                    "missing": None,
                }
            )

    def test_serialize_mixed_ndim(self):
        mixed_dimension_data = [np.array([1, 2, 3]), np.array([[4, 5], [6, 7]])]
        with pytest.raises(
            ValueError,
            match="For variable length properties, each node/edge property must have the "
            "same number of dimensions",
        ):
            serialize_vlen_property_data({"values": mixed_dimension_data, "missing": None})

    def test_serialize_mixed_dtype(self):
        mixed_dtype_data = [
            np.array([1, 2, 3], dtype=np.int64),
            np.array([[4, 5], [6, 7]], np.float64),
        ]
        with pytest.raises(
            ValueError,
            match="For variable length properties, each node/edge property must have the "
            "same number of dimensions",
        ):
            serialize_vlen_property_data({"values": mixed_dtype_data, "missing": None})


class TestDeserializeVlenPropertyData:
    """Test suite for deserialize_vlen_property_data function."""

    @pytest.mark.parametrize(
        "case",
        [
            basic_1d_data,
            data_with_missing,
            basic_2d_data,
            complex_2d_data,
            empty_and_data,
            all_missing_data,
            mixed_dimension_data,
            float_data,
        ],
    )
    def test_deserialize(self, case):
        expected_prop_dict, ser_dict = case()
        values = ser_dict["values"]
        missing = ser_dict["missing"]
        data = ser_dict["data"]
        prop_dict = deserialize_vlen_property_data(values, missing, data)
        val = prop_dict["values"]
        expected_val = expected_prop_dict["values"]
        assert val.shape == expected_val.shape
        assert val.dtype == expected_val.dtype
        for item, expected_item in zip(val, expected_val, strict=True):
            np.testing.assert_array_equal(item, expected_item)

        miss = prop_dict["missing"]
        expected_miss = expected_prop_dict["missing"]
        if miss is None or expected_miss is None:
            assert miss is None and expected_miss is None
        else:
            np.testing.assert_array_equal(miss, expected_miss)

    def test_deserialize_index_out_of_bounds(self):
        """Test deserialization with out of bounds index."""
        _, ser_dict = basic_1d_data()
        with pytest.raises(IndexError, match="Index 5 out of bounds"):
            _deserialize_vlen_value(values=ser_dict["values"], data=ser_dict["data"], index=5)
