import logging
import sys
from pathlib import Path
from typing import Annotated

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


@app.command()
def convert_ctc(
    ctc_path: Annotated[
        Path,
        typer.Argument(help="The path to the directory containing ctc tracks", show_default=False),
    ],
    geff_path: Annotated[
        Path, typer.Argument(help="Path to save the output geff", show_default=False)
    ],
    segm_path: Annotated[
        Path | None,
        typer.Option(
            help="The path to export the segmentation file, if not provided, it won't be exported."
        ),
    ] = None,
    input_image_dir: Annotated[
        Path | None,
        typer.Option(
            help="The path to the input image directory. If not provided, it won't be exported."
        ),
    ] = None,
    output_image_path: Annotated[
        Path | None,
        typer.Option(
            help="The path to export the image file, if not provided, it won't be exported."
        ),
    ] = None,
    tczyx: Annotated[
        bool,
        typer.Option(
            help="Expand data to make it (T, C, Z, Y, X) otherwise it's (T,) + Frame shape."
        ),
    ] = False,
    overwrite: Annotated[
        bool, typer.Option(help="Whether to overwrite the GEFF file if it already exists.")
    ] = False,
) -> None:
    """
    Convert a CTC data directory to a GEFF file.
    """
    from geff.interops import from_ctc_to_geff, ctc_tiffs_to_zarr  # noqa: I001 import at call time to avoid optional dependency issues

    if (input_image_dir is not None and output_image_path is None) or (
        input_image_dir is None and output_image_path is not None
    ):
        raise ValueError("'input_image_dir' and 'output_image_path' must be provided together")

    from_ctc_to_geff(
        ctc_path=ctc_path,
        geff_path=geff_path,
        segmentation_store=segm_path,
        tczyx=tczyx,
        overwrite=overwrite,
    )

    if input_image_dir is not None:
        ctc_tiffs_to_zarr(
            ctc_path=input_image_dir,
            output_store=output_image_path,
            ctzyx=tczyx,
            overwrite=overwrite,
        )


if __name__ == "__main__":
    app()
