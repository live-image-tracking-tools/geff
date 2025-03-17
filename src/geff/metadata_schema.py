import json
from enum import Enum

from typing import Annotated
from pathlib import Path
import yaml
from importlib.resources import files
import geff
import re

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict

with (files(geff) / "supported_versions.yml").open() as f:
    SUPPORTED_VERSIONS = yaml.safe_load(f)["versions"]

def _get_versions_regex(versions: list[str]):
    return r"|".join([r"({})".format(re.escape(version)) for version in versions])
SUPPORTED_VERSIONS_REGEX = _get_versions_regex(SUPPORTED_VERSIONS)

class MetadataModel(BaseModel): 
    """
    Geff metadata schema to validate the attributes json file in a geff zarr
    """
    # this determines the title of the generated json schema
    model_config = ConfigDict(title='geff_metadata')

    geff_version: str = Field(pattern=SUPPORTED_VERSIONS_REGEX)
    directed: bool
    roi_min: tuple[float, ...]
    roi_max: tuple[float, ...]  # validate that the max is >= min in each dimension
    position_attr: str = "position"
    axis_names: tuple[str] | None = None # validate that same length as roi dims, if exists
    axis_units: tuple[str] | None = None # validate that same length as roi dims, if exists


def write_schema(outpath: Path):
    metadata_schema = MetadataModel.model_json_schema()
    with open(outpath, 'w') as f:
        f.write(json.dumps(metadata_schema, indent=2))

write_schema(Path("schema.json"))