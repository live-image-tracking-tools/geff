import shutil
import warnings
from copy import deepcopy
from pathlib import Path
from typing import Any, Literal

import networkx as nx
import typer
from lxml import etree as ET

import geff
from geff.metadata_schema import GeffMetadata

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


def _get_features_metadata(
    it: ET.iterparse,
    ancestor: ET._Element,
) -> dict[str, dict[str, str]]:
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

    Returns
    -------
    dict[str, dict[str, str]]
        A dictionary where the keys are the feature names and the values are
        dictionaries containing the feature attributes as defined by TrackMate
        (name, shortname, dimension, isint).
    """
    feat_md = {}
    event, element = next(it)
    while (event, element) != ("end", ancestor):
        # Features stored in the FeatureDeclarations tag.
        event, element = next(it)  # Feature.
        while (event, element) != ("end", ancestor):
            if element.tag == "Feature" and event == "start":
                attribs = deepcopy(element.attrib)
                feat_md[attribs["feature"]] = attribs
                feat_md[attribs["feature"]].pop("feature", None)
            element.clear()
            event, element = next(it)
    # element.clear()
    # event, element = next(it)
    return feat_md


def _convert_attributes(
    attributes: dict[str, str],
    feats_metadata: dict[str, dict[str, str]],
    feat_type: str,
) -> None:
    """
    Convert the values of `attributes` from string to the correct data type.

    The type to convert to is given by the features metadata.
    TrackMate features are either integers, floats or strings.

    Parameters
    ----------
    attributes : dict[str, str]
        The dictionary whose values we want to convert.
    feats_metadata : dict[str, dict[str, str]]
        The features metadata containing information on the expected data types
        for each feature.
    feat_type : str
        The type of the feature to convert (node, edge, or lineage).

    Warns
    -----
    UserWarning
        If a feature is not found in the features declaration.
    """
    for key in attributes:
        if key in feats_metadata:
            if feats_metadata[key]["isint"] == "true":
                attributes[key] = int(attributes[key])
            else:
                try:
                    attributes[key] = float(attributes[key])
                except ValueError:
                    # Can't be anything but a string.
                    attributes[key] = str(attributes[key])
        elif key == "ID" or key == "ROI_N_POINTS":
            # IDs are always integers in TrackMate.
            attributes[key] = int(attributes[key])
        elif key == "name":
            pass  # "name" is a string so we don't need to convert it.
        else:
            warnings.warn(
                f"{feat_type.capitalize()} feature {key} not found in the features declaration.",
                stacklevel=2,
            )


def _convert_ROI_coordinates(
    element: ET._Element,
    attribs: dict[str, Any],
) -> None:
    """
    Extract, format and add ROI coordinates to the attributes dict.

    Parameters
    ----------
    element : ET._Element
        Element from which to extract ROI coordinates.
    attribs : dict[str, Any]
        Attributes dict to update with ROI coordinates.

    Raises
    ------
    KeyError
        If the "ROI_N_POINTS" attribute is not found in the attributes dict.
    """
    if "ROI_N_POINTS" not in attribs:
        raise KeyError(
            f"No key 'ROI_N_POINTS' in the attributes of current element '{element.tag}'."
        )
    if element.text:
        points_coordinates = element.text.split()
        points_coordinates = [float(x) for x in points_coordinates]
        points_dimension = len(points_coordinates) // attribs["ROI_N_POINTS"]
        it = [iter(points_coordinates)] * points_dimension
        points_coordinates = list(zip(*it))
        attribs["ROI_coords"] = points_coordinates
    else:
        attribs["ROI_coords"] = None


def _add_all_nodes(
    it: ET.iterparse,
    ancestor: ET._Element,
    feat_md: dict[str, dict[str, str]],
    graph: nx.DiGraph,
) -> bool:
    """
    Add nodes and their attributes to a graph and return the presence of segmentation.

    All the elements that are descendants of `ancestor` are explored.

    Parameters
    ----------
    it : ET.iterparse
        An iterator over XML elements.
    ancestor : ET._Element
        The XML element that encompasses the information to be added.
    feat_md : dict[str, dict[str, str]]
        The features metadata containing the expected node attributes.
    graph : nx.DiGraph
        The graph to which the nodes will be added.

    Returns
    -------
    bool
        True if the model has segmentation data, False otherwise

    Raises
    ------
    ValueError
        If a node attribute cannot be converted to the expected type.
    KeyError
        If a node attribute is not found in the features declaration.
    """
    segmentation = False
    event, element = next(it)
    while (event, element) != ("end", ancestor):
        event, element = next(it)
        if element.tag == "Spot" and event == "end":
            # All items in element.attrib are parsed as strings but most
            # of them (if not all) are numbers. So we need to do a
            # conversion based on these attributes type (attribute `isint`)
            # as defined in the features declaration.
            attribs = deepcopy(element.attrib)
            try:
                _convert_attributes(attribs, feat_md, "node")
            except ValueError as err:
                print(f"ERROR: {err} Please check the XML file.")
                raise

            # The ROI coordinates are not stored in a tag attribute but in
            # the tag text. So we need to extract then format them.
            # In case of a single-point detection, the `ROI_N_POINTS` attribute
            # is not present.
            if segmentation:
                try:
                    _convert_ROI_coordinates(element, attribs)
                except KeyError as err:
                    print(err)
            else:
                if "ROI_N_POINTS" in attribs:
                    segmentation = True
                    _convert_ROI_coordinates(element, attribs)

            # Adding the node and its attributes to the graph.
            try:
                graph.add_node(attribs["ID"], **attribs)
            except KeyError as err:
                warnings.warn(
                    f"No key {err} in the attributes of current element "
                    f"'{element.tag}'. Not adding this node to the graph.",
                    stacklevel=2,
                )
            finally:
                element.clear()

    return segmentation


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
            print(feat_md.keys())

        # Adding the spots as nodes.
        if element.tag == "AllSpots" and event == "start":
            segmentation = _add_all_nodes(it, element, feat_md, graph)
            root.clear()

    return graph

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
    graph = _parse_model_tag(
        xml_path=xml_path,
        keep_all_spots=keep_all_spots,
        keep_all_tracks=keep_all_tracks,
    )
    print(graph)
    print(graph.nodes[2004])

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
