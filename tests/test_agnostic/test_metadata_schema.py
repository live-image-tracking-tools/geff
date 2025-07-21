import re

import pydantic
import pytest
import zarr

from geff.metadata_schema import VERSION_PATTERN, Axis, GeffMetadata, write_metadata_schema
from geff.shapes import Ellipsoid, Sphere


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


# class TestShape:
#     def test_valid(self):
#         # Minial fields for each type
#         Shape(name="radius", type="sphere")
#         Shape(name="covariance2d", type="ellipsoid")
#         Shape(name="covariance3d", type="ellipsoid")

#     def test_no_name(self):
#         with pytest.raises(pydantic.ValidationError):
#             Shape(type="sphere")

#     def test_no_type(self):
#         with pytest.raises(pydantic.ValidationError):
#             Shape(name="radius")

#     def test_bad_type(self):
#         with pytest.warns(UserWarning, match=r"Type .* not in valid types"):
#             Shape(name="test", type="other")


class TestSphere:
    def test_valid(self):
        Sphere(name="radius")

    # def test_invalid_radius(self):
    #     with pytest.raises(ValueError, match=r"Radius must be positive"):
    #         Sphere(name="radius", radius=-1)

    #     with pytest.raises(ValueError, match=r"Radius must be positive"):
    #         Sphere(name="radius", radius=0)


class TestEllipsoid:
    def test_valid(self):
        Ellipsoid(name="covariance2d")

    # def test_invalid_covariance(self):
    #     # Not a numpy array
    #     with pytest.raises(TypeError, match=r"Covariance must be a numpy array"):
    #         Ellipsoid(name="covariance2d", covariance=np.array([[1, 0], [0, 1]]))

    #     # Not square
    #     with pytest.raises(ValueError, match=r"Covariance must be a square matrix"):
    #         Ellipsoid(name="covariance2d", covariance=np.array([[1, 0], [0, 1], [0, 0]]))

    #     # Not symmetric
    #     with pytest.raises(ValueError, match=r"Covariance matrix must be symmetric"):
    #         Ellipsoid(name="covariance2d", covariance=np.array([[1, 2], [3, 4]]))

    #     # Not positive-semidefinite
    #     with pytest.raises(ValueError, match=r"Covariance matrix must be positive-semidefinite"):
    #         Ellipsoid(name="covariance2d", covariance=np.array([[1, 2], [2, -1]]))


def test_write_schema(tmp_path):
    schema_path = tmp_path / "schema.json"
    write_metadata_schema(schema_path)
    assert schema_path.is_file()
    assert schema_path.stat().st_size > 0
