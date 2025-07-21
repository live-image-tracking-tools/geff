import shutil
import warnings
from copy import deepcopy
from pathlib import Path
from typing import Literal

import networkx as nx
import typer
from lxml import etree as ET

import geff
from geff.metadata_schema import GeffMetadata
from geff.networkx.io import write_nx

# TODO: check docstrings consistency.


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


def _get_units(
    element: ET._Element,
) -> dict[str, str]:
    """
    Extracts units information from an XML element and returns it as a dictionary.

    This function deep copies the attributes of the XML element into a dictionary,
    then clears the element to free up memory.

    Parameters
    ----------
    element : ET._Element
        The XML element holding the units information.

    Returns
    -------
    dict[str, str]
        A dictionary where the keys are the attribute names and the values are the
        corresponding attribute values (units information).
    """
    units = {}  # type: dict[str, str]
    if element.attrib:
        units = deepcopy(element.attrib)
    if "spatialunits" not in units:
        warnings.warn(
            "No spatial units found in the XML file. Setting to 'pixel'.",
            stacklevel=2,
        )
        units["spatialunits"] = "pixel"  # TrackMate default value.
    if "timeunits" not in units:
        warnings.warn(
            "No time units found in the XML file. Setting to 'frame'.",
            stacklevel=2,
        )
        units["timeunits"] = "frame"  # TrackMate default value.
    element.clear()  # We won't need it anymore so we free up some memory.
    # .clear() does not delete the element: it only removes all subelements
    # and clears or sets to `None` all attributes.
    return units


def _get_features_dict(
    iterator: ET.iterparse,
    ancestor: ET._Element,
) -> list[dict[str, str]]:
    """
    Get all the features of ancestor and return them as a list.

    The ancestor is either a SpotFeatures, EdgeFeatures or a TrackFeatures tag.

    Parameters
    ----------
    iterator : ET.iterparse
        An iterator over XML elements.
    ancestor : ET._Element
        The XML element that encompasses the information to be added.

    Returns
    -------
    list[dict[str, str]]
        A list of dictionaries, each representing a feature.
    """
    features = []
    event, element = next(iterator)  # Feature.
    while (event, element) != ("end", ancestor):
        if element.tag == "Feature" and event == "start":
            attribs = deepcopy(element.attrib)
            features.append(attribs)
        element.clear()
        event, element = next(iterator)
    return features


def _get_features_metadata(
    it: ET.iterparse,
    ancestor: ET._Element,
) -> list[dict[str, str]]:
    """
    Add all the TrackMate model features to a FeaturesDeclaration object.

    The model features are divided in 3 categories: SpotFeatures, EdgeFeatures and
    TrackFeatures. Those features are regrouped under the FeatureDeclarations tag.
    Some other features are used in the Spot and Track tags but are not declared in
    the FeatureDeclarations tag.

    Parameters
    ----------
    it : ET.iterparse
        An iterator over XML elements.
    ancestor : ET._Element
        The XML element that encompasses the information to be added.
    fdec : FeaturesDeclaration
        The FeaturesDeclaration object to add the features to.
    units : dict[str, str]
        The temporal and spatial units of the TrackMate model
        (`timeunits` and `spatialunits`).
    """
    features = []
    event, element = next(it)
    while (event, element) != ("end", ancestor):
        # Features stored in the FeatureDeclarations tag.
        event, element = next(it)  # Feature.
        while (event, element) != ("end", ancestor):
            if element.tag == "Feature" and event == "start":
                attribs = deepcopy(element.attrib)
                features.append(attribs)
            element.clear()
            event, element = next(it)
        # element.clear()
        # event, element = next(it)
    return features


def _parse_model_tag(
    xml_path: Path,
    keep_all_spots: bool,
    keep_all_tracks: bool,
) -> nx.Graph:
    """
    Read an XML file and convert the model data into several graphs.

    Each TrackMate track and its associated data described in the XML file
    are modeled as networkX directed graphs. Spots are modeled as graph
    nodes, and edges as graph edges. Spot, edge and track features are
    stored in node, edge and graph attributes, respectively.

    Parameters
    ----------
    xml_path : str
        Path of the XML file to process.
    keep_all_spots : bool
        True to keep the spots filtered out in TrackMate, False otherwise.
    keep_all_tracks : bool
        True to keep the tracks filtered out in TrackMate, False otherwise.

    Returns
    -------
    tuple[dict[str, str], FeaturesDeclaration, Data]
        A tuple containing the space and time units, the features declaration
        and the data of the model.
    """
    graph = nx.Graph()
    metadata = GeffMetadata(geff_version=geff.__version__, directed=True)
    # TODO: determine axes
    # TODO: remove geff version and related import

    # So as not to load the entire XML file into memory at once, we're
    # using an iterator to browse over the tags one by one.
    # The events 'start' and 'end' correspond respectively to the opening
    # and the closing of the considered tag.
    it = ET.iterparse(xml_path, events=["start", "end"])
    _, root = next(it)  # Saving the root of the tree for later cleaning.

    for event, element in it:
        if element.tag == "Model" and event == "start":
            units = _get_units(element)
            print(f"Units: {units}")
            root.clear()  # Cleaning the tree to free up some memory.
            # All the browsed subelements of `root` are deleted.

        # Get the spot, edge and track features and add them to the
        # features declaration.
        if element.tag == "FeatureDeclarations" and event == "start":
            feat_md = _get_features_metadata(it, element)
            root.clear()
            print(feat_md)

    #     # Adding the spots as nodes.
    #     if element.tag == "AllSpots" and event == "start":
    #         segmentation = _add_all_nodes(it, element, fd, graph)
    #         root.clear()

    #     # Adding the tracks as edges.
    #     if element.tag == "AllTracks" and event == "start":
    #         tracks_attributes = _build_tracks(it, element, fd, graph)
    #         root.clear()

    #         # Removal of filtered spots / nodes.
    #         if not keep_all_spots:
    #             # Those nodes belong to no tracks: they have a degree of 0.
    #             lone_nodes = [n for n, d in graph.degree if d == 0]
    #             graph.remove_nodes_from(lone_nodes)

    #     # Filtering out tracks and adding tracks attribute.
    #     if element.tag == "FilteredTracks" and event == "start":
    #         # Removal of filtered tracks.
    #         id_to_keep = _get_filtered_tracks_ID(it, element)
    #         if not keep_all_tracks:
    #             to_remove = [n for n, t in graph.nodes(data="TRACK_ID") if t not in id_to_keep]
    #             graph.remove_nodes_from(to_remove)

    #     if element.tag == "Model" and event == "end":
    #         break  # We are not interested in the following data.

    # # We want one lineage per track, so we need to split the graph
    # # into its connected components.
    # lineages = _split_graph_into_lineages(graph, tracks_attributes)

    # # For pycellin compatibility, some TrackMate features have to be renamed.
    # # We only rename features that are either essential to the functioning of
    # # pycellin or confusing (e.g. "name" is a spot and a track feature).
    # _update_features_declaration(fd, units, segmentation)
    # for lin in lineages:
    #     for key_name, new_key in [
    #         ("ID", "cell_ID"),  # mandatory
    #         ("FRAME", "frame"),  # mandatory
    #         ("name", "cell_name"),  # confusing
    #     ]:
    #         _update_node_feature_key(lin, key_name, new_key)
    #     _update_lineage_feature_key(lin, "name", "lineage_name")
    #     _update_TRACK_ID(lin)
    #     _update_location_related_features(lin)

    #     # Adding if each track was present in the 'FilteredTracks' tag
    #     # because this info is needed when reconstructing TrackMate XMLs
    #     # from graphs.
    #     if lin.graph["lineage_ID"] in id_to_keep:
    #         lin.graph["FilteredTrack"] = True
    #     else:
    #         lin.graph["FilteredTrack"] = False

    # return units, fd, Data({lin.graph["lineage_ID"]: lin for lin in lineages})


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

    # graph = _build_nx(xml_path)
    _parse_model_tag(
        xml_path=xml_path,
        keep_all_spots=keep_all_spots,
        keep_all_tracks=keep_all_tracks,
    )
    # write_nx(
    #     graph,
    #     geff_path,
    #     zarr_format=zarr_format,
    # )
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
