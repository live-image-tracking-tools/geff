import sys

import pytest
import zarr

import geff._cli as cli
from geff.metadata_schema import GeffMetadata


def run_cli_with_args(args, monkeypatch):
    """Helper to run main() with sys.argv patched."""
    monkeypatch.setattr(sys, "argv", ["geff", *args])
    cli.main()


def test_validate_command_prints_valid(capsys, monkeypatch, path_w_expected_graph_props):
    """Test that the validate command prints the expected output."""
    path, graph_props = path_w_expected_graph_props(
        "int8", {"position": "double"}, {"score": "float64", "color": "uint8"}, True
    )
    run_cli_with_args(["validate", str(path)], monkeypatch)
    captured = capsys.readouterr()
    assert captured.out == f"{path} is valid\n"


def test_info_command_prints_metadata(capsys, monkeypatch, path_w_expected_graph_props):
    path, graph_props = path_w_expected_graph_props(
        "int8", {"position": "double"}, {"score": "float64", "color": "uint8"}, True
    )
    run_cli_with_args(["info", str(path)], monkeypatch)
    captured = capsys.readouterr()
    metadata = GeffMetadata.read(zarr.open(path, mode="r"))
    assert captured.out == metadata.model_dump_json(indent=2) + "\n"


def test_main_invalid_command(monkeypatch):
    with pytest.raises(SystemExit):
        run_cli_with_args([], monkeypatch)
