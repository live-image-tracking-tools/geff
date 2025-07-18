from __future__ import annotations

import json
import re
from importlib.resources import files
from pathlib import Path

import yaml
import zarr
from pydantic import BaseModel, Field
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
    model_config = ConfigDict(title="geff_metadata")

    geff_version: str = Field(pattern=SUPPORTED_VERSIONS_REGEX)
    directed: bool

    spatial_attrs: tuple[str, ...] | None = None
    spatial_units: tuple[str, ...] | None = None
    spatial_min: tuple[float, ...] | None = None
    spatial_max: tuple[float, ...] | None = None

    time_attr: str | None = None
    time_unit: str | None = None
    time_min: float | None = None
    time_max: float | None = None

    def model_post_init(self, *args, **kwargs):  # noqa D102
        # Check spatial metadata only if position is provided
        if self.spatial_attrs is not None:
            # Check that rois are there if position provided
            if self.roi_min is None or self.roi_max is None:
                raise ValueError(
                    f"Spatial attributes {self.spatial_attrs} has been specified, "
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

            if len(self.spatial_attrs) != ndim:
                raise ValueError(
                    f"Length of spatial attributes ({len(self.spatial_attrs)}) does not match"
                    f" number of dimensions in roi ({ndim})"
                )
            if self.spatial_units is not None and len(self.spatial_units) != ndim:
                raise ValueError(
                    f"Length of axis units ({len(self.spatial_units)}) does not match number of"
                    f" dimensions in roi ({ndim})"
                )
        # If no position, check that other spatial metadata is not provided
        else:
            if any([self.roi_min, self.roi_max, self.spatial_units]):
                raise ValueError(
                    "Spatial metadata (roi_min, roi_max, or spatial_units) provided without"
                    " spatial_attrs"
                )

        # Check temporal metadata only if time_attr is provided
        if self.time_attr is not None:
            # Check that min and max are there if time provided
            if self.time_min is None or self.time_max is None:
                raise ValueError(
                    f"time attribute {self.time_attr} has been specified, "
                    "but time_min and/or time_max are not specified."
                )

            if self.time_min > self.time_max:
                raise ValueError(f"Time min {self.time_min} is greater than max {self.time_max}")
        # If no time, check that other temporal metadata is not provided
        else:
            if any([self.time_min, self.time_max, self.time_unit]):
                raise ValueError(
                    "Temporal metadata (time_min, time_max, or time_unit) provided without"
                    " time_attr"
                )

    def write(self, group: zarr.Group | Path):
        """Helper function to write GeffMetadata into the zarr geff group.

        Args:
            group (zarr.Group | Path): The geff group to write the metadata to
        """
        if isinstance(group, Path):
            group = zarr.open(group)
        for key, value in self:
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
        return cls(**group.attrs)


def write_metadata_schema(outpath: Path):
    """Write the current geff metadata schema to a json file

    Args:
        outpath (Path): The file to write the schema to
    """
    metadata_schema = GeffMetadata.model_json_schema()
    with open(outpath, "w") as f:
        f.write(json.dumps(metadata_schema, indent=2))
