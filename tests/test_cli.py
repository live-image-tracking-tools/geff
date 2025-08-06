import pytest
from typer.testing import CliRunner

import geff
from geff._cli import app
from geff.metadata_schema import GeffMetadata
from geff.testing.data import create_simple_temporal_geff
from tests.test_interops.test_ctc import create_mock_data

runner = CliRunner()


@pytest.fixture
def example_geff_path(tmp_path):
    file_path = str(tmp_path / "test.geff")
    store, graph_props = create_simple_temporal_geff()
    # zarr.group(store).copy_store(zarr.open(file_path, mode="w"))
    graph, metadata = geff.read_nx(store)
    geff.write_nx(graph, file_path, metadata=metadata)
    return file_path


def test_validate_command_prints_valid(example_geff_path):
    """Test that the validate command prints the expected output."""
    result = runner.invoke(app, ["validate", example_geff_path])
    assert result.exit_code == 0
    assert f"{example_geff_path} is valid" in result.output


def test_info_command_prints_metadata(example_geff_path):
    result = runner.invoke(app, ["info", example_geff_path])
    metadata = GeffMetadata.read(example_geff_path)
    assert result.exit_code == 0
    assert result.output == metadata.model_dump_json(indent=2) + "\n"


def test_main_invalid_command():
    result = runner.invoke(app, ["invalid"])
    assert result.exit_code != 0


@pytest.mark.parametrize("is_gt", [True, False])
@pytest.mark.parametrize("tczyx", [True, False])
def test_convert_ctc(tmp_path, is_gt, tczyx):
    ctc_path = create_mock_data(tmp_path, is_gt)
    geff_path = ctc_path / "little.geff"
    segm_path = ctc_path / "segm.zarr"

    cmd_args = [
        "convert-ctc",
        str(ctc_path),
        str(geff_path),
        "--segm-path",
        str(segm_path),
        "--input-image-dir",
        str(ctc_path),
        "--output-image-path",
        str(tmp_path / "output_image.zarr"),
    ]
    if tczyx:
        cmd_args.append("--tczyx")
    result = CliRunner().invoke(app, cmd_args)
    assert result.exit_code == 0, (
        f"{cmd_args} failed with exit code {result.exit_code} and message:\n{result.stdout}"
    )


@pytest.mark.parametrize(
    "other_arg", [None, "--discard-filtered-spots", "--discard-filtered-tracks", "--overwrite"]
)
def test_convert_trackmate_xml(tmp_path, other_arg):
    geff_output = str(tmp_path / "test.geff")
    in_data = "tests/data/FakeTracks.xml"

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
