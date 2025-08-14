import pytest

from geff.metadata._schema import GeffMetadata, PropMetadata
from geff.metadata.utils import create_or_update_props_metadata


class TestCreateOrUpdatePropsMetadata:
    """Test cases for create_or_update_props_metadata function."""

    def test_create_node_props_metadata_from_none(self):
        """Test creating node props metadata when metadata has no existing node props."""
        metadata = GeffMetadata(
            directed=False,
            node_props_metadata=None,
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
