from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import zarr

from geff import _path
from geff.core_io._utils import expect_array, expect_group, open_storelike

if TYPE_CHECKING:
    from zarr.storage import StoreLike

    from geff_spec import PropMetadata


from geff_spec import GeffMetadata


def validate_structure(store: StoreLike) -> None:
    """Ensure that the structure of the zarr conforms to geff specification

    Args:
        store (str | Path | zarr store): Check the geff zarr, either str/Path/store

    Raises:
        ValueError: If geff specs are violated
        FileNotFoundError: If store is not a valid zarr store or path doesn't exist
    """

    graph_group = open_storelike(store)

    # graph attrs validation
    # Raises pydantic.ValidationError or ValueError
    metadata = GeffMetadata.read(store)

    nodes_group = expect_group(graph_group, _path.NODES)
    _validate_nodes_group(nodes_group, metadata)

    edges_group = expect_group(graph_group, _path.EDGES)
    _validate_edges_group(edges_group, metadata)

    # Metadata based validation
    if metadata.axes is not None:
        _validate_axes_structure(graph_group, metadata)


def _validate_axes_structure(graph: zarr.Group, meta: GeffMetadata) -> None:
    """Verify that any metadata regarding axes is actually present in the data

    - Property exists with name matching Axis name
    - Data is 1D
    - Missing values not allowed

    Args:
        graph (zarr.Group): The zarr group containing the geff metadata
        meta (GeffMetadata): Metadata from geff
    """
    if meta.axes is not None:
        node_prop_group = expect_group(graph, "nodes/props")
        for ax in meta.axes:
            # Array must be present without missing values
            if f"{ax.name}/values" not in node_prop_group:
                raise ValueError(f"Axis {ax.name} data is missing")
            if f"{ax.name}/missing" in node_prop_group:
                raise ValueError(f"Axis {ax.name} has missing values which are not allowed")
            # Only 1d data allowed, already checked length of first axis
            ndim = len(expect_array(node_prop_group, f"{ax.name}/values").shape)
            if ndim != 1:
                raise ValueError(f"Axis property {ax.name} has {ndim} dimensions, must be 1D")


def _validate_props_group(
    props_group: zarr.Group,
    expected_len: int,
    parent_key: str,
    props_metadata: dict[str, PropMetadata],
) -> None:
    """Validate every property subgroup under `props_group`."""
    # check that all properties in the metadata are in the group
    for prop_name in props_metadata:
        if prop_name not in props_group.keys():
            raise ValueError(
                f"Property {prop_name} is in the metadata but missing from the property group"
            )

    for prop_name in props_group.keys():
        # check that all properties in the group are in the metadata
        if prop_name not in props_metadata:
            raise ValueError(f"Property {prop_name} is missing from the property metadata")
        prop_metadata = props_metadata[prop_name]

        prop_group = props_group[prop_name]
        if not isinstance(prop_group, zarr.Group):
            raise ValueError(
                f"{_path.PROPS!r} group '{prop_name}' under {parent_key!r} "
                f"must be a zarr group. Got {type(prop_group)}"
            )

        arrays = set(prop_group.array_keys())
        if _path.VALUES not in arrays:
            raise ValueError(
                f"{parent_key} property group {prop_name!r} must have a {_path.VALUES!r} array"
            )
        val_arr = expect_array(prop_group, _path.VALUES)

        # Check varlength cases
        if prop_metadata.varlength:
            data_arr = expect_array(prop_group, _path.DATA)
            if not np.issubdtype(val_arr.dtype, np.uint64):
                raise ValueError(
                    f"Varlength property {prop_name} values array does not have type uint64"
                )
            # data array dtype should match metadata dtype
            if not np.issubdtype(data_arr.dtype, np.dtype(prop_metadata.dtype)):
                raise ValueError(
                    f"Property {prop_name} has stated dtype {prop_metadata.dtype} but actual "
                    f"dtype {val_arr.dtype}"
                )
        else:
            # check value dtype against metadata dtype
            if not np.issubdtype(val_arr.dtype, np.dtype(prop_metadata.dtype)):
                raise ValueError(
                    f"Property {prop_name} has stated dtype {prop_metadata.dtype} but actual "
                    f"dtype {val_arr.dtype}"
                )
            if _path.DATA in arrays:
                raise ValueError(
                    f"Found data array for property {prop_name} which is not a varlength property"
                )

        # check values length
        val_len = val_arr.shape[0]
        if val_len != expected_len:
            raise ValueError(
                f"{parent_key} property {prop_name!r} {_path.VALUES} has length {val_len}, "
                f"which does not match id length {expected_len}"
            )

        if _path.MISSING in arrays:
            missing_arr = expect_array(prop_group, _path.MISSING)
            miss_len = missing_arr.shape[0]
            if miss_len != expected_len:
                raise ValueError(
                    f"{parent_key} property {prop_name!r} {_path.MISSING} mask has length "
                    f"{miss_len}, which does not match id length {expected_len}"
                )

            if not np.issubdtype(missing_arr.dtype, np.bool_):
                raise ValueError(
                    f"{parent_key} property {prop_name!r} {_path.MISSING} must be boolean"
                )


def _validate_nodes_group(nodes_group: zarr.Group, metadata: GeffMetadata) -> None:
    """Validate the structure of a nodes group in a GEFF zarr store."""
    node_ids = expect_array(nodes_group, _path.IDS, _path.NODES)

    # Node ids must be int dtype
    if not np.issubdtype(np.dtype(node_ids.dtype), np.integer):
        raise ValueError("Node ids must have an integer dtype")

    id_len = node_ids.shape[0]
    node_props = expect_group(nodes_group, _path.PROPS, _path.NODES)
    _validate_props_group(node_props, id_len, "Node", metadata.node_props_metadata)


def _validate_edges_group(edges_group: zarr.Group, metadata: GeffMetadata) -> None:
    """Validate the structure of an edges group in a GEFF zarr store."""
    # Edges only require ids which contain nodes for each edge
    edges_ids = expect_array(edges_group, _path.IDS, _path.EDGES)
    if edges_ids.ndim != 2 or edges_ids.shape[-1] != 2:
        raise ValueError(
            f"edges ids must be 2d with last dimension of size 2, received shape {edges_ids.shape}"
        )
    if not np.issubdtype(np.dtype(edges_ids.dtype), np.integer):
        raise ValueError("Edge ids must have an integer dtype")

    # Edge property array length should match edge id length
    edge_id_len = edges_ids.shape[0]
    edge_props = edges_group.get(_path.PROPS)
    if edge_props is None:
        return
    if not isinstance(edge_props, zarr.Group):
        raise ValueError(
            f"{_path.EDGES!r} group must contain a {_path.PROPS!r} group. Got {type(edge_props)}"
        )
    _validate_props_group(edge_props, edge_id_len, "Edge", metadata.edge_props_metadata)
