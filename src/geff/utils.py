from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import numpy as np
import zarr
from pydantic import BaseModel

from geff.validators.validators import (
    validate_lineages,
    validate_no_repeated_edges,
    validate_no_self_edges,
    validate_nodes_for_edges,
    validate_tracklets,
)

if TYPE_CHECKING:
    from zarr.storage import StoreLike

    from .dict_representation import GraphDict

from .metadata_schema import GeffMetadata


def remove_tilde(store: StoreLike) -> StoreLike:
    """
    Remove tilde from a store path/str, because zarr (3?) will not recognize
        the tilde and write the zarr in the wrong directory.

    Args:
        store (str | Path | zarr store): The store to remove the tilde from

    Returns:
        StoreLike: The store with the tilde removed
    """
    if isinstance(store, str | Path):
        store_str = str(store)
        if "~" in store_str:
            store = os.path.expanduser(store_str)
    return store


def validate(store: StoreLike):
    """Check that the structure of the zarr conforms to geff specification

    Args:
        store (str | Path | zarr store): Check the geff zarr, either str/Path/store

    Raises:
        AssertionError: If geff specs are violated
        ValueError: If store is not a valid zarr store or path doesn't exist
    """

    # Check if path exists for string/Path inputs
    if isinstance(store, str | Path):
        store_path = Path(store)
        if not store_path.exists():
            raise ValueError(f"Path does not exist: {store}")

    # Open the zarr group from the store
    try:
        graph = zarr.open_group(store, mode="r")
    except Exception as e:
        raise ValueError("store must be a zarr StoreLike") from e

    # graph attrs validation
    # Raises pydantic.ValidationError or ValueError
    meta = GeffMetadata.read(graph)

    validate_zarr_structure(graph, meta)


def validate_zarr_structure(graph: zarr.Group, meta: GeffMetadata):
    """Check that the structure of the zarr conforms to geff specification

    Also checks that any special properties match their spec

    Args:
        graph (zarr.Group): The zarr group containing the geff metadata
        meta (GeffMetadata): Metadata from geff
    """

    assert "nodes" in graph, "graph group must contain a nodes group"
    nodes = graph["nodes"]

    # ids and required and must by int type
    assert "ids" in nodes.array_keys(), "nodes group must contain an ids array"
    assert np.issubdtype(nodes["ids"].dtype, np.integer), "node ids must have an integer dtype"

    # Properties on nodes are optional
    if "props" in nodes.group_keys():
        validate_graph_group(nodes, "node")

    if "edges" in graph.group_keys():
        edges = graph["edges"]

        # Edges only require ids which contain nodes for each edge
        assert "ids" in edges, "edge group must contain ids array"
        id_shape = edges["ids"].shape
        assert id_shape[-1] == 2, (
            f"edges ids must have a last dimension of size 2, received shape {id_shape}"
        )

        if "props" in edges:
            validate_graph_group(edges, "edge")

    # Metadata based validation
    if meta.axes is not None:
        validate_axes_structure(graph, meta)


def validate_zarr_data(graph_dict: GraphDict):
    """Runs checks on loaded data based on information present in the metadata

    Args:
        graph_dict (GraphDict): A graphdict object which contains metadata and
            dictionaries of node/edge property arrays
    """
    node_ids = graph_dict["nodes"]
    edge_ids = graph_dict["edges"]

    valid, invalid_edges = validate_nodes_for_edges(node_ids, edge_ids)
    if not valid:
        raise ValueError(f"Some edges are missing nodes:\n{invalid_edges}")

    valid, invalid_edges = validate_no_self_edges(edge_ids)
    if not valid:
        raise ValueError(f"Self edges found in data:\n{invalid_edges}")

    valid, invalid_edges = validate_no_repeated_edges(edge_ids)
    if not valid:
        raise ValueError(f"Repeated edges found in data:\n{invalid_edges}")


class ValidationConfig(BaseModel):
    sphere: bool = False
    ellipsoid: bool = False
    lineage: bool = False
    tracklet: bool = False


def validate_optional_data(config: ValidationConfig, graph_dict: GraphDict):
    """Run data validation on optional data types based on the input

    Args:
        config (ValidationConfig): Configuration for which validation to run
        graph_dict (GraphDict): A graphdict object which contains metadata and
            dictionaries of node/edge property arrays
    """
    meta = graph_dict["metadata"]
    if config.sphere and meta.sphere is not None:
        raise NotImplementedError

    if config.ellipsoid and meta.ellipsoid is not None:
        raise NotImplementedError

    if meta.track_node_props is not None:
        if config.lineage and "tracklet" in meta.track_node_props:
            node_ids = graph_dict["nodes"]
            edge_ids = graph_dict["edges"]
            tracklet_key = meta.track_node_props["tracklet"]
            tracklet_ids = graph_dict["node_props"][tracklet_key]
            valid, errors = validate_tracklets(node_ids, edge_ids, tracklet_ids)
            if not valid:
                raise ValueError("Found invalid tracklets:\n", "\n".join(errors))

        if config.lineage and "lineage" in meta.track_node_props:
            node_ids = graph_dict["nodes"]
            edge_ids = graph_dict["edges"]
            lineage_key = meta.track_node_props["lineage"]
            lineage_ids = graph_dict["node_props"][lineage_key]
            valid, errors = validate_lineages(node_ids, edge_ids, lineage_ids)
            if not valid:
                raise ValueError("Found invalid lineages:\n", "\n".join(errors))


def validate_graph_group(group: zarr.Group, type: Literal["node", "edge"]):
    """Verify that either a group of nodes or edges has basic correct structure

    - First dimension size must match the number of ids
    - Missing arrays must be boolean

    Args:
        group (zarr.Group): The zarr group containing the geff metadata
        type (Literal[str]): Type of group being evaluated. Either edge or node
    """
    # Property array length should match id length
    id_len = group["ids"].shape[0]
    for prop in group["props"].keys():
        prop_group = group["props"][prop]
        assert "values" in prop_group.array_keys(), (
            f"{type} property group {prop} must have values group"
        )
        prop_len = prop_group["values"].shape[0]
        assert prop_len == id_len, (
            f"{type} property {prop} values has length {prop_len}, which does not match "
            f"id length {id_len}"
        )
        if "missing" in prop_group.array_keys():
            missing_len = prop_group["missing"].shape[0]
            assert missing_len == id_len, (
                f"{type} property {prop} missing mask has length {missing_len}, which "
                f"does not match id length {id_len}"
            )
            missing_dtype = prop_group["missing"].dtype
            assert np.issubdtype(missing_dtype, np.bool_), (
                f"Missing array for property {prop} must be boolean"
            )


def validate_axes_structure(graph: zarr.Group, meta: GeffMetadata):
    """Verify that any metadata regarding axes is actually present in the data

    - Property exists with name matching Axis name
    - Data is 1D
    - Missing values not allowed

    Args:
        graph (zarr.Group): The zarr group containing the geff metadata
        meta (GeffMetadata): Metadata from geff
    """
    if meta.axes is not None:
        node_prop_group = graph["nodes/props"]
        for ax in meta.axes:
            # Array must be present without missing values
            assert f"{ax.name}/values" in node_prop_group, f"Axis {ax.name} data is missing"
            assert f"{ax.name}/missing" not in node_prop_group, (
                f"Axis {ax.name} has missing values which are not allowed"
            )
            # Only 1d data allowed, already checked length of first axis
            ndim = len(node_prop_group[f"{ax.name}/values"].shape)
            assert ndim == 1, f"Axis property {ax.name} has {ndim} dimensions, must be 1D"
