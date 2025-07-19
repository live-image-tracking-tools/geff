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


def validate_space_unit(unit_name: str):
    """validate_space_unit

    Returns True if a space unit is a KNOWN valid unit.
    Return False if the unit is not known. The unit may be valid.
    """
    return unit_name in VALID_SPACE_UNITS


def validate_time_unit(unit_name: str):
    """validate_time_unit

    Returns True if a time unit is a KNOWN valid unit.
    Return False if the unit is not known. The unit may be valid.
    """
    return unit_name in VALID_TIME_UNITS
