from __future__ import annotations

import warnings
from collections.abc import Sequence  # noqa: TC003
from importlib.metadata import version
from pathlib import Path
from typing import Any, Literal

import zarr
from pydantic import BaseModel, Field, model_validator
from pydantic.config import ConfigDict

from .affine import Affine  # noqa: TC001 # Needed at runtime for Pydantic validation
from .valid_values import (
    ALLOWED_DTYPES,
    VALID_AXIS_TYPES,
    VALID_SPACE_UNITS,
    VALID_STR_ENCODINGS,
    VALID_TIME_UNITS,
    validate_axis_type,
    validate_data_type,
    validate_space_unit,
    validate_str_encoding,
    validate_time_unit,
)

VERSION_PATTERN = r"^\d+\.\d+(?:\.\d+)?(?:\.dev\d+)?(?:\+[a-zA-Z0-9]+)?"


class Axis(BaseModel):
    name: str
    type: str | None = None
    unit: str | None = None
    min: float | None = None
    max: float | None = None

    @model_validator(mode="after")
    def _validate_model(self) -> Axis:
        if (self.min is None) != (self.max is None):  # type: ignore
            raise ValueError(
                f"Min and max must both be None or neither: got min {self.min} and max {self.max}"
            )
        if self.min is not None and self.min > self.max:  # type: ignore
            raise ValueError(f"Min {self.min} is greater than max {self.max}")

        if self.type is not None and not validate_axis_type(self.type):  # type: ignore
            warnings.warn(
                f"Type {self.type} not in valid types {VALID_AXIS_TYPES}. "
                "Reader applications may not know what to do with this information.",
                stacklevel=2,
            )

        if self.type == "space" and not validate_space_unit(self.unit):  # type: ignore
            warnings.warn(
                f"Spatial unit {self.unit} not in valid OME-Zarr units {VALID_SPACE_UNITS}. "
                "Reader applications may not know what to do with this information.",
                stacklevel=2,
            )
        elif self.type == "time" and not validate_time_unit(self.unit):  # type: ignore
            warnings.warn(
                f"Temporal unit {self.unit} not in valid OME-Zarr units {VALID_TIME_UNITS}. "
                "Reader applications may not know what to do with this information.",
                stacklevel=2,
            )

        return self


def axes_from_lists(
    axis_names: Sequence[str] | None = None,
    axis_units: Sequence[str | None] | None = None,
    axis_types: Sequence[str | None] | None = None,
    roi_min: Sequence[float | None] | None = None,
    roi_max: Sequence[float | None] | None = None,
) -> list[Axis]:
    """Create a list of Axes objects from lists of axis names, units, types, mins,
    and maxes. If axis_names is None, there are no spatial axes and the list will
    be empty. Nones for all other arguments will omit them from the axes.

    All provided arguments must have the same length. If an argument should not be specified
    for a single property, use None.

    Args:
        axis_names (list[str] | None, optional): Names of properties for spatiotemporal
            axes. Defaults to None.
        axis_units (list[str | None] | None, optional): Units corresponding to named properties.
            Defaults to None.
        axis_types (list[str | None] | None, optional): Axis type for each property.
            Choose from "space", "time", "channel". Defaults to None.
        roi_min (list[float | None] | None, optional): Minimum value for each property.
            Defaults to None.
        roi_max (list[float | None] | None, optional): Maximum value for each property.
            Defaults to None.

    Returns:
        list[Axis]:
    """
    axes: list[Axis] = []
    if axis_names is None:
        return axes

    dims = len(axis_names)
    if axis_types is not None:
        assert len(axis_types) == dims, (
            "The number of axis types has to match the number of axis names"
        )

    if axis_units is not None:
        assert len(axis_units) == dims, (
            "The number of axis types has to match the number of axis names"
        )

    for i in range(len(axis_names)):
        axes.append(
            Axis(
                name=axis_names[i],
                type=axis_types[i] if axis_types is not None else None,
                unit=axis_units[i] if axis_units is not None else None,
                min=roi_min[i] if roi_min is not None else None,
                max=roi_max[i] if roi_max is not None else None,
            )
        )
    return axes


class DisplayHint(BaseModel):
    """Metadata indicating how spatiotemporal axes are displayed by a viewer"""

    display_horizontal: str = Field(
        ..., description="Which spatial axis to use for horizontal display"
    )
    display_vertical: str = Field(..., description="Which spatial axis to use for vertical display")
    display_depth: str | None = Field(
        None, description="Optional, which spatial axis to use for depth display"
    )
    display_time: str | None = Field(
        None, description="Optional, which temporal axis to use for time"
    )


class PropMetadata(BaseModel):
    """Metadata describing a property in the geff graph."""

    identifier: str = Field(
        ...,
        description=(
            "Identifier of the property. Must be unique within its own component "
            "subgroup (nodes or edges). Must be a non-empty string."
        ),
    )
    dtype: str = Field(
        ...,
        description=(
            "Data type of the property. Must be a non-empty string. "
            "Valid values are: "
            f"{', '.join(str(dtype) for dtype in ALLOWED_DTYPES)}"
        ),
    )
    encoding: str | None = Field(
        None,
        description=(
            "Optional encoding when the property is stored as a string. For example, "
            "but not limited to, 'utf-8' or 'ascii'."
        ),
    )
    unit: str | None = Field(
        None,
        description=("Optional unit of the property."),
    )
    name: str | None = Field(
        None,
        description=("Optional human friendly name of the property"),
    )
    description: str | None = Field(
        None,
        description=("Optional description of the property."),
    )

    @model_validator(mode="after")
    def _validate_model(self) -> PropMetadata:
        if not self.identifier:
            raise ValueError("Property identifier cannot be an empty string.")
        if not self.dtype:
            raise ValueError("Property dtype cannot be an empty string.")

        if not validate_data_type(self.dtype):
            warnings.warn(
                f"Data type {self.dtype} not in valid data types {ALLOWED_DTYPES}. "
                "Reader applications may not know what to do with this information.",
                stacklevel=2,
            )
        if self.encoding is not None and not validate_str_encoding(self.encoding):
            warnings.warn(
                f"Encoding {self.encoding} not in valid encodings {VALID_STR_ENCODINGS}. "
                "Reader applications may not know what to do with this information.",
                stacklevel=2,
            )

        return self


def validate_props_metadata(
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
        None,
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
        ...,
        pattern=VERSION_PATTERN,
        description=(
            "Geff version string following semantic versioning (MAJOR.MINOR.PATCH), "
            "optionally with .devN and/or +local parts (e.g., 0.3.1.dev6+g61d5f18).\n"
            "If not provided, the version will be set to the current geff package version."
        ),
    )

    directed: bool = Field(description="True if the graph is directed, otherwise False.")
    axes: Sequence[Axis] | None = Field(
        None,
        description="Optional list of Axis objects defining the axes of each node in the graph.\n"
        "Each object's `name` must be an existing attribute on the nodes. The optional `type` key"
        "must be one of `space`, `time` or `channel`, though readers may not use this information. "
        "Each axis can additionally optionally define a `unit` key, which should match the valid"
        "OME-Zarr units, and `min` and `max` keys to define the range of the axis.",
    )

    node_props_metadata: dict[str, PropMetadata] | None = Field(
        None,
        description=(
            "Metadata for node properties. The keys are the property identifiers, "
            "and the values are PropMetadata objects describing the properties."
        ),
    )
    edge_props_metadata: dict[str, PropMetadata] | None = Field(
        None,
        description=(
            "Metadata for edge properties. The keys are the property identifiers, "
            "and the values are PropMetadata objects describing the properties."
        ),
    )

    sphere: str | None = Field(
        None,
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
        None,
        title="Node property: Detections as ellipsoids",
        description=(
            """
            Name of the `ellipsoid` property.

            An ellipsoid is assumed to be in the same coordinate system as the `space` type
            properties.

            It is defined by
            - a center point :math:`c`, already given by the `space` type properties
            - a covariance matrix :math:`\\Sigma`, symmetric and positive-definite, stored in this
              property as a `2x2`/`3x3` array.

            To plot the ellipsoid:
            - Compute the eigendecomposition of the covariance matrix
            :math:`\\Sigma = Q \\Lambda Q^{\\top}`
            - Sample points :math:`z` on the unit sphere
            - Transform the points to the ellipsoid by
            :math:`x = c + Q \\Lambda^{(1/2)} z`.
            """
        ),
    )
    track_node_props: dict[Literal["lineage", "tracklet"], str] | None = Field(
        None,
        description=(
            "Node properties denoting tracklet and/or lineage IDs.\n"
            "A tracklet is defined as a simple path of connected nodes "
            "where the initiating node has any incoming degree and outgoing degree at most 1,"
            "and the terminating node has incoming degree at most 1 and any outgoing degree, "
            "and other nodes along the path have in/out degree of 1. Each tracklet must contain "
            "the maximal set of connected nodes that match this definition - no sub-tracklets.\n"
            "A lineage is defined as a weakly connected component on the graph.\n"
            "The dictionary can store one or both of 'tracklet' or 'lineage' keys."
        ),
    )
    related_objects: Sequence[RelatedObject] | None = Field(
        None,
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
    affine: Affine | None = Field(
        None,
        description="Affine transformation matrix to transform the graph coordinates to the "
        "physical coordinates. The matrix must have the same number of dimensions as the number of "
        "axes in the graph.",
    )
    display_hints: DisplayHint | None = Field(
        None, description="Metadata indicating how spatiotemporal axes are displayed by a viewer"
    )
    extra: Any = Field(
        default_factory=dict,
        description="Extra metadata that is not part of the schema",
    )

    @model_validator(mode="before")
    @classmethod
    def _validate_model_before(cls, values: dict) -> dict:
        if values.get("geff_version") is None:
            values["geff_version"] = version("geff")
        return values

    @model_validator(mode="after")
    def _validate_model_after(self) -> GeffMetadata:
        # Axes names must be unique
        if self.axes is not None:
            names = [ax.name for ax in self.axes]
            if len(names) != len(set(names)):
                raise ValueError(f"Duplicate axes names found in {names}")

            if self.affine is not None:
                if self.affine.ndim != len(self.axes):
                    raise ValueError(
                        f"Affine transformation matrix must have {len(self.axes)} dimensions, "
                        f"got {self.affine.ndim}"
                    )

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
            validate_props_metadata(self.node_props_metadata, "node")
        if self.edge_props_metadata is not None:
            validate_props_metadata(self.edge_props_metadata, "edge")

        return self

    def write(self, group: zarr.Group | Path | str):
        """Helper function to write GeffMetadata into the zarr geff group.
        Maintains consistency by preserving ignored attributes with their original values.

        Args:
            group (zarr.Group | Path): The geff group to write the metadata to
        """
        if isinstance(group, Path | str):
            group = zarr.open(group)

        group.attrs["geff"] = self.model_dump(mode="json")

    @classmethod
    def read(cls, group: zarr.Group | Path) -> GeffMetadata:
        """Helper function to read GeffMetadata from a zarr geff group.

        Args:
            group (zarr.Group | Path): The zarr group containing the geff metadata

        Returns:
            GeffMetadata: The GeffMetadata object
        """
        if isinstance(group, Path):
            group = zarr.open(group)

        # Check if geff_version exists in zattrs
        if "geff" not in group.attrs:
            raise ValueError(
                f"No geff key found in {group}. This may indicate the path is incorrect or "
                f"zarr group name is not specified (e.g. /dataset.zarr/tracks/ instead of "
                f"/dataset.zarr/)."
            )

        return cls(**group.attrs["geff"])


class GeffSchema(BaseModel):
    geff: GeffMetadata = Field(..., description="geff_metadata")
