import re
import warnings
from pathlib import Path

import numpy as np
import pydantic
import pytest
import zarr

import geff
from geff.affine import Affine
from geff.metadata_schema import (
    VERSION_PATTERN,
    Axis,
    GeffMetadata,
    GeffSchema,
    PropMetadata,
    formatted_schema_json,
    validate_key_identifier_equality,
)
from geff.testing.data import create_simple_2d_geff


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

    def test_valid_init(self) -> None:
        # Minimal required fields
        model = GeffMetadata(geff_version="0.0.1", directed=True)
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
                geff_version="0.0.1", directed=True, axes=[{"name": "test"}, {"name": "test"}]
            )

    def test_related_objects(self) -> None:
        # Valid related objects
        model = GeffMetadata(
            geff_version="0.0.1",
            directed=True,
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
                related_objects=[{"type": "invalid_type", "path": "invalid/"}],
            )

        # Invalid combination of type and label_prop
        with pytest.raises(
            pydantic.ValidationError, match=".*label_prop .+ is only valid for type 'labels'.*"
        ):
            GeffMetadata(
                geff_version="0.0.1",
                directed=True,
                related_objects=[{"type": "image", "path": "raw/", "label_prop": "seg_id"}],
            )

    def test_invalid_version(self) -> None:
        with pytest.raises(pydantic.ValidationError, match="String should match pattern"):
            GeffMetadata(geff_version="aljkdf", directed=True)

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
            )

        # Missing mandatory props metadata
        with pytest.raises(pydantic.ValidationError):
            GeffMetadata(
                geff_version="0.0.1",
                directed=True,
                node_props_metadata={
                    "": PropMetadata(identifier="", name="Empty Property", dtype="int32")
                },
            )
        with pytest.raises(pydantic.ValidationError):
            GeffMetadata(
                geff_version="0.0.1",
                directed=True,
                edge_props_metadata={
                    "prop4": PropMetadata(identifier="prop4", name="Empty Dtype", dtype="")
                },
            )

    def test_extra_attrs(self) -> None:
        # Should not fail
        GeffMetadata(
            geff_version="0.0.1",
            directed=True,
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
            axes=[{"name": "test"}],
        )

        # Create a Zarr group
        store, _ = create_simple_2d_geff()
        # geff_path = tmp_path / "test.geff"

        group = zarr.open_group(store=store)

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


class TestAxis:
    def test_valid(self) -> None:
        # minimal fields
        Axis(name="property")

        # All fields
        Axis(name="property", type="space", unit="micrometer", min=0, max=10)

    def test_no_name(self) -> None:
        # name is the only required field
        with pytest.raises(pydantic.ValidationError):
            Axis(type="space")

    def test_bad_type(self) -> None:
        with pytest.warns(UserWarning, match=r"Type .* not in valid types"):
            Axis(name="test", type="other")

    def test_invalid_units(self) -> None:
        # Spatial
        with pytest.warns(UserWarning, match=r"Spatial unit .* not in valid"):
            Axis(name="test", type="space", unit="bad unit")

        # Temporal
        with pytest.warns(UserWarning, match=r"Temporal unit .* not in valid"):
            Axis(name="test", type="time", unit="bad unit")

        # Don't check units if we don't specify type
        Axis(name="test", unit="not checked")

    def test_min_max(self) -> None:
        # Min no max
        with pytest.raises(ValueError, match=r"Min and max must both be None or neither"):
            Axis(name="test", min=0)

        # Max no min
        with pytest.raises(ValueError, match=r"Min and max must both be None or neither"):
            Axis(name="test", max=0)

        # Min > max
        with pytest.raises(ValueError, match=r"Min .* is greater than max .*"):
            Axis(name="test", min=0, max=-10)


class TestPropMetadata:
    def test_valid(self) -> None:
        # Minimal valid metadata
        PropMetadata(identifier="prop_1", name="property", dtype="int32")

        # All fields
        PropMetadata(
            identifier="prop_2",
            dtype="float64",
            encoding="utf-8",
            unit="micrometer",
            name="property 2",
            description="A property with all fields set.",
        )

    def test_invalid_identifier(self) -> None:
        # identifier must be a string
        with pytest.raises(pydantic.ValidationError):
            PropMetadata(identifier=123, name="property", dtype="int16")

        # identifier must be a non-empty string
        with pytest.raises(ValueError, match="String should have at least 1 character"):
            PropMetadata(identifier="", dtype="int16")

    def test_invalid_dtype(self) -> None:
        # dtype must be a string
        with pytest.raises(pydantic.ValidationError):
            PropMetadata(identifier="prop", dtype=123)
        with pytest.raises(pydantic.ValidationError):
            PropMetadata(identifier="prop", dtype=None)

        # dtype must be a non-empty string
        with pytest.raises(ValueError, match="String should have at least 1 character"):
            PropMetadata(identifier="prop", dtype="")

        # dtype must be in allowed data types
        with pytest.warns(
            UserWarning, match=r"Data type .* cannot be matched to a valid data type"
        ):
            PropMetadata(identifier="prop", dtype="nope")

    def test_invalid_encoding(self) -> None:
        # encoding must be a string
        with pytest.raises(pydantic.ValidationError):
            PropMetadata(identifier="prop", dtype="int16", encoding=123)

        # encoding must be a valid string encoding
        with pytest.warns(UserWarning, match=r"Encoding .* not in valid encodings"):
            PropMetadata(identifier="prop", dtype="float", encoding="invalid_encoding")


def test_validate_key_identifier_equality() -> None:
    # Matching key / identifier
    props_md = {
        "prop1": PropMetadata(identifier="prop1", name="Property 1", dtype="int32"),
        "prop2": PropMetadata(identifier="prop2", name="Property 2", dtype="float64"),
        "prop3": PropMetadata(identifier="prop3", name="Property 3", dtype="str"),
    }
    validate_key_identifier_equality(props_md, "node")

    # Empty metadata
    props_md = {}
    validate_key_identifier_equality(props_md, "edge")

    # Non matching key / identifier
    props_md = {
        "prop1": PropMetadata(identifier="prop1", name="Property 1", dtype="int32"),
        "prop2": PropMetadata(identifier="prop2", name="Property 2", dtype="float64"),
        "prop3": PropMetadata(identifier="prop4", name="Property 3", dtype="str"),
    }
    with pytest.raises(ValueError, match=r".* property key .* does not match "):
        validate_key_identifier_equality(props_md, "node")

    # Incorrect component type
    props_md = {
        "prop1": PropMetadata(identifier="prop1", name="Property 1", dtype="int32"),
        "prop2": PropMetadata(identifier="prop2", name="Property 2", dtype="float64"),
    }
    with pytest.raises(pydantic.ValidationError):
        validate_key_identifier_equality(props_md, "nodeeeee")


class TestAffineTransformation:
    """Comprehensive tests for Affine transformation functionality with metadata."""

    def test_affine_integration_with_metadata(self) -> None:
        """Test integration of Affine with GeffMetadata."""
        # Create a simple affine transformation
        affine = Affine.from_matrix_offset([[1.5, 0.0], [0.0, 1.5]], [10.0, 20.0])

        # Create metadata with affine transformation
        metadata = GeffMetadata(
            geff_version="0.1.0",
            directed=True,
            axes=[
                {"name": "x", "type": "space", "unit": "micrometer"},
                {"name": "y", "type": "space", "unit": "micrometer"},
            ],
            affine=affine,
        )

        # Verify the affine is properly stored
        assert metadata.affine is not None
        assert metadata.affine.ndim == 2
        np.testing.assert_array_almost_equal(
            metadata.affine.linear_matrix, [[1.5, 0.0], [0.0, 1.5]]
        )
        np.testing.assert_array_almost_equal(metadata.affine.offset, [10.0, 20.0])

    def test_unmatched_ndim(self) -> None:
        """Test that an error is raised if the affine matrix and axes have different dimensions."""
        with pytest.raises(
            ValueError, match="Affine transformation matrix must have 3 dimensions, got 2"
        ):
            GeffMetadata(
                geff_version="0.1.0",
                directed=True,
                axes=[
                    {"name": "x", "type": "space", "unit": "micrometer"},
                    {"name": "y", "type": "space", "unit": "micrometer"},
                    {"name": "z", "type": "space", "unit": "micrometer"},
                ],
                # Homogeneous matrix of a 2D affine transformation
                affine=np.eye(3),
            )

    def test_affine_serialization_with_metadata(self, tmp_path: Path) -> None:
        """Test that Affine transformations can be serialized and deserialized with metadata."""
        # Create metadata with affine transformation
        affine = Affine.from_matrix_offset(
            [[2.0, 0.5], [-0.5, 2.0]],  # Scaling with rotation/shear
            [100.0, -50.0],
        )

        original_metadata = GeffMetadata(
            geff_version="0.1.0",
            directed=False,
            axes=[
                {"name": "x", "type": "space", "unit": "micrometer"},
                {"name": "y", "type": "space", "unit": "micrometer"},
            ],
            affine=affine,
        )

        # Write and read back
        zpath = tmp_path / "test_affine.zarr"
        original_metadata.write(zpath)
        loaded_metadata = GeffMetadata.read(zpath)

        # Verify everything matches
        assert loaded_metadata == original_metadata
        assert loaded_metadata.affine is not None
        np.testing.assert_array_almost_equal(
            loaded_metadata.affine.matrix, original_metadata.affine.matrix
        )


def test_schema_and_round_trip() -> None:
    # Ensure it can be created without error
    assert GeffSchema.model_json_schema(mode="serialization")
    assert GeffSchema.model_json_schema(mode="validation")

    model = GeffSchema(
        geff=GeffMetadata(
            geff_version="0.1.0",
            directed=True,
            axes=[
                {"name": "x", "type": "space", "unit": "micrometer"},
                {"name": "y", "type": "space", "unit": "micrometer"},
            ],
            affine=Affine.from_matrix_offset([[1.0, 0.0], [0.0, 1.0]], [0.0, 0.0]),
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
    root = Path(geff.__file__).parent.parent.parent
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

    new_schema_text = formatted_schema_json()
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
