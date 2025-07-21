from pathlib import Path

import lxml
import typer


def from_trackmate_xml_to_geff(
    xml_path: Path,
    geff_path: Path,
    tczyx: bool = False,
    overwrite: bool = False,
) -> None:
    """
    Convert a TrackMate XML file to a GEFF file.

    Args:
        xml_path: The path to the TrackMate XML file.
        geff_path: The path to the GEFF file.
        tczyx: Expand data to make it (T, C, Z, Y, X) otherwise it's (T,) + Frame shape.
        overwrite: Whether to overwrite the GEFF file if it already exists.
    """
    pass


def from_trackmate_xml_to_geff_cli(
    xml_path: Path,
    geff_path: Path,
    tczyx: bool = False,
    overwrite: bool = False,
) -> None:
    """
    Convert a TrackMate XML file to a GEFF file.

    Args:
        xml_path: The path to the TrackMate XML file.
        geff_path: The path to the GEFF file.
        tczyx: Expand data to make it (T, C, Z, Y, X) otherwise it's (T,) + Frame shape.
        overwrite: Whether to overwrite the GEFF file if it already exists.
    """
    from_trackmate_xml_to_geff(
        xml_path=xml_path,
        geff_path=geff_path,
        tczyx=tczyx,
        overwrite=overwrite,
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
