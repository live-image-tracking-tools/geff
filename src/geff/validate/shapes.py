from __future__ import annotations

import numpy as np


def validate_ellipsoid(covariance: np.ndarray) -> None:
    """Validate that ellipsoid data has a valid covariance matrix

    Args:
        covariance (np.ndarray): Covariance array stored as values for an ellipsoid property

    Raises:
        ValueError: Ellipsoid covariance must be square matrices
        ValueError: Ellipsoid covariance matrices must be symmetric
        ValueError: Ellipsoid covariance matrices must be positive-definite
    """
    if covariance.ndim != 3 or covariance.shape[1] != covariance.shape[2]:
        raise ValueError("Ellipsoid covariance must be square matrices")
    if not np.allclose(covariance, covariance.transpose((0, 2, 1))):
        raise ValueError("Ellipsoid covariance matrices must be symmetric")
    if not np.all(np.linalg.eigvals(covariance) > 0):
        raise ValueError("Ellipsoid covariance matrices must be positive-definite")


def validate_sphere(radius: np.ndarray) -> None:
    """Validate that sphere data has non zero radii

    Args:
        radius (np.ndarray): Values array of a sphere property

    Raises:
        ValueError: Sphere radius values must be non-negative
    """
    if np.any(radius < 0):
        raise ValueError("Sphere radius values must be non-negative.")
