from geff.metadata_schema import SUPPORTED_VERSIONS, _get_versions_regex, MetadataModel, write_schema
import re

def test_version_loading():
    assert SUPPORTED_VERSIONS == ["v0.0"]

def test_get_versions_regex_simple():
    version_str = "v0.0.1-a"
    versions = ["v0.0"]
    regex = _get_versions_regex(versions)
    assert re.match(regex, version_str) is not None

def test_get_versions_regex_simple():
    version_str = "v0.1.1-a"
    versions = ["v0.0", "v0.1"]
    regex = _get_versions_regex(versions)
    print(regex)
    assert re.match(regex, version_str) is not None

def test_invalid_version_regex():
    version_str = "v1.0.1-a"
    versions = ["v0.0", "v0.1"]
    regex = _get_versions_regex(versions)
    assert re.match(regex, version_str) is None

def test_invalid_prefix_regex():
    version_str = "981v0.0.1"
    versions = ["v0.0", "v0.1"]
    regex = _get_versions_regex(versions)
    assert re.match(regex, version_str) is None