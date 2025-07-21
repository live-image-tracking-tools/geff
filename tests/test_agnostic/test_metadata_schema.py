import re

import numpy as np
import pydantic
import pytest
import zarr

from geff.affine import Affine
from geff.metadata_schema import VERSION_PATTERN, Axis, GeffMetadata, write_metadata_schema


class TestMetadataModel:
    def test_version_pattern(self):
        # Valid versions
        valid_versions = [
            "1.0",
            "0.1.0",
            "1.0.0.dev1",
            "2.3.4+local",
            "3.4.5.dev6+g61d5f18",
            "10.20.30",
        ]
        for version in valid_versions:
            assert re.fullmatch(VERSION_PATTERN, version)

        # Invalid versions
        invalid_versions = [
            "1.0.0.dev",  # Incomplete dev version
            "1.0.0+local+",  # Extra '+' at the end
            "abc.def",  # Non-numeric version
        ]
        for version in invalid_versions:
            assert not re.fullmatch(VERSION_PATTERN, version)

    def test_valid_init(self):
        # Minimal required fields
        model = GeffMetadata(geff_version="0.0.1", directed=True)
        assert model.geff_version == "0.0.1"
        assert model.axes is None

        # Complete metadata
        model = GeffMetadata(geff_version="0.0.1", directed=True, axes=[{"name": "test"}])
        assert len(model.axes) == 1

        # Multiple axes
        model = GeffMetadata(
            geff_version="0.0.1",
            directed=True,
            axes=[
                {"name": "test"},
                {"name": "complete", "type": "space", "unit": "micrometer", "min": 0, "max": 10},
            ],
        )
        assert len(model.axes) == 2

    def test_duplicate_axes_names(self):
        # duplicate names not allowed
        with pytest.raises(ValueError, match=r"Duplicate axes names found in"):
            GeffMetadata(
                geff_version="0.0.1", directed=True, axes=[{"name": "test"}, {"name": "test"}]
            )

    def test_invalid_version(self):
        with pytest.raises(pydantic.ValidationError, match="String should match pattern"):
            GeffMetadata(geff_version="aljkdf", directed=True)

    def test_extra_attrs(self):
        # Should not fail
        GeffMetadata(
            geff_version="0.0.1",
            directed=True,
            axes=[
                {"name": "test"},
                {"name": "complete", "type": "space", "unit": "micrometer", "min": 0, "max": 10},
            ],
            extra=True,
        )

    def test_read_write(self, tmp_path):
        meta = GeffMetadata(
            geff_version="0.0.1",
            directed=True,
            axes=[
                {"name": "test"},
                {"name": "complete", "type": "space", "unit": "micrometer", "min": 0, "max": 10},
            ],
            extra=True,
        )
        zpath = tmp_path / "test.zarr"
        group = zarr.open(zpath, mode="a")
        meta.write(group)
        compare = GeffMetadata.read(group)
        assert compare == meta

        meta.directed = False
        meta.write(zpath)
        compare = GeffMetadata.read(zpath)
        assert compare == meta

    def test_model_mutation(self):
        """Test that invalid model mutations raise errors."""
        meta = GeffMetadata(
            geff_version="0.0.1",
            directed=True,
            axes=[
                {"name": "test"},
                {"name": "complete", "type": "space", "unit": "micrometer", "min": 0, "max": 10},
            ],
        )

        meta.directed = False  # fine...

        with pytest.raises(pydantic.ValidationError):
            meta.geff_version = "abcde"


class TestAxis:
    def test_valid(self):
        # minimal fields
        Axis(name="property")

        # All fields
        Axis(name="property", type="space", unit="micrometer", min=0, max=10)

    def test_no_name(self):
        # name is the only required field
        with pytest.raises(pydantic.ValidationError):
            Axis(type="space")

    def test_bad_type(self):
        with pytest.warns(UserWarning, match=r"Type .* not in valid types"):
            Axis(name="test", type="other")

    def test_invalid_units(self):
        # Spatial
        with pytest.warns(UserWarning, match=r"Spatial unit .* not in valid"):
            Axis(name="test", type="space", unit="bad unit")

        # Temporal
        with pytest.warns(UserWarning, match=r"Temporal unit .* not in valid"):
            Axis(name="test", type="time", unit="bad unit")

        # Don't check units if we don't specify type
        Axis(name="test", unit="not checked")

    def test_min_max(self):
        # Min no max
        with pytest.raises(ValueError, match=r"Min and max must both be None or neither"):
            Axis(name="test", min=0)

        # Max no min
        with pytest.raises(ValueError, match=r"Min and max must both be None or neither"):
            Axis(name="test", max=0)

        # Min > max
        with pytest.raises(ValueError, match=r"Min .* is greater than max .*"):
            Axis(name="test", min=0, max=-10)


class TestAffineTransformation:
    """Comprehensive tests for Affine transformation functionality."""

    def test_basic_affine_creation(self):
        """Test basic creation of Affine transformations."""
        # 2D identity matrix
        identity_2d = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        affine = Affine(matrix=identity_2d)
        assert affine.ndim == 2
        np.testing.assert_array_equal(affine.matrix, identity_2d)

        # 3D identity matrix
        identity_3d = np.array(
            [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]
        )
        affine_3d = Affine(matrix=identity_3d)
        assert affine_3d.ndim == 3

    def test_affine_validation_errors(self):
        """Test that invalid matrices raise appropriate validation errors."""
        # Non-square matrix
        with pytest.raises(ValueError, match="Matrix must be square"):
            Affine(matrix=np.array([[1, 0], [0, 1], [0, 0]]))

        # Wrong bottom row
        bad_matrix = np.array(
            [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [1.0, 0.0, 1.0],  # Should be [0, 0, 1]
            ]
        )
        with pytest.raises(ValueError, match="Bottom row of homogeneous matrix must be"):
            Affine(matrix=bad_matrix)

        # Too small matrix
        with pytest.raises(ValueError, match="Matrix must be at least 2x2"):
            Affine(matrix=np.array([[1.0]]))

        # Non-2D matrix
        with pytest.raises(ValueError, match="Matrix must be 2D"):
            Affine(matrix=np.array([1, 2, 3]))

    def test_affine_properties(self):
        """Test linear matrix and offset extraction."""
        # Create a transformation with rotation and translation
        matrix = np.array(
            [
                [0.0, -1.0, 5.0],  # 90° rotation + translation
                [1.0, 0.0, 3.0],
                [0.0, 0.0, 1.0],
            ]
        )
        affine = Affine(matrix=matrix)

        # Check linear part
        expected_linear = np.array([[0.0, -1.0], [1.0, 0.0]])
        np.testing.assert_array_equal(affine.linear_matrix, expected_linear)

        # Check offset
        expected_offset = np.array([5.0, 3.0])
        np.testing.assert_array_equal(affine.offset, expected_offset)

    def test_point_transformation(self):
        """Test point transformation functionality."""
        # Simple translation
        translation_matrix = np.array([[1.0, 0.0, 2.0], [0.0, 1.0, 3.0], [0.0, 0.0, 1.0]])
        affine = Affine(matrix=translation_matrix)

        # Single point
        point = np.array([1.0, 1.0])
        transformed = affine.transform_points(point)
        expected = np.array([3.0, 4.0])  # [1+2, 1+3]
        np.testing.assert_array_almost_equal(transformed, expected)

        # Multiple points
        points = np.array([[0.0, 0.0], [1.0, 1.0], [2.0, 2.0]])
        transformed = affine.transform_points(points)
        expected = np.array([[2.0, 3.0], [3.0, 4.0], [4.0, 5.0]])
        np.testing.assert_array_almost_equal(transformed, expected)

        # Test callable interface
        transformed_callable = affine(points)
        np.testing.assert_array_almost_equal(transformed_callable, expected)

        # Test with higher dimensional arrays
        points_3d = np.array([[[0.0, 0.0], [1.0, 1.0]], [[2.0, 2.0], [3.0, 3.0]]])
        transformed_3d = affine.transform_points(points_3d)
        expected_3d = np.array([[[2.0, 3.0], [3.0, 4.0]], [[4.0, 5.0], [5.0, 6.0]]])
        np.testing.assert_array_almost_equal(transformed_3d, expected_3d)

    def test_inverse_transformation(self):
        """Test inverse transformation functionality."""
        # Simple translation
        affine_matrix = np.array([[1.2, 0.8, 2.0], [0.3, 1.6, 3.0], [0.0, 0.0, 1.0]])
        affine = Affine(matrix=affine_matrix)
        from numpy.linalg import inv

        inv_affine_matrix = inv(affine.numpy())
        inv_affine = Affine(matrix=inv_affine_matrix)
        np.testing.assert_array_almost_equal(inv_affine.numpy(), inv(affine_matrix))

        points = np.array([[1.0, 1.0], [2.0, 2.0], [3.0, 3.0]])
        transformed_points = affine.transform_points(points)
        inverse_transformed_points = inv_affine.transform_points(transformed_points)
        np.testing.assert_array_almost_equal(inverse_transformed_points, points)

    def test_from_matrix_offset_factory(self):
        """Test creation from separate matrix and offset."""
        # 2D case with matrix and offset
        linear_matrix = np.array([[2.0, 0.0], [0.0, 0.5]])
        offset = np.array([1.0, -2.0])
        affine = Affine.from_matrix_offset(linear_matrix, offset)

        expected_matrix = np.array([[2.0, 0.0, 1.0], [0.0, 0.5, -2.0], [0.0, 0.0, 1.0]])
        np.testing.assert_array_almost_equal(affine.matrix, expected_matrix)

        # Scalar offset
        affine_scalar = Affine.from_matrix_offset(linear_matrix, 5.0)
        expected_scalar = np.array([[2.0, 0.0, 5.0], [0.0, 0.5, 5.0], [0.0, 0.0, 1.0]])
        np.testing.assert_array_almost_equal(affine_scalar.matrix, expected_scalar)

        # No offset (default to 0)
        affine_no_offset = Affine.from_matrix_offset(linear_matrix)
        expected_no_offset = np.array([[2.0, 0.0, 0.0], [0.0, 0.5, 0.0], [0.0, 0.0, 1.0]])
        np.testing.assert_array_almost_equal(affine_no_offset.matrix, expected_no_offset)

    def test_from_matrix_offset_validation(self):
        """Test validation in from_matrix_offset factory method."""
        # Non-square matrix
        with pytest.raises(ValueError, match="Matrix must be square 2D array"):
            Affine.from_matrix_offset([[1, 0, 0], [0, 1, 0]])

        # Wrong offset dimensions
        matrix = np.eye(2)
        with pytest.raises(ValueError, match="Offset length .* doesn't match matrix size"):
            Affine.from_matrix_offset(matrix, [1, 2, 3])  # 3D offset for 2D matrix

        # Multi-dimensional offset
        with pytest.raises(ValueError, match="Offset must be scalar or 1D"):
            Affine.from_matrix_offset(matrix, [[1, 2], [3, 4]])

    def test_affine_integration_with_metadata(self):
        """Test integration of Affine with GeffMetadata."""
        # Create a simple affine transformation
        affine = Affine.from_matrix_offset([[1.5, 0.0], [0.0, 1.5]], [10.0, 20.0])

        # Create metadata with affine transformation
        metadata = GeffMetadata(
            geff_version="0.1.0",
            directed=True,
            axes=[
                {"name": "x", "type": "space", "unit": "micrometer"},
                {"name": "y", "type": "space", "unit": "micrometer"},
            ],
            affine=affine,
        )

        # Verify the affine is properly stored
        assert metadata.affine is not None
        assert metadata.affine.ndim == 2
        np.testing.assert_array_almost_equal(
            metadata.affine.linear_matrix, [[1.5, 0.0], [0.0, 1.5]]
        )
        np.testing.assert_array_almost_equal(metadata.affine.offset, [10.0, 20.0])

    def test_affine_serialization_with_metadata(self, tmp_path):
        """Test that Affine transformations can be serialized and deserialized with metadata."""
        # Create metadata with affine transformation
        affine = Affine.from_matrix_offset(
            [[2.0, 0.5], [-0.5, 2.0]],  # Scaling with rotation/shear
            [100.0, -50.0],
        )

        original_metadata = GeffMetadata(
            geff_version="0.1.0",
            directed=False,
            axes=[
                {"name": "x", "type": "space", "unit": "micrometer"},
                {"name": "y", "type": "space", "unit": "micrometer"},
            ],
            affine=affine,
        )

        # Write and read back
        zpath = tmp_path / "test_affine.zarr"
        group = zarr.open(zpath, mode="a")
        original_metadata.write(group)
        loaded_metadata = GeffMetadata.read(group)

        # Verify everything matches
        assert loaded_metadata == original_metadata
        assert loaded_metadata.affine is not None
        np.testing.assert_array_almost_equal(
            loaded_metadata.affine.matrix, original_metadata.affine.matrix
        )


def test_write_schema(tmp_path):
    schema_path = tmp_path / "schema.json"
    write_metadata_schema(schema_path)
    assert schema_path.is_file()
    assert schema_path.stat().st_size > 0
