from __future__ import annotations

from typing import Annotated

import numpy as np
from annotated_types import MinLen
from pydantic import BaseModel, Field, field_validator

from ._valid_values import (
    VALID_DTYPES,
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
        description=("Data type of the property. Must be one of the allowed string dtypes."),
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

    @field_validator("dtype", mode="before")
    @classmethod
    def _convert_dtype(cls, value: str | np.dtype) -> str:
        if value is None:
            raise ValueError("Provided dtype cannot be None")
        try:
            np_dtype = np.dtype(value)
            if np.issubdtype(np_dtype, np.str_):
                name = "str"
            else:
                name = np_dtype.name
        except TypeError as err:
            raise ValueError(
                f"Provided dtype {value} cannot be parsed into any of the valid dtypes "
                f"{VALID_DTYPES}"
            ) from err

        if name not in VALID_DTYPES:
            raise ValueError(
                f"Provided dtype name {name} is not one of the valid dtypes {VALID_DTYPES}"
            )
        return name
