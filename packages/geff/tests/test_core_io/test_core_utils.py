import os
from pathlib import Path

import numpy as np
import pytest
import zarr
import zarr.storage

from geff import _path
from geff.core_io._base_write import write_arrays
from geff.core_io._utils import (
    _detect_zarr_spec_version,
    _infer_int_dtype,
    check_for_geff,
    construct_props,
    default_for_value,
    delete_geff,
    open_storelike,
    setup_zarr_group,
)
from geff.testing.data import create_simple_2d_geff


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        # Python native types
        (True, False),
        (False, False),
        (1, 0),
        (3.14, 0.0),
        ("hello", ""),
        # numpy scalar types (preserves dtype)
        (np.bool_(True), np.bool_(False)),
        (np.bool_(False), np.bool_(False)),
        (np.int64(5), np.int64(0)),
        (np.int32(5), np.int32(0)),
        (np.int16(5), np.int16(0)),
        (np.uint8(5), np.uint8(0)),
        (np.float64(2.5), np.float64(0)),
        (np.float32(2.5), np.float32(0)),
        # fallback: returns value itself
        ([1, 2, 3], [1, 2, 3]),
    ],
)
def test_default_for_value(value, expected):
    result = default_for_value(value)
    assert result == expected
    assert type(result) is type(expected)


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


class Test_infer_int_dtype:
    def test_small_unsigned(self):
        values = np.array([0, 1, 255])
        assert _infer_int_dtype(values) == np.dtype(np.uint8)

    def test_uint16(self):
        values = np.array([0, 256])
        assert _infer_int_dtype(values) == np.dtype(np.uint16)

    def test_uint32(self):
        values = np.array([0, 2**16])
        assert _infer_int_dtype(values) == np.dtype(np.uint32)

    def test_uint64(self):
        values = np.array([0, 2**32])
        assert _infer_int_dtype(values) == np.dtype(np.uint64)

    def test_negative_int8(self):
        values = np.array([-1, 0, 127])
        assert _infer_int_dtype(values) == np.dtype(np.int8)

    def test_negative_int16(self):
        values = np.array([-129, 0])
        assert _infer_int_dtype(values) == np.dtype(np.int16)

    def test_negative_int32(self):
        values = np.array([-(2**15) - 1, 0])
        assert _infer_int_dtype(values) == np.dtype(np.int32)

    def test_negative_int64(self):
        values = np.array([-(2**31) - 1, 0])
        assert _infer_int_dtype(values) == np.dtype(np.int64)


class Test_construct_props:
    @pytest.mark.parametrize(
        ("values", "expected_values", "expected_missing", "expected_dtype"),
        [
            # Python native types
            ([True, None, False], [True, False, False], [False, True, False], np.bool_),
            ([1, None, 3], [1, 0, 3], [False, True, False], np.uint8),
            ([1.5, None, 3.5], [1.5, 0, 3.5], [False, True, False], np.float64),
            (["a", None, "c"], ["a", "", "c"], [False, True, False], np.dtype("<U1")),
            ([1, 2, 3], [1, 2, 3], None, np.uint8),
            ([True, False, True], [True, False, True], None, np.bool_),
            # numpy scalar types (e.g. from pandas iteration)
            (
                [np.bool_(True), None, np.bool_(False)],
                [True, False, False],
                [False, True, False],
                np.bool_,
            ),
            ([np.int64(1), None, np.int64(3)], [1, 0, 3], [False, True, False], np.uint8),
            (
                [np.float32(1.5), None, np.float32(3.5)],
                [1.5, 0, 3.5],
                [False, True, False],
                np.float32,
            ),
        ],
    )
    def test_values_and_missing(self, values, expected_values, expected_missing, expected_dtype):
        result = construct_props(values)
        np.testing.assert_array_equal(result["values"], np.array(expected_values))
        assert result["values"].dtype == expected_dtype
        if expected_missing is None:
            assert result["missing"] is None
        else:
            np.testing.assert_array_equal(result["missing"], np.array(expected_missing, dtype=bool))

    def test_all_none(self):
        with pytest.warns(UserWarning, match="All values are None"):
            result = construct_props([None, None, None])
        np.testing.assert_array_equal(result["values"], np.array([0, 0, 0]))
        np.testing.assert_array_equal(result["missing"], np.array([True, True, True]))


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
            UserWarning,
            match=r"Found non-geff members in zarr. Exiting without deleting root zarr.",
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


class Test_check_for_geff:
    def test_path(self, tmp_path):
        geff_path = tmp_path / "test.geff"
        # does not exist
        assert check_for_geff(geff_path) is False
        # exists
        os.mkdir(geff_path)
        assert check_for_geff(geff_path) is True

    def test_str(self, tmp_path):
        geff_path = str(tmp_path / "test.geff")
        # does not exist
        assert check_for_geff(geff_path) is False
        # exists
        os.mkdir(geff_path)
        assert check_for_geff(geff_path) is True

    def test_Store(self):
        store = zarr.storage.MemoryStore()
        # does not exist
        assert check_for_geff(store) is False
        # exists
        root = zarr.open(store)
        root.attrs["geff"] = "metadata"
        assert check_for_geff(store) is True
