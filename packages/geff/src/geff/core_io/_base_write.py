from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Any, Literal

import numpy as np

from geff import _path
from geff.core_io._utils import construct_var_len_props, delete_geff, remove_tilde, setup_zarr_group
from geff.validate.structure import validate_structure
from geff_spec.utils import (
    add_or_update_props_metadata,
    compute_and_add_axis_min_max,
    create_props_metadata,
)

from ._serialization import serialize_vlen_property_data

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

    from zarr.storage import StoreLike

    from geff._typing import PropDictNpArray
    from geff_spec import GeffMetadata, PropMetadata


def write_dicts(
    geff_store: StoreLike,
    node_data: Iterable[tuple[Any, dict[str, Any]]],
    edge_data: Iterable[tuple[Any, dict[str, Any]]],
    node_prop_names: Sequence[str],
    edge_prop_names: Sequence[str],
    metadata: GeffMetadata,
    zarr_format: Literal[2, 3] = 2,
    structure_validation: bool = True,
) -> None:
    """Write a dict-like graph representation to geff

    Args:
        geff_store (str | Path | zarr store): The path/str to the geff zarr, or the store
            itself. Opens in append mode, so will only overwrite geff-controlled groups.
        node_data (Sequence[tuple[Any, dict[str, Any]]]): A sequence of tuples with
            node_ids and node_data, where node_data is a dictionary from str names
            to any values.
        edge_data (Sequence[tuple[Any, dict[str, Any]]]): A sequence of tuples with
            edge_ids and edge_data, where edge_data is a dictionary from str names
            to any values.
        node_prop_names (Sequence[str]): A list of node properties to include in the
            geff
        edge_prop_names (Sequence[str]): A list of edge properties to include in the
            geff
        metadata (GeffMetadata): The core metadata to write. Node/edge properties and
            axis min and maxes will be overwritten.
        zarr_format (Literal[2, 3]): The zarr specification to use when writing the zarr.
            Defaults to 2.
        structure_validation (bool): If True, runs structural validation and does not write
            a geff that is invalid. Defaults to True.

    Raises:
        ValueError: If the position prop is given and is not present on all nodes.
    """

    geff_store = remove_tilde(geff_store)

    node_data = list(node_data)
    edge_data = list(edge_data)
    node_ids = [idx for idx, _ in node_data]
    edge_ids = [idx for idx, _ in edge_data]

    if len(node_ids) > 0:
        nodes_arr = np.asarray(node_ids)
        # Check if we can cast to uint
        if any(nodes_arr < 0):
            raise ValueError("Cannot write a geff with node ids that are negative")
        if not np.issubdtype(nodes_arr.dtype, np.integer):
            warnings.warn(
                f"Node ids with dtype {nodes_arr.dtype} are being cast to uint", stacklevel=2
            )
        nodes_arr = nodes_arr.astype("uint")
    else:
        nodes_arr = np.empty((0,), dtype=np.uint64)

    if len(edge_ids) > 0:
        edges_arr = np.asarray(edge_ids, dtype=nodes_arr.dtype)
    else:
        edges_arr = np.empty((0, 2), dtype=nodes_arr.dtype)

    node_props_dict = dict_props_to_arr(node_data, node_prop_names)

    edge_props_dict = dict_props_to_arr(edge_data, edge_prop_names)
    write_arrays(
        geff_store,
        nodes_arr,
        node_props_dict,
        edges_arr,
        edge_props_dict,
        metadata,
        zarr_format=zarr_format,
        structure_validation=structure_validation,
    )


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
) -> dict[str, PropDictNpArray]:
    """Convert dict-like properties to values and missing array representation.

    Note: The order of the sequence of data should be the same as that used to write
    the ids, or this will not work properly.

    Args:
        data (Sequence[tuple[Any, dict[str, Any]]]): A sequence of elements and a dictionary
            holding the properties of that element
        prop_names (str): The properties to include in the dictionary of property arrays.

    Returns:
        dict[PropDictNpArray]: A dictionary from property names
            to a tuple of (value, missing) arrays, where the missing array can be None.
    """
    props_dict: dict[str, PropDictNpArray] = {}
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
        # try casting the list of values to a numpy array
        try:
            values_arr = np.asarray(values)
        # catch a value error which will happen if we have elements that are different shapes
        except ValueError:
            # try to construct variable length properties - will raise an error if internal
            # dtypes are not compatible (e.g. floats and strings)
            values_arr = construct_var_len_props(values)["values"]
        missing_arr = np.asarray(missing, dtype=bool) if missing_any else None
        props_dict[name] = {"missing": missing_arr, "values": values_arr}
    return props_dict


def write_arrays(
    geff_store: StoreLike,
    node_ids: np.ndarray,
    node_props: dict[str, PropDictNpArray] | None,
    edge_ids: np.ndarray,
    edge_props: dict[str, PropDictNpArray] | None,
    metadata: GeffMetadata,
    node_props_unsquish: dict[str, list[str]] | None = None,
    edge_props_unsquish: dict[str, list[str]] | None = None,
    zarr_format: Literal[2, 3] = 2,
    structure_validation: bool = True,
) -> None:
    """Write a geff file from already constructed arrays of node and edge ids and props

    Currently does not do any validation that the arrays are valid, but could be added
    as an optional flag.
    Adds the PropMetadata for the nodes and edges, if not provided.

    Args:
        geff_store (str | Path | zarr store): The path/str to the geff zarr, or the store
            itself. Opens in append mode, so will only overwrite geff-controlled groups.
        node_ids (np.ndarray): An array containing the node ids. Must have same dtype as
            edge_ids.
        node_props (dict[str, PropDictNpArray] | None): A dictionary
            from node property names to (values, missing) arrays, which should have same
            length as node_ids.
        edge_ids (np.ndarray): An array containing the edge ids. Must have same dtype
            as node_ids.
        edge_props (dict[str, PropDictNpArray] | None): A dictionary
            from edge property names to (values, missing) arrays, which should have same
            length as edge_ids.
        metadata (GeffMetadata): The metadata of the graph.
        zarr_format (Literal[2, 3]): The zarr specification to use when writing the zarr.
            Defaults to 2.
        node_props_unsquish (dict[str, list[str]] | None): a dictionary
            indicication how to "unsquish" a property into individual scalars
            (e.g.: `{"pos": ["z", "y", "x"]}` will store the position property
            as three individual properties called "z", "y", and "x".
        edge_props_unsquish (dict[str, list[str]] | None): a dictionary
            indicication how to "unsquish" a property into individual scalars
            (e.g.: `{"pos": ["z", "y", "x"]}` will store the position property
            as three individual properties called "z", "y", and "x".
        structure_validation (bool): If True, runs structural validation and does not write
            a geff that is invalid. Defaults to True.
    """
    geff_store = remove_tilde(geff_store)

    write_id_arrays(geff_store, node_ids, edge_ids, zarr_format=zarr_format)
    if node_props is not None:
        node_meta = write_props_arrays(
            geff_store, _path.NODES, node_props, node_props_unsquish, zarr_format=zarr_format
        )
    else:
        node_meta = []
    if edge_props is not None:
        edge_meta = write_props_arrays(
            geff_store, _path.EDGES, edge_props, edge_props_unsquish, zarr_format=zarr_format
        )
    else:
        edge_meta = []

    metadata = add_or_update_props_metadata(metadata, node_meta, "node")
    metadata = add_or_update_props_metadata(metadata, edge_meta, "edge")
    if node_props is not None:
        metadata = compute_and_add_axis_min_max(metadata, node_props)
    metadata.write(geff_store)

    if structure_validation:
        try:
            validate_structure(geff_store)
        except ValueError as e:
            message = "\nCannot write invalid geff."
            try:
                delete_geff(geff_store, zarr_format=zarr_format)
            except:  # noqa: E722
                message = (
                    "\nWritten geff is invalid, but cannot be deleted automatically. "
                    "Please delete manually."
                )
            raise ValueError(e.args[0] + message) from e


def write_id_arrays(
    geff_store: StoreLike,
    node_ids: np.ndarray,
    edge_ids: np.ndarray,
    zarr_format: Literal[2, 3] = 2,
) -> None:
    """Writes a set of node ids and edge ids to a geff group.

    Args:
        geff_store (str | Path | zarr store): path/str to geff group, or the store itself,
            to write the nodes/ids and edges/ids into
        node_ids (np.ndarray): an array of strings or ints with shape (N,)
        edge_ids (np.ndarray): an array with same type as node_ds and shape (N, 2)
        zarr_format (Literal[2, 3]): The zarr specification to use when writing the zarr.
            Defaults to 2.
    Raises:
        TypeError if node_ids and edge_ids have different types, or if either are float
    """
    geff_store = remove_tilde(geff_store)

    if node_ids.dtype != edge_ids.dtype:
        raise TypeError(
            f"Node ids and edge ids must have same dtype: {node_ids.dtype=}, {edge_ids.dtype=}"
        )
    if not np.issubdtype(node_ids.dtype, np.integer):
        raise TypeError(
            f"Node ids and edge ids must have int dtype: {node_ids.dtype=}, {edge_ids.dtype=}"
        )

    geff_root = setup_zarr_group(geff_store, zarr_format)
    geff_root[_path.NODE_IDS] = node_ids
    geff_root[_path.EDGE_IDS] = edge_ids


def write_props_arrays(
    geff_store: StoreLike,
    group: Literal["nodes", "edges"],
    props: dict[str, PropDictNpArray],
    props_unsquish: dict[str, list[str]] | None = None,
    zarr_format: Literal[2, 3] = 2,
) -> Sequence[PropMetadata]:
    """Writes a set of properties to a geff nodes or edges group.

    Can be used to add new properties if they don't already exist.

    Args:
        geff_store (str | Path | zarr store): The path/str to the geff zarr, or the store
            itself. Opens in append mode, so will only overwrite geff-controlled groups.
        group (Literal["nodes", "edges"]): "nodes" or "edges"
        props (dict[str, PropDictNpArray]): a dictionary from
            attr name to (attr_values, attr_missing) arrays.
        props_unsquish (dict[str, list[str]] | None): a dictionary indicication
            how to "unsquish" a property into individual scalars (e.g.:
            `{"pos": ["z", "y", "x"]}` will store the position property as
            three individual properties called "z", "y", and "x".
        zarr_format (Literal[2, 3]): The zarr specification to use when writing the zarr.
            Defaults to 2.

    Returns:
        PropMetadata: The property metadata for each of the property arrays
    Raises:
        ValueError: If the group is not a 'nodes' or 'edges' group.
    TODO: validate attrs length based on group ids shape?
    """

    geff_store = remove_tilde(geff_store)

    if group not in [_path.NODES, _path.EDGES]:
        raise ValueError(f"Group must be a {_path.NODES!r} or {_path.EDGES!r} group. Found {group}")

    if props_unsquish is not None:
        for name, replace_names in props_unsquish.items():
            values = props[name]["values"]
            missing = props[name]["missing"]
            if (not len(values.shape) == 2) or np.issubdtype(values.dtype, np.object_):
                raise ValueError(
                    "Can only unsquish 2D array properties that are not variable length."
                )

            replace_arrays: dict[str, PropDictNpArray]
            for i, replace_name in enumerate(replace_names):
                replace_arrays = {
                    replace_name: {
                        "values": values[:, i],
                        "missing": None if missing is None else missing,
                    }
                }
                props.update(replace_arrays)
            del props[name]

    geff_root = setup_zarr_group(geff_store, zarr_format)
    props_group = geff_root.require_group(f"{group}/{_path.PROPS}")
    metadata = []
    for prop, prop_dict in props.items():
        prop_metadata = create_props_metadata(prop, prop_dict)
        metadata.append(prop_metadata)

        if prop_metadata.varlength:
            values, missing, data = serialize_vlen_property_data(prop_dict)
        else:
            values = prop_dict["values"]
            missing = prop_dict["missing"]
            data = None

        prop_group = props_group.create_group(prop)
        prop_group[_path.VALUES] = values
        if missing is not None:
            prop_group[_path.MISSING] = missing
        if data is not None:
            prop_group[_path.DATA] = data

    return metadata
