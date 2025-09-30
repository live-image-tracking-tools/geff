import pydantic
import pytest

from geff_spec._axis import Axis


class TestAxis:
    def test_valid(self) -> None:
        # minimal fields
        Axis(name="property")

        # All fields
        Axis(
            name="property",
            type="space",
            unit="micrometer",
            min=0,
            max=10,
            scale=10,
            scaled_units="millimeter",
            offset=1,
        )

    def test_no_name(self) -> None:
        # name is the only required field
        with pytest.raises(pydantic.ValidationError):
            Axis(type="space")

    def test_bad_type(self) -> None:
        # Bad type
        with pytest.raises(
            pydantic.ValidationError, match=r"Input should be 'space', 'time' or 'channel'"
        ):
            Axis(name="test", type="other")

        # None is allowed
        Axis(name="test", type=None)

    def test_invalid_units(self) -> None:
        # Spatial
        with pytest.warns(UserWarning, match=r"Spatial unit .* not in valid"):
            Axis(name="test", type="space", unit="bad unit")

        # Temporal
        with pytest.warns(UserWarning, match=r"Temporal unit .* not in valid"):
            Axis(name="test", type="time", unit="bad unit")

        # Don't check units if we don't specify type
        Axis(name="test", unit="not checked")

    def test_min_max(self) -> None:
        # Min no max
        with pytest.raises(ValueError, match=r"Min and max must both be None or neither"):
            Axis(name="test", min=0)

        # Max no min
        with pytest.raises(ValueError, match=r"Min and max must both be None or neither"):
            Axis(name="test", max=0)

        # Min > max
        with pytest.raises(ValueError, match=r"Min .* is greater than max .*"):
            Axis(name="test", min=0, max=-10)

    def test_invalid_scaled_units(self) -> None:
        # Scaled unit without scale
        with pytest.raises(
            ValueError, match="`scaled_unit` specified without setting a `scale` value"
        ):
            Axis(name="test", type="space", scaled_unit="unit")

        # Spatial
        with pytest.warns(UserWarning, match=r"Spatial scaled_unit .* not in valid"):
            Axis(name="test", type="space", scale=1, scaled_unit="bad unit")

        # Temporal
        with pytest.warns(UserWarning, match=r"Temporal scaled_unit .* not in valid"):
            Axis(name="test", type="time", scale=1, scaled_unit="bad unit")

        # Don't check units if we don't specify type
        Axis(name="test", scale=1, scaled_unit="not checked")
