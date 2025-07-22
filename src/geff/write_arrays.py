from pathlib import Path
from typing import Literal

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
    node_props_unsquish: dict[str, list[str]] | None = None,
    edge_props_unsquish: dict[str, list[str]] | None = None,
    zarr_format: Literal[2, 3] = 2,
):
    """Write a geff file from already constructed arrays of node and edge ids and props

    Currently does not do any validation that the arrays are valid, but could be added
    as an optional flag.

    Args:
        geff_path (Path | str): The path to the zarr group where the graph will be written
        node_ids (np.ndarray): An array containing the node ids. Must have same dtype as
            edge_ids.
        node_props (dict[str, tuple[np.ndarray, np.ndarray  |  None]] | None): A dictionary
            from node property names to (values, missing) arrays, which should have same
            length as node_ids.
        edge_ids (np.ndarray): An array containing the edge ids. Must have same dtype
            as node_ids.
        edge_props (dict[str, tuple[np.ndarray, np.ndarray  |  None]] | None): A dictionary
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
    """
    write_id_arrays(geff_path, node_ids, edge_ids)
    if node_props is not None:
        write_props_arrays(
            geff_path, "nodes", node_props, node_props_unsquish, zarr_format=zarr_format
        )
    if edge_props is not None:
        write_props_arrays(
            geff_path, "edges", edge_props, edge_props_unsquish, zarr_format=zarr_format
        )
    metadata.write(geff_path)


def write_id_arrays(
    geff_path: Path | str,
    node_ids: np.ndarray,
    edge_ids: np.ndarray,
    zarr_format: Literal[2, 3] = 2,
) -> None:
    """Writes a set of node ids and edge ids to a geff group.

    Args:
        geff_path (Path): path to geff group to write the nodes/ids and edges/ids into
        node_ids (np.ndarray): an array of strings or ints with shape (N,)
        edge_ids (np.ndarray): an array with same type as node_ds and shape (N, 2)
        zarr_format (Literal[2, 3]): The zarr specification to use when writing the zarr.
            Defaults to 2.
    Raises:
        TypeError if node_ids and edge_ids have different types, or if either are float
    """
    if node_ids.dtype != edge_ids.dtype:
        raise TypeError(
            f"Node ids and edge ids must have same dtype: {node_ids.dtype=}, {edge_ids.dtype=}"
        )
    path = str(geff_path)
    if zarr.__version__.startswith("3"):
        geff_root = zarr.open(path, mode="a", zarr_format=zarr_format)  # zarr format defaulted to 2
    else:
        geff_root = zarr.open(path, mode="a")
    geff_root["nodes/ids"] = node_ids
    geff_root["edges/ids"] = edge_ids


def write_props_arrays(
    geff_path: Path | str,
    group: str,
    props: dict[str, tuple[np.ndarray, np.ndarray | None]],
    props_unsquish: dict[str, list[str]] | None = None,
    zarr_format: Literal[2, 3] = 2,
) -> None:
    """Writes a set of properties to a geff nodes or edges group.

    Can be used to add new properties if they don't already exist.

    Args:
        geff_path (Path): path to geff group to write the properties to
        group (str): "nodes" or "edges"
        props (dict[str, tuple[np.ndarray, np.ndarray  |  None]]): a dictionary from
            attr name to (attr_values, attr_missing) arrays.
        props_unsquish (dict[str, list[str]] | None): a dictionary indicication
            how to "unsquish" a property into individual scalars (e.g.:
            `{"pos": ["z", "y", "x"]}` will store the position property as
            three individual properties called "z", "y", and "x".
        zarr_format (Literal[2, 3]): The zarr specification to use when writing the zarr.
            Defaults to 2.
    Raises:
        ValueError: If the group is not a 'nodes' or 'edges' group.
    TODO: validate attrs length based on group ids shape?
    """
    if group not in ["nodes", "edges"]:
        raise ValueError(f"Group must be a 'nodes' or 'edges' group. Found {group}")

    if props_unsquish is not None:
        for name, replace_names in props_unsquish.items():
            array, missing = props[name]
            assert len(array.shape) == 2, "Can only unsquish 2D arrays."
            replace_arrays = {
                replace_name: (array[:, i], None if not missing else missing[:, i])
                for i, replace_name in enumerate(replace_names)
            }
            del props[name]
            props.update(replace_arrays)

    path = str(geff_path)
    if zarr.__version__.startswith("3"):
        geff_root = zarr.open(path, mode="a", zarr_format=zarr_format)  # zarr format defaulted to 2
    else:
        geff_root = zarr.open(path, mode="a")
    props_group = geff_root.require_group(f"{group}/props")
    for prop, arrays in props.items():
        prop_group = props_group.create_group(prop)
        values, missing = arrays
        prop_group["values"] = values
        if missing is not None:
            prop_group["missing"] = missing
