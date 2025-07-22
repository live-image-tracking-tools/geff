import warnings
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Literal

import numpy as np

from .write_arrays import write_id_arrays, write_props_arrays


def write_dicts(
    geff_path: Path | str,
    node_data: Sequence[tuple[Any, dict[str, Any]]],
    edge_data: Sequence[tuple[Any, dict[str, Any]]],
    node_prop_names: Sequence[str],
    edge_prop_names: Sequence[str],
    axis_names: list[str] | None = None,
    zarr_format: Literal[2, 3] = 2,
) -> None:
    """Write a dict-like graph representation to geff

    Args:
        geff_path (Path | str): The path to the geff zarr group to write to
        node_data (Sequence[tuple[Any, dict[str, Any]]]): A sequence of tuples with
            node_ids and node_data, where node_data is a dictionary from str names
            to any values.
        edge_data (Sequence[tuple[Any, dict[str, Any]]]): A sequence of tuples with
            edge_ids and edge_data, where edge_data is a dictionary from str names
            to any values.
        node_prop_names (Sequence[str]): A list of node properties to include in the
            geff
        edge_prop_names (Sequence[str]): a list of edge properties to include in the
            geff
        axis_names (Sequence[str] | None): The name of the spatiotemporal properties, if
            any. Defaults to None
        zarr_format (Literal[2, 3]): The zarr specification to use when writing the zarr.
            Defaults to 2.

    Raises:
        ValueError: If the position prop is given and is not present on all nodes.
    """
    node_ids = [idx for idx, _ in node_data]
    edge_ids = [idx for idx, _ in edge_data]

    if len(node_ids) > 0:
        nodes_arr = np.asarray(node_ids)
    else:
        nodes_arr = np.empty((0,), dtype=np.int64)

    if len(edge_ids) > 0:
        edges_arr = np.asarray(edge_ids, dtype=nodes_arr.dtype)
    else:
        edges_arr = np.empty((0, 2), dtype=nodes_arr.dtype)

    write_id_arrays(geff_path, nodes_arr, edges_arr, zarr_format=zarr_format)

    if axis_names is not None:
        node_prop_names = list(node_prop_names)
        for axis in axis_names:
            if axis not in node_prop_names:
                node_prop_names.append(axis)

    node_props_dict = dict_props_to_arr(node_data, node_prop_names)
    if axis_names is not None:
        for axis in axis_names:
            missing_arr = node_props_dict[axis][1]
            if missing_arr is not None:
                raise ValueError(
                    f"Spatiotemporal property '{axis}' not found in : "
                    f"{nodes_arr[missing_arr].tolist()}"
                )
    write_props_arrays(geff_path, "nodes", node_props_dict, zarr_format=zarr_format)

    edge_props_dict = dict_props_to_arr(edge_data, edge_prop_names)
    write_props_arrays(geff_path, "edges", edge_props_dict, zarr_format=zarr_format)


def _get_max_length_in_bytes(data: Sequence[Any] | str) -> int:
    """Recursively get the maximum length of strings in bytes in a nested sequence

    Args:
        data (Sequence[Any]): A sequence that may contain nested sequences or strings

    Returns:
        int: The maximum length of the strings in bytes
    """
    if isinstance(data, str):
        return len(data.encode("utf-8"))
    max_length = 0
    for item in data:
        if isinstance(item, Sequence):
            max_length = max(max_length, _get_max_length_in_bytes(item))
    return max_length


def _to_padded_utf8_bytes(
    data: Sequence[Any] | str,
    length: int,
) -> np.ndarray:
    """Convert a string or sequence of strings to a padded UTF-8 byte array.

    Args:
        data (Sequence[Any] | str): The data to convert, which can be a string or a
        sequence of strings.
        length (int): The length to pad the byte array to.
    Returns:
        np.ndarray: A numpy array of type `uint8` containing the padded UTF-8 bytes.
    Raises:
        TypeError: If the data is not a string or a sequence of strings.
    """
    if isinstance(data, str):
        encoded_bytes = np.frombuffer(data.encode("utf-8"), dtype=np.uint8)
        padded = np.zeros(length, dtype=np.uint8)
        padded[: len(encoded_bytes)] = encoded_bytes
        return padded
    elif isinstance(data, Sequence):
        return [_to_padded_utf8_bytes(item, length) for item in data]
    else:
        raise TypeError("Data must be a string or a sequence of strings.")


def _determine_value_type(data: Sequence[tuple[Any, dict[str, Any]]], prop_name: str) -> Any:
    """Determine the type of the property values

    Find the first non-missing value and returns its type. If there are no non-missing
    values, returns None.

    Args:
        data (Sequence[tuple[Any, dict[str, Any]]]): A sequence of elements and a dictionary
            holding the properties of that element
        prop_name (str): The property to get the type for

    Returns:
        Any: The type of the property values, or None if no non-missing values are found.
    """
    for _, data_dict in data:
        if prop_name in data_dict:
            value = data_dict[prop_name]
            while isinstance(value, list | tuple):
                value = value[0]
            return type(value)
    return None


def _determine_default_value(data: Sequence[tuple[Any, dict[str, Any]]], prop_name: str) -> Any:
    """Determine default value to fill in missing values

    Find the first non-missing value and then uses the following heuristics:
    - Native python numerical types (int, float) -> 0
    - Native python string -> ""
    - Otherwise, return the  value, which is definitely the right type and
    shape, but is potentially both confusing and inefficient. Should reconsider in
    the future.

    If there are no non-missing values, warns and then returns 0.

    Args:
        data (Sequence[tuple[Any, dict[str, Any]]]): A sequence of elements and a dictionary
            holding the properties of that element
        prop_name (str): The property to get the default value for

    Returns:
        Any: A value to use as the default that is the same dtype and shape as the rest
            of the values, for casting to a numpy array without errors.
    """
    for _, data_dict in data:
        # find first non-missing value
        if prop_name in data_dict:
            value = data_dict[prop_name]
            if isinstance(value, int | float):
                return 0
            elif isinstance(value, str):
                return ""
            else:
                return value
    warnings.warn(
        f"Property {prop_name} is not present on any graph elements. Using 0 as the default.",
        stacklevel=2,
    )
    return 0


def dict_props_to_arr(
    data: Sequence[tuple[Any, dict[str, Any]]],
    prop_names: Sequence[str],
) -> dict[str, tuple[np.ndarray, np.ndarray | None]]:
    """Convert dict-like properties to values and missing array representation.

    Note: The order of the sequence of data should be the same as that used to write
    the ids, or this will not work properly.

    Args:
        data (Sequence[tuple[Any, dict[str, Any]]]): A sequence of elements and a dictionary
            holding the properties of that element
        prop_names (str): The properties to include in the dictionary of property arrays.

    Returns:
        dict[tuple[np.ndarray, np.ndarray | None]]: A dictionary from property names
            to a tuple of (value, missing) arrays, where the missing array can be None.
    """
    props_dict = {}
    for name in prop_names:
        values = []
        missing = []
        # iterate over the data and checks for missing content
        missing_any = False
        # to ensure valid dtype of missing, take first non-missing value
        default_val = None
        for _, data_dict in data:
            if name in data_dict:
                values.append(data_dict[name])
                missing.append(False)
            else:
                if default_val is None:
                    default_val = _determine_default_value(data, name)
                values.append(default_val)
                missing.append(True)
                missing_any = True
        if _determine_value_type(data, name) is str:
            max_length = _get_max_length_in_bytes(values)
            values = [_to_padded_utf8_bytes(v, max_length) for v in values]
        values_arr = np.asarray(values)
        missing_arr = np.asarray(missing, dtype=bool) if missing_any else None
        props_dict[name] = (values_arr, missing_arr)
    return props_dict
