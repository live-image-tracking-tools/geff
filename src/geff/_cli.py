import argparse

import utils


def validate() -> None:
    """Command-line interface for validating geff files."""
    parser = argparse.ArgumentParser(description="Validate a GEFF file")
    parser.add_argument("input_path", help="Path to the GEFF file")
    args = parser.parse_args()
    utils.validate(args.input_path)
    print(f"{args.input_path} is valid")
