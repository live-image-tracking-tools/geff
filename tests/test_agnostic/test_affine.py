import numpy as np
import pytest

from geff.affine import Affine


class TestAffineValidation:
    """Test validation of Affine transformation matrices."""

    def test_valid_2d_homogeneous_matrix(self) -> None:
        """Test creation with valid 2D homogeneous matrix."""
        matrix = np.array([[1, 0, 5], [0, 1, 10], [0, 0, 1]])
        affine = Affine(matrix=matrix)
        assert affine.ndim == 2
        np.testing.assert_array_equal(affine.matrix, matrix)

    def test_valid_3d_homogeneous_matrix(self) -> None:
        """Test creation with valid 3D homogeneous matrix."""
        matrix = np.array([[2, 0, 0, 1], [0, 2, 0, 2], [0, 0, 2, 3], [0, 0, 0, 1]])
        affine = Affine(matrix=matrix)
        assert affine.ndim == 3
        np.testing.assert_array_equal(affine.matrix, matrix)

    def test_invalid_non_2d_matrix(self) -> None:
        """Test rejection of non-2D matrices."""
        with pytest.raises(ValueError, match="Matrix must be 2D"):
            Affine(matrix=np.array([1, 2, 3]))

        with pytest.raises(ValueError, match="Matrix must be 2D"):
            Affine(matrix=np.zeros((2, 2, 2)))

    def test_invalid_non_square_matrix(self) -> None:
        """Test rejection of non-square matrices."""
        with pytest.raises(ValueError, match="Matrix must be square"):
            Affine(matrix=np.zeros((2, 3)))

    def test_invalid_small_matrix(self) -> None:
        """Test rejection of matrices smaller than 2x2."""
        with pytest.raises(ValueError, match="Matrix must be at least 2x2"):
            Affine(matrix=np.array([[1]]))

    def test_invalid_bottom_row(self) -> None:
        """Test rejection of invalid homogeneous bottom row."""
        # Wrong bottom row [1, 0, 1]
        matrix = np.array(
            [
                [1, 0, 5],
                [0, 1, 10],
                [1, 0, 1],  # Should be [0, 0, 1]
            ]
        )
        with pytest.raises(ValueError, match="Bottom row of homogeneous matrix must be"):
            Affine(matrix=matrix)

        # Wrong bottom row [0, 0, 0]
        matrix = np.array(
            [
                [1, 0, 5],
                [0, 1, 10],
                [0, 0, 0],  # Should be [0, 0, 1]
            ]
        )
        with pytest.raises(ValueError, match="Bottom row of homogeneous matrix must be"):
            Affine(matrix=matrix)


class TestAffineProperties:
    """Test properties of Affine transformations."""

    def test_ndim_property(self) -> None:
        """Test ndim property calculation."""
        # 2D case
        matrix_2d = np.array([[1, 0, 5], [0, 1, 10], [0, 0, 1]])
        affine_2d = Affine(matrix=matrix_2d)
        assert affine_2d.ndim == 2

        # 3D case
        matrix_3d = np.array([[2, 0, 0, 1], [0, 2, 0, 2], [0, 0, 2, 3], [0, 0, 0, 1]])
        affine_3d = Affine(matrix=matrix_3d)
        assert affine_3d.ndim == 3

    def test_linear_matrix_property(self) -> None:
        """Test extraction of linear transformation matrix."""
        matrix = np.array([[2, 1, 5], [0, 3, 10], [0, 0, 1]])
        affine = Affine(matrix=matrix)

        expected_linear = np.array([[2, 1], [0, 3]])
        np.testing.assert_array_equal(affine.linear_matrix, expected_linear)

        # Test that it's a copy (modifying shouldn't affect original)
        linear = affine.linear_matrix
        linear[0, 0] = 999
        assert affine.matrix[0][0] == 2  # Original unchanged

    def test_offset_property(self) -> None:
        """Test extraction of translation offset."""
        matrix = np.array([[2, 1, 5], [0, 3, 10], [0, 0, 1]])
        affine = Affine(matrix=matrix)

        expected_offset = np.array([5, 10])
        np.testing.assert_array_equal(affine.offset, expected_offset)

        # Test that it's a copy
        offset = affine.offset
        offset[0] = 999
        assert affine.matrix[0][2] == 5  # Original unchanged


class TestAffineTransformation:
    """Test point transformation functionality."""

    def test_identity_transformation_2d(self) -> None:
        """Test identity transformation in 2D."""
        identity_matrix = np.eye(3)
        affine = Affine(matrix=identity_matrix)

        points = np.array([[1, 2], [3, 4], [5, 6]])
        transformed = affine.transform_points(points)

        np.testing.assert_array_almost_equal(transformed, points)

    def test_translation_transformation_2d(self) -> None:
        """Test pure translation in 2D."""
        matrix = np.array([[1, 0, 5], [0, 1, 10], [0, 0, 1]])
        affine = Affine(matrix=matrix)

        points = np.array([[0, 0], [1, 1]])
        transformed = affine.transform_points(points)

        expected = np.array([[5, 10], [6, 11]])
        np.testing.assert_array_almost_equal(transformed, expected)

    def test_scaling_transformation_2d(self) -> None:
        """Test scaling transformation in 2D."""
        # Note: scipy convention - inverse scaling for pull transform
        matrix = np.array(
            [
                [0.5, 0, 0],  # Scale by 1/0.5 = 2 in x
                [0, 0.25, 0],  # Scale by 1/0.25 = 4 in y
                [0, 0, 1],
            ]
        )
        affine = Affine(matrix=matrix)

        points = np.array([[2, 4]])
        transformed = affine.transform_points(points)

        expected = np.array([[1, 1]])  # 2*0.5=1, 4*0.25=1
        np.testing.assert_array_almost_equal(transformed, expected)

    def test_rotation_transformation_2d(self) -> None:
        """Test 2D rotation transformation."""
        # 90 degree counter-clockwise rotation
        angle = np.pi / 2
        cos_a, sin_a = np.cos(angle), np.sin(angle)
        matrix = np.array([[cos_a, -sin_a, 0], [sin_a, cos_a, 0], [0, 0, 1]])
        affine = Affine(matrix=matrix)

        points = np.array([[1, 0], [0, 1]])
        transformed = affine.transform_points(points)

        expected = np.array([[0, 1], [-1, 0]])
        np.testing.assert_array_almost_equal(transformed, expected, decimal=10)

    def test_combined_transformation_2d(self) -> None:
        """Test combined scaling, rotation, and translation."""
        # Scale by 2, rotate 90°, translate by (1, 2)
        matrix = np.array(
            [
                [0, -0.5, 1],  # cos(90°)=0, -sin(90°)=-1, scale=0.5 (inverse)
                [0.5, 0, 2],  # sin(90°)=1, cos(90°)=0, scale=0.5 (inverse)
                [0, 0, 1],
            ]
        )
        affine = Affine(matrix=matrix)

        points = np.array([[2, 0]])
        transformed = affine.transform_points(points)

        # Expected: scale 2*0.5=1, rotate (1,0)->(-0,1), translate (0,1)+(1,2)=(1,3)
        expected = np.array([[1, 3]])
        np.testing.assert_array_almost_equal(transformed, expected)

    def test_3d_transformation(self) -> None:
        """Test 3D transformation."""
        matrix = np.array([[2, 0, 0, 1], [0, 2, 0, 2], [0, 0, 2, 3], [0, 0, 0, 1]])
        affine = Affine(matrix=matrix)

        points = np.array([[1, 1, 1]])
        transformed = affine.transform_points(points)

        expected = np.array([[3, 4, 5]])  # [2*1+1, 2*1+2, 2*1+3]
        np.testing.assert_array_almost_equal(transformed, expected)

    def test_batch_point_transformation(self) -> None:
        """Test transformation of multiple points."""
        matrix = np.array([[1, 0, 1], [0, 1, 1], [0, 0, 1]])
        affine = Affine(matrix=matrix)

        points = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
        transformed = affine.transform_points(points)

        expected = np.array([[1, 1], [2, 1], [1, 2], [2, 2]])
        np.testing.assert_array_almost_equal(transformed, expected)

    def test_multidimensional_point_arrays(self) -> None:
        """Test transformation of multidimensional point arrays."""
        matrix = np.array([[1, 0, 1], [0, 1, 2], [0, 0, 1]])
        affine = Affine(matrix=matrix)

        # Test 3D array of points (2, 3, 2) - 2x3 grid of 2D points
        points = np.array([[[0, 0], [1, 0], [2, 0]], [[0, 1], [1, 1], [2, 1]]])
        transformed = affine.transform_points(points)

        expected = np.array([[[1, 2], [2, 2], [3, 2]], [[1, 3], [2, 3], [3, 3]]])
        np.testing.assert_array_almost_equal(transformed, expected)

        # Verify shape is preserved
        assert transformed.shape == points.shape

    def test_callable_interface(self) -> None:
        """Test that Affine can be called directly."""
        matrix = np.array([[1, 0, 5], [0, 1, 10], [0, 0, 1]])
        affine = Affine(matrix=matrix)

        points = np.array([[0, 0]])

        # Both interfaces should give same result
        result1 = affine.transform_points(points)
        result2 = affine(points)

        np.testing.assert_array_equal(result1, result2)

    def test_invalid_point_dimensions(self) -> None:
        """Test error on mismatched point dimensions."""
        matrix = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        affine = Affine(matrix=matrix)  # 2D transformation

        # 3D points should fail
        points_3d = np.array([[1, 2, 3]])
        with pytest.raises(ValueError, match="Points last dimension 3 doesn't match"):
            affine.transform_points(points_3d)

        # 1D points should fail
        points_1d = np.array([[1]])
        with pytest.raises(ValueError, match="Points last dimension 1 doesn't match"):
            affine.transform_points(points_1d)


class TestFromMatrixOffset:
    """Test the from_matrix_offset static method."""

    def test_basic_matrix_offset(self) -> None:
        """Test basic matrix and offset conversion."""
        linear_matrix = np.array([[2, 1], [0, 3]])
        offset = np.array([5, 10])

        affine = Affine.from_matrix_offset(linear_matrix, offset)

        expected_matrix = np.array([[2, 1, 5], [0, 3, 10], [0, 0, 1]])
        np.testing.assert_array_equal(affine.matrix, expected_matrix)
        assert affine.ndim == 2

    def test_scalar_offset(self) -> None:
        """Test scalar offset (broadcasted to all dimensions)."""
        linear_matrix = np.eye(2)
        offset = 5.0

        affine = Affine.from_matrix_offset(linear_matrix, offset)

        expected_matrix = np.array([[1, 0, 5], [0, 1, 5], [0, 0, 1]])
        np.testing.assert_array_equal(affine.matrix, expected_matrix)

    def test_zero_offset(self) -> None:
        """Test with zero offset."""
        linear_matrix = np.array([[2, 1], [0, 3]])

        affine = Affine.from_matrix_offset(linear_matrix, 0.0)

        expected_matrix = np.array([[2, 1, 0], [0, 3, 0], [0, 0, 1]])
        np.testing.assert_array_equal(affine.matrix, expected_matrix)

    def test_3d_matrix_offset(self) -> None:
        """Test 3D matrix and offset."""
        linear_matrix = np.diag([2, 3, 4])
        offset = np.array([1, 2, 3])

        affine = Affine.from_matrix_offset(linear_matrix, offset)

        expected_matrix = np.array([[2, 0, 0, 1], [0, 3, 0, 2], [0, 0, 4, 3], [0, 0, 0, 1]])
        np.testing.assert_array_equal(affine.matrix, expected_matrix)
        assert affine.ndim == 3

    def test_list_inputs(self) -> None:
        """Test with list inputs instead of numpy arrays."""
        linear_matrix = [[1, 0], [0, 1]]
        offset = [5, 10]

        affine = Affine.from_matrix_offset(linear_matrix, offset)

        expected_matrix = np.array([[1, 0, 5], [0, 1, 10], [0, 0, 1]])
        np.testing.assert_array_equal(affine.matrix, expected_matrix)

    def test_invalid_matrix_shape(self) -> None:
        """Test error on invalid matrix shapes."""
        # Non-square matrix
        with pytest.raises(ValueError, match="Matrix must be square 2D array"):
            Affine.from_matrix_offset(np.zeros((2, 3)), 0)

        # 1D matrix
        with pytest.raises(ValueError, match="Matrix must be square 2D array"):
            Affine.from_matrix_offset(np.array([1, 2]), 0)

        # 3D matrix
        with pytest.raises(ValueError, match="Matrix must be square 2D array"):
            Affine.from_matrix_offset(np.zeros((2, 2, 2)), 0)

    def test_invalid_offset_shape(self) -> None:
        """Test error on invalid offset shapes."""
        linear_matrix = np.eye(2)

        # Wrong offset length
        with pytest.raises(ValueError, match="Offset length 3 doesn't match matrix size 2"):
            Affine.from_matrix_offset(linear_matrix, [1, 2, 3])

        # 2D offset
        with pytest.raises(ValueError, match="Offset must be scalar or 1D"):
            Affine.from_matrix_offset(linear_matrix, [[1, 2]])

    def test_functionality_equivalence(self) -> None:
        """Test that from_matrix_offset produces equivalent transformations."""
        linear_matrix = np.array([[2, 1], [0, 2]])
        offset = np.array([3, 4])

        affine = Affine.from_matrix_offset(linear_matrix, offset)

        # Test point transformation
        points = np.array([[1, 1]])
        transformed = affine.transform_points(points)

        # Manual calculation: [2*1 + 1*1 + 3, 0*1 + 2*1 + 4] = [6, 6]
        expected = np.array([[6, 6]])
        np.testing.assert_array_almost_equal(transformed, expected)

        # Verify properties
        np.testing.assert_array_equal(affine.linear_matrix, linear_matrix)
        np.testing.assert_array_equal(affine.offset, offset)
