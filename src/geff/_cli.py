# /// script
# dependencies = [
#   "zarr>2,<4",
# ]
# ///

import argparse
import logging
import sys

import zarr

from . import utils
from .metadata_schema import GeffMetadata

logging.basicConfig(stream=sys.stderr, level=logging.WARNING, format="%(levelname)s: %(message)s")
logging.captureWarnings(True)  # Capture warnings and log them


def validate() -> None:
    """Command-line interface for validating geff files."""
    parser = argparse.ArgumentParser(description="Validate a GEFF file")
    parser.add_argument("input_path", help="Path to the GEFF file")
    args = parser.parse_args()
    utils.validate(args.input_path)
    print(f"{args.input_path} is valid")


def info() -> None:
    """Command-line interface for displaying information about a GEFF file."""
    parser = argparse.ArgumentParser(description="Display information about a GEFF file")
    parser.add_argument("input_path", help="Path to the GEFF file")
    args = parser.parse_args()
    metadata = GeffMetadata.read(zarr.open(args.input_path, mode="r"))
    print(metadata.model_dump_json(indent=2))  # Convert metadata to dict for display
