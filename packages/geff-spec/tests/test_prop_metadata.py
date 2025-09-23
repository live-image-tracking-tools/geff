import numpy as np
import pydantic
import pytest

from geff_spec._prop_metadata import PropMetadata


class TestPropMetadata:
    def test_valid(self) -> None:
        # Minimal valid metadata
        PropMetadata(identifier="prop_1", name="property", dtype="int32")

        # All fields
        PropMetadata(
            identifier="prop_2",
            dtype="float64",
            unit="micrometer",
            name="property 2",
            description="A property with all fields set.",
        )

    def test_invalid_identifier(self) -> None:
        # identifier must be a string
        with pytest.raises(pydantic.ValidationError):
            PropMetadata(identifier=123, name="property", dtype="int16")

        # identifier must be a non-empty string
        with pytest.raises(ValueError, match="String should have at least 1 character"):
            PropMetadata(identifier="", dtype="int16")

    def test_invalid_dtype(self) -> None:
        # dtype must be parsable into a numpy dtype
        with pytest.raises(
            ValueError, match="Provided dtype .* cannot be parsed into any of the valid dtypes"
        ):
            PropMetadata(identifier="prop", dtype=123)
        # parsed dtype must be valid
        with pytest.raises(
            ValueError, match="Provided dtype name .* is not one of the valid dtypes "
        ):
            PropMetadata(identifier="prop", dtype=np.float16)

        # dtype must be a non-empty string
        with pytest.raises(
            pydantic.ValidationError,
            match="Provided dtype .* cannot be parsed into any of the valid dtypes",
        ):
            PropMetadata(identifier="prop", dtype="")
        with pytest.raises(pydantic.ValidationError, match="Provided dtype cannot be None"):
            PropMetadata(identifier="prop", dtype=None)

        # dtype MUST be in allowed data types
        with pytest.raises(
            pydantic.ValidationError,
            match=r"Provided dtype .* cannot be parsed into any of the valid dtypes",
        ):
            PropMetadata(identifier="prop", dtype="nope")

    @pytest.mark.parametrize(
        "dtype",
        [
            np.bool_,
            np.int8,
            np.int16,
            np.int32,
            np.int64,
            np.uint8,
            np.uint16,
            np.uint32,
            np.uint64,
            np.float32,
            np.float64,
            np.bytes_,
            np.str_,
        ],
    )
    def test_numpy_dtypes(self, dtype) -> None:
        PropMetadata(identifier="prop", dtype=dtype)

    def test_string(self) -> None:
        string_arr = np.array(["test", "strings"])
        PropMetadata(identifier="prop", dtype=string_arr.dtype)

        string_arr = np.array(["test", "st"], dtype="<U7")
        PropMetadata(identifier="prop", dtype=string_arr.dtype)
