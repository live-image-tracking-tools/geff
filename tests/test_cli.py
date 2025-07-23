import sys

import pytest
import zarr

import geff
import geff._cli as cli
from geff.metadata_schema import GeffMetadata
from geff.testing.data import create_simple_temporal_geff


@pytest.fixture
def example_geff_path(tmp_path):
    file_path = str(tmp_path / "test.geff")
    store, graph_props = create_simple_temporal_geff()
    # zarr.group(store).copy_store(zarr.open(file_path, mode="w"))
    graph, metadata = geff.read_nx(store)
    geff.write_nx(graph, file_path, metadata=metadata)
    return file_path


def run_cli_with_args(args, monkeypatch):
    """Helper to run main() with sys.argv patched."""
    monkeypatch.setattr(sys, "argv", ["geff", *args])
    cli.main()


def test_validate_command_prints_valid(capsys, monkeypatch, example_geff_path):
    """Test that the validate command prints the expected output."""
    run_cli_with_args(["validate", example_geff_path], monkeypatch)
    captured = capsys.readouterr()
    assert captured.out == f"{example_geff_path} is valid\n"


def test_info_command_prints_metadata(capsys, monkeypatch, example_geff_path):
    run_cli_with_args(["info", example_geff_path], monkeypatch)
    captured = capsys.readouterr()
    metadata = GeffMetadata.read(zarr.open(example_geff_path, mode="r"))
    assert captured.out == metadata.model_dump_json(indent=2) + "\n"


def test_main_invalid_command(monkeypatch):
    with pytest.raises(SystemExit):
        run_cli_with_args([], monkeypatch)
