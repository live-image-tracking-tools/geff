from __future__ import annotations

import warnings
from typing import Annotated

import numpy as np
from annotated_types import MinLen
from pydantic import BaseModel, Field, field_validator, model_validator

from ._valid_values import (
    ALLOWED_NUMPY_DTYPES,
    validate_data_type,
)


class PropMetadata(BaseModel):
    """Each property must have a string identifier (the group name for the
    property) and a dtype. The dtype can be any string
    that can be coerced into a numpy dtype, or the special `varlength` dtype
    indicating this is a variable length property (coming soon). String properties
    should have dtype `str`, not `varlength`, even though they are stored using the
    same variable length mechanism.
    """

    identifier: Annotated[str, MinLen(1)] = Field(
        ...,
        description=(
            "Identifier of the property. Must be unique within its own component "
            "subgroup (nodes or edges). Must be a non-empty string."
        ),
    )
    dtype: Annotated[str, MinLen(1)] = Field(
        ...,
        description=(
            "Data type of the property. Must be a non-empty string that can be "
            "parsed into a numpy dtype."
            "Examples of valid values: 'int', 'int16', 'float64', 'str', 'bool'. "
            "Examples of invalid values: 'integer', 'np.int16', 'number', 'string'."
        ),
    )
    varlength: bool = Field(
        default=False,
        description="True if the property contains variable length arrays. Variable length "
        "arrays cannot be of dtype string (e.g. you cannot have a property where each "
        "node has an array of strings)",
    )
    unit: str | None = Field(
        default=None,
        description=("Optional unit of the property."),
    )
    name: str | None = Field(
        default=None,
        description=("Optional human friendly name of the property"),
    )
    description: str | None = Field(
        default=None,
        description=("Optional description of the property."),
    )

    @field_validator("dtype", mode="after")
    @classmethod
    def _validate_dtype(cls, value: str) -> str:
        if not validate_data_type(value):
            # TODO: error?
            warnings.warn(
                f"Data type {value} cannot be matched to a valid data type {ALLOWED_NUMPY_DTYPES}."
                "Reader applications may not know what to do with this dtype.",
                stacklevel=2,
            )
        return value

    @model_validator(mode="after")
    def _no_varlength_strings(self) -> PropMetadata:
        if self.varlength and np.dtype(self.dtype) == np.str_:
            raise ValueError("Cannot have a variable length property with type str")
        return self
