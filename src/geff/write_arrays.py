from pathlib import Path

import numpy as np
import zarr

from .metadata_schema import GeffMetadata


def write_arrays(
    geff_path: Path | str,
    node_ids: np.ndarray,
    node_props: dict[str, tuple[np.ndarray, np.ndarray | None]] | None,
    edge_ids: np.ndarray,
    edge_props: dict[str, tuple[np.ndarray, np.ndarray | None]] | None,
    metadata: GeffMetadata,
):
    """Write a geff file from already constructed arrays of node and edge ids and props

    Currently does not do any validation that the arrays are valid, but could be added
    as an optional flag.

    Args:
        geff_path (Path | str): _description_
        node_ids (np.ndarray): _description_
        node_props (dict[str, tuple[np.ndarray, np.ndarray  |  None]] | None): _description_
        edge_ids (np.ndarray): _description_
        edge_props (dict[str, tuple[np.ndarray, np.ndarray  |  None]] | None): _description_
        metadata (GeffMetadata): _description_
    """
    write_id_arrays(geff_path, node_ids, edge_ids)
    if node_props is not None:
        write_props_arrays(geff_path, "nodes", node_props)
    if edge_props is not None:
        write_props_arrays(geff_path, "edges", edge_props)
    metadata.write(geff_path)


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
