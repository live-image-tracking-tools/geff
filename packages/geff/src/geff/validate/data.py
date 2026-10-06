from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

from geff.validate.graph import (
    validate_no_repeated_edges,
    validate_no_self_edges,
    validate_nodes_for_edges,
    validate_unique_node_ids,
)
from geff.validate.shapes import (
    validate_ellipsoid,
    validate_mesh,
    validate_polygon,
    validate_sphere,
)
from geff.validate.tracks import (
    validate_lineages,
    validate_tracklets,
)
from geff_spec.utils import validate_metadata

if TYPE_CHECKING:
    from geff._typing import InMemoryGeff


class ValidationConfig(BaseModel):
    graph: bool = False
    metadata: bool = True
    sphere: bool = False
    ellipsoid: bool = False
    polygon: bool = False
    mesh: bool = False
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

    if config.metadata:
        validate_metadata(meta)

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
        sphere_prop = memory_geff["node_props"][meta.sphere]
        validate_sphere(sphere_prop["values"], sphere_prop["missing"])

    if config.ellipsoid and meta.ellipsoid is not None:
        ellipsoid_prop = memory_geff["node_props"][meta.ellipsoid]
        validate_ellipsoid(ellipsoid_prop["values"], meta.axes, ellipsoid_prop["missing"])

    if config.polygon and meta.polygon is not None:
        polygon_prop = memory_geff["node_props"][meta.polygon]
        validate_polygon(polygon_prop["values"], meta.axes, polygon_prop["missing"])

    if config.mesh and meta.mesh is not None:
        mesh = meta.mesh
        vertices_prop = memory_geff["node_props"][mesh.vertices]
        triangles_prop = memory_geff["node_props"][mesh.triangles]
        vertex_normals_prop = (
            memory_geff["node_props"][mesh.vertex_normals]
            if mesh.vertex_normals is not None
            else None
        )
        triangle_normals_prop = (
            memory_geff["node_props"][mesh.triangle_normals]
            if mesh.triangle_normals is not None
            else None
        )
        validate_mesh(
            vertices_prop["values"],
            triangles_prop["values"],
            meta.axes,
            vertex_normals=vertex_normals_prop["values"] if vertex_normals_prop else None,
            triangle_normals=triangle_normals_prop["values"] if triangle_normals_prop else None,
            vertices_missing=vertices_prop["missing"],
            triangles_missing=triangles_prop["missing"],
            vertex_normals_missing=vertex_normals_prop["missing"] if vertex_normals_prop else None,
            triangle_normals_missing=triangle_normals_prop["missing"]
            if triangle_normals_prop
            else None,
        )

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
