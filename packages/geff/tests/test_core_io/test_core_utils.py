import os
from pathlib import Path

import numpy as np
import pytest
import zarr

from geff import _path
from geff.core_io._base_write import write_arrays
from geff.core_io._utils import (
    _detect_zarr_spec_version,
    delete_geff,
    open_storelike,
    setup_zarr_group,
)
from geff.testing.data import create_simple_2d_geff


@pytest.mark.skipif(zarr.__version__.startswith("2"), reason="tests for zarr-python>=v3 only")
class TestZarrV3Warnings:
    """Test warnings for zarr version mismatches."""

    def test_detect_zarr_spec_version_v2(self, tmp_path: Path) -> None:
        """Test detection of zarr spec v2 files created explicitly."""
        zarr_path = tmp_path / "test_v2.zarr"

        # Create a zarr file explicitly using spec v2
        group = setup_zarr_group(str(zarr_path), zarr_format=2)
        group.create_array("test", shape=(10,), dtype=int)

        # Should detect as v2
        version = _detect_zarr_spec_version(str(zarr_path))
        assert version == 2

        # Should detect as v2
        version = _detect_zarr_spec_version(group.store)
        assert version == 2

    def test_detect_zarr_spec_version_v3(self, tmp_path: Path) -> None:
        """Test detection of zarr spec v3 files created explicitly."""
        zarr_path = tmp_path / "test_v3.zarr"

        # Create a zarr file explicitly using spec v3
        group = setup_zarr_group(str(zarr_path), zarr_format=3)
        group.create_array("test", shape=(10,), dtype=int)

        # Should detect as v3
        version = _detect_zarr_spec_version(str(zarr_path))
        assert version == 3

        # Should detect as v3
        version = _detect_zarr_spec_version(group.store)
        assert version == 3

    def test_open_storelike_warns_for_v3_with_zarr_v2(self, tmp_path: Path, monkeypatch) -> None:
        """Test that opening zarr spec v2 files with zarr python v2 produces a warning.

        Note: This test mocks that we're using zarr-python v2.
        """
        zarr_path = tmp_path / "test_v2.zarr"

        # Create a real zarr v2 file
        group = setup_zarr_group(str(zarr_path), zarr_format=3)
        group.create_array("test", shape=(10,), dtype=int)

        # Mock that we're using zarr-python v2
        monkeypatch.setattr(zarr, "__version__", "2.17.0")

        # Opening should produce a warning
        with pytest.warns(
            UserWarning, match="Attempting to open a zarr spec v3 file with zarr-python v2"
        ):
            open_storelike(str(zarr_path))


def test_detect_zarr_spec_version_returns_none_for_invalid_path():
    """Test that _detect_zarr_spec_version returns None for invalid paths."""
    version = _detect_zarr_spec_version("/nonexistent/path")
    assert version is None


@pytest.mark.skipif(not zarr.__version__.startswith("2"), reason="tests for zarr python v2 only")
class TestZarrV2Warnings:
    """Test warnings for zarr version mismatches."""

    def test_detect_zarr_spec_version_v2(self, tmp_path: Path) -> None:
        """Test detection of zarr spec v2 files created explicitly."""
        zarr_path = tmp_path / "test_v2.zarr"

        # Create a zarr file explicitly using spec v2
        group = setup_zarr_group(str(zarr_path), zarr_format=2)
        group.create_dataset("test", shape=(10,), dtype=int)

        # Should detect as v2
        version = _detect_zarr_spec_version(str(zarr_path))
        assert version == 2

    def test_warn_if_writing_zarr_format_3(self, tmp_path: Path):
        with pytest.warns(UserWarning, match="Requesting zarr spec v3 with zarr-python v2"):
            setup_zarr_group(tmp_path / "test.zarr", zarr_format=3)


class Test_delete_geff:
    def test_basic_path(self, tmp_path):
        _, mem_geff = create_simple_2d_geff()
        path = tmp_path / "test.geff"
        write_arrays(path, **mem_geff)
        assert os.path.exists(path)

        delete_geff(path)

        assert not os.path.exists(path)

    def test_extra_data(self, tmp_path):
        _, mem_geff = create_simple_2d_geff()
        path = tmp_path / "test.geff"
        write_arrays(path, **mem_geff, zarr_format=2)
        assert os.path.exists(path)
        # Test with extra data
        root = zarr.open(path, mode="a")
        root["other_data"] = np.zeros(shape=(10, 10))

        with pytest.raises(
            UserWarning, match="Found non-geff members in zarr. Exiting without deleting root zarr."
        ):
            delete_geff(path)
            root = zarr.open(path)
            assert _path.NODES not in root
            assert _path.EDGES not in root
            assert "geff" not in root.attrs

    def test_mem_store(self):
        store, _ = create_simple_2d_geff()

        with pytest.raises(
            UserWarning,
            match="Cannot delete root zarr directory, but geff contents have been deleted",
        ):
            delete_geff(store)
            root = zarr.open(store)
            assert "geff" not in root.attrs
