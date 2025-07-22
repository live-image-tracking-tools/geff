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

# Type aliases
PropertyValue = str | int | float | list[float] | None

# TODO: check docstrings consistency.
# TODO: rename features by properties to fit geff vocabulary.


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
) -> dict[str, dict[str, PropertyValue]]:
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
    dict[str, dict[str, PropertyValue]]
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
    attributes: dict[str, int | float | str],
    feats_metadata: dict[str, dict[str, PropertyValue]],
    feat_type: str,
) -> None:
    """
    Convert the values of `attributes` from string to the correct data type.

    The type to convert to is given by the features metadata.
    TrackMate features are either integers, floats or strings.

    Parameters
    ----------
    attributes : dict[str, int | float | str]
        The dictionary whose values we want to convert.
    feats_metadata : dict[str, dict[str, PropertyValue]]
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
    attribs: dict[str, PropertyValue],
) -> None:
    """
    Extract, format and add ROI coordinates to the attributes dict.

    Parameters
    ----------
    element : ET._Element
        Element from which to extract ROI coordinates.
    attribs : dict[str, PropertyValue]
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
        assert type(attribs["ROI_N_POINTS"]) is int, "ROI_N_POINTS should be an integer"
        points_dimension = len(points_coordinates) // attribs["ROI_N_POINTS"]
        it = [iter(points_coordinates)] * points_dimension
        points_coordinates = list(zip(*it))
        attribs["ROI_coords"] = points_coordinates
    else:
        attribs["ROI_coords"] = None


def _add_all_nodes(
    it: ET.iterparse,
    ancestor: ET._Element,
    feat_md: dict[str, dict[str, PropertyValue]],
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
    feat_md : dict[str, dict[str, PropertyValue]]
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
            # of them are numbers. So we need to do a
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


def _add_edge(
    element: ET._Element,
    feat_md: dict[str, dict[str, PropertyValue]],
    graph: nx.Graph,
    current_track_id: int,
) -> None:
    """
    Add an edge between two nodes in the graph based on the XML element.

    This function extracts source and target node identifiers from the
    given XML element, along with any additional attributes defined
    within. It then adds an edge between these nodes in the specified
    graph. If the nodes have a 'TRACK_ID' attribute, it ensures consistency
    with the current track ID.

    Parameters
    ----------
    element : ET._Element
        The XML element containing edge information.
    feat_md: dict[str, dict[str, PropertyValue]]
        The features metadata containing the expected edge attributes.
    graph : nx.Graph
        The graph to which the edge and its attributes will be added.
    current_track_id : int
        Track ID of the track holding the edge.

    Raises
    ------
    AssertionError
        If the 'TRACK_ID' attribute of either the source or target node
        does not match the current track ID, indicating an inconsistency
        in track assignment.
    """
    attribs = deepcopy(element.attrib)
    _convert_attributes(attribs, feat_md, "edge")
    try:
        entry_node_id = int(attribs["SPOT_SOURCE_ID"])
        exit_node_id = int(attribs["SPOT_TARGET_ID"])
    except KeyError as err:
        warnings.warn(
            f"No key {err} in the attributes of current element '{element.tag}'. "
            f"Not adding this edge to the graph.",
            stacklevel=2,
        )
    else:
        graph.add_edge(entry_node_id, exit_node_id)
        nx.set_edge_attributes(graph, {(entry_node_id, exit_node_id): attribs})
        # Adding the current track ID to the nodes of the newly created
        # edge. This will be useful later to filter nodes by track and
        # add the saved tracks attributes (as returned by this method).
        err_msg = f"Incoherent track ID for nodes {entry_node_id} and {exit_node_id}."
        entry_node = graph.nodes[entry_node_id]
        if "TRACK_ID" not in entry_node:
            entry_node["TRACK_ID"] = current_track_id
        else:
            assert entry_node["TRACK_ID"] == current_track_id, err_msg
        exit_node = graph.nodes[exit_node_id]
        if "TRACK_ID" not in exit_node:
            exit_node["TRACK_ID"] = current_track_id
        else:
            assert exit_node["TRACK_ID"] == current_track_id, err_msg
    finally:
        element.clear()


def _build_tracks(
    iterator: ET.iterparse,
    ancestor: ET._Element,
    feat_md: dict[str, dict[str, PropertyValue]],
    graph: nx.Graph,
) -> list[dict[str, PropertyValue]]:
    """
    Add edges and their attributes to a graph based on the XML elements.

    This function explores all elements that are descendants of the
    specified `ancestor` element, adding edges and their attributes to
    the provided graph. It iterates through the XML elements using
    the provided iterator, extracting and processing relevant information
    to construct track attributes.

    Parameters
    ----------
    iterator : ET.iterparse
        An iterator over XML elements.
    ancestor : ET._Element
        The XML element that encompasses the information to be added.
    feat_md: dict[str, dict[str, PropertyValue]]
        The features metadata containing the expected edge attributes.
    graph: nx.Graph
        The graph to which the edges and their attributes will be added.

    Returns
    -------
    list[dict[str, PropertyValue]]
        A list of dictionaries, each representing the attributes for a
        track.
    """
    tracks_attributes = []
    current_track_id = None
    event, element = next(iterator)
    while (event, element) != ("end", ancestor):
        # Saving the current track information.
        if element.tag == "Track" and event == "start":
            attribs = deepcopy(element.attrib)
            _convert_attributes(attribs, feat_md, "lineage")
            tracks_attributes.append(attribs)
            try:
                current_track_id = attribs["TRACK_ID"]
            except KeyError as err:
                raise KeyError(
                    f"No key TRACK_ID in the attributes of current element "
                    f"'{element.tag}'. Please check the XML file.",
                    stacklevel=2,
                ) from err

        # Edge creation.
        if element.tag == "Edge" and event == "start":
            assert current_track_id is not None, "No current track ID."
            _add_edge(element, feat_md, graph, current_track_id)

        event, element = next(iterator)

    return tracks_attributes


def _parse_model_tag(
    xml_path: Path,
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

        # Adding the tracks as edges.
        if element.tag == "AllTracks" and event == "start":
            tracks_attributes = _build_tracks(it, element, feat_md, graph)
            root.clear()

    return graph

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
    overwrite: bool = False,
    zarr_format: Literal[2, 3] | None = 2,
) -> None:
    """
    Convert a TrackMate XML file to a GEFF file.

    Args:
        xml_path (Path | str): The path to the TrackMate XML file.
        geff_path (Path | str): The path to the GEFF file.
        tczyx (bool): Expand data to make it (T, C, Z, Y, X) otherwise it's (T,) + Frame shape.
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
    )
    print(graph)
    print(graph.nodes[2004])
    print(graph.edges[2005, 2007])

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
    overwrite: bool = False,
    zarr_format: Literal[2, 3] | None = 2,
) -> None:
    """
    Convert a TrackMate XML file to a GEFF file.

    Args:
        xml_path (Path | str): The path to the TrackMate XML file.
        geff_path (Path | str): The path to the GEFF file.
        tczyx (bool): Expand data to make it (T, C, Z, Y, X) otherwise it's (T,) + Frame shape.
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
