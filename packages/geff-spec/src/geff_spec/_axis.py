from __future__ import annotations

import warnings
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from ._valid_values import (
    VALID_AXIS_TYPES,
    VALID_SPACE_UNITS,
    VALID_TIME_UNITS,
    AxisType,
    SpaceUnits,
    TimeUnits,
    validate_space_unit,
    validate_time_unit,
)


class Axis(BaseModel):
    """The axes list is modeled after the
    [OME-zarr](https://ngff.openmicroscopy.org/0.5/index.html#axes-md)
    specifications and is used to identify spatio-temporal properties on the
    graph nodes.

    The `name` must be an existing attribute on the nodes. The optional `type` key
    must be one of `space`, `time` or `channel`, though readers may not use this information.
    An optional `unit` key should match the valid OME-Zarr units and `min` and `max` keys
    define the range of the axis

    The optional `scale` field can be used to store a scaling factor such as converting
    the data from pixel space into real world units. The associated, optional `scaled_unit`
    field specifies the output unit after applying `scale` to the data.
    """

    name: str = Field(..., description="Name of the corresponding node property")
    type: Literal[AxisType] | None = Field(
        default=None,
        description=f"The type of data encoded in this axis, one of {VALID_AXIS_TYPES} or None",
    )
    unit: str | Literal[SpaceUnits] | Literal[TimeUnits] | None = Field(
        default=None,
        description="Optional, the unit for this axis. If the type is 'space' "
        "or 'time', we recommend utilizing the OME-NGFF spatial or temporal units respectively.",
    )
    min: float | None = Field(
        default=None, description="Optional, the minimum value for this axis."
    )
    max: float | None = Field(
        default=None, description="Optional, the minimum value for this axis."
    )
    scale: float | None = Field(
        default=None, description="Optional, a scaling factor that can be applied to the data"
    )
    scaled_unit: str | Literal[SpaceUnits] | Literal[TimeUnits] | None = Field(
        default=None,
        description="Optional, the unit after applying the `scale` value to the data. "
        "If `scaled_unit` is set, a `scale` value must also be provided.",
    )
    offset: float | None = Field(
        default=None,
        description="Optional, the amount by which to offset this axis after applying "
        "the `scale` if specified.",
    )

    @model_validator(mode="after")
    def _validate_model(self) -> Axis:
        if (self.min is None) != (self.max is None):
            raise ValueError(
                f"Min and max must both be None or neither: got min {self.min} and max {self.max}"
            )
        if self.min is not None and self.max is not None and self.min > self.max:
            raise ValueError(f"Min {self.min} is greater than max {self.max}")

        if self.unit:
            self._check_units(self.unit, "unit")

        if self.scaled_unit:
            if self.scale is None:
                raise ValueError("`scaled_unit` specified without setting a `scale` value")
            self._check_units(self.scaled_unit, "scaled_unit")

        return self

    def _check_units(self, unit: str, field: str) -> None:
        if self.type == "space" and not validate_space_unit(unit):
            warnings.warn(
                f"Spatial {field} {unit} not in valid OME-Zarr units {VALID_SPACE_UNITS}. "
                "Reader applications may not know what to do with this information.",
                stacklevel=2,
            )
        elif self.type == "time" and not validate_time_unit(unit):
            warnings.warn(
                f"Temporal {field} {unit} not in valid OME-Zarr units {VALID_TIME_UNITS}. "
                "Reader applications may not know what to do with this information.",
                stacklevel=2,
            )
