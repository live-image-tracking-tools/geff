import re

import pydantic
import pytest

from geff.metadata_schema import SUPPORTED_VERSIONS, GeffMetadata, _get_versions_regex


class TestVersionRegex:
    def test_version_loading(self):
        assert SUPPORTED_VERSIONS == ["v0.0"]

    def test_get_versions_regex_simple(self):
        version_str = "v0.0.1-a"
        versions = ["v0.0"]
        regex = _get_versions_regex(versions)
        assert re.match(regex, version_str) is not None

    def test_get_versions_regex_complex(self):
        version_str = "v0.1.1-a"
        versions = ["v0.0", "v0.1"]
        regex = _get_versions_regex(versions)
        assert re.match(regex, version_str) is not None

    def test_invalid_version_regex(self):
        version_str = "v1.0.1-a"
        versions = ["v0.0", "v0.1"]
        regex = _get_versions_regex(versions)
        assert re.match(regex, version_str) is None

    def test_invalid_prefix_regex(self):
        version_str = "981v0.0.1"
        versions = ["v0.0", "v0.1"]
        regex = _get_versions_regex(versions)
        assert re.match(regex, version_str) is None


class TestMetadataModel:
    def test_valid_init(self):
        model = GeffMetadata(
            geff_version="v0.0.1",
            directed=True,
            roi_min=[0, 0, 0],
            roi_max=[100, 100, 100],
            axis_names=["t", "y", "x"],
            axis_units=["min", "nm", "nm"],
        )
        assert model.geff_version == "v0.0.1"

        model = GeffMetadata(
            geff_version="v0.0.1",
            directed=True,
            roi_min=[0, 0, 0],
            roi_max=[100, 100, 100],
        )
        assert model.axis_names is None
        assert model.axis_units is None

    def test_invalid_version(self):
        with pytest.raises(pydantic.ValidationError, match="String should match pattern"):
            GeffMetadata(
                geff_version="aljkdf",
                directed=True,
                roi_min=[0, 0, 0],
                roi_max=[100, 100, 100],
                axis_names=["t", "y", "x"],
                axis_units=["min", "nm", "nm"],
            )

    def test_invalid_roi(self):
        with pytest.raises(ValueError, match="Roi min .* is greater than max .* in dimension 0"):
            GeffMetadata(
                geff_version="v0.0.1-a",
                directed=False,
                roi_min=[1000, 0, 0],
                roi_max=[100, 100, 100],
            )

    def test_invalid_axis_annotations(self):
        with pytest.raises(
            ValueError,
            match="Length of axis names (.*) does not match number of dimensions in roi (3)",
        ):
            GeffMetadata(
                geff_version="v0.0.1-a",
                directed=False,
                roi_min=[0, 0, 0],
                roi_max=[100, 100, 100],
                axis_names=["t", "y"],
                axis_units=["min", "nm", "nm"],
            )

        with pytest.raises(
            ValueError,
            match="Length of axis units (.*) does not match number of dimensions in roi (3)",
        ):
            GeffMetadata(
                geff_version="v0.0.1-a",
                directed=False,
                roi_min=[0, 0, 0],
                roi_max=[100, 100, 100],
                axis_names=["t", "y", "x"],
                axis_units=["nm", "nm"],
            )
