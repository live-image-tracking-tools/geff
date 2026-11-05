from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from geff import GeffMetadata
from geff._cli import app
from geff.core_io._base_write import write_arrays
from geff.testing.data import create_simple_temporal_geff
from tests.test_convert.test_ctc import create_mock_data

runner = CliRunner()
TEST_DATA = Path(__file__).parent / "data"


@pytest.fixture
def example_geff_path(tmp_path: Path) -> str:
    file_path = str(tmp_path / "test.geff")
    _store, memory_geff = create_simple_temporal_geff()
    write_arrays(file_path, **memory_geff)
    return file_path


def test_validate_command_prints_valid(example_geff_path: str) -> None:
    """Test that the validate command prints the expected output."""
    result = runner.invoke(app, ["validate", example_geff_path])
    assert result.exit_code == 0


def test_info_command_prints_metadata(example_geff_path: str) -> None:
    result = runner.invoke(app, ["info", example_geff_path])
    metadata = GeffMetadata.read(example_geff_path)
    assert result.exit_code == 0
    assert result.output == metadata.model_dump_json(indent=2) + "\n"


def test_main_invalid_command() -> None:
    result = runner.invoke(app, ["invalid"])
    assert result.exit_code != 0


@pytest.mark.parametrize("is_gt", [True, False])
@pytest.mark.parametrize("tczyx", [True, False])
def test_convert_ctc(tmp_path: Path, is_gt: bool, tczyx: bool) -> None:
    ctc_path = create_mock_data(tmp_path, is_gt)
    zarr_path = tmp_path / "root.zarr"

    cmd_args = [
        "convert-ctc", str(ctc_path), str(ctc_path), str(zarr_path),
        "--label-name", "cells",
        "--pixel-size", "0.5", "--pixel-size", "0.5",
        "--pixel-unit", "micrometer",
        "--time-scale", "2.0", "--time-unit", "second",
    ]  # fmt: skip
    if tczyx:
        cmd_args.append("--tczyx")
    result = CliRunner().invoke(app, cmd_args)
    assert result.exit_code == 0, (
        f"{cmd_args} failed with exit code {result.exit_code} and message:\n{result.stdout}"
    )
    assert (zarr_path / "labels" / "cells" / "zarr.json").exists()
    assert (zarr_path / "tracks.geff").exists()


@pytest.mark.parametrize(
    ("args", "message"),
    [
        # (case-insensitive: Typer versions differ in how they name missing arguments)
        (["CTC"], "missing argument 'image_dir'"),
        (["CTC", "CTC"], "missing argument 'output_path'"),
        (["CTC", "CTC", "OUT", "--pixel-unit", "furlong"], "not a valid space unit"),
    ],
)
def test_convert_ctc_invalid_options(tmp_path: Path, args: list[str], message: str) -> None:
    ctc_path = create_mock_data(tmp_path, is_gt=True)
    subs = {"CTC": str(ctc_path), "OUT": str(tmp_path / "out")}
    result = runner.invoke(app, ["convert-ctc", *(subs.get(a, a) for a in args)])
    assert result.exit_code != 0
    assert message in result.output.lower()


@pytest.mark.parametrize(
    "other_arg", [None, "--discard-filtered-spots", "--discard-filtered-tracks", "--overwrite"]
)
def test_convert_trackmate_xml(tmp_path: Path, other_arg: str | None) -> None:
    geff_output = str(tmp_path / "test.geff")
    in_data = str(TEST_DATA / "FakeTracks.xml")

    cmd_args = ["convert-trackmate-xml", in_data, geff_output]
    if other_arg is not None:
        cmd_args.append(other_arg)

    with pytest.warns() as warning_list:
        result = CliRunner().invoke(app, cmd_args)
    warning_messages = [str(warning.message) for warning in warning_list]
    assert any("node properties were removed from the metadata" in msg for msg in warning_messages)
    assert any("edge property was removed from the metadata" in msg for msg in warning_messages)
    assert result.exit_code == 0, (
        f"{cmd_args} failed with exit code {result.exit_code} and message:\n{result.stdout}"
    )


def test_convert_to_csv(example_geff_path, tmp_path):
    out_path = tmp_path / "dataframe"
    result = CliRunner().invoke(app, ["convert-to-csv", str(example_geff_path), str(out_path)])
    assert result.exit_code == 0
