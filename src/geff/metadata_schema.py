from __future__ import annotations

import json
import warnings
from collections.abc import Sequence  # noqa: TC003
from importlib.metadata import version
from pathlib import Path
from typing import Literal

import zarr
from pydantic import BaseModel, Field, model_validator
from pydantic.config import ConfigDict

from .units import (
    VALID_AXIS_TYPES,
    VALID_SPACE_UNITS,
    VALID_TIME_UNITS,
    validate_axis_type,
    validate_space_unit,
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


class RelatedObject(BaseModel):
    type: Literal["labels", "image"] = Field(
        ...,
        description=(
            "Type of the related object. 'labels' for label objects, 'image' for image objects."
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
    directed: bool
    axes: Sequence[Axis] | None = None
    related_objects: Sequence[RelatedObject] | None = Field(
        None,
        description=(
            "A list of dictionaries of related objects such as labels or images. "
            "Each dictionary must contain 'type', 'path', and optionally 'label_prop' properties. "
            "The 'type' must be either 'labels' or 'image'. "
            "The 'path' should be relative to the geff zarr-attributes file. "
            "It is strongly recommended all related objects are stored as siblings "
            "of the geff group within the top-level zarr group. "
            "The 'label_prop' is only valid for type 'labels' and specifies the node property "
            "that will be used to identify the labels in the related object. "
        ),
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
        return self

    def write(self, group: zarr.Group | Path | str):
        """Helper function to write GeffMetadata into the zarr geff group.

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


def write_metadata_schema(outpath: Path):
    """Write the current geff metadata schema to a json file

    Args:
        outpath (Path): The file to write the schema to
    """
    metadata_schema = GeffSchema.model_json_schema()
    with open(outpath, "w") as f:
        f.write(json.dumps(metadata_schema, indent=2))
