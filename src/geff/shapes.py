from __future__ import annotations

import warnings
from pydantic import BaseModel, Field, model_validator, field_serializer
from pydantic_core import core_schema
import numpy as np
import numpy.typing as npt
from typing import Any

VALID_SHAPE_TYPES = [
    "sphere",
    "ellipsoid",
]


def validate_shape_type(shape_type: str) -> bool:
    """Validate shape type against standard list

    Args:
        shape_type (str): Shape type to check

    Returns:
        bool: False if the shape is not in valid types
    """
    return shape_type in VALID_SHAPE_TYPES


class Shape(BaseModel):
    name: str
    type: str

    @model_validator(mode="after")
    def _validate_model(self) -> Shape:
        if not validate_shape_type(self.type):
            warnings.warn(
                f"Type {self.type} not in valid types {VALID_SHAPE_TYPES}. "
                "Reader applications may not know what to do with this information.",
                stacklevel=2,
            )

        return self


class Sphere(Shape):
    """Hypersphere shape with a radius"""

    radius: float | int

    @model_validator(mode="after")
    def _validate_model(self) -> Sphere:
        if self.radius <= 0:
            raise ValueError(f"Radius must be positive, got {self.radius}")
        return self


class Ellipsoid(Shape):
    """Ellipsoid shape with a covariance matrix"""

    covariance: npt.NDArray[np.floating]

    @field_serializer("covariance")
    def serialize_covariance(self, covariance: np.ndarray) -> list[list[float]]:
        """Serialize numpy array to nested list for JSON compatibility."""
        return covariance.tolist()

    @model_validator(mode="after")
    def _validate_model(self) -> Ellipsoid:
        # Check for square, symmetric and positive-semidefinite covariance matrix
        if not isinstance(self.covariance, np.ndarray):
            raise TypeError("Covariance must be a numpy array")
        if self.covariance.ndim != 2 or self.covariance.shape[0] != self.covariance.shape[1]:
            raise ValueError("Covariance must be a square matrix")
        if not np.allclose(self.covariance, self.covariance.T):
            raise ValueError("Covariance matrix must be symmetric")
        if not np.all(np.linalg.eigvals(self.covariance) >= 0):
            raise ValueError("Covariance matrix must be positive-semidefinite")

        return self

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler):
        """Custom schema generation for numpy array field."""

        def validate_covariance(value):
            if isinstance(value, list):
                value = np.array(value, dtype=np.floating)
            elif not isinstance(value, np.ndarray):
                raise ValueError("Covariance must be a numpy array or nested list")
            return value

        return core_schema.no_info_plain_validator_function(validate_covariance)
