from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from geff_spec import Axis


def _spatial_dim(axes: list[Axis] | None) -> int:
    """Count the number of spatial-type axes."""
    if axes is None:
        return 0
    return sum(1 for ax in axes if ax.type == "space")


def validate_ellipsoid(
    covariance: np.ndarray,
    axes: list[Axis] | None,
    missing: np.ndarray | None = None,
) -> None:
    """Validate that ellipsoid data has a valid covariance matrix

    The first axis of the covariance array corresponds to the number of nodes. The
    remaining axes correspond to the number of spatial axes.

    Args:
        covariance (np.ndarray): Covariance array stored as values for an ellipsoid property
        axes (list[Axis]): List of Axis metadata
        missing (np.ndarray | None): Optional 1D boolean array marking nodes that do not
            have ellipsoid data. Rows flagged `True` are excluded from the numeric checks.

    Raises:
        ValueError: Must define space axes in order to have ellipsoid data
        ValueError: Ellipsoid covariance matrix must have 1 + number of spatial dimensions
        ValueError: Spatial dimensions of covariance matrix must be equal
        ValueError: Ellipsoid covariance matrices must be symmetric
        ValueError: Ellipsoid covariance matrices must be positive-definite
    """
    spatial_dim = _spatial_dim(axes)
    if spatial_dim == 0:
        raise ValueError("Must define space axes in order to have ellipsoid data")

    if covariance.ndim != (exp_dim := spatial_dim + 1):
        raise ValueError(
            f"Ellipsoid covariance matrix must have {exp_dim} dimensions, got {covariance.ndim}"
        )

    if covariance.shape[1] != covariance.shape[2]:
        raise ValueError(
            f"Spatial dimensions of covariance matrix must be equal, got {covariance.shape[1:]}"
        )

    present = covariance if missing is None else covariance[~missing]

    transpose = [0, *list(range(present.ndim - 1, 0, -1))]
    if not np.allclose(present, np.transpose(present, axes=transpose)):
        raise ValueError("Ellipsoid covariance matrices must be symmetric")

    if not np.all(np.linalg.eigvals(present) > 0):
        raise ValueError("Ellipsoid covariance matrices must be positive-definite")


def validate_sphere(radius: np.ndarray, missing: np.ndarray | None = None) -> None:
    """Validate that sphere data has nonzero radii and is 1d

    Args:
        radius (np.ndarray): Values array of a sphere property
        missing (np.ndarray | None): Optional 1D boolean array marking nodes that do not
            have sphere data. Rows flagged `True` are excluded from the non-negativity check.

    Raises:
        ValueError: Sphere radius values must be non-negative
        ValueError: Sphere radius values must be 1D
    """
    if radius.ndim != 1:
        raise ValueError(f"Sphere radius values must be 1D, got {radius.ndim} dimensions")

    present = radius if missing is None else radius[~missing]
    if np.any(present < 0):
        raise ValueError("Sphere radius values must be non-negative.")


def validate_polygon(
    polygon: np.ndarray,
    axes: list[Axis] | None,
    missing: np.ndarray | None = None,
) -> None:
    """Validate that polygon data is well-formed.

    `polygon` is an object array with one entry per node (the deserialized values of a
    variable length property). For a single node, the entry is a `(n_points, n_dims)`
    array of points defined relative to the node's position, where `n_dims` matches the
    number of spatial axes.

    Args:
        polygon (np.ndarray): Object array of per-node polygon point arrays.
        axes (list[Axis] | None): List of Axis metadata.
        missing (np.ndarray | None): Optional 1D boolean array marking nodes that do not
            have polygon data. Rows flagged `True` are skipped.

    Raises:
        ValueError: Must define space axes in order to have polygon data
        ValueError: Polygon points must be a 2D array
        ValueError: Polygon points must match the number of spatial dimensions
        ValueError: Polygon must have at least 3 points
        ValueError: Polygon points must be finite
    """
    spatial_dim = _spatial_dim(axes)
    if spatial_dim == 0:
        raise ValueError("Must define space axes in order to have polygon data")

    for i, points in enumerate(polygon):
        if missing is not None and missing[i]:
            continue

        if points.ndim != 2:
            raise ValueError(
                f"Polygon points must be a 2D array, got {points.ndim} dimensions at node index {i}"
            )
        if points.shape[1] != spatial_dim:
            raise ValueError(
                f"Polygon points must have {spatial_dim} spatial dimensions, "
                f"got {points.shape[1]} at node index {i}"
            )
        if points.shape[0] < 3:
            raise ValueError(
                f"Polygon must have at least 3 points, got {points.shape[0]} at node index {i}"
            )
        if not np.all(np.isfinite(points)):
            raise ValueError(
                f"Polygon points must be finite, got non-finite values at node index {i}"
            )
