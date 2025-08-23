import warnings
from pathlib import Path

import pytest
import zarr

from geff.core_io._utils import _detect_zarr_spec_version, open_storelike, setup_zarr_group


class TestZarrVersionWarnings:
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

    @pytest.mark.skipif(
        zarr.__version__.startswith("2"), reason="zarr-python v2 cannot create zarr spec v3"
    )
    def test_detect_zarr_spec_version_v3(self, tmp_path: Path) -> None:
        """Test detection of zarr spec v3 files created explicitly."""
        zarr_path = tmp_path / "test_v3.zarr"

        # Create a zarr file explicitly using spec v3
        group = setup_zarr_group(str(zarr_path), zarr_format=3)
        group.create_array("test", shape=(10,), dtype=int)

        # Should detect as v3
        version = _detect_zarr_spec_version(str(zarr_path))
        assert version == 3

    @pytest.mark.skipif(
        not zarr.__version__.startswith("2"), reason="Only test zarr v2 warning with zarr-python v2"
    )
    def test_open_storelike_warns_for_v3_with_zarr_v2(self, tmp_path: Path) -> None:
        """Test that opening zarr spec v3 files with zarr python v2 produces a warning.

        Note: This test simulates a zarr v3 file since zarr-python v2 cannot create them.
        """
        zarr_path = tmp_path / "test_v3.zarr"

        # Simulate a zarr v3 file by creating the zarr.json indicator
        # (zarr-python v2 cannot create real zarr v3 files)
        zarr_path.mkdir()
        (zarr_path / "zarr.json").write_text('{"zarr_format": 3}')

        # Opening should produce a warning
        with pytest.warns(
            UserWarning, match="Attempting to open a zarr spec v3 file with zarr-python v2"
        ):
            # Create a minimal zarr structure that can be opened by zarr v2
            group = zarr.open_group(str(zarr_path), mode="w")
            group.attrs["test"] = "data"

            # Now test opening it with our warning function
            _ = open_storelike(str(zarr_path))

    @pytest.mark.skipif(
        not zarr.__version__.startswith("3"),
        reason="Only test zarr v3 behavior with zarr-python v3",
    )
    def test_open_storelike_no_warn_with_zarr_v3(self, tmp_path: Path) -> None:
        """Test that opening files with zarr python v3 does not produce zarr version warnings."""
        zarr_path = tmp_path / "test.zarr"

        # Create a zarr group
        group = zarr.open_group(str(zarr_path), mode="w")
        group.attrs["test"] = "data"

        # Opening should not produce a zarr version warning
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            _ = open_storelike(str(zarr_path))

            # Filter out any warnings that are about zarr version mismatch
            zarr_warnings = [
                warning
                for warning in w
                if "zarr spec v3 file with zarr-python v2" in str(warning.message)
            ]
            assert len(zarr_warnings) == 0

    @pytest.mark.skipif(
        not zarr.__version__.startswith("2"), reason="Only test zarr v2 warning with zarr-python v2"
    )
    def test_setup_zarr_group_warns_for_v3_format_with_zarr_v2(self, tmp_path: Path) -> None:
        """Test that requesting zarr format v3 with zarr python v2 produces a warning."""
        zarr_path = tmp_path / "test_write_v3.zarr"

        # Requesting zarr_format=3 with zarr python v2 should produce a warning
        with pytest.warns(UserWarning, match="Requesting zarr spec v3 with zarr-python v2"):
            _ = setup_zarr_group(str(zarr_path), zarr_format=3)

    @pytest.mark.skipif(
        not zarr.__version__.startswith("2"),
        reason="Only test zarr v2 behavior with zarr-python v2",
    )
    def test_setup_zarr_group_no_warn_for_v2_format_with_zarr_v2(self, tmp_path: Path) -> None:
        """Test that requesting zarr format v2 with zarr python v2 does not produce a warning."""
        zarr_path = tmp_path / "test_write_v2.zarr"

        # Requesting zarr_format=2 with zarr python v2 should not produce a warning
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            _ = setup_zarr_group(str(zarr_path), zarr_format=2)

            # Should not have any zarr version warnings
            zarr_warnings = [
                warning
                for warning in w
                if "zarr spec v3 with zarr-python v2" in str(warning.message)
            ]
            assert len(zarr_warnings) == 0

    @pytest.mark.skipif(
        not zarr.__version__.startswith("3"),
        reason="Only test zarr v3 behavior with zarr-python v3",
    )
    def test_setup_zarr_group_no_warn_with_zarr_v3(self, tmp_path: Path) -> None:
        """Test that using zarr python v3 does not produce zarr version warnings."""
        zarr_path = tmp_path / "test_write.zarr"

        # Using zarr python v3 should not produce warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            _ = setup_zarr_group(str(zarr_path), zarr_format=3)

            # Should not have any zarr version warnings
            zarr_warnings = [
                warning
                for warning in w
                if "zarr spec v3 with zarr-python v2" in str(warning.message)
            ]
            assert len(zarr_warnings) == 0

    def test_detect_zarr_spec_version_returns_none_for_invalid_path(self) -> None:
        """Test that _detect_zarr_spec_version returns None for invalid paths."""
        version = _detect_zarr_spec_version("/nonexistent/path")
        assert version is None
