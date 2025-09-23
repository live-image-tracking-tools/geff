from __future__ import annotations

import json
import warnings
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal

import zarr
from pydantic import BaseModel, Field, model_validator, validate_call
from pydantic.config import ConfigDict
from zarr.storage import StoreLike

import geff_spec

# The next imports are needed at runtime for Pydantic validation
from ._axis import Axis  # noqa: TC001
from ._prop_metadata import PropMetadata  # noqa: TC001

if TYPE_CHECKING:
    from zarr.storage import StoreLike


VERSION_PATTERN = r"^\d+\.\d+(?:\.\d+)?(?:\.dev\d+)?(?:\+[a-zA-Z0-9]+)?"


class DisplayHint(BaseModel):
    """Metadata indicating how spatiotemporal axes are displayed by a viewer"""

    display_horizontal: str = Field(
        ...,
        description="Which spatial axis to use for horizontal display",
    )
    display_vertical: str = Field(
        ...,
        description="Which spatial axis to use for vertical display",
    )
    display_depth: str | None = Field(
        default=None,
        description="Optional, which spatial axis to use for depth display",
    )
    display_time: str | None = Field(
        None,
        description="Optional, which temporal axis to use for time",
    )


@validate_call
def _validate_key_identifier_equality(
    props_metadata: dict[str, PropMetadata],
    c_type: Literal["node", "edge", "tracklet", "lineage"],
) -> None:
    """Check that the keys in the property metadata dictionary match the identifiers
    in the PropMetadata objects.

    Args:
        props_metadata (dict[str, PropMetadata]): The property metadata dictionary
            where keys are property identifiers and values are PropMetadata objects.
        c_type (Literal["node", "edge", "tracklet", "lineage"]): The type of component
            to which the property belongs.

    Raises:
        ValueError: If the key does not match the identifier.
    """
    for key, prop_md in props_metadata.items():
        if key != prop_md.identifier:
            raise ValueError(
                f"{c_type.capitalize()} property key '{key}' does not match "
                f"identifier {prop_md.identifier}"
            )


class RelatedObject(BaseModel):
    """A set of metadata for data that is associated with the graph. The types
    'labels' and 'image' should be used for label and image objects, respectively.
    Other types are also allowed.
    """

    type: str = Field(
        ...,
        description=(
            "Type of the related object. 'labels' for label objects, "
            "'image' for image objects. Other types are also allowed, but may not be "
            "recognized by reader applications. "
        ),
    )
    path: str = Field(
        ...,
        description=(
            "Path of the related object within the zarr group, relative "
            "to the geff zarr-attributes file. "
            "It is strongly recommended all related objects are stored as siblings "
            "of the geff group within the top-level zarr group."
        ),
    )
    label_prop: str | None = Field(
        default=None,
        description=(
            "Property name for label objects. This is the node property that will be used "
            "to identify the labels in the related object. "
            "This is only valid for type 'labels'."
        ),
    )

    @model_validator(mode="after")
    def _validate_model(self) -> RelatedObject:
        if self.type != "labels" and self.label_prop is not None:
            raise ValueError(
                f"label_prop {self.label_prop} is only valid for type 'labels', "
                f"but got type {self.type}."
            )
        if self.type not in ["labels", "image"]:
            warnings.warn(
                f"Got type {self.type} for related object, "
                "which might not be recognized by reader applications. ",
                stacklevel=2,
            )
        return self


GEFF_VERSION = ".".join(geff_spec.__version__.split(".")[:2])


class GeffMetadata(BaseModel):
    """
    Geff metadata schema to validate the attributes json file in a geff zarr
    """

    # this determines the title of the generated json schema
    model_config = ConfigDict(
        title="geff_metadata",
        validate_assignment=True,
    )

    geff_version: str = Field(
        default=GEFF_VERSION,
        pattern=VERSION_PATTERN,
        description=(
            "Geff version string following semantic versioning (MAJOR.MINOR.PATCH), "
            "optionally with .devN and/or +local parts (e.g., 0.3.1.dev6+g61d5f18).\n"
            "If not provided, the version will be set to the current geff package version."
        ),
    )

    directed: bool = Field(description="True if the graph is directed, otherwise False.")
    axes: list[Axis] | None = Field(
        default=None,
        description="""Optional list of `Axis` objects defining the axes of each node
            in the graph. The axes list is modeled after the
            [OME-zarr](https://ngff.openmicroscopy.org/0.5/index.html#axes-md)
            specifications and is used to identify spatio-temporal properties on the
            graph nodes. If the same names are used in the axes metadata of the
            related image or segmentation data, applications can use this information
            to align graph node locations with image data.
            The order of the axes in the list is meaningful. For one, any downstream
            properties that are an array of values with one value per (spatial) axis
            will be in the order of the axis list (filtering to only the spatial axes by
            the `type` field if needed). Secondly, if associated image or segmentation
            data does not have axes metadata, the order of the spatiotemporal axes is a
            good default guess for aligning the graph and the image data, although there
            is no way to denote the channel dimension in the graph spec. If you are
            writing out a geff with an associated segmentation and/or image dataset, we
            highly recommend providing the axis names for your segmentation/image using
            the OME-zarr spec, including channel dimensions if needed.""",
    )

    node_props_metadata: dict[str, PropMetadata] = Field(
        description=(
            "Metadata for node properties. The keys are the property identifiers, "
            "and the values are PropMetadata objects describing the properties."
            "There must be one entry for each node property."
        ),
    )
    edge_props_metadata: dict[str, PropMetadata] = Field(
        description=(
            "Metadata for edge properties. The keys are the property identifiers, "
            "and the values are PropMetadata objects describing the properties."
            "There must be one entry for each edge property."
        ),
    )

    sphere: str | None = Field(
        default=None,
        title="Node property: Detections as spheres",
        description=(
            """
            Name of the optional `sphere` property.

            A sphere is defined by

            - a center point, already given by the `space` type properties
            - a radius scalar, stored in this property
            """
        ),
    )
    ellipsoid: str | None = Field(
        default=None,
        title="Node property: Detections as ellipsoids",
        description=(
            """
            Name of the `ellipsoid` property.

            An ellipsoid is assumed to be in the same coordinate system as the `space` type
            properties.

            It is defined by

            - a center point $c$, already given by the `space` type properties
            - a covariance matrix $\\Sigma$, symmetric and positive-definite, stored in this
              property as a `2x2`/`3x3` array.

            To plot the ellipsoid:

            - Compute the eigendecomposition of the covariance matrix
            $\\Sigma = Q \\Lambda Q^{\\top}$
            - Sample points $z$ on the unit sphere
            - Transform the points to the ellipsoid by
            $x = c + Q \\Lambda^{(1/2)} z$.
            """
        ),
    )
    track_node_props: dict[Literal["lineage", "tracklet"], str] | None = Field(
        default=None,
        description=(
            "Node properties denoting tracklet and/or lineage IDs.\n"
            "A tracklet is defined as a simple path of connected nodes "
            "where the initiating node has any incoming degree and outgoing degree at most 1, "
            "and the terminating node has incoming degree at most 1 and any outgoing degree, "
            "and other nodes along the path have in/out degree of 1. Each tracklet must contain "
            "the maximal set of connected nodes that match this definition - no sub-tracklets.\n"
            "A lineage is defined as a weakly connected component on the graph.\n"
            "The dictionary can store one or both of 'tracklet' or 'lineage' keys."
        ),
    )
    related_objects: list[RelatedObject] | None = Field(
        default=None,
        description=(
            "A list of dictionaries of related objects such as labels or images. "
            "Each dictionary must contain 'type', 'path', and optionally 'label_prop' "
            "properties. The 'type' represents the data type. 'labels' and 'image' should "
            "be used for label and image objects, respectively. Other types are also allowed, "
            "The 'path' should be relative to the geff zarr-attributes file. "
            "It is strongly recommended all related objects are stored as siblings "
            "of the geff group within the top-level zarr group. "
            "The 'label_prop' is only valid for type 'labels' and specifies the node property "
            "that will be used to identify the labels in the related object. "
        ),
    )
    display_hints: DisplayHint | None = Field(
        default=None,
        description="Metadata indicating how spatiotemporal axes are displayed by a viewer",
    )
    extra: dict[str, Any] = Field(
        default_factory=dict,
        description="The optional `extra` object is a free-form dictionary that can hold any "
        "additional, application-specific metadata that is **not** covered by the core geff "
        "schema. Users may place arbitrary keys and values inside `extra` without fear of "
        "clashing with future reserved fields. Although the core `geff` reader makes these "
        "attributes available, their meaning and use are left entirely to downstream "
        "applications. ",
    )

    @model_validator(mode="after")
    def _validate_model_after(self) -> GeffMetadata:
        # Axes names must be unique
        if self.axes is not None:
            names = [ax.name for ax in self.axes]
            if len(names) != len(set(names)):
                raise ValueError(f"Duplicate axes names found in {names}")

        # Display hint axes match names in axes
        if self.axes is not None and self.display_hints is not None:
            ax_names = [ax.name for ax in self.axes]
            if self.display_hints.display_horizontal not in ax_names:
                raise ValueError(
                    f"Display hint display_horizontal name {self.display_hints.display_horizontal} "
                    f"not found in axes {ax_names}"
                )
            if self.display_hints.display_vertical not in ax_names:
                raise ValueError(
                    f"Display hint display_vertical name {self.display_hints.display_vertical} "
                    f"not found in axes {ax_names}"
                )
            if (
                self.display_hints.display_time is not None
                and self.display_hints.display_time not in ax_names
            ):
                raise ValueError(
                    f"Display hint display_time name {self.display_hints.display_time} "
                    f"not found in axes {ax_names}"
                )
            if (
                self.display_hints.display_depth is not None
                and self.display_hints.display_depth not in ax_names
            ):
                raise ValueError(
                    f"Display hint display_depth name {self.display_hints.display_depth} "
                    f"not found in axes {ax_names}"
                )

        # Property metadata validation
        if self.node_props_metadata is not None:
            _validate_key_identifier_equality(self.node_props_metadata, "node")
        if self.edge_props_metadata is not None:
            _validate_key_identifier_equality(self.edge_props_metadata, "edge")

        return self

    def write(self, store: StoreLike) -> None:
        """Helper function to write GeffMetadata into the group of a zarr geff store.
        Maintains consistency by preserving ignored attributes with their original values.

        Args:
            store (zarr store | Path | str): The geff store to write the metadata to
        """

        if isinstance(store, zarr.Group):
            raise TypeError("Unsupported type for store_like: should be a zarr store | Path | str")

        group = zarr.open_group(store)
        group.attrs["geff"] = self.model_dump(mode="json")

    @classmethod
    def read(cls, store: StoreLike) -> GeffMetadata:
        """Helper function to read GeffMetadata from a zarr geff group.

        Args:
            store (zarr store | Path | str): The geff store to read the metadata from

        Returns:
            GeffMetadata: The GeffMetadata object
        """

        if isinstance(store, zarr.Group):
            raise TypeError("Unsupported type for store_like: should be a zarr store | Path | str")

        group = zarr.open_group(store)

        # Check if geff_version exists in zattrs
        if "geff" not in group.attrs:
            raise ValueError(
                f"No geff key found in {group}. This may indicate the path is incorrect or "
                f"zarr group name is not specified (e.g. /dataset.zarr/tracks/ instead of "
                f"/dataset.zarr/)."
            )
        if not isinstance(geff_dict := group.attrs["geff"], Mapping):
            raise ValueError(f"Expected geff metadata to be a Mapping. Got {type(geff_dict)}")
        return cls.model_validate(geff_dict)


class GeffSchema(BaseModel):
    geff: GeffMetadata = Field(..., description="geff_metadata")


def _formatted_schema_json() -> str:
    """Get the formatted JSON schema for the GeffMetadata model."""
    schema = GeffSchema.model_json_schema()

    # this is a hacky way to ensure that the schema says geff_version is required
    # while still being able to instantiate GeffMetadata without it.
    # Once we cleanly version the schema independently, this *might* be a bit cleaner
    # Note: one could also pass a custom `schema_generator` to `model_json_schema()`
    # above... but this is simpler for now.
    geff_meta = schema["$defs"]["GeffMetadata"]
    geff_meta["properties"]["geff_version"].pop("default")
    geff_meta["required"].append("geff_version")

    return json.dumps(schema, indent=2)
