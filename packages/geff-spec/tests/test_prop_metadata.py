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
        # dtype must be a string
        with pytest.raises(pydantic.ValidationError):
            PropMetadata(identifier="prop", dtype=123)
        with pytest.raises(pydantic.ValidationError):
            PropMetadata(identifier="prop", dtype=None)

        # dtype must be a non-empty string
        with pytest.raises(ValueError, match="String should have at least 1 character"):
            PropMetadata(identifier="prop", dtype="")

        # dtype must be in allowed data types
        with pytest.warns(
            UserWarning, match=r"Data type .* cannot be matched to a valid data type"
        ):
            PropMetadata(identifier="prop", dtype="nope")

        # variable length string metadata
        with pytest.raises(
            ValueError, match="Cannot have a variable length property with type str"
        ):
            PropMetadata(identifier="test", dtype="str", varlength=True)
