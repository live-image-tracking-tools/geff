import numpy as np

# OME-NGFF 0.5 units
# https://github.com/ome/ngff/blob/7ac3430c74a66e5bcf53e41c429143172d68c0a4/index.bs#L240-L245

VALID_SPACE_UNITS = [
    None,
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
]

VALID_TIME_UNITS = [
    None,
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
]

VALID_AXIS_TYPES = [
    "space",
    "time",
    "channel",  # TODO: discuss
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
ALLOWED_DTYPES: set[np.dtype] = {
    np.bool_,
    np.int8,
    np.int16,
    np.int32,
    np.int64,
    np.uint8,
    np.uint16,
    np.uint32,
    np.uint64,
    np.float32,
    np.float64,
    np.bytes_,
    np.str_,
}


def validate_data_type(data_type: np.dtype | str | type) -> bool:
    """Return *True* when *data_type* is allowed for Java-Zarr.

    The function is intentionally *permissive* in what it accepts - any object
    that can be interpreted as a NumPy dtype (including a dtype object itself
    or a string like ``"int16"``) is valid input.  Internally we normalise the
    value to the canonical dtype and compare it against a allow-list.

    Examples
    --------
    >>> validate_data_type("int32")
    True
    >>> validate_data_type(">i4")
    True
    >>> validate_data_type(_np.float16)
    False
    """
    return np.dtype(data_type).type in ALLOWED_DTYPES


def validate_axis_type(axis_type: str) -> bool:
    """Validate axis type against standard list

    Args:
        axis_type (str): Axis type to check

    Returns:
        bool: False if the axis is not in valid types
    """
    return axis_type in VALID_AXIS_TYPES


def validate_space_unit(unit_name: str) -> bool:
    """Checks space unit against ome-zarr supported units

    Args:
        unit_name (str): Unit name to check

    Returns:
        bool: True if a space unit is a KNOWN valid unit.
        False if the unit is not known. The unit may be valid.
    """
    return unit_name in VALID_SPACE_UNITS


def validate_time_unit(unit_name: str) -> bool:
    """Check time unit against ome-zarr supported units

    Args:
        unit_name (str): Unit name to check

    Returns:
        bool: True if a time unit is a KNOWN valid unit.
        False if the unit is not known. The unit may be valid.
    """
    return unit_name in VALID_TIME_UNITS
