from typing import ClassVar

import numpy as np
import pytest

from geff.validate.shapes import (
    validate_ellipsoid,
    validate_polygon,
    validate_sphere,
)
from geff_spec import Axis

AXES_2D: list[Axis] = [Axis(name="x", type="space"), Axis(name="y", type="space")]
AXES_3D: list[Axis] = [
    Axis(name="x", type="space"),
    Axis(name="y", type="space"),
    Axis(name="z", type="space"),
]


def _object_array(items: list[np.ndarray]) -> np.ndarray:
    """Build a 1D object array of per-node arrays, even when the per-node shapes coincide.

    `np.array(items, dtype=object)` only produces a ragged container when numpy can't
    broadcast `items` into a single dense array; when every item happens to share the same
    shape, it silently stacks them into a dense `object`-dtype array instead.
    """
    arr = np.empty(len(items), dtype=object)
    for i, item in enumerate(items):
        arr[i] = item
    return arr


class Test_validate_ellipsoid:
    axes_2d: ClassVar[list[Axis]] = AXES_2D
    axes_3d: ClassVar[list[Axis]] = AXES_3D

    def test_axes(self):
        arr = np.ones((10, 2, 2))
        # Must provided axes
        with pytest.raises(
            ValueError, match="Must define space axes in order to have ellipsoid data"
        ):
            validate_ellipsoid(arr, None)

        # Axes must be spatial
        axes = [Axis(name="t", type="time"), Axis(name="c", type="channel")]
        with pytest.raises(
            ValueError, match="Must define space axes in order to have ellipsoid data"
        ):
            validate_ellipsoid(arr, axes)

    def test_square_matrix(self):
        arr = np.ones((10, 2, 5))
        with pytest.raises(
            ValueError, match="Spatial dimensions of covariance matrix must be equal"
        ):
            validate_ellipsoid(arr, self.axes_2d)

    def test_ndim(self):
        arr = np.ones((10, 2, 2))
        with pytest.raises(
            ValueError, match=r"Ellipsoid covariance matrix must have .* dimensions"
        ):
            validate_ellipsoid(arr, self.axes_3d)

    def test_symmetric(self):
        arr = np.ones((10, 2, 2))
        arr[:, 0, 1] = 0
        with pytest.raises(ValueError, match="Ellipsoid covariance matrices must be symmetric"):
            validate_ellipsoid(arr, self.axes_2d)

    def test_pos_def(self):
        arr = np.ones((10, 2, 2))
        with pytest.raises(
            ValueError, match="Ellipsoid covariance matrices must be positive-definite"
        ):
            validate_ellipsoid(arr, self.axes_2d)

    def test_missing_rows_are_excluded(self):
        # A non positive-definite matrix at a missing index must not raise.
        arr = np.tile(np.eye(2), (3, 1, 1))
        arr[1] = np.ones((2, 2))  # not positive-definite, but flagged missing
        missing = np.array([False, True, False])
        validate_ellipsoid(arr, self.axes_2d, missing)

        # Sanity check: without the missing mask, the bad row is caught.
        with pytest.raises(
            ValueError, match="Ellipsoid covariance matrices must be positive-definite"
        ):
            validate_ellipsoid(arr, self.axes_2d)


class Test_validate_sphere:
    def test_not_1d(self):
        with pytest.raises(ValueError, match="Sphere radius values must be 1D"):
            validate_sphere(np.ones((2, 2, 2)))

    def test_negative_radius(self):
        with pytest.raises(ValueError, match=r"Sphere radius values must be non-negative."):
            validate_sphere(np.full((2), fill_value=-1))

    def test_missing_rows_are_excluded(self):
        radius = np.array([1.0, -5.0, 2.0])
        missing = np.array([False, True, False])
        validate_sphere(radius, missing)

        with pytest.raises(ValueError, match=r"Sphere radius values must be non-negative."):
            validate_sphere(radius)


class Test_validate_polygon:
    def _polygon(self, *point_counts: int, ndim: int = 2) -> np.ndarray:
        return _object_array([np.ones((n, ndim), dtype="float64") for n in point_counts])

    def test_no_space_axes(self):
        polygon = self._polygon(3)
        with pytest.raises(
            ValueError, match="Must define space axes in order to have polygon data"
        ):
            validate_polygon(polygon, None)

    def test_wrong_ndim(self):
        polygon = _object_array([np.ones(3)])
        with pytest.raises(ValueError, match="Polygon points must be a 2D array"):
            validate_polygon(polygon, AXES_2D)

    def test_wrong_spatial_dims(self):
        polygon = self._polygon(3, ndim=3)
        with pytest.raises(ValueError, match="Polygon points must have 2 spatial dimensions"):
            validate_polygon(polygon, AXES_2D)

    def test_too_few_points(self):
        polygon = self._polygon(2)
        with pytest.raises(ValueError, match="Polygon must have at least 3 points"):
            validate_polygon(polygon, AXES_2D)

    def test_non_finite(self):
        polygon = self._polygon(3)
        polygon[0][0, 0] = np.nan
        with pytest.raises(ValueError, match="Polygon points must be finite"):
            validate_polygon(polygon, AXES_2D)

    def test_valid_polygon(self):
        polygon = self._polygon(3, 4, 5)
        validate_polygon(polygon, AXES_2D)

    def test_missing_rows_are_skipped(self):
        polygon = self._polygon(3, 2)
        missing = np.array([False, True])
        validate_polygon(polygon, AXES_2D, missing)

        with pytest.raises(ValueError, match="Polygon must have at least 3 points"):
            validate_polygon(polygon, AXES_2D)
