from copy import deepcopy
import io
from pathlib import Path

import pytest
from lxml import etree as ET

import geff.interops.trackmate_xml as tm_xml


def test_get_units():
    space_warning = "No space unit found in the XML file. Setting to 'pixel'."
    time_warning = "No time unit found in the XML file. Setting to 'frame'."

    # Both spatial and time units
    xml_data = '<Model spatialunits="µm" timeunits="min"></Model>'
    it = ET.iterparse(io.BytesIO(xml_data.encode("utf-8")), events=["start", "end"])
    _, element = next(it)
    obtained = tm_xml._get_units(element)
    expected = {"spatialunits": "µm", "timeunits": "min"}
    assert obtained == expected

    # Missing spatial units
    xml_data = '<Model timeunits="min"></Model>'
    it = ET.iterparse(io.BytesIO(xml_data.encode("utf-8")), events=["start", "end"])
    _, element = next(it)
    with pytest.warns(UserWarning, match=space_warning):
        obtained = tm_xml._get_units(element)
    expected = {"spatialunits": "pixel", "timeunits": "min"}
    assert obtained == expected

    # Missing time units
    xml_data = '<Model spatialunits="µm"></Model>'
    it = ET.iterparse(io.BytesIO(xml_data.encode("utf-8")), events=["start", "end"])
    _, element = next(it)
    with pytest.warns(UserWarning, match=time_warning):
        obtained = tm_xml._get_units(element)
    expected = {"spatialunits": "µm", "timeunits": "frame"}
    assert obtained == expected

    # Missing both spatial and time units
    xml_data = "<Model></Model>"
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
    xml_data = (
        "<FeatureDeclarations>"
        "   <SpotFeatures>"
        '       <Feature feature="QUALITY" isint="false" />'
        '       <Feature feature="FRAME" isint="true" />'
        "   </SpotFeatures>"
        "</FeatureDeclarations>"
    )
    it = ET.iterparse(io.BytesIO(xml_data.encode("utf-8")), events=["start", "end"])
    _, element = next(it)
    obtained_attrs = tm_xml._get_attributes_metadata(it, element)
    expected_attrs = {
        "QUALITY": {"isint": "false"},
        "FRAME": {"isint": "true"},
    }
    assert obtained_attrs == expected_attrs

    # Without any Feature tags
    xml_data = "<SpotFeatures></SpotFeatures>"
    it = ET.iterparse(io.BytesIO(xml_data.encode("utf-8")), events=["start", "end"])
    _, element = next(it)
    obtained_attrs = tm_xml._get_attributes_metadata(it, element)
    assert obtained_attrs == {}

    # With non Feature tag
    xml_data = (
        "<FeatureDeclarations>"
        "   <SpotFeatures>"
        '       <Feature feature="QUALITY" isint="false" />'
        '       <Other feature="FRAME" isint="true" />'
        "   </SpotFeatures>"
        "</FeatureDeclarations>"
    )
    it = ET.iterparse(io.BytesIO(xml_data.encode("utf-8")), events=["start", "end"])
    _, element = next(it)
    obtained_attrs = tm_xml._get_attributes_metadata(it, element)
    expected_attrs = {"QUALITY": {"isint": "false"}}
    assert obtained_attrs == expected_attrs


# def _convert_attributes(
#     attrs: dict[str, Attribute],
#     attrs_metadata: dict[str, dict[str, str]],
#     attr_type: str,
# ) -> None:


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
    # Only ID attribute
    # NO nodes attributes
    # No nodes
    pass
