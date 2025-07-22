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

    def test_related_objects(self):
        # Valid related objects
        model = GeffMetadata(
            geff_version="0.0.1",
            directed=True,
            related_objects=[
                {"type": "labels", "path": "segmentation/", "label_prop": "seg_id"},
                {"type": "image", "path": "raw/"},
            ],
        )
        assert len(model.related_objects) == 2

        # Related object type
        with pytest.warns(
            UserWarning, match=r".* might not be recognized by reader applications.*"
        ):
            GeffMetadata(
                geff_version="0.0.1",
                directed=True,
                related_objects=[{"type": "invalid_type", "path": "invalid/"}],
            )

        # Invalid combination of type and label_prop
        with pytest.raises(
            pydantic.ValidationError, match=".*label_prop .+ is only valid for type 'labels'.*"
        ):
            GeffMetadata(
                geff_version="0.0.1",
                directed=True,
                related_objects=[{"type": "image", "path": "raw/", "label_prop": "seg_id"}],
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
    """Comprehensive tests for Affine transformation functionality with metadata."""

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

    def test_unmatched_ndim(self):
        """Test that an error is raised if the affine matrix and axes have different dimensions."""
        with pytest.raises(
            ValueError, match="Affine transformation matrix must have 3 dimensions, got 2"
        ):
            # Homogeneous matrix of a 2D affine transformation
            matrix = np.diag([1.0, 1.0, 1.0])
            affine = Affine(matrix=matrix)
            GeffMetadata(
                geff_version="0.1.0",
                directed=True,
                axes=[
                    {"name": "x", "type": "space", "unit": "micrometer"},
                    {"name": "y", "type": "space", "unit": "micrometer"},
                    {"name": "z", "type": "space", "unit": "micrometer"},
                ],
                affine=affine,
            )

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
