import shutil
from pathlib import Path
from typing import Literal

import lxml
import networkx as nx
import typer

from geff.networkx.io import write_nx


def _preliminary_checks(
    xml_path: Path,
    geff_path: Path,
    overwrite: bool,
) -> None:
    """
    Perform preliminary checks before conversion.

    Args:
        xml_path (Path): The path to the TrackMate XML file.
        geff_path (Path): The path to the GEFF file.
        overwrite (bool): Whether to overwrite the GEFF file if it already exists.

    Raises:
        FileNotFoundError: If the XML file does not exist.
        FileExistsError: If the GEFF file exists and overwrite is False.
    """
    # TODO: extract this to a common module since similar code is already
    # used in ctc_to_geff. Need to wait for CTC PR.
    if not xml_path.exists():
        raise FileNotFoundError(f"TrackMate XML file {xml_path} does not exist")

    if geff_path.exists() and not overwrite:
        raise FileExistsError(f"GEFF file {geff_path} already exists")

    if geff_path.exists() and overwrite:
        shutil.rmtree(geff_path)


def _build_nx(xml_path: Path) -> nx.Graph:
    """
    Build the NX file from the XML path.

    Args:
        xml_path : The path to the TrackMate XML file.
    Returns:
        A networkx graph representing the TrackMate data.
    """

    pass


def from_trackmate_xml_to_geff(
    xml_path: Path | str,
    geff_path: Path | str,
    tczyx: bool = False,
    keep_all_spots: bool = False,
    keep_all_tracks: bool = False,
    overwrite: bool = False,
    zarr_format: Literal[2, 3] | None = 2,
) -> None:
    """
    Convert a TrackMate XML file to a GEFF file.

    Args:
        xml_path (Path | str): The path to the TrackMate XML file.
        geff_path (Path | str): The path to the GEFF file.
        tczyx (bool): Expand data to make it (T, C, Z, Y, X) otherwise it's (T,) + Frame shape.
        keep_all_spots (bool): True to keep the spots filtered out in TrackMate, False otherwise.
        keep_all_tracks (bool): True to keep the tracks filtered out in TrackMate, False otherwise.
        overwrite (bool): Whether to overwrite the GEFF file if it already exists.
        zarr_format (int, optional): The version of zarr to write. Defaults to 2.
    """
    if isinstance(xml_path, str):
        xml_path = Path(xml_path)
    if isinstance(geff_path, str):
        geff_path = Path(geff_path)
    _preliminary_checks(xml_path, geff_path, overwrite)

    graph = _build_nx(xml_path)
    write_nx(
        graph,
        geff_path,
        zarr_format=zarr_format,
    )
    # TODO: add the following parameters (cf write_nx definition)
    #     metadata: GeffMetadata | None = None,
    #     axis_names: list[str] | None = None,
    #     axis_units: list[str | None] | None = None,
    #     axis_types: list[str | None] | None = None,


def from_trackmate_xml_to_geff_cli(
    xml_path: Path | str,
    geff_path: Path | str,
    tczyx: bool = False,
    keep_all_spots: bool = False,
    keep_all_tracks: bool = False,
    overwrite: bool = False,
    zarr_format: Literal[2, 3] | None = 2,
) -> None:
    """
    Convert a TrackMate XML file to a GEFF file.

    Args:
        xml_path (Path | str): The path to the TrackMate XML file.
        geff_path (Path | str): The path to the GEFF file.
        tczyx (bool): Expand data to make it (T, C, Z, Y, X) otherwise it's (T,) + Frame shape.
        keep_all_spots (bool): True to keep the spots filtered out in TrackMate, False otherwise.
        keep_all_tracks (bool): True to keep the tracks filtered out in TrackMate, False otherwise.
        overwrite (bool): Whether to overwrite the GEFF file if it already exists.
        zarr_format (int, optional): The version of zarr to write. Defaults to 2.
    """
    from_trackmate_xml_to_geff(
        xml_path=xml_path,
        geff_path=geff_path,
        tczyx=tczyx,
        overwrite=overwrite,
        zarr_format=zarr_format,
    )


app = typer.Typer()
app.command()(from_trackmate_xml_to_geff_cli)


if __name__ == "__main__":
    # app()
    xml_path = "C:/Users/lxenard/Documents/Code/pycellin/sample_data/FakeTracks.xml"
    geff_path = (
        "C:/Users/lxenard/Documents/Janelia_Cell_Trackathon/test_trackmate_to_geff/FakeTracks.geff"
    )
    from_trackmate_xml_to_geff(xml_path, geff_path)
