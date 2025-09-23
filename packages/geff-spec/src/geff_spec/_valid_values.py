from __future__ import annotations

from typing import Any, Literal, TypeAlias, TypeGuard, get_args

# -----------------------------------------------------------------------------
# Unit validation
# -----------------------------------------------------------------------------
# OME-NGFF 0.5 units
# https://github.com/ome/ngff/blob/7ac3430c74a66e5bcf53e41c429143172d68c0a4/index.bs#L240-L245

SpaceUnits: TypeAlias = Literal[
    "angstrom",
    "attometer",
    "centimeter",
    "decimeter",
    "exameter",
    "femtometer",
    "foot",
    "gigameter",
    "hectometer",
    "inch",
    "kilometer",
    "megameter",
    "meter",
    "micrometer",
    "mile",
    "millimeter",
    "nanometer",
    "parsec",
    "petameter",
    "picometer",
    "terameter",
    "yard",
    "yoctometer",
    "yottameter",
    "zeptometer",
    "zettameter",
    "pixel",
]

TimeUnits: TypeAlias = Literal[
    "attosecond",
    "centisecond",
    "day",
    "decisecond",
    "exasecond",
    "femtosecond",
    "gigasecond",
    "hectosecond",
    "hour",
    "kilosecond",
    "megasecond",
    "microsecond",
    "millisecond",
    "minute",
    "nanosecond",
    "petasecond",
    "picosecond",
    "second",
    "terasecond",
    "yoctosecond",
    "yottasecond",
    "zeptosecond",
    "zettasecond",
    "frame",
]


AxisType: TypeAlias = Literal[
    "space",
    "time",
    "channel",
]

# -----------------------------------------------------------------------------
# Data-type validation
# -----------------------------------------------------------------------------
# The Java reference implementations for Zarr (e.g. JZarr, zarr-java) currently
# do not support some of the more exotic NumPy types such as float16 ("half")
# or the various complex dtypes.  In order to guarantee that a written geff
# file can be consumed by those libraries we provide a small helper that can
# be used throughout the codebase to disallow them at write-time.

# References:
#   https://github.com/zarr-developers/zarr-java/blob/e758d5465d4ff8bb0ccaf2e632c8096b02a9d51c/src/main/java/dev/zarr/zarrjava/v3/DataType.java#L41
#   https://numpy.org/doc/stable/reference/arrays.dtypes.html
DTypes: TypeAlias = Literal[
    "bool",
    "int8",
    "int16",
    "int32",
    "int64",
    "uint8",
    "uint16",
    "uint32",
    "uint64",
    "float32",
    "float64",
    "bytes",
    "str",
]

VALID_SPACE_UNITS: tuple[SpaceUnits, ...] = get_args(SpaceUnits)
VALID_TIME_UNITS: tuple[TimeUnits, ...] = get_args(TimeUnits)
VALID_AXIS_TYPES: tuple[AxisType, ...] = get_args(AxisType)
VALID_DTYPES: tuple[DTypes, ...] = get_args(DTypes)


def validate_axis_type(axis_type: Any) -> TypeGuard[AxisType]:
    """Validate axis type against standard list

    Args:
        axis_type (str): Axis type to check

    Returns:
        bool: False if the axis is not in valid types
    """
    return axis_type in VALID_AXIS_TYPES


def validate_space_unit(unit_name: Any) -> TypeGuard[SpaceUnits]:
    """Checks space unit against ome-zarr supported units

    Args:
        unit_name (str): Unit name to check

    Returns:
        bool: True if a space unit is a KNOWN valid unit.
        False if the unit is not known. The unit may be valid.
    """
    return unit_name in VALID_SPACE_UNITS


def validate_time_unit(unit_name: Any) -> TypeGuard[TimeUnits]:
    """Check time unit against ome-zarr supported units

    Args:
        unit_name (str): Unit name to check

    Returns:
        bool: True if a time unit is a KNOWN valid unit.
        False if the unit is not known. The unit may be valid.
    """
    return unit_name in VALID_TIME_UNITS
