from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from geff_spec import Axis


def validate_ellipsoid(covariance: np.ndarray, axes: list[Axis] | None) -> None:
    """Validate that ellipsoid data has a valid covariance matrix

    The first axis of the covariance array corresponds to the number of nodes. The
    remaining axes correspond to the number of spatial axes.

    Args:
        covariance (np.ndarray): Covariance array stored as values for an ellipsoid property
        axes (list[Axis]): List of Axis metadata

    Raises:
        ValueError: Must define space axes in order to have ellipsoid data
        ValueError: Ellipsoid covariance matrix must have 1 + number of spatial dimensions
        ValueError: Spatial dimensions of covariance matrix must be equal
        ValueError: Ellipsoid covariance matrices must be symmetric
        ValueError: Ellipsoid covariance matrices must be positive-definite
    """
    bad_axes = True
    spatial_dim = 0
    # Axes need to exist and contain spatial data
    if axes is not None:
        for ax in axes:
            if ax.type == "space":
                spatial_dim += 1

        if spatial_dim > 0:
            bad_axes = False

    if bad_axes:
        raise ValueError("Must define space axes in order to have ellipsoid data")

    if covariance.ndim != (exp_dim := spatial_dim + 1):
        raise ValueError(
            f"Ellipsoid covariance matrix must have {exp_dim} dimensions, got {covariance.ndim}"
        )

    if covariance.shape[1] != covariance.shape[2]:
        raise ValueError(
            f"Spatial dimensions of covariance matrix must be equal, got {covariance.shape[1:]}"
        )

    transpose = [0, *list(range(covariance.ndim - 1, 0, -1))]
    if not np.allclose(covariance, np.transpose(covariance, axes=transpose)):
        raise ValueError("Ellipsoid covariance matrices must be symmetric")

    if not np.all(np.linalg.eigvals(covariance) > 0):
        raise ValueError("Ellipsoid covariance matrices must be positive-definite")


def validate_sphere(radius: np.ndarray) -> None:
    """Validate that sphere data has nonzero radii and is 1d

    Args:
        radius (np.ndarray): Values array of a sphere property

    Raises:
        ValueError: Sphere radius values must be non-negative
        ValueError: Sphere radius values must be 1D
    """
    if radius.ndim != 1:
        raise ValueError(f"Sphere radius values must be 1D, got {radius.ndim} dimensions")

    if np.any(radius < 0):
        raise ValueError("Sphere radius values must be non-negative.")
