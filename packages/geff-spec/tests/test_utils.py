import numpy as np
import pytest

from geff_spec import Axis, GeffMetadata, PropMetadata
from geff_spec.utils import (
    add_or_update_props_metadata,
    compute_and_add_axis_min_max,
    create_props_metadata,
    update_metadata_axes,
)


class TestCreateOrUpdatePropsMetadata:
    """Test cases for create_or_update_props_metadata function."""

    def test_create_node_props_metadata_from_empty(self):
        """Test creating node props metadata when metadata has empty node props."""
        metadata = GeffMetadata(
            directed=False,
            node_props_metadata={},
            edge_props_metadata={},
        )
        props_md = [
            PropMetadata(identifier="prop1", dtype="int64"),
            PropMetadata(identifier="prop2", dtype="float32"),
        ]
        result = add_or_update_props_metadata(metadata, props_md, "node")
        assert result.node_props_metadata == {
            "prop1": PropMetadata(identifier="prop1", dtype="int64"),
            "prop2": PropMetadata(identifier="prop2", dtype="float32"),
        }

    def test_create_edge_props_metadata_from_none(self):
        """Test creating edge props metadata when metadata has no existing edge props."""
        metadata = GeffMetadata(
            directed=True,
            node_props_metadata={},
            edge_props_metadata={},
        )
        props_md = [
            PropMetadata(identifier="prop1", dtype="float64"),
            PropMetadata(identifier="prop2", dtype="str"),
        ]
        result = add_or_update_props_metadata(metadata, props_md, "edge")
        assert result.edge_props_metadata == {
            "prop1": PropMetadata(identifier="prop1", dtype="float64"),
            "prop2": PropMetadata(identifier="prop2", dtype="str"),
        }

    def test_update_existing_node_props_metadata(self):
        """Test updating existing node props metadata."""
        existing_props = {"existing_prop": PropMetadata(identifier="existing_prop", dtype="int32")}
        metadata = GeffMetadata(
            directed=True,
            node_props_metadata=existing_props,
            edge_props_metadata={},
        )
        props_md = [
            PropMetadata(identifier="new_prop", dtype="float64", name="New prop"),
        ]
        result = add_or_update_props_metadata(metadata, props_md, "node")
        assert len(result.node_props_metadata) == 2
        assert "existing_prop" in result.node_props_metadata
        assert "new_prop" in result.node_props_metadata

    def test_update_existing_edge_props_metadata(self):
        """Test updating existing edge props metadata."""
        existing_props = {
            "existing_edge_prop": PropMetadata(identifier="existing_edge_prop", dtype="bool")
        }
        metadata = GeffMetadata(
            directed=True,
            node_props_metadata={},
            edge_props_metadata=existing_props,
        )
        props_md = [
            PropMetadata(identifier="new_edge_prop", dtype="str"),
        ]
        result = add_or_update_props_metadata(metadata, props_md, "edge")
        assert len(result.edge_props_metadata) == 2
        assert "existing_edge_prop" in result.edge_props_metadata
        assert "new_edge_prop" in result.edge_props_metadata

    def test_overwrite_existing_prop(self):
        """Test that existing props are overwritten when same identifier is provided."""
        existing_props = {"prop1": PropMetadata(identifier="prop1", dtype="int32")}
        metadata = GeffMetadata(
            directed=True,
            node_props_metadata=existing_props,
            edge_props_metadata={},
        )
        props_md = [
            PropMetadata(identifier="prop1", dtype="float64"),
        ]
        result = add_or_update_props_metadata(metadata, props_md, "node")
        assert len(result.node_props_metadata) == 1
        assert result.node_props_metadata["prop1"].dtype == "float64"

    def test_empty_props_md_list(self):
        """Test handling of empty props metadata list."""
        existing_props = {"existing_prop": PropMetadata(identifier="existing_prop", dtype="int32")}
        metadata = GeffMetadata(
            directed=True,
            node_props_metadata=existing_props,
            edge_props_metadata={},
        )
        result = add_or_update_props_metadata(metadata, [], "node")
        assert len(result.node_props_metadata) == 1
        assert "existing_prop" in result.node_props_metadata

    def test_multiple_props_same_call(self):
        """Test adding multiple props in a single call."""
        existing_props = {"newprop": PropMetadata(identifier="newprop", dtype="int")}
        metadata = GeffMetadata(
            directed=True,
            node_props_metadata={},
            edge_props_metadata=existing_props,
        )
        props_md = [
            PropMetadata(identifier="newprop1", dtype="float64"),
            PropMetadata(identifier="newprop2", dtype="str"),
            PropMetadata(identifier="newprop3", dtype="bool"),
        ]
        result = add_or_update_props_metadata(metadata, props_md, "edge")
        assert len(result.edge_props_metadata) == 4
        assert "newprop" in result.edge_props_metadata
        assert "newprop1" in result.edge_props_metadata
        assert "newprop2" in result.edge_props_metadata
        assert "newprop3" in result.edge_props_metadata
        assert result.edge_props_metadata["newprop"].dtype == "int64"
        assert result.edge_props_metadata["newprop1"].dtype == "float64"
        assert result.edge_props_metadata["newprop2"].dtype == "str"
        assert result.edge_props_metadata["newprop3"].dtype == "bool"

    def test_invalid_c_type_raises_error(self):
        """Test that invalid c_type parameter raises appropriate error."""
        metadata = GeffMetadata(
            geff_version="0.1.0",
            directed=True,
            node_props_metadata={},
            edge_props_metadata={},
        )
        props_md = [PropMetadata(identifier="prop1", dtype="int64")]
        with pytest.raises(ValueError):
            add_or_update_props_metadata(metadata, props_md, "invalid_type")


class TestCreatePropMetadata:
    """Test cases for create_prop_metadata function."""

    def test_normal_prop_int(self):
        """Test creating PropMetadata from normal integer property."""
        values = np.array([1, 2, 3, 4], dtype=np.int64)
        prop_data = {"values": values, "missing": None}

        result = create_props_metadata("test_prop", prop_data)

        assert result.identifier == "test_prop"
        assert result.dtype == "int64"
        assert not result.varlength
        assert result.unit is None
        assert result.name is None
        assert result.description is None

    def test_normal_prop_float_with_missing(self):
        """Test creating PropMetadata from normal float property with missing values."""
        values = np.array([1.5, 2.0, 0.0, 4.2], dtype=np.float32)
        missing = np.array([False, False, True, False], dtype=bool)
        prop_data = {"values": values, "missing": missing}

        result = create_props_metadata("float_prop", prop_data, unit="meters", name="Distance")

        assert result.identifier == "float_prop"
        assert result.dtype == "float32"
        assert not result.varlength
        assert result.unit == "meters"
        assert result.name == "Distance"
        assert result.description is None

    def test_normal_prop_string(self):
        """Test creating PropMetadata from normal string property."""
        values = np.array(["apple", "banana", "cherry"], dtype=np.str_)
        prop_data = {"values": values, "missing": None}

        result = create_props_metadata("fruit", prop_data, description="Types of fruit")

        assert result.identifier == "fruit"
        assert np.issubdtype(result.dtype, "U")
        assert not result.varlength
        assert result.unit is None
        assert result.name is None
        assert result.description == "Types of fruit"

    def test_varlen_prop_valid(self):
        """Test creating PropMetadata from variable length property."""
        arr1 = np.array([1, 2], dtype=np.int32)
        arr2 = np.array([3, 4, 5], dtype=np.int32)
        arr3 = np.array([6], dtype=np.int32)
        prop_data = {"values": np.array([arr1, arr2, arr3], dtype=object)}

        result = create_props_metadata("varlen_prop", prop_data)

        assert result.identifier == "varlen_prop"
        assert result.dtype == "int32"
        assert result.varlength
        assert result.unit is None

    def test_varlen_prop_with_none_values(self):
        """Test creating PropMetadata from variable length property with some None values."""
        arr1 = np.array([1.0, 2.0], dtype=np.float64)
        arr2 = np.array([], dtype=np.float64)
        arr3 = np.array([3.0, 4.0, 5.0], dtype=np.float64)
        prop_data = {
            "values": np.array([arr1, arr2, arr3], dtype=object),
            "missing": np.array([0, 1, 0], dtype=bool),
        }

        result = create_props_metadata("sparse_varlen", prop_data, unit="kg")

        assert result.identifier == "sparse_varlen"
        assert result.dtype == "float64"
        assert result.varlength
        assert result.unit == "kg"

    def test_varlen_prop_all_none_raises_error(self):
        """Test that variable length property with mixed dtypes raises ValueError."""

        arr1 = np.array([1, 2], dtype=np.int32)
        arr2 = np.array([3, 4, 5], dtype=np.int32)
        arr3 = np.array([6], dtype=np.int64)
        prop_data = {"values": np.array([arr1, arr2, arr3], dtype=object)}

        with pytest.raises(
            ValueError, match="Object array containing variable length properties has two dtypes.*"
        ):
            create_props_metadata("mixed_dtype", prop_data)

    def test_invalid_prop_data_raises_error(self):
        """Test that invalid property data raises ValueError."""
        invalid_data = "not_valid_data"

        with pytest.raises(ValueError, match="Expected dict of property data, got.*"):
            create_props_metadata("invalid", invalid_data)

    def test_all_optional_parameters(self):
        """Test creating PropMetadata with all optional parameters provided."""
        values = np.array([True, False, True], dtype=bool)
        prop_data = {"values": values, "missing": None}

        result = create_props_metadata(
            identifier="bool_prop",
            prop_data=prop_data,
            unit="boolean",
            name="Boolean Flag",
            description="A test boolean property",
        )

        assert result.identifier == "bool_prop"
        assert result.dtype == "bool"
        assert not result.varlength
        assert result.unit == "boolean"
        assert result.name == "Boolean Flag"
        assert result.description == "A test boolean property"

    def test_cast_to_float(self):
        values = np.array([0.1, 0.2, 0.3], dtype=np.float16)
        prop_data = {"values": values, "missing": None}
        with pytest.warns(
            UserWarning, match="Dtype float16 is being upcast to float32 for Java compatibility"
        ):
            result = create_props_metadata(identifier="float16_test", prop_data=prop_data)
        assert result.dtype == "float32"
        assert np.issubdtype(prop_data["values"].dtype, np.float32)


class TestUpdateMetadataAxes:
    def test_valid(self):
        metadata = GeffMetadata(directed=True, node_props_metadata={}, edge_props_metadata={})
        axis_names = ["x", "y"]
        axis_units = ["meter", None]
        axis_types = [None, "space"]
        axis_scales = [0.5, 2]
        scaled_units = ["pixel", None]
        axis_offset = [1.0, 10.0]
        new_meta = update_metadata_axes(
            metadata, axis_names, axis_units, axis_types, axis_scales, scaled_units, axis_offset
        )
        axes = new_meta.axes
        assert axes is not None
        assert len(axes) == 2
        assert axes[0].name == "x"
        assert axes[0].unit == "meter"
        assert axes[0].type is None
        assert axes[0].scale == 0.5
        assert axes[0].scaled_unit == "pixel"
        assert axes[0].offset == 1

    def test_invalid_units(self):
        metadata = GeffMetadata(directed=True, node_props_metadata={}, edge_props_metadata={})
        axis_names = ["x", "y"]
        axis_units: list[str | None] = ["meter"]
        with pytest.raises(
            ValueError, match="Axis units .* does not have same length as axis names .*"
        ):
            update_metadata_axes(metadata, axis_names, axis_units)

    def test_invalid_types(self):
        metadata = GeffMetadata(directed=True, node_props_metadata={}, edge_props_metadata={})
        axis_names = ["x", "y"]
        axis_types = ["space", None, None]
        with pytest.raises(
            ValueError, match="Axis types .* does not have same length as axis names .*"
        ):
            update_metadata_axes(metadata, axis_names, axis_types=axis_types)


class TestComputeAndAddAxisMinMax:
    def test_no_missing(self):
        metadata = GeffMetadata(
            directed=True,
            axes=[Axis(name="x", type="space")],
            node_props_metadata={},
            edge_props_metadata={},
        )
        x_prop = {"values": np.array([0, 1, 2, 3], dtype=np.uint32), "missing": None}
        node_props = {"x": x_prop}
        new_meta = compute_and_add_axis_min_max(metadata, node_props)
        assert new_meta.axes[0].max == 3

    def test_with_missing(self):
        metadata = GeffMetadata(
            directed=True,
            axes=[Axis(name="x", type="space")],
            node_props_metadata={},
            edge_props_metadata={},
        )
        x_prop = {
            "values": np.array([0, 1, 2, 3], dtype=np.uint32),
            "missing": np.array([0, 0, 1, 1], dtype=np.bool_),
        }
        node_props = {"x": x_prop}
        new_meta = compute_and_add_axis_min_max(metadata, node_props)
        assert new_meta.axes[0].max == 1
