from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any

import numpy as np
from pydantic import BaseModel, Field, GetCoreSchemaHandler, model_validator, version
from pydantic_core import core_schema

if TYPE_CHECKING:
    from collections.abc import Sequence

    from numpy.typing import DTypeLike, NDArray


PYDANTIC_211 = tuple(int(x) for x in version.VERSION.split(".")[:2]) >= (2, 11)


def _validate_tform(val: Any) -> np.ndarray:
    try:
        arr = np.asarray(val, dtype=float)
    except Exception as e:
        raise ValueError(f"Matrix must be convertible to numpy array: {e}") from e

    if arr.ndim != 2:
        raise ValueError(f"Matrix must be 2D, got {arr.ndim}D")

    nr, nc = arr.shape
    if nr != nc:
        raise ValueError(f"Matrix must be square, got shape {arr.shape}")
    if nr < 2:
        raise ValueError(
            f"Matrix must be at least 2x2 for homogeneous coordinates, got {arr.shape}"
        )

    # Check that bottom row is [0, 0, ..., 1]
    expected_bottom_row = [0.0] * (nc - 1) + [1.0]
    if not np.allclose(arr[-1], expected_bottom_row):
        raise ValueError(
            f"Bottom row of homogeneous matrix must be {expected_bottom_row}, got {arr[-1]}"
        )

    return arr


class TFormMeta:
    """Pydantic-compatible 4x4 numpy array."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        list_of_float = core_schema.list_schema(core_schema.float_schema())
        list_of_list_of_float = core_schema.list_schema(list_of_float)

        if PYDANTIC_211:
            # this is the schema for the input (i.e. "validation" mode)
            # only available in Pydantic 2.11+
            kwargs = {"json_schema_input_schema": list_of_list_of_float}
        else:
            kwargs = {}

        return core_schema.no_info_before_validator_function(
            _validate_tform,
            core_schema.is_instance_schema(np.ndarray),
            # this is the schema for the output (i.e. "serialization" mode)
            serialization=core_schema.plain_serializer_function_ser_schema(
                np.ndarray.tolist,
                return_schema=list_of_list_of_float,
            ),
            **kwargs,  # type: ignore[arg-type]
        )


class Affine(BaseModel):
    """Affine transformation matrix following scipy conventions.

    Internally stores transformations as homogeneous coordinate matrices (N+1, N+1).
    The transformation matrix follows scipy.ndimage.affine_transform convention
    where the matrix maps output coordinates to input coordinates (inverse/pull transformation).

    For a point p_out in output space, the corresponding input point p_in is computed as:
    p_in_homo = matrix @ p_out_homo
    where p_out_homo = [p_out; 1] and p_in = p_in_homo[:-1]

    Attributes:
        matrix (np.ndarray) : square, homogeneous transformation matrix (ndim+1, ndim+1)
    """

    matrix: Annotated[np.ndarray, TFormMeta] = Field(
        ...,
        description="Homogeneous transformation matrix (ndim+1, ndim+1)",
    )

    @model_validator(mode="before")
    @classmethod
    def _validate_input(cls, v: Any) -> dict:
        # if a numpy array or list is provided directly
        # assign it to the matrix (as a convenience)
        if isinstance(v, np.ndarray | list):
            v = {"matrix": v}
        return v

    def __array__(self, dtype: DTypeLike | None = None) -> np.ndarray:
        """Convert the transform to a numpy array."""
        return self.matrix.astype(dtype)

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Affine):
            return NotImplemented
        return np.array_equal(self.matrix, value.matrix)

    @property
    def ndim(self) -> int:
        """Number of spatial dimensions (excluding homogeneous coordinate)."""
        return len(self.matrix) - 1

    @property
    def linear_matrix(self) -> NDArray[np.floating]:
        """Extract the linear transformation part (ndim, ndim)."""
        return self.matrix[:-1, :-1].copy()

    @property
    def offset(self) -> NDArray[np.floating]:
        """Extract the translation offset (ndim,)."""
        return self.matrix[:-1, -1].copy()

    def transform_points(self, points: NDArray[np.floating]) -> NDArray[np.floating]:
        """
        Transform points using the affine transformation.

        Args:
            points: Input points of shape (..., ndim)

        Returns:
            Transformed points of same shape as input
        """
        points = np.asarray(points, dtype=float)
        original_shape = points.shape

        if points.shape[-1] != self.ndim:
            raise ValueError(
                f"Points last dimension {points.shape[-1]} doesn't match "
                f"transformation dimensions {self.ndim}"
            )

        # Reshape to (N, ndim) for easier processing
        points_flat = points.reshape(-1, self.ndim)

        # Add homogeneous coordinate
        ones = np.ones((points_flat.shape[0], 1))
        points_homo = np.concatenate([points_flat, ones], axis=1)

        # Transform using numpy conversion
        result_homo = (self.matrix @ points_homo.T).T

        # Extract non-homogeneous coordinates
        result = result_homo[:, :-1]

        return result.reshape(original_shape)

    def __call__(self, points: NDArray[np.floating]) -> NDArray[np.floating]:
        """Apply transformation to points (callable interface)."""
        return self.transform_points(points)

    @staticmethod
    def from_matrix_offset(
        matrix: NDArray[np.floating] | Sequence[Sequence[float]],
        offset: NDArray[np.floating] | Sequence[float] | float = 0.0,
    ) -> Affine:
        """
        Create affine transformation from linear matrix and offset.

        Args:
            matrix: Linear transformation matrix of shape (ndim, ndim)
            offset: Translation offset of shape (ndim,) or scalar

        Returns:
            Affine transformation
        """
        matrix = np.asarray(matrix, dtype=float)
        offset = np.asarray(offset, dtype=float)

        if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
            raise ValueError(f"Matrix must be square 2D array, got shape {matrix.shape}")

        ndim = matrix.shape[0]

        # Handle offset
        if offset.ndim == 0:
            offset = np.full(ndim, float(offset))
        elif offset.ndim == 1:
            if len(offset) != ndim:
                raise ValueError(f"Offset length {len(offset)} doesn't match matrix size {ndim}")
        else:
            raise ValueError(f"Offset must be scalar or 1D, got {offset.ndim}D")

        # Build homogeneous matrix
        homo_matrix = np.eye(ndim + 1)
        homo_matrix[:-1, :-1] = matrix
        homo_matrix[:-1, -1] = offset

        return Affine(matrix=homo_matrix)
