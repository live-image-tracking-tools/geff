from __future__ import annotations

import warnings

from pydantic import BaseModel, model_validator

from ._valid_values import (
    VALID_AXIS_TYPES,
    VALID_SPACE_UNITS,
    VALID_TIME_UNITS,
    validate_axis_type,
    validate_space_unit,
    validate_time_unit,
)


class Axis(BaseModel):
    """The spatiotemporal axes representing the position of a node in space.

    The axes list is modeled after the OME-zarr specifications. If the same names are
    used in the axes metadata of the related image or segmentation data,
    applications can use this information to align graph node locations with image data.

    The order of the axes in the list is meaningful. Any downstream properties that are
    an array of values with one value per (spatial) axis will be in the order of the axis
    list (filtering to only the spatial axes by the type field if needed).
    """

    name: str
    type: str | None = None
    unit: str | None = None
    min: float | None = None
    max: float | None = None

    @model_validator(mode="after")
    def _validate_model(self) -> Axis:
        if (self.min is None) != (self.max is None):
            raise ValueError(
                f"Min and max must both be None or neither: got min {self.min} and max {self.max}"
            )
        if self.min is not None and self.max is not None and self.min > self.max:
            raise ValueError(f"Min {self.min} is greater than max {self.max}")

        if self.type is not None and not validate_axis_type(self.type):
            warnings.warn(
                f"Type {self.type} not in valid types {VALID_AXIS_TYPES}. "
                "Reader applications may not know what to do with this information.",
                stacklevel=2,
            )

        if self.unit:
            if self.type == "space" and not validate_space_unit(self.unit):
                warnings.warn(
                    f"Spatial unit {self.unit} not in valid OME-Zarr units {VALID_SPACE_UNITS}. "
                    "Reader applications may not know what to do with this information.",
                    stacklevel=2,
                )
            elif self.type == "time" and not validate_time_unit(self.unit):
                warnings.warn(
                    f"Temporal unit {self.unit} not in valid OME-Zarr units {VALID_TIME_UNITS}. "
                    "Reader applications may not know what to do with this information.",
                    stacklevel=2,
                )

        return self
