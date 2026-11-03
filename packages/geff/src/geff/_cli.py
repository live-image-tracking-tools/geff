from pathlib import Path
from typing import TYPE_CHECKING, Annotated, cast

import typer

from geff_spec import GeffMetadata
from geff_spec._valid_values import VALID_SPACE_UNITS, VALID_TIME_UNITS

from . import validate_structure

if TYPE_CHECKING:
    from typing import Literal

    from geff_spec._valid_values import SpaceUnits, TimeUnits

app = typer.Typer(help="GEFF Command Line Interface")


@app.command()
def validate(
    input_path: str = typer.Argument(
        ..., help="Path to the GEFF folder, e.g. data.zarr/tracks.geff"
    ),
) -> None:
    """Validate a GEFF file."""
    validate_structure(input_path)


@app.command()
def info(
    input_path: str = typer.Argument(
        ..., help="Path to the GEFF folder, e.g. data.zarr/tracks.geff"
    ),
) -> None:
    """Display information about a GEFF file."""
    metadata = GeffMetadata.read(input_path)
    print(metadata.model_dump_json(indent=2))  # noqa


@app.command()
def convert_ctc(
    ctc_path: Annotated[
        Path,
        typer.Argument(
            help="The path to the directory containing ctc tracks (man_track.txt or res_track.txt),"
            " e.g. data/01_GT/TRA or data/01_RES",
            show_default=False,
        ),
    ],
    geff_path: Annotated[
        Path,
        typer.Argument(
            help="Path to save the output geff, including the geff directory name "
            "(eg. ~/folder/folder/data.zarr/tracks.geff)",
            show_default=False,
        ),
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
        bool,
        typer.Option(help="Whether to overwrite the GEFF file if it already exists."),
    ] = False,
    pixel_size: Annotated[
        list[float] | None,
        typer.Option(
            help="Physical size of a pixel along each spatial dimension, given once per "
            "dimension in (z,) y, x order, e.g. --pixel-size 0.5 --pixel-size 0.5. Defaults to 1.0."
        ),
    ] = None,
    pixel_unit: Annotated[
        str | None,
        typer.Option(help=f"Unit of --pixel-size, one of {', '.join(VALID_SPACE_UNITS)}."),
    ] = None,
    time_scale: Annotated[
        float | None,
        typer.Option(help="Physical time between frames. Defaults to 1.0."),
    ] = None,
    time_unit: Annotated[
        str | None,
        typer.Option(help=f"Unit of --time-scale, one of {', '.join(VALID_TIME_UNITS)}."),
    ] = None,
) -> None:
    """
    Convert a CTC data directory to a GEFF file.
    """
    from geff.convert import from_ctc_to_geff, ctc_tiffs_to_zarr  # noqa: I001 import at call time to avoid optional dependency issues

    if (input_image_dir is not None and output_image_path is None) or (
        input_image_dir is None and output_image_path is not None
    ):
        raise ValueError("'input_image_dir' and 'output_image_path' must be provided together")

    # because of Typer not supporting Literal types
    if pixel_unit is not None and pixel_unit not in VALID_SPACE_UNITS:
        raise typer.BadParameter(
            f"'{pixel_unit}' is not a valid space unit, expected one of {VALID_SPACE_UNITS}",
            param_hint="--pixel-unit",
        )
    if time_unit is not None and time_unit not in VALID_TIME_UNITS:
        raise typer.BadParameter(
            f"'{time_unit}' is not a valid time unit, expected one of {VALID_TIME_UNITS}",
            param_hint="--time-unit",
        )
    space_unit = cast("SpaceUnits | None", pixel_unit)
    temporal_unit = cast("TimeUnits | None", time_unit)

    from_ctc_to_geff(
        ctc_path=ctc_path,
        geff_path=geff_path,
        segmentation_store=segm_path,
        tczyx=tczyx,
        overwrite=overwrite,
        pixel_size=pixel_size,
        pixel_unit=space_unit,
        time_scale=time_scale,
        time_unit=temporal_unit,
    )

    if input_image_dir is not None:
        ctc_tiffs_to_zarr(
            ctc_path=input_image_dir,
            output_store=output_image_path,
            ctzyx=tczyx,
            overwrite=overwrite,
            pixel_size=pixel_size,
            pixel_unit=space_unit,
            time_scale=time_scale,
            time_unit=temporal_unit,
        )


@app.command()
def convert_trackmate_xml(
    xml_path: Annotated[
        Path,
        typer.Argument(help="The path to the TrackMate XML file", show_default=False),
    ],
    geff_path: Annotated[
        Path,
        typer.Argument(
            help="Path to save the output geff, including the geff directory name"
            " (eg. ~/folder/folder/data.zarr/tracks.geff)",
            show_default=False,
        ),
    ],
    discard_filtered_spots: Annotated[
        bool,
        typer.Option(help="True to discard the spots filtered out in TrackMate, False otherwise."),
    ] = False,
    discard_filtered_tracks: Annotated[
        bool,
        typer.Option(help="True to discard the tracks filtered out in TrackMate, False otherwise."),
    ] = False,
    overwrite: Annotated[
        bool,
        typer.Option(help="Whether to overwrite the GEFF file if it already exists."),
    ] = False,
    zarr_format: Annotated[int, typer.Option(help="The version of zarr to write.")] = 2,
    # because of Typer not supporting Literal types
) -> None:
    """
    Convert a TrackMate XML file to a GEFF file.
    """
    from geff.convert import from_trackmate_xml_to_geff

    from_trackmate_xml_to_geff(
        xml_path=xml_path,
        geff_path=geff_path,
        discard_filtered_spots=discard_filtered_spots,
        discard_filtered_tracks=discard_filtered_tracks,
        overwrite=overwrite,
        zarr_format=cast("Literal[2, 3]", zarr_format),
    )


@app.command()
def convert_to_csv(
    store: Annotated[Path, typer.Argument(help="Path to geff group to convert")],
    outpath: Annotated[
        Path,
        typer.Argument(
            help="Path to save output csvs. Any file extension will"
            " be stripped and replaced with '-nodes.csv' and '-edges.csv'"
        ),
    ],
) -> None:
    from geff.convert import geff_to_csv

    geff_to_csv(store=store, outpath=outpath)


if __name__ == "__main__":
    app()
