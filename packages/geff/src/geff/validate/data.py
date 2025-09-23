from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

from geff.validate.graph import (
    validate_no_repeated_edges,
    validate_no_self_edges,
    validate_nodes_for_edges,
    validate_unique_node_ids,
)
from geff.validate.shapes import validate_ellipsoid, validate_sphere
from geff.validate.tracks import (
    validate_lineages,
    validate_tracklets,
)

if TYPE_CHECKING:
    from geff._typing import InMemoryGeff


class ValidationConfig(BaseModel):
    graph: bool = False
    sphere: bool = False
    ellipsoid: bool = False
    lineage: bool = False
    tracklet: bool = False


def validate_data(memory_geff: InMemoryGeff, config: ValidationConfig) -> None:
    """Validate the data of a geff based on the options selected in ValidationConfig

    Args:
        memory_geff (InMemoryGeff): An InMemoryGeff which contains metadata and
            dictionaries of node/edge property arrays
        config (ValidationConfig): Configuration for which validation to run
    """
    meta = memory_geff["metadata"]

    if config.graph:
        node_ids = memory_geff["node_ids"]
        edge_ids = memory_geff["edge_ids"]

        valid, nonunique_nodes = validate_unique_node_ids(node_ids)
        if not valid:
            raise ValueError(f"Some node ids are not unique:\n{nonunique_nodes}")

        valid, invalid_edges = validate_nodes_for_edges(node_ids, edge_ids)
        if not valid:
            raise ValueError(f"Some edges are missing nodes:\n{invalid_edges}")

        valid, invalid_edges = validate_no_self_edges(edge_ids)
        if not valid:
            raise ValueError(f"Self edges found in data:\n{invalid_edges}")

        valid, invalid_edges = validate_no_repeated_edges(edge_ids)
        if not valid:
            raise ValueError(f"Repeated edges found in data:\n{invalid_edges}")

    if config.sphere and meta.sphere is not None:
        radius = memory_geff["node_props"][meta.sphere]["values"]
        validate_sphere(radius)

    if config.ellipsoid and meta.ellipsoid is not None:
        covariance = memory_geff["node_props"][meta.ellipsoid]["values"]
        validate_ellipsoid(covariance, memory_geff["metadata"].axes)

    if meta.track_node_props is not None:
        if config.tracklet and "tracklet" in meta.track_node_props:
            node_ids = memory_geff["node_ids"]
            edge_ids = memory_geff["edge_ids"]
            tracklet_key = meta.track_node_props["tracklet"]
            tracklet_ids = memory_geff["node_props"][tracklet_key]["values"]
            valid, errors = validate_tracklets(node_ids, edge_ids, tracklet_ids)
            if not valid:
                raise ValueError("Found invalid tracklets:\n", "\n".join(errors))

        if config.lineage and "lineage" in meta.track_node_props:
            node_ids = memory_geff["node_ids"]
            edge_ids = memory_geff["edge_ids"]
            lineage_key = meta.track_node_props["lineage"]
            lineage_ids = memory_geff["node_props"][lineage_key]["values"]
            valid, errors = validate_lineages(node_ids, edge_ids, lineage_ids)
            if not valid:
                raise ValueError("Found invalid lineages:\n", "\n".join(errors))
