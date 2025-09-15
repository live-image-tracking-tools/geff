from importlib.metadata import PackageNotFoundError, version

try:
    __version__: str = version("geff_spec")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "uninstalled"

from ._affine import Affine
from ._prop_metadata import PropMetadata
from ._schema import Axis, DisplayHint, GeffMetadata, GeffSchema, RelatedObject
from ._valid_values import (
    AxisType,
    SpaceUnits,
    TimeUnits,
    validate_axis_type,
    validate_data_type,
    validate_space_unit,
    validate_time_unit,
)

__all__ = [
    "Affine",
    "Axis",
    "AxisType",
    "DisplayHint",
    "GeffMetadata",
    "GeffSchema",
    "PropMetadata",
    "RelatedObject",
    "SpaceUnits",
    "TimeUnits",
    "validate_axis_type",
    "validate_data_type",
    "validate_space_unit",
    "validate_time_unit",
]
