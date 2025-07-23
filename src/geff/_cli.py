import argparse
import logging
import sys

import zarr

from . import utils
from .metadata_schema import GeffMetadata

logging.basicConfig(stream=sys.stderr, level=logging.WARNING, format="%(levelname)s: %(message)s")
logging.captureWarnings(True)  # Capture warnings and log them


def main() -> None:
    """Main entry point for the geff command-line interface."""
    parser = argparse.ArgumentParser(description="GEFF Command Line Interface")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand for validation
    validate_parser = subparsers.add_parser("validate", help="Validate a GEFF file")
    validate_parser.add_argument("input_path", help="Path to the GEFF file")

    # Subcommand for displaying information
    info_parser = subparsers.add_parser("info", help="Display information about a GEFF file")
    info_parser.add_argument("input_path", help="Path to the GEFF file")

    args = parser.parse_args()

    if args.command == "validate":
        validate(args.input_path)
    elif args.command == "info":
        info(args.input_path)


def validate(input_path) -> None:
    """Command-line interface for validating geff files."""
    utils.validate(input_path)
    print(f"{input_path} is valid")


def info(input_path) -> None:
    metadata = GeffMetadata.read(zarr.open(input_path, mode="r"))
    print(metadata.model_dump_json(indent=2))  # Convert metadata to dict for display


if __name__ == "__main__":
    main()
