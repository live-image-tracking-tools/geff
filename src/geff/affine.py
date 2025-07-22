from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, model_validator

if TYPE_CHECKING:
    from collections.abc import Sequence

    from numpy.typing import NDArray


class Affine(BaseModel):
    """
    Affine transformation class following scipy conventions.

    Internally stores transformations as homogeneous coordinate matrices (N+1, N+1).
    The transformation matrix follows scipy.ndimage.affine_transform convention
    where the matrix maps output coordinates to input coordinates (inverse/pull transformation).

    For a point p_out in output space, the corresponding input point p_in is computed as:
    p_in_homo = matrix @ p_out_homo
    where p_out_homo = [p_out; 1] and p_in = p_in_homo[:-1]

    Attributes:
        matrix: Homogeneous transformation matrix as list of lists (ndim+1, ndim+1)
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    matrix: Any = Field(
        ..., description="Homogeneous transformation matrix as list of lists (ndim+1, ndim+1)"
    )

    @model_validator(mode="after")
    def validate_matrix(self) -> Affine:
        """Validate that matrix is a proper homogeneous transformation matrix.

        Converts to list of lists format.
        """
        # Convert input to numpy array for validation
        try:
            matrix_array = np.asarray(self.matrix, dtype=float)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Matrix must be convertible to numpy array: {e}") from e

        if matrix_array.ndim != 2:
            raise ValueError(f"Matrix must be 2D, got {matrix_array.ndim}D")

        if matrix_array.shape[0] != matrix_array.shape[1]:
            raise ValueError(f"Matrix must be square, got shape {matrix_array.shape}")

        if matrix_array.shape[0] < 2:
            raise ValueError(
                f"Matrix must be at least 2x2 for homogeneous coordinates, got {matrix_array.shape}"
            )

        # Check that bottom row is [0, 0, ..., 1]
        expected_bottom_row = np.zeros(matrix_array.shape[1])
        expected_bottom_row[-1] = 1.0

        if not np.allclose(matrix_array[-1, :], expected_bottom_row):
            raise ValueError(
                f"Bottom row of homogeneous matrix must be [0, 0, ..., 1], "
                f"got {matrix_array[-1, :]}"
            )

        # Convert to list of lists for storage
        self.matrix = matrix_array.tolist()
        return self

    def numpy(self) -> NDArray[np.floating]:
        """Convert the stored list of lists matrix to numpy array."""
        return np.array(self.matrix, dtype=float)

    @property
    def ndim(self) -> int:
        """Number of spatial dimensions (excluding homogeneous coordinate)."""
        return len(self.matrix) - 1

    @property
    def linear_matrix(self) -> NDArray[np.floating]:
        """Extract the linear transformation part (ndim, ndim)."""
        matrix_array = self.numpy()
        return matrix_array[:-1, :-1].copy()

    @property
    def offset(self) -> NDArray[np.floating]:
        """Extract the translation offset (ndim,)."""
        matrix_array = self.numpy()
        return matrix_array[:-1, -1].copy()

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
        matrix_array = self.numpy()
        result_homo = (matrix_array @ points_homo.T).T

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
