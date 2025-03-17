import json
import re
from importlib.resources import files
from pathlib import Path

import yaml
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
    roi_min: tuple[float, ...]
    roi_max: tuple[float, ...]
    position_attr: str = "position"
    axis_names: tuple[str, ...] | None = None
    axis_units: tuple[str, ...] | None = None

    def model_post_init(self, *args, **kwargs):
        if len(self.roi_min) != len(self.roi_max):
            raise ValueError(
                f"Roi min {self.roi_min} and roi max {self.roi_max} have different lengths."
            )
        ndim = len(self.roi_min)
        for dim in range(ndim):
            if self.roi_min[dim] > self.roi_max[dim]:
                raise ValueError(
                    f"Roi min {self.roi_min} is greater than max {self.roi_max} in dimension {dim}"
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


def write_metadata_schema(outpath: Path):
    metadata_schema = GeffMetadata.model_json_schema()
    with open(outpath, "w") as f:
        f.write(json.dumps(metadata_schema, indent=2))
