import re

import pydantic
import pytest
import zarr

from geff.metadata_schema import Axis, GeffMetadata, _get_versions_regex, write_metadata_schema


class TestVersionRegex:
    def test_get_versions_regex_simple(self):
        version_str = "0.0.1-a"
        versions = ["0.0"]
        regex = _get_versions_regex(versions)
        assert re.match(regex, version_str) is not None

    def test_get_versions_regex_complex(self):
        version_str = "0.1.1-a"
        versions = ["0.0", "0.1"]
        regex = _get_versions_regex(versions)
        assert re.match(regex, version_str) is not None

    def test_invalid_version_regex(self):
        version_str = "v1.0.1-a"
        versions = ["0.0", "0.1"]
        regex = _get_versions_regex(versions)
        assert re.match(regex, version_str) is None

    def test_invalid_prefix_regex(self):
        version_str = "9810.0.1"
        versions = ["0.0", "0.1"]
        regex = _get_versions_regex(versions)
        assert re.match(regex, version_str) is None


class TestMetadataModel:
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


def test_write_schema(tmp_path):
    schema_path = tmp_path / "schema.json"
    write_metadata_schema(schema_path)
    assert schema_path.is_file()
    assert schema_path.stat().st_size > 0
