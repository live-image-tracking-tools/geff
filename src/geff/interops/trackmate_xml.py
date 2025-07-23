import shutil
import warnings
from copy import deepcopy
from pathlib import Path
from typing import Literal, cast

import networkx as nx
import typer
from lxml import etree as ET

from geff.metadata_schema import Axis, GeffMetadata
from geff.networkx.io import write_nx

# Type aliases
Attribute = str | int | float | list[float] | None

# TODO: extract _preliminary_checks() to a common module since similar code is already
# used in ctc_to_geff. Need to wait for CTC PR.


def _preliminary_checks(
    xml_path: Path,
    geff_path: Path,
    overwrite: bool,
) -> None:
    """Check the validity of input paths and clean up the output path if needed.

    Args:
        xml_path (Path): The path to the TrackMate XML file.
        geff_path (Path): The path to the GEFF file.
        overwrite (bool): Whether to overwrite the GEFF file if it already exists.

    Raises:
        FileNotFoundError: If the XML file does not exist.
        FileExistsError: If the GEFF file exists and overwrite is False.
    """
    if not xml_path.exists():
        raise FileNotFoundError(f"TrackMate XML file {xml_path} does not exist")

    if geff_path.exists() and not overwrite:
        raise FileExistsError(f"GEFF file {geff_path} already exists")

    if geff_path.exists() and overwrite:
        shutil.rmtree(geff_path)


def _get_units(
    element: ET._Element,
) -> dict[str, str]:
    """Extract units information from an XML element and return it as a dictionary.

    This function deep copies the attributes of the XML element into a dictionary,
    then clears the element to free up memory.

    Args:
        element (ET._Element): The XML element holding the units information.

    Returns:
        dict[str, str]: A dictionary containing the units information.
        Keys are 'spatialunits' and 'timeunits'.

    Warns:
        UserWarning: If the 'spatialunits' or 'timeunits' attributes are not found,
            defaulting them to 'pixel' and 'frame', respectively.
    """
    units = {}  # type: dict[str, str]
    if element.attrib:
        units = deepcopy(element.attrib)
    if "spatialunits" not in units:
        warnings.warn(
            "No space unit found in the XML file. Setting to 'pixel'.",
            stacklevel=2,
        )
        units["spatialunits"] = "pixel"  # TrackMate default value.
    if "timeunits" not in units:
        warnings.warn(
            "No time unit found in the XML file. Setting to 'frame'.",
            stacklevel=2,
        )
        units["timeunits"] = "frame"  # TrackMate default value.
    element.clear()  # We won't need it anymore so we free up some memory.
    # .clear() does not delete the element: it only removes all subelements
    # and clears or sets to `None` all attributes.
    return units


def _get_attributes_metadata(
    it: ET.iterparse,
    ancestor: ET._Element,
) -> dict[str, dict[str, str]]:
    """Extract the TrackMate model features to a attributes dictionary.

    The model features are divided in 3 categories: SpotFeatures, EdgeFeatures and
    TrackFeatures. Those features are regrouped under the FeatureDeclarations tag.
    Some other features are used in the Spot and Track tags but are not declared in
    the FeatureDeclarations tag.

    Args:
        it (ET.iterparse): An iterator over XML elements.
        ancestor (ET._Element): The XML element that encompasses the information to be added.

    Returns:
        dict[str, dict[str, str]]: A dictionary where the keys are the attributes names
        and the values are dictionaries containing the attributes metadata as defined by TrackMate
        (name, shortname, dimension, isint).
    """
    attrs_md = {}
    event, element = next(it)
    while (event, element) != ("end", ancestor):
        # Features stored in the FeatureDeclarations tag.
        event, element = next(it)  # Feature.
        while (event, element) != ("end", ancestor):
            if element.tag == "Feature" and event == "start":
                attrs = deepcopy(element.attrib)
                attrs_md[attrs["feature"]] = attrs
                attrs_md[attrs["feature"]].pop("feature", None)
            element.clear()
            event, element = next(it)
    return attrs_md


def _convert_attributes(
    attrs: dict[str, Attribute],
    attrs_metadata: dict[str, dict[str, str]],
    attr_type: str,
) -> None:
    """
    Convert the values of the attributes from string to the correct data type.

    TrackMate features are either integers, floats or strings. The type to
    convert to is given by the attributes metadata.

    Args:
        attrs (dict[str, Attribute): The dictionary whose values we want to convert.
        attrs_metadata (dict[str, dict[str, str]]): The attributes metadata containing
        information on the expected data types for each attribute.
        attr_type (str): The type of the attribute to convert (node, edge, or lineage).

    Raises:
        ValueError: If an attribute value cannot be converted to the expected type.

    Warns:
        UserWarning: If an attribute is not found in the attributes metadata.
    """
    for key in attrs:
        if key in attrs_metadata:
            if attrs_metadata[key]["isint"] == "true":
                try:
                    attrs[key] = int(attrs[key])  # type: ignore
                except ValueError as err:
                    raise ValueError(f"Invalid integer value for {key}: {attrs[key]}") from err
            else:
                try:
                    attrs[key] = float(attrs[key])  # type: ignore
                except ValueError:
                    # Then it's a string and no need to convert.
                    pass
        elif key == "ID" or key == "ROI_N_POINTS":
            # IDs are always integers in TrackMate.
            attrs[key] = int(attrs[key])  # type: ignore
        elif key == "name":
            pass  # "name" is a string so we don't need to convert it.
        else:
            warnings.warn(
                f"{attr_type.capitalize()} attribute {key} not found in the attributes metadata.",
                stacklevel=2,
            )


def _convert_ROI_coordinates(
    element: ET._Element,
    attrs: dict[str, Attribute],
) -> None:
    """Extract, format and add ROI coordinates to the attributes dict.

    Args:
        element (ET._Element): Element from which to extract ROI coordinates.
        attrs (dict[str, Attribute]): Attributes dict to update with ROI coordinates.

    Raises:
        KeyError: If the "ROI_N_POINTS" attribute is not found in the attributes dict.
    """
    if "ROI_N_POINTS" not in attrs:
        raise KeyError(
            f"No key 'ROI_N_POINTS' in the attributes of current element '{element.tag}'."
        )
    if element.text:
        points_coordinates = element.text.split()
        points_coordinates = [float(x) for x in points_coordinates]
        assert type(attrs["ROI_N_POINTS"]) is int, "ROI_N_POINTS should be an integer"
        points_dimension = len(points_coordinates) // attrs["ROI_N_POINTS"]
        it = [iter(points_coordinates)] * points_dimension
        points_coordinates = list(zip(*it, strict=True))
        attrs["ROI_coords"] = points_coordinates
    else:
        attrs["ROI_coords"] = None


def _add_all_nodes(
    it: ET.iterparse,
    ancestor: ET._Element,
    attrs_md: dict[str, dict[str, str]],
    graph: nx.Graph,
) -> bool:
    """Add nodes and their attributes to a graph and return the presence of segmentation.

    All the elements that are descendants of `ancestor` are explored.

    Args:
        it (ET.iterparse): An iterator over XML elements.
        ancestor (ET._Element): The XML element that encompasses the information to be added.
        attrs_md (dict[str, dict[str, str]]): The attributes metadata containing the
            expected node attributes.
        graph (nx.Graph): The graph to which the nodes will be added.

    Returns:
        bool: True if the model has segmentation data, False otherwise.

    Warns:
        UserWarning: If a node cannot be added to the graph due to missing attributes.
    """
    segmentation = False
    event, element = next(it)
    while (event, element) != ("end", ancestor):
        event, element = next(it)
        if element.tag == "Spot" and event == "end":
            # All items in element.attrib are parsed as strings but most
            # of them are numbers. So we need to do a conversion based
            # on these attributes type as defined in the attributes
            # metadata (attribute `isint`).
            attrs = deepcopy(element.attrib)
            _convert_attributes(attrs, attrs_md, "node")

            # The ROI coordinates are not stored in a tag attribute but in
            # the tag text. So we need to extract then format them.
            # In case of a single-point detection, the `ROI_N_POINTS` attribute
            # is not present.
            # TODO: waiting for polygons support in GEFF.
            # if segmentation:
            #     _convert_ROI_coordinates(element, attrs)
            # else:
            #     if "ROI_N_POINTS" in attrs:
            #         segmentation = True
            #         _convert_ROI_coordinates(element, attrs)

            # Adding the node and its attributes to the graph.
            try:
                graph.add_node(attrs["ID"], **attrs)
            except KeyError:
                warnings.warn(
                    f"No key 'ID' in the attributes of current element "
                    f"'{element.tag}'. Not adding this node to the graph.",
                    stacklevel=2,
                )
            finally:
                element.clear()

    return segmentation


def _add_edge(
    element: ET._Element,
    attrs_md: dict[str, dict[str, str]],
    graph: nx.Graph,
    current_track_id: int,
) -> None:
    """Add an edge between two nodes in the graph based on the XML element.

    This function extracts source and target node identifiers from the
    given XML element, along with any additional attributes defined
    within. It then adds an edge between these nodes in the specified
    graph. If the nodes have a 'TRACK_ID' attribute, it ensures consistency
    with the current track ID.

    Args:
        element (ET._Element): The XML element containing edge information.
        attrs_md (dict[str, dict[str, str]]): The attributes metadata containing
            the expected edge attributes.
        graph (nx.Graph): The graph to which the edge and its attributes will be added.
        current_track_id (int): Track ID of the track holding the edge.

    Raises:
        AssertionError: If the 'TRACK_ID' attribute of either the source or target node
            does not match the current track ID, indicating an inconsistency in track
            assignment.

    Warns:
        UserWarning: If an edge cannot be added due to missing required attributes.
    """
    attrs = deepcopy(element.attrib)
    _convert_attributes(attrs, attrs_md, "edge")
    try:
        entry_node_id = int(attrs["SPOT_SOURCE_ID"])
        exit_node_id = int(attrs["SPOT_TARGET_ID"])
    except KeyError:
        warnings.warn(
            f"No key 'SPOT_SOURCE_ID' or 'SPOT_TARGET_ID' in the attributes of "
            f"current element '{element.tag}'. Not adding this edge to the graph.",
            stacklevel=2,
        )
    else:
        graph.add_edge(entry_node_id, exit_node_id)
        nx.set_edge_attributes(graph, {(entry_node_id, exit_node_id): attrs})
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
    attrs_md: dict[str, dict[str, str]],
    graph: nx.Graph,
) -> list[dict[str, Attribute]]:
    """Add edges and their attributes to a graph based on the XML elements.

    This function explores all elements that are descendants of the
    specified `ancestor` element, adding edges and their attributes to
    the provided graph. It iterates through the XML elements using
    the provided iterator, extracting and processing relevant information
    to construct track attributes.

    Args:
        iterator (ET.iterparse): An iterator over XML elements.
        ancestor (ET._Element): The XML element that encompasses the information to be added.
        attrs_md (dict[str, dict[str, str]]): The attributes metadata containing the
            expected edge attributes.
        graph (nx.Graph): The graph to which the edges and their attributes will be added.

    Returns:
        list[dict[str, Attribute]]: A list of dictionaries, each representing the
            attributes for a track.

    Raises:
        KeyError: If no TRACK_ID is found in the attributes of a Track element.
    """
    tracks_attrs = []
    current_track_id = None
    event, element = next(iterator)
    while (event, element) != ("end", ancestor):
        # Saving the current track information.
        if element.tag == "Track" and event == "start":
            attrs = deepcopy(element.attrib)
            _convert_attributes(attrs, attrs_md, "lineage")
            tracks_attrs.append(attrs)
            try:
                current_track_id = attrs["TRACK_ID"]
            except KeyError as err:
                raise KeyError(
                    f"No key 'TRACK_ID' in the attributes of current element "
                    f"'{element.tag}'. Please check the XML file.",
                ) from err

        # Edge creation.
        if element.tag == "Edge" and event == "start":
            assert current_track_id is not None, "No current track ID."
            _add_edge(element, attrs_md, graph, current_track_id)

        event, element = next(iterator)

    return tracks_attrs


def _get_filtered_tracks_ID(
    iterator: ET.iterparse,
    ancestor: ET._Element,
) -> list[int]:
    """
    Extract and return a list of track IDs identifying the tracks to keep.

    Args:
        iterator (ET.iterparse): An iterator over XML elements.
        ancestor (ET._Element): The XML element that encompasses the information to be added.

    Returns:
        list[int]: List of tracks ID to identify the tracks to keep.

    Warns:
        UserWarning: If the "TRACK_ID" attribute is not found in the attributes.
    """
    filtered_tracks_ID = []
    event, element = next(iterator)
    attrs = deepcopy(element.attrib)
    try:
        filtered_tracks_ID.append(int(attrs["TRACK_ID"]))
    except KeyError:
        warnings.warn(
            f"No key 'TRACK_ID' in the attributes of current element "
            f"'{element.tag}'. Ignoring this track.",
            stacklevel=2,
        )

    while (event, element) != ("end", ancestor):
        event, element = next(iterator)
        if element.tag == "TrackID" and event == "start":
            attrs = deepcopy(element.attrib)
            try:
                filtered_tracks_ID.append(int(attrs["TRACK_ID"]))
            except KeyError:
                warnings.warn(
                    f"No key 'TRACK_ID' in the attributes of current element "
                    f"'{element.tag}'. Ignoring this track.",
                    stacklevel=2,
                )

    return filtered_tracks_ID


def _parse_model_tag(
    xml_path: Path,
    discard_filtered_spots: bool = False,
    discard_filtered_tracks: bool = False,
) -> tuple[nx.Graph, dict[str, str]]:
    """Read an XML file and convert the model data into several graphs.

    All TrackMate tracks and their associated data described in the XML file
    are modeled as a networkX graph. Spots are modeled as graph
    nodes, and edges as graph edges. Spot, edge and track features are
    stored in node, edge and graph attributes, respectively.

    Args:
        xml_path (Path): Path of the XML file to process.
        discard_filtered_spots (bool, optional): True to discard the spots
            filtered out in TrackMate, False otherwise. False by default.
        discard_filtered_tracks (bool, optional): True to discard the tracks
            filtered out in TrackMate, False otherwise. False by default.

    Returns:
        nx.Graph: A NetworkX graph representing the TrackMate data.
        dict[str, str]: A dictionary containing the units of the model, with keys
            'spatialunits' and 'timeunits'.
    """
    graph = nx.Graph()

    # So as not to load the entire XML file into memory at once, we're
    # using an iterator to browse over the tags one by one.
    # The events 'start' and 'end' correspond respectively to the opening
    # and the closing of the considered tag.
    it = ET.iterparse(xml_path, events=["start", "end"])
    _, root = next(it)  # Saving the root of the tree for later cleaning.

    for event, element in it:
        if element.tag == "Model" and event == "start":
            units = _get_units(element)
            root.clear()  # Cleaning the tree to free up some memory.
            # All the browsed subelements of `root` are deleted.

        # Get the spot, edge and track features and add them to the
        # attributes metadata.
        if element.tag == "FeatureDeclarations" and event == "start":
            attrs_md = _get_attributes_metadata(it, element)
            root.clear()

        # Adding the spots as nodes.
        if element.tag == "AllSpots" and event == "start":
            # TODO: segmentation will be used when GEFF supports polygons.
            # segmentation = _add_all_nodes(it, element, attrs_md, graph)
            _add_all_nodes(it, element, attrs_md, graph)
            root.clear()

        # Adding the tracks as edges.
        if element.tag == "AllTracks" and event == "start":
            # TODO: implement storage of track attributes.
            # tracks_attrs = _build_tracks(it, element, attrs_md, graph)
            _build_tracks(it, element, attrs_md, graph)
            root.clear()

            # Removal of filtered spots / nodes.
            if discard_filtered_spots:
                # Those nodes belong to no tracks: they have a degree of 0.
                lone_nodes = [n for n, d in graph.degree if d == 0]
                graph.remove_nodes_from(lone_nodes)

        # Filtering out tracks.
        if element.tag == "FilteredTracks" and event == "start":
            # Removal of filtered tracks.
            id_to_keep = _get_filtered_tracks_ID(it, element)
            if discard_filtered_tracks:
                to_remove = [n for n, t in graph.nodes(data="TRACK_ID") if t not in id_to_keep]
                graph.remove_nodes_from(to_remove)

        if element.tag == "Model" and event == "end":
            root.clear()

    return graph, units


def from_trackmate_xml_to_geff(
    xml_path: Path | str,
    geff_path: Path | str,
    discard_filtered_spots: bool = False,
    discard_filtered_tracks: bool = False,
    overwrite: bool = False,
    zarr_format: Literal[2, 3] = 2,
) -> None:
    """
    Convert a TrackMate XML file to a GEFF file.

    Args:
        xml_path (Path | str): The path to the TrackMate XML file.
        geff_path (Store): The path to the GEFF file.
        discard_filtered_spots (bool, optional): True to discard the spots
            filtered out in TrackMate, False otherwise. False by default.
        discard_filtered_tracks (bool, optional): True to discard the tracks
            filtered out in TrackMate, False otherwise. False by default.
        overwrite (bool, optional): Whether to overwrite the GEFF file if it already exists.
        zarr_format (Literal[2, 3], optional): The version of zarr to write. Defaults to 2.
    """
    xml_path = Path(xml_path)
    geff_path = Path(geff_path).with_suffix(".geff")
    _preliminary_checks(xml_path, geff_path, overwrite=overwrite)

    graph, units = _parse_model_tag(
        xml_path=xml_path,
        discard_filtered_spots=discard_filtered_spots,
        discard_filtered_tracks=discard_filtered_tracks,
    )
    metadata = GeffMetadata(
        axes=[
            Axis(name="POSITION_X", type="space", unit=units.get("spatialunits", "pixel")),
            Axis(name="POSITION_Y", type="space", unit=units.get("spatialunits", "pixel")),
            Axis(name="POSITION_Z", type="space", unit=units.get("spatialunits", "pixel")),
            Axis(name="POSITION_T", type="time", unit=units.get("timeunits", "frame")),
        ],
        directed=True,
        track_node_props={"lineage": "TRACK_ID"},
    )

    write_nx(
        graph,
        store=geff_path,
        metadata=metadata,
        zarr_format=zarr_format,
    )


def from_trackmate_xml_to_geff_cli(
    xml_path: Path,
    geff_path: Path,
    discard_filtered_spots: bool = False,
    discard_filtered_tracks: bool = False,
    overwrite: bool = False,
    zarr_format: int = 2,  # type: ignore
    # because of Typer not supporting Literal types
) -> None:
    """
    Convert a TrackMate XML file to a GEFF file.

    Args:
        xml_path (Path | str): The path to the TrackMate XML file.
        geff_path (Path | str): The path to the GEFF file.
        discard_filtered_spots (bool, optional): True to discard the spots
            filtered out in TrackMate, False otherwise. False by default.
        discard_filtered_tracks (bool, optional): True to discard the tracks
            filtered out in TrackMate, False otherwise. False by default.
        overwrite (bool, optional): Whether to overwrite the GEFF file if it already exists.
        zarr_format (Literal[2, 3], optional): The version of zarr to write. Defaults to 2.
    """
    from_trackmate_xml_to_geff(
        xml_path=xml_path,
        geff_path=geff_path,
        discard_filtered_spots=discard_filtered_spots,
        discard_filtered_tracks=discard_filtered_tracks,
        overwrite=overwrite,
        zarr_format=cast("Literal[2, 3]", zarr_format),
    )


app = typer.Typer()
app.command()(from_trackmate_xml_to_geff_cli)

if __name__ == "__main__":
    app()
