import io
from copy import deepcopy

import networkx as nx
import networkx.algorithms.isomorphism as iso
import pytest
from lxml import etree as ET

import geff.interops.trackmate_xml as tm_xml


def is_equal(obt, exp):
    """Check if two graphs are perfectly identical.

    It checks that the graphs are isomorphic, and that their graph,
    nodes and edges attributes are all identical.

    Args:
        obt (nx.Graph): The obtained graph, built from trackmate_xml.py.
        exp (nx.Graph): The expected graph, built from here.

    Returns:
        bool: True if the graphs are identical, False otherwise.
    """
    edges_attr = list({k for (n1, n2, d) in exp.edges.data() for k in d})
    edges_default = len(edges_attr) * [0]
    em = iso.categorical_edge_match(edges_attr, edges_default)
    nodes_attr = list({k for (n, d) in exp.nodes.data() for k in d})
    nodes_default = len(nodes_attr) * [0]
    nm = iso.categorical_node_match(nodes_attr, nodes_default)

    if not obt.nodes.data() and not exp.nodes.data():
        same_nodes = True
    elif len(obt.nodes.data()) != len(exp.nodes.data()):
        same_nodes = False
    else:
        for data1, data2 in zip(sorted(obt.nodes.data()), sorted(exp.nodes.data()), strict=False):
            n1, attr1 = data1
            n2, attr2 = data2
            if sorted(attr1) == sorted(attr2) and n1 == n2:
                same_nodes = True
            else:
                same_nodes = False

    if not obt.edges.data() and not exp.edges.data():
        same_edges = True
    elif len(obt.edges.data()) != len(exp.edges.data()):
        same_edges = False
    else:
        for data1, data2 in zip(sorted(obt.edges.data()), sorted(exp.edges.data()), strict=False):
            n11, n12, attr1 = data1
            n21, n22, attr2 = data2
            if sorted(attr1) == sorted(attr2) and sorted((n11, n12)) == sorted((n21, n22)):
                same_edges = True
            else:
                same_edges = False

    if (
        nx.is_isomorphic(obt, exp, edge_match=em, node_match=nm)
        and obt.graph == exp.graph
        and same_nodes
        and same_edges
    ):
        return True
    else:
        return False


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
    obtained = nx.Graph()
    tm_xml._add_all_nodes(it, element, attrs_md, obtained)
    expected = nx.Graph()
    expected.add_nodes_from(
        [
            (1001, {"name": "ID1001", "y": 30, "ID": 1001, "x": 30.5}),
            (1000, {"name": "ID1000", "ID": 1000, "x": 10.0, "y": 20}),
        ]
    )
    assert is_equal(obtained, expected)

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
    obtained = nx.Graph()
    tm_xml._add_all_nodes(it, element, {}, obtained)
    expected = nx.Graph()
    expected.add_nodes_from([(1001, {"ID": 1001}), (1000, {"ID": 1000})])
    assert is_equal(obtained, expected)

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
    obtained = nx.Graph()
    msg = (
        "No key 'ID' in the attributes of current element 'Spot'. "
        "Not adding this node to the graph."
    )
    with pytest.warns(UserWarning, match=msg):
        tm_xml._add_all_nodes(it, element, {}, obtained)

    # No nodes
    xml_data = """
        <data>
            <frame />
        </data>
    """
    it = ET.iterparse(io.BytesIO(xml_data.encode("utf-8")), events=["start", "end"])
    _, element = next(it)
    obtained = nx.Graph()
    tm_xml._add_all_nodes(it, element, {}, obtained)
    assert is_equal(obtained, nx.Graph())


def test_add_edge():
    pass


def test_build_tracks():
    pass


def test_get_filtered_tracks_ID():
    pass
