from __future__ import annotations

import warnings
from typing import Annotated

from annotated_types import MinLen
from pydantic import BaseModel, Field, field_validator

from ._valid_values import (
    ALLOWED_NUMPY_DTYPES,
    validate_data_type,
)


class PropMetadata(BaseModel):
    """Metadata describing a property in the geff graph."""

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
            "Data type of the property. Must be a non-empty string that can be"
            "parsed into a numpy dtype, or the special value 'varlength' to indicate"
            "a variable length property. "
            "Examples of valid values: 'int', 'int16', 'float64', 'str', 'bool'. "
            "Examples of invalid values: 'integer', 'np.int16', 'number', 'string'."
        ),
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
                f"Data type {value} cannot be matched to a valid data type {ALLOWED_NUMPY_DTYPES}"
                "or `varlength`. Reader applications may not know what to do with this dtype.",
                stacklevel=2,
            )
        return value
