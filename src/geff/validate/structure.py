from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, cast

import numpy as np
import zarr

from geff import _path
from geff.core_io._utils import expect_array, expect_group, is_remote_url

if TYPE_CHECKING:
    from collections.abc import Mapping

    from zarr.storage import StoreLike


from geff.metadata import GeffMetadata, PropMetadata


def validate_structure(store: StoreLike) -> None:
    """Ensure that the structure of the zarr conforms to geff specification

    Args:
        store (str | Path | zarr store): Check the geff zarr, either str/Path/store

    Raises:
        ValueError: If geff specs are violated
        FileNotFoundError: If store is not a valid zarr store or path doesn't exist
    """

    # Check if path exists for string/Path inputs
    if isinstance(store, str | Path):
        store_path = Path(store)
        if not is_remote_url(str(store_path)) and not store_path.exists():
            raise FileNotFoundError(f"Path does not exist: {store}")

    # Open the zarr group from the store
    try:
        graph_group = zarr.open_group(store, mode="r")
    except Exception as e:
        raise ValueError(f"store must be a zarr StoreLike: {e}") from e

    # graph attrs validation
    # Raises pydantic.ValidationError or ValueError
    metadata = GeffMetadata.read(store)

    nodes_group = expect_group(graph_group, _path.NODES)
    _validate_nodes_group(nodes_group, metadata)

    # TODO: Do we want to prevent missing values on spatialtemporal properties
    if _path.EDGES in graph_group.keys():
        edges_group = expect_group(graph_group, _path.EDGES)
        _validate_edges_group(edges_group, metadata)


def _validate_props_metadata(
    props_metadata_dict: Mapping[str, PropMetadata],
    component_props: zarr.Group,
    component_type: str,
) -> None:
    """Validate that properties described in metadata are compatible with the data in zarr arrays.

    Args:
        props_metadata_dict (dict): Dictionary of property metadata with identifier keys
            and PropMetadata values
        component_props (zarr.Group): Zarr group containing the component properties (nodes
            or edges)
        component_type (str): Component type for error messages ("Node" or "Edge")

    Raises:
        AssertionError: If properties in metadata don't match zarr arrays
    """
    for prop in props_metadata_dict.values():
        prop_id = prop.identifier
        # Properties described in metadata should be present in zarr arrays
        if not isinstance(props_group := component_props.get(prop_id), zarr.Group):
            raise ValueError(
                f"{component_type} property {prop_id} described in metadata is not present "
                f"in props arrays"
            )

        # dtype in metadata should match dtype in zarr arrays
        values_array = expect_array(props_group, _path.VALUES, component_type)
        array_dtype = values_array.dtype
        prop_dtype = np.dtype(prop.dtype).type
        if array_dtype != prop_dtype:
            raise ValueError(
                f"{component_type} property {prop_id} with dtype {array_dtype} does not match "
                f"metadata dtype {prop_dtype}"
            )


def _validate_props_group(
    props_group: zarr.Group,
    expected_len: int,
    parent_key: str,
) -> None:
    """Validate every property subgroup under `props_group`."""
    for prop_name in props_group.keys():
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

        val_len = cast("zarr.Array", prop_group[_path.VALUES]).shape[0]
        if val_len != expected_len:
            raise ValueError(
                f"{parent_key} property {prop_name!r} {_path.VALUES} has length {val_len}, "
                f"which does not match id length {expected_len}"
            )

        if _path.MISSING in arrays:
            miss_len = cast("zarr.Array", prop_group[_path.MISSING]).shape[0]
            if miss_len != expected_len:
                raise ValueError(
                    f"{parent_key} property {prop_name!r} {_path.MISSING} mask has length "
                    f"{miss_len}, which does not match id length {expected_len}"
                )


def _validate_nodes_group(nodes_group: zarr.Group, metadata: GeffMetadata) -> None:
    """Validate the structure of a nodes group in a GEFF zarr store."""
    node_ids = expect_array(nodes_group, _path.IDS, _path.NODES)
    id_len = node_ids.shape[0]
    node_props = expect_group(nodes_group, _path.PROPS, _path.NODES)
    _validate_props_group(node_props, id_len, "Node")

    # Node properties metadata validation
    if metadata.node_props_metadata is not None:
        _validate_props_metadata(metadata.node_props_metadata, node_props, "Node")


def _validate_edges_group(edges_group: zarr.Group, metadata: GeffMetadata) -> None:
    """Validate the structure of an edges group in a GEFF zarr store."""
    # Edges only require ids which contain nodes for each edge
    edges_ids = expect_array(edges_group, _path.IDS, _path.EDGES)
    if edges_ids.shape[-1] != 2:
        raise ValueError(
            f"edges ids must have a last dimension of size 2, received shape {edges_ids.shape}"
        )

    # Edge property array length should match edge id length
    edge_id_len = edges_ids.shape[0]
    edge_props = edges_group.get(_path.PROPS)
    if edge_props is None:
        return
    if not isinstance(edge_props, zarr.Group):
        raise ValueError(
            f"{_path.EDGES!r} group must contain a {_path.PROPS!r} group. Got {type(edge_props)}"
        )
    _validate_props_group(edge_props, edge_id_len, "Edge")
    # Edge properties metadata validation
    if metadata.edge_props_metadata is not None:
        _validate_props_metadata(metadata.edge_props_metadata, edge_props, "Edge")
