from __future__ import annotations

import json
import re
from importlib.resources import files
from pathlib import Path
from typing import Any

import yaml
import zarr
from pydantic import BaseModel, Field, model_validator
from pydantic.config import ConfigDict

import geff

with (files(geff) / "supported_versions.yml").open() as f:
    SUPPORTED_VERSIONS = yaml.safe_load(f)["versions"]


def _get_versions_regex(versions: list[str]):
    return r"|".join([rf"({re.escape(version)})" for version in versions])


SUPPORTED_VERSIONS_REGEX = _get_versions_regex(SUPPORTED_VERSIONS)


class GeffMetadata(BaseModel):
    """
    Geff metadata schema to validate the attributes json file in a geff zarr
    """

    # this determines the title of the generated json schema
    model_config = ConfigDict(validate_assignment=True, extra="allow")

    geff_version: str = Field(pattern=SUPPORTED_VERSIONS_REGEX)
    directed: bool
    roi_min: tuple[float, ...] | None = None
    roi_max: tuple[float, ...] | None = None
    position_prop: str | None = None
    axis_names: tuple[str, ...] | None = None
    axis_units: tuple[str, ...] | None = None

    @model_validator(mode="after")
    def _validate_model(self) -> GeffMetadata:
        # Check spatial metadata only if position is provided
        if self.position_prop is not None:
            # Check that rois are there if position provided
            if self.roi_min is None or self.roi_max is None:
                raise ValueError(
                    f"Position property {self.position_prop} has been specified, "
                    "but roi_min and/or roi_max are not specified."
                )

            if len(self.roi_min) != len(self.roi_max):
                raise ValueError(
                    f"Roi min {self.roi_min} and roi max {self.roi_max} have different lengths."
                )
            ndim = len(self.roi_min)
            for dim in range(ndim):
                if self.roi_min[dim] > self.roi_max[dim]:
                    raise ValueError(
                        f"Roi min {self.roi_min} is greater than "
                        f"max {self.roi_max} in dimension {dim}"
                    )

            if self.axis_names is not None and len(self.axis_names) != ndim:
                raise ValueError(
                    f"Length of axis names ({len(self.axis_names)}) does not match number of"
                    f" dimensions in roi ({ndim})"
                )
            if self.axis_units is not None and len(self.axis_units) != ndim:
                raise ValueError(
                    f"Length of axis units ({len(self.axis_units)}) does not match number of"
                    f" dimensions in roi ({ndim})"
                )
        # If no position, check that other spatial metadata is not provided
        elif any([self.roi_min, self.roi_max, self.axis_names, self.axis_units]):
            raise ValueError(
                "Spatial metadata (roi_min, roi_max, axis_names or axis_units) provided without"
                " position_prop"
            )
        return self

    def write(self, group: zarr.Group | Path):
        """Helper function to write GeffMetadata into the zarr geff group.
        Maintains consistency by preserving ignored attributes with their original values.

        Args:
            group (zarr.Group | Path): The geff group to write the metadata to
        """
        if isinstance(group, Path):
            group = zarr.open(group)

        all_data = self.model_dump(mode="json")
        geff_data = {k: v for k, v in all_data.items() if k in GeffMetadata.model_fields}

        group.attrs["geff"] = geff_data

        # Write extra attributes as individual attributes with their original values
        for key, value in self:
            if key not in GeffMetadata.model_fields:
                group.attrs[key] = value

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

        # Separate known geff attributes from others to be passed as ignored_attrs
        geff_attrs = group.attrs.asdict()
        model_fields = set(cls.model_fields.keys())
        ignored_attrs = {
            key: value for key, value in geff_attrs.items() if key not in model_fields and key != "geff"
        }

        # Check if geff_version exists in zattrs
        if "geff" not in group.attrs:
            raise ValueError(
                f"No geff key found in {group}. This may indicate the path is incorrect or "
                f"zarr group name is not specified (e.g. /dataset.zarr/tracks/ instead of "
                f"/dataset.zarr/)."
            )

        geff_data = group.attrs["geff"]
        if ignored_attrs:
            geff_data.update(ignored_attrs)

        return cls(**geff_data)


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
