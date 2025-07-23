import logging
import sys

import typer
import zarr

from . import utils
from .metadata_schema import GeffMetadata

app = typer.Typer(help="GEFF Command Line Interface")

logging.basicConfig(stream=sys.stderr, level=logging.WARNING, format="%(levelname)s: %(message)s")
logging.captureWarnings(True)


@app.command()
def validate(input_path: str = typer.Argument(..., help="Path to the GEFF file")):
    """Validate a GEFF file."""
    utils.validate(input_path)
    print(f"{input_path} is valid")


@app.command()
def info(input_path: str = typer.Argument(..., help="Path to the GEFF file")):
    """Display information about a GEFF file."""
    metadata = GeffMetadata.read(zarr.open(input_path, mode="r"))
    print(metadata.model_dump_json(indent=2))


if __name__ == "__main__":
    app()
