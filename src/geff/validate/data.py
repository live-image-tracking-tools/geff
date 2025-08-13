from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from pydantic import BaseModel

from geff.validate.graph import (
    validate_no_repeated_edges,
    validate_no_self_edges,
    validate_nodes_for_edges,
)
from geff.validate.tracks import (
    validate_lineages,
    validate_tracklets,
)

if TYPE_CHECKING:
    from geff._typing import InMemoryGeff

    from .dict_representation import GraphDict


def validate_zarr_data(graph_dict: InMemoryGeff) -> None:
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


def validate_optional_data(config: ValidationConfig, graph_dict: GraphDict) -> None:
    """Run data validation on optional data types based on the input

    Args:
        config (ValidationConfig): Configuration for which validation to run
        graph_dict (GraphDict): A graphdict object which contains metadata and
            dictionaries of node/edge property arrays
    """
    meta = graph_dict["metadata"]
    if config.sphere and meta.sphere is not None:
        if np.any(graph_dict["node_props"][meta.sphere]["values"] < 0):
            raise ValueError("Sphere radius values must be non-negative.")

    if config.ellipsoid and meta.ellipsoid is not None:
        covariance = graph_dict["node_props"][meta.ellipsoid]["values"]
        if not isinstance(covariance, np.ndarray):
            raise TypeError("Ellipsoid covariance must be a numpy array")
        if covariance.ndim != 3 or covariance.shape[1] != covariance.shape[2]:
            raise ValueError("Ellipsoid covariance must be square matrices")
        if not np.allclose(covariance, covariance.transpose((0, 2, 1))):
            raise ValueError("Ellipsoid covariance matrices must be symmetric")
        if not np.all(np.linalg.eigvals(covariance) > 0):
            raise ValueError("Ellipsoid covariance matrices must be positive-definite")

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
