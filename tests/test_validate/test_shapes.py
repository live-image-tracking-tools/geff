from typing import ClassVar

import numpy as np
import pytest

from geff.metadata._schema import Axis
from geff.validate.shapes import validate_ellipsoid


class Test_validate_ellipsoid:
    axes_2d: ClassVar[list[Axis]] = [Axis(name="x", type="space"), Axis(name="y", type="space")]
    axes_3d: ClassVar[list[Axis]] = [
        Axis(name="x", type="space"),
        Axis(name="y", type="space"),
        Axis(name="z", type="space"),
    ]

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
        with pytest.raises(ValueError, match="Ellipsoid covariance matrix must have .* dimensions"):
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
