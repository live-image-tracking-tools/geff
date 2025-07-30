import numpy as np
import pytest

from geff.serialization import (
    _deserialize_vlen_array,
    deserialize_vlen_property_data,
    serialize_vlen_property_data,
    serialize_vlen_property_data_as_dict,
)


@pytest.fixture
def basic_1d_data():
    """Basic 1D test data."""
    return [
        np.array([1, 2, 3]),
        np.array([4, 5]),
        np.array([6]),
    ]


@pytest.fixture
def data_with_none():
    """Test data containing None values."""
    return [
        np.array([1, 2]),
        None,
        np.array([3, 4, 5]),
        None,
    ]


@pytest.fixture
def basic_2d_data():
    """Basic 2D test data."""
    return [
        np.array([[1, 2], [3, 4]]),
        np.array([[5, 6, 7], [8, 9, 10]]),
    ]


@pytest.fixture
def complex_2d_data():
    """Complex 2D test data with different shapes."""
    return [
        np.array([[1, 2], [3, 4]]),  # 2x2
        None,  # missing
        np.array([[5, 6, 7]]),  # 1x3
        np.array([[8], [9], [10]]),  # 3x1
    ]


@pytest.fixture
def empty_and_data():
    """Test data with empty arrays."""
    return [
        np.array([]),
        np.array([1, 2]),
        np.array([]),
    ]


@pytest.fixture
def all_none_data():
    """Test data with all None values."""
    return [None, None, None]


@pytest.fixture
def mixed_dimension_data():
    """Test data with mixed dimensions (should cause error)."""
    return [np.array([1, 2, 3]), np.array([[4, 5], [6, 7]])]  # 1D  # 2D


@pytest.fixture
def float_data():
    """Floating point test data."""
    return [
        np.array([1.1, 2.2, 3.3]),
        None,
        np.array([4.4]),
    ]


@pytest.fixture
def roundtrip_1d_data():
    """1D data for round-trip testing."""
    return [
        np.array([1, 2, 3]),
        None,
        np.array([4, 5]),
        np.array([]),
        np.array([6]),
    ]


@pytest.fixture
def roundtrip_2d_data():
    """2D data for round-trip testing."""
    return [
        np.array([[1, 2], [3, 4]]),
        np.array([[5, 6, 7]]),
        None,
        np.array([[8], [9]]),
    ]


@pytest.fixture
def serialized_vlen_props():
    """Pre-serialized vlen props for deserialization tests."""
    return {
        "values": np.array(
            [
                [0, 3],
                [3, 2],
                [5, 1],
            ],
            dtype=np.int64,
        ),
        "missing": np.array([False, False, False], dtype=bool),
        "data": np.array([1, 2, 3, 4, 5, 6], dtype=np.float32),
    }


@pytest.fixture
def serialized_vlen_props_with_missing():
    """Pre-serialized vlen props with missing values."""
    return {
        "values": np.array(
            [
                [0, 2],
                [2, 0],
                [2, 1],
            ],
            dtype=np.int64,
        ),
        "missing": np.array([False, True, False], dtype=bool),
        "data": np.array([1, 2, 3], dtype=np.float32),
    }


@pytest.fixture
def serialized_vlen_props_no_missing():
    """Pre-serialized vlen props without missing array."""
    return {
        "values": np.array(
            [
                [0, 2],
                [2, 1],
            ],
            dtype=np.int64,
        ),
        "data": np.array([1, 2, 3], dtype=np.float32),
    }


@pytest.fixture
def deserialize_array_data():
    """Test data for _deserialize_vlen_array function."""
    return {
        "values": np.array(
            [
                [0, 3],
                [3, 2],
                [5, 1],
            ],
            dtype=np.int64,
        ),
        "missing": np.array([False, False, False], dtype=bool),
        "data": np.array([1, 2, 3, 4, 5, 6], dtype=np.float32),
    }


@pytest.fixture
def deserialize_2d_array_data():
    """Test data for deserializing 2D arrays."""
    return {
        "values": np.array(
            [
                [0, 2, 2],
                [4, 1, 3],
            ],
            dtype=np.int64,
        ),
        "missing": np.array([False, False], dtype=bool),
        "data": np.array([1, 2, 3, 4, 5, 6, 7], dtype=np.float32),
    }


class TestSerializeVlenPropertyData:
    """Test suite for serialize_vlen_property_data function."""

    def test_serialize_basic_data(self, basic_1d_data):
        """Test serialization of basic variable-length data."""
        values, missing, data = serialize_vlen_property_data(basic_1d_data)

        # Check values array (offset, shape)
        expected_values = np.array(
            [
                [0, 3],  # offset=0, shape=(3,)
                [3, 2],  # offset=3, shape=(2,)
                [5, 1],  # offset=5, shape=(1,)
            ],
            dtype=np.int64,
        )

        # Check missing array
        expected_missing = np.array([False, False, False], dtype=bool)

        # Check flattened data
        expected_data = np.array([1, 2, 3, 4, 5, 6], dtype=np.float32)

        np.testing.assert_array_equal(values, expected_values)
        np.testing.assert_array_equal(missing, expected_missing)
        np.testing.assert_array_equal(data, expected_data)

    def test_serialize_with_none_values(self, data_with_none):
        """Test serialization with None values."""
        values, missing, data = serialize_vlen_property_data(data_with_none)

        expected_values = np.array(
            [
                [0, 2],  # offset=0, shape=(2,)
                [2, 0],  # offset=2, shape=(0,) for None
                [2, 3],  # offset=2, shape=(3,)
                [5, 0],  # offset=5, shape=(0,) for None
            ],
            dtype=np.int64,
        )

        expected_missing = np.array([False, True, False, True], dtype=bool)
        expected_data = np.array([1, 2, 3, 4, 5], dtype=np.float32)

        np.testing.assert_array_equal(values, expected_values)
        np.testing.assert_array_equal(missing, expected_missing)
        np.testing.assert_array_equal(data, expected_data)

    def test_serialize_2d_arrays(self, basic_2d_data):
        """Test serialization of 2D arrays."""
        values, missing, data = serialize_vlen_property_data(basic_2d_data)

        expected_values = np.array(
            [
                [0, 2, 2],  # offset=0, shape=(2, 2)
                [4, 2, 3],  # offset=4, shape=(2, 3)
            ],
            dtype=np.int64,
        )

        expected_missing = np.array([False, False], dtype=bool)
        expected_data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], dtype=np.float32)

        np.testing.assert_array_equal(values, expected_values)
        np.testing.assert_array_equal(missing, expected_missing)
        np.testing.assert_array_equal(data, expected_data)

    def test_serialize_all_none(self, all_none_data):
        """Test serialization when all elements are None."""
        values, missing, data = serialize_vlen_property_data(all_none_data)

        assert values.dtype == np.int64
        assert missing is not None
        assert missing.dtype == np.bool_
        assert data.dtype == np.float32
        assert np.all(missing)
        assert len(values) == len(all_none_data)
        assert len(missing) == len(all_none_data)
        assert len(data) == 0

    def test_serialize_different_dimensions_raises_error(self, mixed_dimension_data):
        """Test that mixed dimensionality raises ValueError."""
        with pytest.raises(
            ValueError, match="All elements must have the same number of dimensions"
        ):
            serialize_vlen_property_data(mixed_dimension_data)

    def test_serialize_custom_dtype(self, basic_1d_data):
        """Test serialization with custom dtype."""
        values, missing, data = serialize_vlen_property_data(basic_1d_data, dtype=np.int32)

        assert data.dtype == np.int32
        expected_data = np.array([1, 2, 3, 4, 5, 6], dtype=np.int32)
        np.testing.assert_array_equal(data, expected_data)

    def test_serialize_empty_arrays(self, empty_and_data):
        """Test serialization with empty arrays."""
        values, missing, data = serialize_vlen_property_data(empty_and_data)

        expected_values = np.array(
            [
                [0, 0],  # offset=0, shape=(0,)
                [0, 2],  # offset=0, shape=(2,)
                [2, 0],  # offset=2, shape=(0,)
            ],
            dtype=np.int64,
        )

        expected_missing = np.array([False, False, False], dtype=bool)
        expected_data = np.array([1, 2], dtype=np.float32)

        np.testing.assert_array_equal(values, expected_values)
        np.testing.assert_array_equal(missing, expected_missing)
        np.testing.assert_array_equal(data, expected_data)


class TestSerializeVlenPropertyDataAsDict:
    """Test suite for serialize_vlen_property_data_as_dict function."""

    def test_serialize_as_dict_basic(self, data_with_none):
        """Test serialization as dictionary format."""
        result = serialize_vlen_property_data_as_dict(data_with_none)

        assert isinstance(result, dict)
        assert "values" in result
        assert "missing" in result
        assert "data" in result

        expected_values = np.array(
            [
                [0, 2],
                [2, 0],
                [2, 3],
                [5, 0],
            ],
            dtype=np.int64,
        )

        expected_missing = np.array([False, True, False, True], dtype=bool)
        expected_data = np.array([1, 2, 3, 4, 5], dtype=np.float32)

        np.testing.assert_array_equal(result["values"], expected_values)
        np.testing.assert_array_equal(result["missing"], expected_missing)
        np.testing.assert_array_equal(result["data"], expected_data)

    def test_serialize_as_dict_custom_dtype(self):
        """Test serialization as dictionary with custom dtype."""
        prop_data = [np.array([1.5, 2.5]), np.array([3.5])]
        result = serialize_vlen_property_data_as_dict(prop_data, dtype=np.float64)

        assert result["data"] is not None
        assert result["data"].dtype == np.float64
        expected_data = np.array([1.5, 2.5, 3.5], dtype=np.float64)
        np.testing.assert_array_equal(result["data"], expected_data)


class TestDeserializeVlenArray:
    """Test suite for _deserialize_vlen_array function."""

    def test_deserialize_valid_index(self, deserialize_array_data):
        """Test deserialization with valid index."""
        result = _deserialize_vlen_array(
            deserialize_array_data["values"],
            deserialize_array_data["missing"],
            deserialize_array_data["data"],
            1,
        )
        expected = np.array([4, 5], dtype=np.float32)
        np.testing.assert_array_equal(result, expected)

    def test_deserialize_missing_value(self):
        """Test deserialization with missing value."""
        values = np.array(
            [
                [0, 2],
                [2, 0],  # missing entry
                [2, 1],
            ],
            dtype=np.int64,
        )
        missing = np.array([False, True, False], dtype=bool)
        data = np.array([1, 2, 3], dtype=np.float32)

        result = _deserialize_vlen_array(values, missing, data, 1)
        assert result is None

    def test_deserialize_2d_array(self, deserialize_2d_array_data):
        """Test deserialization of 2D arrays."""
        result = _deserialize_vlen_array(
            deserialize_2d_array_data["values"],
            deserialize_2d_array_data["missing"],
            deserialize_2d_array_data["data"],
            0,
        )
        expected = np.array([[1, 2], [3, 4]], dtype=np.float32)
        np.testing.assert_array_equal(result, expected)

    def test_deserialize_index_out_of_bounds(self):
        """Test deserialization with out of bounds index."""
        values = np.array([[0, 2]], dtype=np.int64)
        missing = np.array([False], dtype=bool)
        data = np.array([1, 2], dtype=np.float32)

        with pytest.raises(IndexError, match="Index 5 out of bounds"):
            _deserialize_vlen_array(values, missing, data, 5)

        with pytest.raises(IndexError, match="Index -1 out of bounds"):
            _deserialize_vlen_array(values, missing, data, -1)

    def test_deserialize_no_missing_array(self):
        """Test deserialization when missing array is None."""
        values = np.array([[0, 2]], dtype=np.int64)
        data = np.array([1, 2], dtype=np.float32)

        result = _deserialize_vlen_array(values, None, data, 0)
        expected = np.array([1, 2], dtype=np.float32)
        np.testing.assert_array_equal(result, expected)


class TestDeserializeVlenPropertyData:
    """Test suite for deserialize_vlen_property_data function."""

    def test_deserialize_from_dict_single_index(self, serialized_vlen_props):
        """Test deserialization from dictionary with single index."""
        result = deserialize_vlen_property_data(serialized_vlen_props, index=1)
        expected = np.array([4, 5], dtype=np.float32)
        np.testing.assert_array_equal(result, expected)

    def test_deserialize_from_dict_all_indices(self, serialized_vlen_props_with_missing):
        """Test deserialization from dictionary returning all indices."""
        result = deserialize_vlen_property_data(serialized_vlen_props_with_missing)

        assert len(result) == 3
        np.testing.assert_array_equal(result[0], np.array([1, 2], dtype=np.float32))
        assert result[1] is None
        np.testing.assert_array_equal(result[2], np.array([3], dtype=np.float32))

    def test_deserialize_from_dict_no_missing_array(self, serialized_vlen_props_no_missing):
        """Test deserialization when missing array is not present."""
        result = deserialize_vlen_property_data(serialized_vlen_props_no_missing)

        assert len(result) == 2
        np.testing.assert_array_equal(result[0], np.array([1, 2], dtype=np.float32))
        np.testing.assert_array_equal(result[1], np.array([3], dtype=np.float32))

    def test_deserialize_missing_values_key(self):
        """Test error when 'values' key is missing."""
        vlen_props = serialize_vlen_property_data_as_dict([1, 2, 3])
        vlen_props.pop("values")

        with pytest.raises(ValueError, match="does not contain 'values'"):
            deserialize_vlen_property_data(vlen_props)

    def test_deserialize_missing_data_key(self):
        """Test error when 'data' key is missing."""
        vlen_props = serialize_vlen_property_data_as_dict([1, 2, 3])
        vlen_props.pop("data")

        with pytest.raises(ValueError, match="does not contain 'data'"):
            deserialize_vlen_property_data(vlen_props)

    def test_deserialize_mismatched_missing_length(self):
        """Test error when missing array length doesn't match values length."""
        vlen_props = {
            "values": np.array(
                [
                    [0, 2],
                    [2, 1],
                ],
                dtype=np.int64,
            ),
            "missing": np.array([False], dtype=bool),  # Wrong length
            "data": np.array([1, 2, 3], dtype=np.float32),
        }

        with pytest.raises(
            ValueError, match="Length of 'missing'.*does not match length of 'values'"
        ):
            deserialize_vlen_property_data(vlen_props)

    def test_deserialize_index_out_of_bounds(self, serialized_vlen_props_no_missing):
        """Test deserialization with out of bounds index."""
        with pytest.raises(IndexError, match="Index 5 out of bounds"):
            deserialize_vlen_property_data(serialized_vlen_props_no_missing, index=5)

    def test_deserialize_missing_value_at_index(self, serialized_vlen_props_with_missing):
        """Test deserialization returns None for missing value at specific index."""
        result = deserialize_vlen_property_data(serialized_vlen_props_with_missing, index=1)
        assert result is None

    @pytest.mark.parametrize("index", [None, 0, 1])
    def test_deserialize_overload_return_types(self, serialized_vlen_props_no_missing, index):
        """Test that overloaded return types work correctly."""
        result = deserialize_vlen_property_data(serialized_vlen_props_no_missing, index=index)

        if index is None:
            # Should return Sequence[NDArray | None]
            assert isinstance(result, list)
            assert len(result) == 2
        else:
            # Should return NDArray | None
            assert isinstance(result, np.ndarray)

    def test_deserialize_complex_2d_data(self, complex_2d_data):
        """Test deserialization of complex 2D variable-length data."""
        # Serialize the data first
        values, missing, data = serialize_vlen_property_data(complex_2d_data)

        vlen_props = {
            "values": values,
            "missing": missing,
            "data": data,
        }

        # Test full deserialization
        result = deserialize_vlen_property_data(vlen_props)

        assert len(result) == 4
        np.testing.assert_array_equal(result[0], complex_2d_data[0])
        assert result[1] is None
        np.testing.assert_array_equal(result[2], complex_2d_data[2])
        np.testing.assert_array_equal(result[3], complex_2d_data[3])

        # Test individual index deserialization
        np.testing.assert_array_equal(
            deserialize_vlen_property_data(vlen_props, index=0), complex_2d_data[0]
        )
        assert deserialize_vlen_property_data(vlen_props, index=1) is None
        np.testing.assert_array_equal(
            deserialize_vlen_property_data(vlen_props, index=2), complex_2d_data[2]
        )
        np.testing.assert_array_equal(
            deserialize_vlen_property_data(vlen_props, index=3), complex_2d_data[3]
        )


class TestSerializationRoundTrip:
    """Test suite for round-trip serialization/deserialization."""

    def test_roundtrip_1d_arrays(self, roundtrip_1d_data):
        """Test round-trip serialization and deserialization of 1D arrays."""
        # Serialize
        values, missing, data = serialize_vlen_property_data(roundtrip_1d_data)

        # Package as dict
        vlen_props = {
            "values": values,
            "missing": missing,
            "data": data,
        }

        # Deserialize
        result = deserialize_vlen_property_data(vlen_props)

        # Compare
        assert len(result) == len(roundtrip_1d_data)
        for original, deserialized in zip(roundtrip_1d_data, result, strict=False):
            if original is None:
                assert deserialized is None
            else:
                np.testing.assert_array_equal(deserialized, original)

    def test_roundtrip_2d_arrays(self, roundtrip_2d_data):
        """Test round-trip serialization and deserialization of 2D arrays."""
        # Serialize
        values, missing, data = serialize_vlen_property_data(roundtrip_2d_data)

        # Package as dict
        vlen_props = {
            "values": values,
            "missing": missing,
            "data": data,
        }

        # Deserialize
        result = deserialize_vlen_property_data(vlen_props)

        # Compare
        assert len(result) == len(roundtrip_2d_data)
        for original, deserialized in zip(roundtrip_2d_data, result, strict=False):
            if original is None:
                assert deserialized is None
            else:
                np.testing.assert_array_equal(deserialized, original)

    def test_roundtrip_dict_format(self, float_data):
        """Test round-trip using dictionary serialization format."""
        # Serialize as dict
        serialized_dict = serialize_vlen_property_data_as_dict(float_data, dtype=np.float64)

        # Deserialize
        result = deserialize_vlen_property_data(serialized_dict)

        # Compare
        assert len(result) == len(float_data)
        for original, deserialized in zip(float_data, result, strict=False):
            if original is None:
                assert deserialized is None
            else:
                np.testing.assert_array_equal(deserialized, original)
                assert deserialized is not None
                assert deserialized.dtype == np.float64
