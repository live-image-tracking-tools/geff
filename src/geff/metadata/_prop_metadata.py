from __future__ import annotations

import warnings
from typing import Annotated

from annotated_types import MinLen
from pydantic import BaseModel, Field, field_validator

from ._valid_values import (
    ALLOWED_DTYPES,
    VALID_STR_ENCODINGS,
    validate_data_type,
    validate_str_encoding,
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
            "Data type of the property. Must be a non-empty string. "
            "Examples of valid values: 'int', 'int16', 'float64', 'str', 'bool'. "
            "Examples of invalid values: 'integer', 'np.int16', 'number', 'string'."
        ),
    )
    encoding: str | None = Field(
        default=None,
        description=(
            "Optional encoding when the property is stored as a string. For example, "
            "but not limited to, 'utf-8' or 'ascii'."
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
        try:
            validate_data_type(value)
        except TypeError:
            warnings.warn(
                f"Data type {value} cannot be matched to a valid data type {ALLOWED_DTYPES}. "
                "Reader applications may not know what to do with this information.",
                stacklevel=2,
            )
        return value

    @field_validator("encoding", mode="after")
    @classmethod
    def _validate_encoding(cls, value: str | None) -> str | None:
        if value is not None and not validate_str_encoding(value):
            warnings.warn(
                f"Encoding {value} not in valid encodings {VALID_STR_ENCODINGS}. "
                "Reader applications may not know what to do with this information.",
                stacklevel=2,
            )
        return value
