from __future__ import annotations

import json
import re
import warnings
from importlib.resources import files
from pathlib import Path

import yaml
import zarr
from pydantic import BaseModel, Field, model_validator
from pydantic.config import ConfigDict

import geff

from .units import VALID_AXIS_TYPES, validate_axis_type, validate_space_unit

with (files(geff) / "supported_versions.yml").open() as f:
    SUPPORTED_VERSIONS = yaml.safe_load(f)["versions"]


def _get_versions_regex(versions: list[str]):
    return r"|".join([rf"({re.escape(version)})" for version in versions])


SUPPORTED_VERSIONS_REGEX = _get_versions_regex(SUPPORTED_VERSIONS)


class Axis(BaseModel):
    name: str
    type: str | None = None
    unit: str | None = None
    min: float | None = None
    max: float | None = None

    @model_validator(mode="after")
    def _validate_model(self) -> GeffMetadata:
        if (self.min is None) != (self.max is None):
            raise ValueError(
                f"Min and max must both be None or neither: got min {min} and max {max}"
            )
        if self.min is not None and self.min > self.max:
            raise ValueError(f"Min {min} is greater than max {max}")
        if self.type is not None and validate_axis_type(self.type):
            warnings.warn(
                f"Type {self.type} not in valid types {VALID_AXIS_TYPES}."
                "Reader applications may not know what to do with this information."
            )
        if self.type == "space" and not validate_space_unit(self.unit):
            raise ValueError()
        elif self.type == "time" and not validate_space_unit(self.unit):
            raise ValueError()


class GeffMetadata(BaseModel):
    """
    Geff metadata schema to validate the attributes json file in a geff zarr
    """

    # this determines the title of the generated json schema
    model_config = ConfigDict(title="geff_metadata", validate_assignment=True)
    axes: list[Axis]

    geff_version: str = Field(pattern=SUPPORTED_VERSIONS_REGEX)
    directed: bool

    def write(self, group: zarr.Group | Path):
        """Helper function to write GeffMetadata into the zarr geff group.

        Args:
            group (zarr.Group | Path): The geff group to write the metadata to
        """
        if isinstance(group, Path):
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
