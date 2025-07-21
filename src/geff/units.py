# OME-NGFF 0.5 units
# https://github.com/ome/ngff/blob/7ac3430c74a66e5bcf53e41c429143172d68c0a4/index.bs#L240-L245

VALID_SPACE_UNITS = [
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

VALID_SHAPE_TYPES = [
    "sphere",
    "ellipsoid",
]


def validate_axis_type(axis_type: str) -> bool:
    """Validate axis type against standard list

    Args:
        axis_type (str): Axis type to check

    Returns:
        bool: False if the axis is not in valid types
    """
    return axis_type in VALID_AXIS_TYPES


def validate_shape_type(shape_type: str) -> bool:
    """Validate shape type against standard list

    Args:
        shape_type (str): Shape type to check

    Returns:
        bool: False if the shape is not in valid types
    """
    return shape_type in VALID_SHAPE_TYPES


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
