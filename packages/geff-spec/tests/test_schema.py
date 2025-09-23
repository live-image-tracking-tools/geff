import re
import warnings
from pathlib import Path

import pydantic
import pytest
import zarr
import zarr.storage

import geff
from geff_spec import GeffMetadata, GeffSchema, PropMetadata
from geff_spec._schema import (
    VERSION_PATTERN,
    _formatted_schema_json,
    _validate_key_identifier_equality,
)


class TestMetadataModel:
    def test_version_pattern(self) -> None:
        # Valid versions
        valid_versions = [
            "1.0",
            "0.1.0",
            "1.0.0.dev1",
            "2.3.4+local",
            "3.4.5.dev6+g61d5f18",
            "10.20.30",
        ]
        for version in valid_versions:
            assert re.fullmatch(VERSION_PATTERN, version)

        # Invalid versions
        invalid_versions = [
            "1.0.0.dev",  # Incomplete dev version
            "1.0.0+local+",  # Extra '+' at the end
            "abc.def",  # Non-numeric version
        ]
        for version in invalid_versions:
            assert not re.fullmatch(VERSION_PATTERN, version)

    def test_invalid_version(self) -> None:
        with pytest.raises(pydantic.ValidationError, match="String should match pattern"):
            GeffMetadata(
                geff_version="aljkdf", directed=True, node_props_metadata={}, edge_props_metadata={}
            )

    def test_valid_init(self) -> None:
        # Minimal required fields
        model = GeffMetadata(
            geff_version="0.0.1", directed=True, node_props_metadata={}, edge_props_metadata={}
        )
        assert model.geff_version == "0.0.1"
        assert model.axes is None

        # Complete metadata
        node_props = {"prop1": PropMetadata(identifier="prop1", name="Property 1", dtype="int32")}
        edge_props = {
            "prop2": PropMetadata(identifier="prop2", dtype="float32"),
            "prop3": PropMetadata(identifier="prop3", dtype="str"),
        }
        model = GeffMetadata(
            geff_version="0.0.1",
            directed=True,
            axes=[{"name": "test"}],
            node_props_metadata=node_props,
            edge_props_metadata=edge_props,
            related_objects=[
                {"type": "labels", "path": "segmentation/", "label_prop": "seg_id"},
                {"type": "image", "path": "raw/"},
            ],
        )
        assert model.axes and len(model.axes) == 1

        # Multiple axes
        model = GeffMetadata(
            geff_version="0.0.1",
            directed=True,
            node_props_metadata={},
            edge_props_metadata={},
            axes=[
                {"name": "test"},
                {"name": "complete", "type": "space", "unit": "micrometer", "min": 0, "max": 10},
            ],
        )
        assert model.axes and len(model.axes) == 2

    def test_duplicate_axes_names(self) -> None:
        # duplicate names not allowed
        with pytest.raises(ValueError, match=r"Duplicate axes names found in"):
            GeffMetadata(
                geff_version="0.0.1",
                directed=True,
                node_props_metadata={},
                edge_props_metadata={},
                axes=[{"name": "test"}, {"name": "test"}],
            )

    def test_related_objects(self) -> None:
        # Valid related objects
        model = GeffMetadata(
            geff_version="0.0.1",
            directed=True,
            node_props_metadata={},
            edge_props_metadata={},
            related_objects=[
                {"type": "labels", "path": "segmentation/", "label_prop": "seg_id"},
                {"type": "image", "path": "raw/"},
            ],
        )
        assert len(model.related_objects) == 2

        # Related object type
        with pytest.warns(
            UserWarning, match=r".* might not be recognized by reader applications.*"
        ):
            GeffMetadata(
                geff_version="0.0.1",
                directed=True,
                node_props_metadata={},
                edge_props_metadata={},
                related_objects=[{"type": "invalid_type", "path": "invalid/"}],
            )

        # Invalid combination of type and label_prop
        with pytest.raises(
            pydantic.ValidationError, match=".*label_prop .+ is only valid for type 'labels'.*"
        ):
            GeffMetadata(
                geff_version="0.0.1",
                directed=True,
                node_props_metadata={},
                edge_props_metadata={},
                related_objects=[{"type": "image", "path": "raw/", "label_prop": "seg_id"}],
            )

    def test_props_metadata(self) -> None:
        # Valid props metadata
        node_props = {
            "prop1": PropMetadata(identifier="prop1", name="Property 1", dtype="int32"),
            "prop2": PropMetadata(identifier="prop2", dtype="float32"),
        }
        edge_props = {
            "prop3": PropMetadata(identifier="prop3", dtype="str"),
        }
        meta = GeffMetadata(
            geff_version="0.0.1",
            directed=True,
            node_props_metadata=node_props,
            edge_props_metadata=edge_props,
        )
        assert len(meta.node_props_metadata) == 2
        assert len(meta.edge_props_metadata) == 1

        # Unmatching keys and identifiers
        with pytest.raises(ValueError, match=r".* property key .* does not match identifier .*"):
            GeffMetadata(
                geff_version="0.0.1",
                directed=True,
                node_props_metadata={
                    "prop1": PropMetadata(identifier="prop2", name="Property 1", dtype="int32")
                },
                edge_props_metadata={},
            )

        # Missing mandatory props metadata
        with pytest.raises(pydantic.ValidationError):
            GeffMetadata(
                geff_version="0.0.1",
                directed=True,
                node_props_metadata={
                    "": PropMetadata(identifier="", name="Empty Property", dtype="int32")
                },
                edge_props_metadata={},
            )
        with pytest.raises(pydantic.ValidationError):
            GeffMetadata(
                geff_version="0.0.1",
                directed=True,
                node_props_metadata={},
                edge_props_metadata={
                    "prop4": PropMetadata(identifier="prop4", name="Empty Dtype", dtype="")
                },
            )

    def test_extra_attrs(self) -> None:
        # Should not fail
        GeffMetadata(
            geff_version="0.0.1",
            directed=True,
            node_props_metadata={},
            edge_props_metadata={},
            axes=[
                {"name": "test"},
                {"name": "complete", "type": "space", "unit": "micrometer", "min": 0, "max": 10},
            ],
            extra={"foo": "bar", "bar": {"baz": "qux"}},
        )

    def test_read_write(self, tmp_path: Path) -> None:
        meta = GeffMetadata(
            geff_version="0.0.1",
            directed=True,
            node_props_metadata={},
            edge_props_metadata={},
            axes=[
                {"name": "test"},
                {"name": "complete", "type": "space", "unit": "micrometer", "min": 0, "max": 10},
            ],
            extra={"foo": "bar", "bar": {"baz": "qux"}},
        )
        zpath = tmp_path / "test.zarr"
        meta.write(zpath)
        compare = GeffMetadata.read(zpath)
        assert compare == meta

        meta.directed = False
        meta.write(zpath)
        compare = GeffMetadata.read(zpath)
        assert compare == meta

    def test_meta_write_raises_type_error_upon_group(self) -> None:
        # Create a GeffMetadata instance
        meta = GeffMetadata(
            geff_version="0.0.1",
            directed=True,
            node_props_metadata={},
            edge_props_metadata={},
            axes=[{"name": "test"}],
        )

        # Create a Zarr group
        group = zarr.open_group(store=zarr.storage.MemoryStore())

        # Assert that a TypeError is raised when meta.write is called with a Group
        with pytest.raises(
            TypeError,
            match=r"Unsupported type for store_like: should be a zarr store | Path | str",
        ):
            meta.write(group)

        with pytest.raises(
            TypeError, match=r"Unsupported type for store_like: should be a zarr store | Path | str"
        ):
            meta.read(group)

    def test_model_mutation(self) -> None:
        """Test that invalid model mutations raise errors."""
        meta = GeffMetadata(
            geff_version="0.0.1",
            directed=True,
            node_props_metadata={},
            edge_props_metadata={},
            axes=[
                {"name": "test"},
                {"name": "complete", "type": "space", "unit": "micrometer", "min": 0, "max": 10},
            ],
        )

        meta.directed = False  # fine...

        with pytest.raises(pydantic.ValidationError):
            meta.geff_version = "abcde"

    def test_read_write_ignored_metadata(self, tmp_path: Path) -> None:
        meta = GeffMetadata(
            geff_version="0.0.1",
            directed=True,
            node_props_metadata={},
            edge_props_metadata={},
            extra={"foo": "bar", "bar": {"baz": "qux"}},
        )
        zpath = tmp_path / "test.zarr"
        meta.write(zpath)
        compare = GeffMetadata.read(zpath)
        assert compare.extra["foo"] == "bar"
        assert compare.extra["bar"]["baz"] == "qux"

        # Check that extra metadata is not accessible as attributes
        with pytest.raises(AttributeError, match="object has no attribute 'foo'"):
            compare.foo  # noqa: B018

    def test_display_hints(self) -> None:
        meta = {
            "geff_version": "0.0.1",
            "directed": True,
            "node_props_metadata": {},
            "edge_props_metadata": {},
            "axes": [
                {"name": "x"},
                {"name": "y"},
                {"name": "z"},
                {"name": "t"},
            ],
        }
        # Horizontal and vertical are required
        with pytest.raises(pydantic.ValidationError, match=r"display_vertical"):
            GeffMetadata(**{"display_hints": {"display_horizontal": "x"}, **meta})
        with pytest.raises(pydantic.ValidationError, match=r"display_horizontal"):
            GeffMetadata(**{"display_hints": {"display_vertical": "x"}, **meta})

        # Names of axes in hint must be in axes
        with pytest.raises(ValueError, match=r"display_horizontal .* not found in axes"):
            GeffMetadata(
                **{"display_hints": {"display_vertical": "y", "display_horizontal": "a"}, **meta}
            )
        with pytest.raises(ValueError, match=r"display_vertical .* not found in axes"):
            GeffMetadata(
                **{"display_hints": {"display_vertical": "a", "display_horizontal": "x"}, **meta}
            )
        with pytest.raises(ValueError, match=r"display_depth .* not found in axes"):
            GeffMetadata(
                **{
                    "display_hints": {
                        "display_vertical": "y",
                        "display_horizontal": "x",
                        "display_depth": "a",
                    },
                    **meta,
                }
            )
        with pytest.raises(ValueError, match=r"display_time .* not found in axes"):
            GeffMetadata(
                **{
                    "display_hints": {
                        "display_vertical": "y",
                        "display_horizontal": "x",
                        "display_time": "a",
                    },
                    **meta,
                }
            )


def test__validate_key_identifier_equality() -> None:
    # Matching key / identifier
    props_md = {
        "prop1": PropMetadata(identifier="prop1", name="Property 1", dtype="int32"),
        "prop2": PropMetadata(identifier="prop2", name="Property 2", dtype="float64"),
        "prop3": PropMetadata(identifier="prop3", name="Property 3", dtype="str"),
    }
    _validate_key_identifier_equality(props_md, "node")

    # Empty metadata
    props_md = {}
    _validate_key_identifier_equality(props_md, "edge")

    # Non matching key / identifier
    props_md = {
        "prop1": PropMetadata(identifier="prop1", name="Property 1", dtype="int32"),
        "prop2": PropMetadata(identifier="prop2", name="Property 2", dtype="float64"),
        "prop3": PropMetadata(identifier="prop4", name="Property 3", dtype="str"),
    }
    with pytest.raises(ValueError, match=r".* property key .* does not match "):
        _validate_key_identifier_equality(props_md, "node")

    # Incorrect component type
    props_md = {
        "prop1": PropMetadata(identifier="prop1", name="Property 1", dtype="int32"),
        "prop2": PropMetadata(identifier="prop2", name="Property 2", dtype="float64"),
    }
    with pytest.raises(pydantic.ValidationError):
        _validate_key_identifier_equality(props_md, "nodeeeee")


def test_schema_and_round_trip() -> None:
    # Ensure it can be created without error
    assert GeffSchema.model_json_schema(mode="serialization")
    assert GeffSchema.model_json_schema(mode="validation")

    model = GeffSchema(
        geff=GeffMetadata(
            geff_version="0.1.0",
            directed=True,
            node_props_metadata={},
            edge_props_metadata={},
            axes=[
                {"name": "x", "type": "space", "unit": "micrometer"},
                {"name": "y", "type": "space", "unit": "micrometer"},
            ],
            related_objects=[
                {"type": "labels", "path": "segmentation/", "label_prop": "seg_id"},
                {"type": "image", "path": "raw/"},
            ],
            display_hints={"display_horizontal": "x", "display_vertical": "y"},
        )
    )

    # ensure round trip
    # it's important to test model_dump_json on a fully-populated model
    # to test that all fields can be serialized
    model2 = GeffSchema.model_validate_json(model.model_dump_json())
    assert model2 == model


def test_schema_file_updated(pytestconfig: pytest.Config) -> None:
    """Ensure that geff-schema.json at the repo root is up to date.

    To update the schema file, run `pytest --update-schema`.
    """
    root = Path(geff.__file__).parent.parent.parent.parent.parent
    schema_path = root / "geff-schema.json"
    if schema_path.is_file():
        current_schema_text = schema_path.read_text()
    else:
        if not pytestconfig.getoption("--update-schema"):
            raise AssertionError(
                f"could not find geff-schema.json at {schema_path}. "
                "Please run `pytest` with the `--update-schema` flag to create it."
            )
        current_schema_text = ""

    new_schema_text = _formatted_schema_json()
    if current_schema_text != new_schema_text:
        if pytestconfig.getoption("--update-schema"):
            schema_path.write_text(new_schema_text)
            # with our current pytest settings, this will fail tests...
            # but only once (the schema will be up to date next time tests are run)
            warnings.warn(
                "The geff_metadata_schema.json file has been updated. "
                "Please commit the changes to the repository.",
                stacklevel=2,
            )
        else:
            raise AssertionError(
                "The geff_metadata_schema.json file is out of date. "
                "Please rerun `pytest` with the `--update-schema` flag to update it."
            )
