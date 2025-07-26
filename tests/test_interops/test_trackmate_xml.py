import io
from copy import deepcopy

import networkx as nx
import pytest

import geff.interops.trackmate_xml as tm_xml
from geff.utils import nx_is_equal, validate

try:
    from lxml import etree as ET
except ImportError:
    import xml.etree.ElementTree as ET


def test_get_units():
    space_warning = "No space unit found in the XML file. Setting to 'pixel'."
    time_warning = "No time unit found in the XML file. Setting to 'frame'."

    # Both spatial and time units
    xml_data = """<Model spatialunits="µm" timeunits="min"></Model>"""
    it = ET.iterparse(io.BytesIO(xml_data.encode("utf-8")), events=["start", "end"])
    _, element = next(it)
    obtained = tm_xml._get_units(element)
    expected = {"spatialunits": "µm", "timeunits": "min"}
    assert obtained == expected

    # Missing spatial units
    xml_data = """<Model timeunits="min"></Model>"""
    it = ET.iterparse(io.BytesIO(xml_data.encode("utf-8")), events=["start", "end"])
    _, element = next(it)
    with pytest.warns(UserWarning, match=space_warning):
        obtained = tm_xml._get_units(element)
    expected = {"spatialunits": "pixel", "timeunits": "min"}
    assert obtained == expected

    # Missing time units
    xml_data = """<Model spatialunits="µm"></Model>"""
    it = ET.iterparse(io.BytesIO(xml_data.encode("utf-8")), events=["start", "end"])
    _, element = next(it)
    with pytest.warns(UserWarning, match=time_warning):
        obtained = tm_xml._get_units(element)
    expected = {"spatialunits": "µm", "timeunits": "frame"}
    assert obtained == expected

    # Missing both spatial and time units
    xml_data = """<Model></Model>"""
    it = ET.iterparse(io.BytesIO(xml_data.encode("utf-8")), events=["start", "end"])
    _, element = next(it)
    with pytest.warns() as warning_list:
        obtained = tm_xml._get_units(element)
    expected = {"spatialunits": "pixel", "timeunits": "frame"}
    assert obtained == expected
    assert len(warning_list) == 2
    assert space_warning in str(warning_list[0].message)
    assert time_warning in str(warning_list[1].message)


def test_get_attributes_metadata():
    # Several attributes with Feature tags
    xml_data = """
        <FeatureDeclarations>
            <SpotFeatures>
                <Feature feature="QUALITY" isint="false" />
                <Feature feature="FRAME" isint="true" />
            </SpotFeatures>
        </FeatureDeclarations>
    """
    it = ET.iterparse(io.BytesIO(xml_data.encode("utf-8")), events=["start", "end"])
    _, element = next(it)
    obtained_attrs = tm_xml._get_attributes_metadata(it, element)
    expected_attrs = {
        "QUALITY": {"isint": "false"},
        "FRAME": {"isint": "true"},
    }
    assert obtained_attrs == expected_attrs

    # Without any Feature tags
    xml_data = """<SpotFeatures></SpotFeatures>"""
    it = ET.iterparse(io.BytesIO(xml_data.encode("utf-8")), events=["start", "end"])
    _, element = next(it)
    obtained_attrs = tm_xml._get_attributes_metadata(it, element)
    assert obtained_attrs == {}

    # With non Feature tag
    xml_data = """
        <FeatureDeclarations>
            <SpotFeatures>
                <Feature feature="QUALITY" isint="false" />
                <Other feature="FRAME" isint="true" />
            </SpotFeatures>
        </FeatureDeclarations>
    """
    it = ET.iterparse(io.BytesIO(xml_data.encode("utf-8")), events=["start", "end"])
    _, element = next(it)
    obtained_attrs = tm_xml._get_attributes_metadata(it, element)
    expected_attrs = {"QUALITY": {"isint": "false"}}
    assert obtained_attrs == expected_attrs


def test_convert_attributes():
    # Normal conversion with various data types
    attrs_md = {
        "feat_float": {"name": "feat_float", "isint": "false", "random": "info1"},
        "feat_int": {"name": "feat_int", "isint": "true", "random": "info1"},
        "feat_neg": {"name": "feat_neg", "isint": "true", "random": "info2"},
        "feat_string": {"name": "feat_string", "isint": "false", "random": "info3"},
    }
    converted_attrs = {
        "feat_float": "30",
        "feat_int": "20",
        "feat_neg": "-10",
        "feat_string": "nope",
    }
    tm_xml._convert_attributes(converted_attrs, attrs_md, "node")
    expected_attr = {
        "feat_float": 30.0,
        "feat_int": 20,
        "feat_neg": -10.0,
        "feat_string": "nope",
    }
    assert converted_attrs == expected_attr

    # Special attributes
    attrs_md = {}
    converted_attrs = {"ID": "42", "name": "ID42", "ROI_N_POINTS": "10"}
    tm_xml._convert_attributes(converted_attrs, attrs_md, "node")
    expected_attr = {"ID": 42, "name": "ID42", "ROI_N_POINTS": 10}
    assert converted_attrs == expected_attr

    # ValueError for invalid integer conversion
    attrs_md = {
        "feat_int": {"name": "feat_int", "isint": "true", "random": "info1"},
    }
    converted_attrs = {"feat_int": "not_an_int"}
    with pytest.raises(ValueError, match="Invalid integer value for feat_int: not_an_int"):
        tm_xml._convert_attributes(converted_attrs, attrs_md, "node")

    # Missing attribute in metadata
    attrs_md = {
        "feat_float": {"name": "feat_float", "isint": "false", "random": "info1"},
        "feat_string": {"name": "feat_string", "isint": "false", "random": "info3"},
    }
    converted_attrs = {"feat_int": "10"}
    with pytest.warns(
        UserWarning, match="Node attribute feat_int not found in the attributes metadata."
    ):
        tm_xml._convert_attributes(converted_attrs, attrs_md, "node")


def test_convert_ROI_coordinates():
    # 2D points
    el_obtained = ET.Element("Spot")
    el_obtained.attrib["ROI_N_POINTS"] = "3"
    el_obtained.text = "1 2.0 -3 -4.0 5.5 6"
    attr_obtained = deepcopy(el_obtained.attrib)
    attr_obtained["ROI_N_POINTS"] = int(attr_obtained["ROI_N_POINTS"])
    tm_xml._convert_ROI_coordinates(el_obtained, attr_obtained)
    attr_expected = {
        "ROI_N_POINTS": 3,
        "ROI_coords": [(1.0, 2.0), (-3.0, -4.0), (5.5, 6.0)],
    }
    assert attr_obtained == attr_expected

    # 3D points
    el_obtained = ET.Element("Spot")
    el_obtained.attrib["ROI_N_POINTS"] = "2"
    el_obtained.text = "1 2.0 -3 -4.0 5.5 6"
    attr_obtained = deepcopy(el_obtained.attrib)
    attr_obtained["ROI_N_POINTS"] = int(attr_obtained["ROI_N_POINTS"])
    tm_xml._convert_ROI_coordinates(el_obtained, attr_obtained)
    attr_expected = {
        "ROI_N_POINTS": 2,
        "ROI_coords": [(1.0, 2.0, -3.0), (-4.0, 5.5, 6.0)],
    }
    assert attr_obtained == attr_expected

    # KeyError for missing ROI_N_POINTS
    el_obtained = ET.Element("Spot")
    el_obtained.text = "1 2.0 -3 -4.0 5.5 6"
    attr_obtained = deepcopy(el_obtained.attrib)
    with pytest.raises(
        KeyError, match="No key 'ROI_N_POINTS' in the attributes of current element 'Spot'"
    ):
        tm_xml._convert_ROI_coordinates(el_obtained, attr_obtained)

    # No coordinates
    el_obtained = ET.Element("Spot")
    el_obtained.attrib["ROI_N_POINTS"] = "2"
    attr_obtained = deepcopy(el_obtained.attrib)
    attr_obtained["ROI_N_POINTS"] = int(attr_obtained["ROI_N_POINTS"])
    tm_xml._convert_ROI_coordinates(el_obtained, attr_obtained)
    attr_expected = {"ROI_N_POINTS": 2, "ROI_coords": None}
    assert attr_obtained == attr_expected


def test_add_all_nodes():
    # Several attributes
    xml_data = """
        <data>
           <frame>
               <Spot name="ID1000" ID="1000" x="10" y="20" />
               <Spot name="ID1001" ID="1001" x="30.5" y="30" />
           </frame>
        </data>
    """
    it = ET.iterparse(io.BytesIO(xml_data.encode("utf-8")), events=["start", "end"])
    _, element = next(it)
    attrs_md = {
        "x": {"name": "x", "isint": "false", "random": "info1"},
        "y": {"name": "y", "isint": "true", "random": "info3"},
    }
    obtained = nx.DiGraph()
    tm_xml._add_all_nodes(it, element, attrs_md, obtained)
    expected = nx.DiGraph()
    expected.add_nodes_from(
        [
            (1001, {"name": "ID1001", "y": 30, "ID": 1001, "x": 30.5}),
            (1000, {"name": "ID1000", "ID": 1000, "x": 10.0, "y": 20}),
        ]
    )
    assert nx_is_equal(obtained, expected)

    # Only ID attribute
    xml_data = """
        <data>
           <frame>
               <Spot ID="1000" />
               <Spot ID="1001" />
           </frame>
        </data>
    """
    it = ET.iterparse(io.BytesIO(xml_data.encode("utf-8")), events=["start", "end"])
    _, element = next(it)
    obtained = nx.DiGraph()
    tm_xml._add_all_nodes(it, element, {}, obtained)
    expected = nx.DiGraph()
    expected.add_nodes_from([(1001, {"ID": 1001}), (1000, {"ID": 1000})])
    assert nx_is_equal(obtained, expected)

    # No nodes
    xml_data = """
        <data>
            <frame />
        </data>
    """
    it = ET.iterparse(io.BytesIO(xml_data.encode("utf-8")), events=["start", "end"])
    _, element = next(it)
    obtained = nx.DiGraph()
    tm_xml._add_all_nodes(it, element, {}, obtained)
    assert nx_is_equal(obtained, nx.DiGraph())

    # No ID attribute
    xml_data = """
        <data>
            <frame>
                <Spot />
                <Spot ID="1001" />
            </frame>
        </data>
    """
    it = ET.iterparse(io.BytesIO(xml_data.encode("utf-8")), events=["start", "end"])
    _, element = next(it)
    msg = (
        "No key 'ID' in the attributes of current element 'Spot'. "
        "Not adding this node to the graph."
    )
    with pytest.warns(UserWarning, match=msg):
        tm_xml._add_all_nodes(it, element, {}, nx.DiGraph())


def test_add_edge():
    # Normal case with several attributes
    xml_data = """<data SPOT_SOURCE_ID="1" SPOT_TARGET_ID="2" x="20.5" y="25" />"""
    it = ET.iterparse(io.BytesIO(xml_data.encode("utf-8")), events=["start", "end"])
    _, element = next(it)
    track_id = 0
    attrs_md = {
        "x": {"name": "x", "isint": "false", "random": "info1"},
        "y": {"name": "y", "isint": "true", "random": "info3"},
        "SPOT_SOURCE_ID": {"name": "SPOT_SOURCE_ID", "isint": "true", "random": "info2"},
        "SPOT_TARGET_ID": {"name": "SPOT_TARGET_ID", "isint": "true", "random": "info4"},
    }
    obtained = nx.DiGraph()
    tm_xml._add_edge(element, attrs_md, obtained, track_id)
    expected = nx.DiGraph()
    expected.add_edge(1, 2, x=20.5, y=25, SPOT_SOURCE_ID=1, SPOT_TARGET_ID=2)
    expected.nodes[1]["TRACK_ID"] = track_id
    expected.nodes[2]["TRACK_ID"] = track_id
    assert nx_is_equal(obtained, expected)

    # No edge attributes
    xml_data = """<data SPOT_SOURCE_ID="1" SPOT_TARGET_ID="2" />"""
    it = ET.iterparse(io.BytesIO(xml_data.encode("utf-8")), events=["start", "end"])
    _, element = next(it)
    track_id = 0
    attrs_md = {
        "x": {"name": "x", "isint": "false", "random": "info1"},
        "y": {"name": "y", "isint": "true", "random": "info3"},
        "SPOT_SOURCE_ID": {"name": "SPOT_SOURCE_ID", "isint": "true", "random": "info2"},
        "SPOT_TARGET_ID": {"name": "SPOT_TARGET_ID", "isint": "true", "random": "info4"},
    }
    obtained = nx.DiGraph()
    tm_xml._add_edge(element, attrs_md, obtained, track_id)
    expected = nx.DiGraph()
    expected.add_edge(1, 2, SPOT_SOURCE_ID=1, SPOT_TARGET_ID=2)
    expected.nodes[1]["TRACK_ID"] = track_id
    expected.nodes[2]["TRACK_ID"] = track_id
    assert nx_is_equal(obtained, expected)

    # Missing SPOT_TARGET_ID
    xml_data = """<data SPOT_SOURCE_ID="1" x="20.5" y="25" />"""
    it = ET.iterparse(io.BytesIO(xml_data.encode("utf-8")), events=["start", "end"])
    _, element = next(it)
    attrs_md = {
        "x": {"name": "x", "isint": "false", "random": "info1"},
        "y": {"name": "y", "isint": "true", "random": "info3"},
        "SPOT_SOURCE_ID": {"name": "SPOT_SOURCE_ID", "isint": "true", "random": "info2"},
        "SPOT_TARGET_ID": {"name": "SPOT_TARGET_ID", "isint": "true", "random": "info4"},
    }
    with pytest.warns(
        UserWarning,
        match=(
            "No key 'SPOT_SOURCE_ID' or 'SPOT_TARGET_ID' in the attributes of "
            "current element 'data'. Not adding this edge to the graph."
        ),
    ):
        tm_xml._add_edge(element, attrs_md, nx.DiGraph(), track_id)

    # Inconsistent TRACK_ID
    xml_data = """<data SPOT_SOURCE_ID="1" SPOT_TARGET_ID="2" x="20.5" y="25" />"""
    it = ET.iterparse(io.BytesIO(xml_data.encode("utf-8")), events=["start", "end"])
    _, element = next(it)
    attrs_md = {
        "x": {"name": "x", "isint": "false", "random": "info1"},
        "y": {"name": "y", "isint": "true", "random": "info3"},
        "SPOT_SOURCE_ID": {"name": "SPOT_SOURCE_ID", "isint": "true", "random": "info2"},
        "SPOT_TARGET_ID": {"name": "SPOT_TARGET_ID", "isint": "true", "random": "info4"},
    }
    obtained = nx.DiGraph()
    obtained.add_nodes_from([(1, {"TRACK_ID": 1}), (2, {"TRACK_ID": 2})])
    with pytest.raises(
        AssertionError,
        match="Incoherent track ID for nodes 1 and 2.",
    ):
        tm_xml._add_edge(element, attrs_md, obtained, 1)


def test_build_tracks():
    # Normal case with several attributes
    xml_data = """
        <data>
            <Track TRACK_ID="1" name="blob">
                <Edge SPOT_SOURCE_ID="11" SPOT_TARGET_ID="12" x="10.5" y="20" />
                <Edge SPOT_SOURCE_ID="12" SPOT_TARGET_ID="13" x="30" y="30" />
            </Track>
            <Track TRACK_ID="2" name="blub">
                <Edge SPOT_SOURCE_ID="21" SPOT_TARGET_ID="22" x="15.2" y="25" />
            </Track>
        </data>
    """
    it = ET.iterparse(io.BytesIO(xml_data.encode("utf-8")), events=["start", "end"])
    _, element = next(it)
    attrs_md = {
        "x": {"name": "x", "isint": "false", "random": "info1"},
        "y": {"name": "y", "isint": "true", "random": "info3"},
        "SPOT_SOURCE_ID": {"name": "SPOT_SOURCE_ID", "isint": "true", "random": "info2"},
        "SPOT_TARGET_ID": {"name": "SPOT_TARGET_ID", "isint": "true", "random": "info4"},
        "TRACK_ID": {"name": "TRACK_ID", "isint": "true", "random": "info5"},
    }
    obtained = nx.DiGraph()
    obtained_tracks_attrib = tm_xml._build_tracks(it, element, attrs_md, obtained)
    obtained_tracks_attrib = sorted(obtained_tracks_attrib, key=lambda d: d["TRACK_ID"])
    expected = nx.DiGraph()
    expected.add_edge(11, 12, SPOT_SOURCE_ID=11, SPOT_TARGET_ID=12, x=10.5, y=20)
    expected.add_edge(12, 13, SPOT_SOURCE_ID=12, SPOT_TARGET_ID=13, x=30.0, y=30)
    expected.add_edge(21, 22, SPOT_SOURCE_ID=21, SPOT_TARGET_ID=22, x=15.2, y=25)
    expected.add_nodes_from(
        [
            (11, {"TRACK_ID": 1}),
            (12, {"TRACK_ID": 1}),
            (13, {"TRACK_ID": 1}),
            (21, {"TRACK_ID": 2}),
            (22, {"TRACK_ID": 2}),
        ]
    )
    expected_tracks_attrib = [
        {"TRACK_ID": 2, "name": "blub"},
        {"TRACK_ID": 1, "name": "blob"},
    ]
    expected_tracks_attrib = sorted(expected_tracks_attrib, key=lambda d: d["TRACK_ID"])
    assert nx_is_equal(obtained, expected)
    assert obtained_tracks_attrib == expected_tracks_attrib

    # No edges in the tracks
    xml_data = """
        <data>
            <Track TRACK_ID="1" name="blob" />
            <Track TRACK_ID="2" name="blub" />
        </data>
    """
    it = ET.iterparse(io.BytesIO(xml_data.encode("utf-8")), events=["start", "end"])
    _, element = next(it)
    attrs_md = {
        "TRACK_ID": {"name": "TRACK_ID", "isint": "true", "random": "info5"},
    }
    obtained = nx.DiGraph()
    obtained_tracks_attrib = tm_xml._build_tracks(it, element, attrs_md, obtained)
    obtained_tracks_attrib = sorted(obtained_tracks_attrib, key=lambda d: d["TRACK_ID"])
    expected = nx.DiGraph()
    expected_tracks_attrib = [
        {"TRACK_ID": 2, "name": "blub"},
        {"TRACK_ID": 1, "name": "blob"},
    ]
    expected_tracks_attrib = sorted(expected_tracks_attrib, key=lambda d: d["TRACK_ID"])
    assert nx_is_equal(obtained, expected)
    assert obtained_tracks_attrib == expected_tracks_attrib

    # No node ID
    xml_data = """
        <data>
            <Track TRACK_ID="1" name="blob">
                <Edge x="10" y="20" />
                <Edge x="30" y="30" />
            </Track>
            <Track TRACK_ID="2" name="blub">
                <Edge x="15" y="25" />
            </Track>
        </data>
    """
    it = ET.iterparse(io.BytesIO(xml_data.encode("utf-8")), events=["start", "end"])
    _, element = next(it)
    attrs_md = {
        "x": {"name": "x", "isint": "false", "random": "info1"},
        "y": {"name": "y", "isint": "true", "random": "info3"},
        "TRACK_ID": {"name": "TRACK_ID", "isint": "true", "random": "info5"},
    }
    obtained = nx.DiGraph()
    with pytest.warns(
        UserWarning,
        match=(
            "No key 'SPOT_SOURCE_ID' or 'SPOT_TARGET_ID' in the attributes of "
            "current element 'Edge'. Not adding this edge to the graph."
        ),
    ):
        tm_xml._build_tracks(it, element, attrs_md, obtained)

    # No track ID
    xml_data = """
        <data>
            <Track name="blob">
                <Edge SPOT_SOURCE_ID="11" SPOT_TARGET_ID="12" x="10" y="20" />
                <Edge SPOT_SOURCE_ID="12" SPOT_TARGET_ID="13" x="30" y="30" />
            </Track>
            <Track name="blub">
                <Edge SPOT_SOURCE_ID="21" SPOT_TARGET_ID="22" x="15" y="25" />
            </Track>
        </data>
    """
    it = ET.iterparse(io.BytesIO(xml_data.encode("utf-8")), events=["start", "end"])
    _, element = next(it)
    attrs_md = {
        "x": {"name": "x", "isint": "false", "random": "info1"},
        "y": {"name": "y", "isint": "true", "random": "info3"},
        "SPOT_SOURCE_ID": {"name": "SPOT_SOURCE_ID", "isint": "true", "random": "info2"},
        "SPOT_TARGET_ID": {"name": "SPOT_TARGET_ID", "isint": "true", "random": "info4"},
    }
    with pytest.raises(
        KeyError,
        match=(
            "No key 'TRACK_ID' in the attributes of current element 'Track'. "
            "Please check the XML file."
        ),
    ):
        tm_xml._build_tracks(it, element, attrs_md, nx.DiGraph())


def test_get_filtered_tracks_ID():
    # Normal case with TRACK_ID attributes
    xml_data = """
        <data>
            <TrackID TRACK_ID="0" />
            <TrackID TRACK_ID="1" />
        </data>
    """
    it = ET.iterparse(io.BytesIO(xml_data.encode("utf-8")), events=["start", "end"])
    _, element = next(it)
    obtained_ID = tm_xml._get_filtered_tracks_ID(it, element)
    expected_ID = [0, 1]
    assert obtained_ID.sort() == expected_ID.sort()

    # No TRACK_ID
    xml_data = """
        <data>
            <TrackID />
            <TrackID />
        </data>
    """
    it = ET.iterparse(io.BytesIO(xml_data.encode("utf-8")), events=["start", "end"])
    _, element = next(it)
    with pytest.warns(
        UserWarning,
        match=(
            "No key 'TRACK_ID' in the attributes of current element 'TrackID'. Ignoring this track."
        ),
    ):
        tm_xml._get_filtered_tracks_ID(it, element)

    # No Track elements
    xml_data = """
        <data>
            <tag />
            <tag />
        </data>
    """
    it = ET.iterparse(io.BytesIO(xml_data.encode("utf-8")), events=["start", "end"])
    _, element = next(it)
    with pytest.warns(
        UserWarning,
        match=(
            "No key 'TRACK_ID' in the attributes of current element 'tag'. Ignoring this track."
        ),
    ):
        tm_xml._get_filtered_tracks_ID(it, element)


def test_from_trackmate_xml_to_geff(tmp_path):
    # No arguments, should use default values
    geff_output = tmp_path / "test.geff"
    tm_xml.from_trackmate_xml_to_geff("tests/data/FakeTracks.xml", geff_output)
    validate(geff_output)

    # Discard filtered spots and tracks
    tm_xml.from_trackmate_xml_to_geff(
        "tests/data/FakeTracks.xml",
        geff_output,
        discard_filtered_spots=True,
        discard_filtered_tracks=True,
        overwrite=True,
    )
    validate(geff_output)

    # Geff file already exists
    with pytest.raises(FileExistsError):
        tm_xml.from_trackmate_xml_to_geff(
            "tests/data/FakeTracks.xml",
            geff_output,
        )
