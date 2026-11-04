from pathlib import Path
from typing import TYPE_CHECKING, Annotated, cast

import typer

from geff_spec import GeffMetadata
from geff_spec._valid_values import VALID_SPACE_UNITS, VALID_TIME_UNITS

from . import validate_structure

if TYPE_CHECKING:
    from typing import Literal


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
            help="The path to the directory containing ctc tracks (man_track.txt or res_track.txt)"
            " and segmentation, e.g. data/01_GT/TRA or data/01_RES",
            show_default=False,
        ),
    ],
    output_path: Annotated[
        Path,
        typer.Argument(
            help="Without --image-dir: path to save the output geff, including the geff directory "
            "name (eg. ~/folder/folder/data.zarr/tracks.geff). With --image-dir: path of the "
            "OME-Zarr to write, which will contain the image, the segmentation in its labels "
            "group and the geff as tracks.geff (eg. data.ome.zarr).",
            show_default=False,
        ),
    ],
    image_dir: Annotated[
        Path | None,
        typer.Option(
            help="The path to the directory containing the raw image tiffs, e.g. data/01. If "
            "provided, the images, segmentation and geff are all written into one OME-Zarr at "
            "OUTPUT_PATH. If not provided, only the geff (and optionally --segm-path) is written."
        ),
    ] = None,
    segm_path: Annotated[
        Path | None,
        typer.Option(
            help="Without --image-dir: the path to export the segmentation to, if not provided, "
            "it won't be exported. Not allowed with --image-dir, where the segmentation is "
            "always written inside the OME-Zarr."
        ),
    ] = None,
    label_name: Annotated[
        str | None,
        typer.Option(
            help="With --image-dir: the name of the segmentation inside the OME-Zarr labels "
            "group. Defaults to 'segmentation'."
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
        typer.Option(help="Whether to overwrite the output (GEFF or OME-Zarr) if it exists."),
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
    num_scale_levels: Annotated[
        int | None,
        typer.Option(
            help="With --image-dir: total number of scale levels including the base. If not "
            "provided, chosen so the coarsest level fits in a single --min-chunk-size chunk."
        ),
    ] = None,
    min_chunk_size: Annotated[
        int | None,
        typer.Option(
            help="With --image-dir: spatial chunk size of the generated scale levels, also used "
            "when auto-computing the number of levels. Defaults to 128."
        ),
    ] = None,
) -> None:
    """
    Convert a CTC data directory to a GEFF file, or with --image-dir to an OME-Zarr containing
    the image, the segmentation and the tracks (as tracks.geff).
    """
    from geff.convert import convert_ctc as _convert_ctc
    from geff.convert import from_ctc_to_geff

    if image_dir is not None and segm_path is not None:
        raise typer.BadParameter(
            "not allowed with --image-dir, use --label-name",
            param_hint="--segm-path",
        )
    if image_dir is None and label_name is not None:
        raise typer.BadParameter("only applies with --image-dir", param_hint="--label-name")
    if image_dir is None and num_scale_levels is not None:
        raise typer.BadParameter("only applies with --image-dir", param_hint="--num-scale-levels")
    if image_dir is None and min_chunk_size is not None:
        raise typer.BadParameter("only applies with --image-dir", param_hint="--min-chunk-size")

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

    if image_dir is None:
        from_ctc_to_geff(
            ctc_path=ctc_path,
            geff_path=output_path,
            segmentation_store=segm_path,
            tczyx=tczyx,
            overwrite=overwrite,
            pixel_size=pixel_size,
            pixel_unit=pixel_unit,
            time_scale=time_scale,
            time_unit=time_unit,
        )
    else:
        from geff.convert._scale_pyramid import DEFAULT_SPATIAL_CHUNK_SIZE

        _convert_ctc(
            ctc_path=ctc_path,
            image_dir=image_dir,
            zarr_path=output_path,
            label_name=label_name or "segmentation",
            tczyx=tczyx,
            overwrite=overwrite,
            pixel_size=pixel_size,
            pixel_unit=pixel_unit,
            time_scale=time_scale,
            time_unit=time_unit,
            num_scale_levels=num_scale_levels,
            min_chunk_size=min_chunk_size or DEFAULT_SPATIAL_CHUNK_SIZE,
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
    zarr_format: Annotated[int, typer.Option(help="The version of zarr to write.")] = 3,
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
