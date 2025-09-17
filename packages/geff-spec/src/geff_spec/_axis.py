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
    graph nodes. If the same names are used in the axes metadata of the
    related image or segmentation data, applications can use this information
    to align graph node locations with image data.

    The order of the axes in the list is meaningful. For one, any downstream
    properties that are an array of values with one value per (spatial) axis
    will be in the order of the axis list (filtering to only the spatial axes by
    the `type` field if needed). Secondly, if associated image or segmentation
    data does not have axes metadata, the order of the spatiotemporal axes is a
    good default guess for aligning the graph and the image data, although there
    is no way to denote the channel dimension in the graph spec. If you are
    writing out a geff with an associated segmentation and/or image dataset, we
    highly recommend providing the axis names for your segmentation/image using
    the OME-zarr spec, including channel dimensions if needed.
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

    @model_validator(mode="after")
    def _validate_model(self) -> Axis:
        if (self.min is None) != (self.max is None):
            raise ValueError(
                f"Min and max must both be None or neither: got min {self.min} and max {self.max}"
            )
        if self.min is not None and self.max is not None and self.min > self.max:
            raise ValueError(f"Min {self.min} is greater than max {self.max}")

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
