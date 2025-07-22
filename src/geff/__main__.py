import argparse

from .utils import validate


def main() -> None:
    """Command-line interface for validating geff files."""
    parser = argparse.ArgumentParser(description="Validate a GEFF file")
    parser.add_argument("input_path", help="Path to the GEFF file")
    args = parser.parse_args()
    validate(args.input_path)
    print(f"{args.input_path} is valid")


if __name__ == "__main__":
    main()
