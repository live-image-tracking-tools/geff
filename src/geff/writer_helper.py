from pathlib import Path
from typing import Any, Sequence

import numpy as np
import zarr


def write_dict_like(
    geff_path: Path | str,
    node_data: Sequence[tuple[Any, dict[str, Any]]],
    edge_data: Sequence[tuple[Any, dict[str, Any]]],
    node_prop_names: Sequence[str],
    edge_prop_names: Sequence[str],
    position_prop: str | None = None,
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
        position_prop (str | None, optional): The position property, if any,
            for checking if it has missing values. Defaults to None.

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

    write_id_arrays(geff_path, nodes_arr, edges_arr)

    if position_prop is not None and position_prop not in node_prop_names:
        node_prop_names = list(node_prop_names)
        node_prop_names.append(position_prop)

    node_props_dict = dict_props_to_arr(node_data, node_prop_names)
    if position_prop is not None:
        pos_missing_arr = node_props_dict[position_prop][1]
        if pos_missing_arr is not None:
            raise ValueError(
                f"Position property '{position_prop}' not found in : "
                "{nodes_arr[pos_missing_arr].tolist()}"
            )
    write_props_arrays(geff_path, "nodes", node_props_dict)

    edge_props_dict = dict_props_to_arr(edge_data, edge_prop_names)
    write_props_arrays(geff_path, "edges", edge_props_dict)


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
        for _, data_dict in data:
            if name in data_dict:
                values.append(data_dict[name])
                missing.append(False)
            else:
                values.append(0)  # this fails to non-scalar properties
                missing.append(True)
                missing_any = True
        values_arr = np.asarray(values)
        missing_arr = np.asarray(missing, dtype=bool) if missing_any else None
        props_dict[name] = (values_arr, missing_arr)
    return props_dict


def write_id_arrays(geff_path: Path | str, node_ids: np.ndarray, edge_ids: np.ndarray) -> None:
    """Writes a set of node ids and edge ids to a geff group.

    Args:
        geff_path (Path): path to geff group to write the nodes/ids and edges/ids into
        node_ids (np.ndarray): an array of strings or ints with shape (N,)
        edge_ids (np.ndarray): an array with same type as node_ds and shape (N, 2)
    Raises:
        TypeError if node_ids and edge_ids have different types, or if either are float
    """
    if node_ids.dtype != edge_ids.dtype:
        raise TypeError(
            f"Node ids and edge ids must have same dtype: {node_ids.dtype=}, {edge_ids.dtype=}"
        )
    geff_root = zarr.open(str(geff_path))
    geff_root["nodes/ids"] = node_ids
    geff_root["edges/ids"] = edge_ids


def write_props_arrays(
    geff_path: Path | str, group: str, props: dict[str, tuple[np.ndarray, np.ndarray | None]]
) -> None:
    """Writes a set of properties to a geff nodes or edges group.

    Can be used to add new properties if they don't already exist.

    Args:
        geff_path (Path): path to geff group to write the properties to
        group (str): "nodes" or "edges"
        props (dict[str, tuple[np.ndarray, np.ndarray  |  None]]): a dictionary from
            attr name to (attr_values, attr_missing) arrays.
    Raises:
        ValueError: If the group is not a 'nodes' or 'edges' group.
    TODO: validate attrs length based on group ids shape?
    """
    if group not in ["nodes", "edges"]:
        raise ValueError(f"Group must be a 'nodes' or 'edges' group. Found {group}")
    geff_root = zarr.open(str(geff_path))
    props_group = geff_root.require_group(f"{group}/props")
    for prop, arrays in props.items():
        prop_group = props_group.create_group(prop)
        values, missing = arrays
        prop_group["values"] = values
        if missing is not None:
            prop_group["missing"] = missing
