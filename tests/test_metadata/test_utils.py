import numpy as np
import pytest

from geff.metadata._schema import GeffMetadata, PropMetadata
from geff.metadata.utils import create_or_update_props_metadata, create_prop_metadata


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
        result = create_or_update_props_metadata(metadata, props_md, "node")
        assert result.node_props_metadata == {
            "prop1": PropMetadata(identifier="prop1", dtype="int64"),
            "prop2": PropMetadata(identifier="prop2", dtype="float32"),
        }

    def test_create_edge_props_metadata_from_none(self):
        """Test creating edge props metadata when metadata has no existing edge props."""
        metadata = GeffMetadata(
            directed=True,
            edge_props_metadata=None,
        )
        props_md = [
            PropMetadata(identifier="prop1", dtype="float64"),
            PropMetadata(identifier="prop2", dtype="str"),
        ]
        result = create_or_update_props_metadata(metadata, props_md, "edge")
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
        )
        props_md = [
            PropMetadata(identifier="new_prop", dtype="float64", name="New prop"),
        ]
        result = create_or_update_props_metadata(metadata, props_md, "node")
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
            edge_props_metadata=existing_props,
        )
        props_md = [
            PropMetadata(identifier="new_edge_prop", dtype="str"),
        ]
        result = create_or_update_props_metadata(metadata, props_md, "edge")
        assert len(result.edge_props_metadata) == 2
        assert "existing_edge_prop" in result.edge_props_metadata
        assert "new_edge_prop" in result.edge_props_metadata

    def test_overwrite_existing_prop(self):
        """Test that existing props are overwritten when same identifier is provided."""
        existing_props = {"prop1": PropMetadata(identifier="prop1", dtype="int32")}
        metadata = GeffMetadata(
            directed=True,
            node_props_metadata=existing_props,
        )
        props_md = [
            PropMetadata(identifier="prop1", dtype="float64"),
        ]
        result = create_or_update_props_metadata(metadata, props_md, "node")
        assert len(result.node_props_metadata) == 1
        assert result.node_props_metadata["prop1"].dtype == "float64"

    def test_empty_props_md_list(self):
        """Test handling of empty props metadata list."""
        existing_props = {"existing_prop": PropMetadata(identifier="existing_prop", dtype="int32")}
        metadata = GeffMetadata(
            directed=True,
            node_props_metadata=existing_props,
        )
        result = create_or_update_props_metadata(metadata, [], "node")
        assert len(result.node_props_metadata) == 1
        assert "existing_prop" in result.node_props_metadata

    def test_multiple_props_same_call(self):
        """Test adding multiple props in a single call."""
        existing_props = {"newprop": PropMetadata(identifier="newprop", dtype="int")}
        metadata = GeffMetadata(
            directed=True,
            edge_props_metadata=existing_props,
        )
        props_md = [
            PropMetadata(identifier="newprop1", dtype="float64"),
            PropMetadata(identifier="newprop2", dtype="str"),
            PropMetadata(identifier="newprop3", dtype="bool"),
        ]
        result = create_or_update_props_metadata(metadata, props_md, "edge")
        assert len(result.edge_props_metadata) == 4
        assert "newprop" in result.edge_props_metadata
        assert "newprop1" in result.edge_props_metadata
        assert "newprop2" in result.edge_props_metadata
        assert "newprop3" in result.edge_props_metadata
        assert result.edge_props_metadata["newprop"].dtype == "int"
        assert result.edge_props_metadata["newprop1"].dtype == "float64"
        assert result.edge_props_metadata["newprop2"].dtype == "str"
        assert result.edge_props_metadata["newprop3"].dtype == "bool"

    def test_invalid_c_type_raises_error(self):
        """Test that invalid c_type parameter raises appropriate error."""
        metadata = GeffMetadata(
            geff_version="0.1.0",
            directed=True,
        )
        props_md = [PropMetadata(identifier="prop1", dtype="int64")]
        with pytest.raises(ValueError):
            create_or_update_props_metadata(metadata, props_md, "invalid_type")


class TestCreatePropMetadata:
    """Test cases for create_prop_metadata function."""

    def test_normal_prop_int(self):
        """Test creating PropMetadata from normal integer property."""
        values = np.array([1, 2, 3, 4], dtype=np.int64)
        prop_data = {"values": values, "missing": None}

        result = create_prop_metadata("test_prop", prop_data)

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

        result = create_prop_metadata("float_prop", prop_data, unit="meters", name="Distance")

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

        result = create_prop_metadata("fruit", prop_data, description="Types of fruit")

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

        result = create_prop_metadata("varlen_prop", prop_data)

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

        result = create_prop_metadata("sparse_varlen", prop_data, unit="kg")

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
            create_prop_metadata("mixed_dtype", prop_data)

    def test_invalid_prop_data_raises_error(self):
        """Test that invalid property data raises ValueError."""
        invalid_data = "not_valid_data"

        with pytest.raises(ValueError, match="Expected dict of property data, got.*"):
            create_prop_metadata("invalid", invalid_data)

    def test_all_optional_parameters(self):
        """Test creating PropMetadata with all optional parameters provided."""
        values = np.array([True, False, True], dtype=bool)
        prop_data = {"values": values, "missing": None}

        result = create_prop_metadata(
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
