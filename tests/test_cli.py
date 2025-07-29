import pytest
from typer.testing import CliRunner

import geff
from geff._cli import app
from geff.metadata_schema import GeffMetadata
from geff.testing.data import create_simple_temporal_geff

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
