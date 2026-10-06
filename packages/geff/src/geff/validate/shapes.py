from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from geff_spec import Axis


def _spatial_dim(axes: list[Axis] | None) -> int:
    """Count the number of spatial-type axes."""
    if axes is None:
        return 0
    return sum(1 for ax in axes if ax.type == "space")


def validate_ellipsoid(
    covariance: np.ndarray,
    axes: list[Axis] | None,
    missing: np.ndarray | None = None,
) -> None:
    """Validate that ellipsoid data has a valid covariance matrix

    The first axis of the covariance array corresponds to the number of nodes. The
    remaining axes correspond to the number of spatial axes.

    Args:
        covariance (np.ndarray): Covariance array stored as values for an ellipsoid property
        axes (list[Axis]): List of Axis metadata
        missing (np.ndarray | None): Optional 1D boolean array marking nodes that do not
            have ellipsoid data. Rows flagged `True` are excluded from the numeric checks.

    Raises:
        ValueError: Must define space axes in order to have ellipsoid data
        ValueError: Ellipsoid covariance matrix must have 1 + number of spatial dimensions
        ValueError: Spatial dimensions of covariance matrix must be equal
        ValueError: Ellipsoid covariance matrices must be symmetric
        ValueError: Ellipsoid covariance matrices must be positive-definite
    """
    spatial_dim = _spatial_dim(axes)
    if spatial_dim == 0:
        raise ValueError("Must define space axes in order to have ellipsoid data")

    if covariance.ndim != (exp_dim := spatial_dim + 1):
        raise ValueError(
            f"Ellipsoid covariance matrix must have {exp_dim} dimensions, got {covariance.ndim}"
        )

    if covariance.shape[1] != covariance.shape[2]:
        raise ValueError(
            f"Spatial dimensions of covariance matrix must be equal, got {covariance.shape[1:]}"
        )

    present = covariance if missing is None else covariance[~missing]

    transpose = [0, *list(range(present.ndim - 1, 0, -1))]
    if not np.allclose(present, np.transpose(present, axes=transpose)):
        raise ValueError("Ellipsoid covariance matrices must be symmetric")

    if not np.all(np.linalg.eigvals(present) > 0):
        raise ValueError("Ellipsoid covariance matrices must be positive-definite")


def validate_sphere(radius: np.ndarray, missing: np.ndarray | None = None) -> None:
    """Validate that sphere data has nonzero radii and is 1d

    Args:
        radius (np.ndarray): Values array of a sphere property
        missing (np.ndarray | None): Optional 1D boolean array marking nodes that do not
            have sphere data. Rows flagged `True` are excluded from the non-negativity check.

    Raises:
        ValueError: Sphere radius values must be non-negative
        ValueError: Sphere radius values must be 1D
    """
    if radius.ndim != 1:
        raise ValueError(f"Sphere radius values must be 1D, got {radius.ndim} dimensions")

    present = radius if missing is None else radius[~missing]
    if np.any(present < 0):
        raise ValueError("Sphere radius values must be non-negative.")


def validate_polygon(
    polygon: np.ndarray,
    axes: list[Axis] | None,
    missing: np.ndarray | None = None,
) -> None:
    """Validate that polygon data is well-formed.

    `polygon` is an object array with one entry per node (the deserialized values of a
    variable length property). For a single node, the entry is a `(n_points, n_dims)`
    array of points defined relative to the node's position, where `n_dims` matches the
    number of spatial axes.

    Args:
        polygon (np.ndarray): Object array of per-node polygon point arrays.
        axes (list[Axis] | None): List of Axis metadata.
        missing (np.ndarray | None): Optional 1D boolean array marking nodes that do not
            have polygon data. Rows flagged `True` are skipped.

    Raises:
        ValueError: Must define space axes in order to have polygon data
        ValueError: Polygon points must be a 2D array
        ValueError: Polygon points must match the number of spatial dimensions
        ValueError: Polygon must have at least 3 points
        ValueError: Polygon points must be finite
    """
    spatial_dim = _spatial_dim(axes)
    if spatial_dim == 0:
        raise ValueError("Must define space axes in order to have polygon data")

    for i, points in enumerate(polygon):
        if missing is not None and missing[i]:
            continue

        if points.ndim != 2:
            raise ValueError(
                f"Polygon points must be a 2D array, got {points.ndim} dimensions at node index {i}"
            )
        if points.shape[1] != spatial_dim:
            raise ValueError(
                f"Polygon points must have {spatial_dim} spatial dimensions, "
                f"got {points.shape[1]} at node index {i}"
            )
        if points.shape[0] < 3:
            raise ValueError(
                f"Polygon must have at least 3 points, got {points.shape[0]} at node index {i}"
            )
        if not np.all(np.isfinite(points)):
            raise ValueError(
                f"Polygon points must be finite, got non-finite values at node index {i}"
            )


def validate_mesh(
    vertices: np.ndarray,
    triangles: np.ndarray,
    axes: list[Axis] | None,
    vertex_normals: np.ndarray | None = None,
    triangle_normals: np.ndarray | None = None,
    vertices_missing: np.ndarray | None = None,
    triangles_missing: np.ndarray | None = None,
    vertex_normals_missing: np.ndarray | None = None,
    triangle_normals_missing: np.ndarray | None = None,
) -> None:
    """Validate that mesh data is well-formed.

    `vertices` and `triangles` (and, if given, `vertex_normals`/`triangle_normals`) are
    object arrays with one entry per node (the deserialized values of variable length
    properties). For a single node, `vertices` is `(V, 3)`, `triangles` is `(T, 3)` holding
    integer indices into that same node's `vertices`, `vertex_normals` is `(V, 3)` and
    `triangle_normals` is `(T, 3)`.

    Args:
        vertices (np.ndarray): Object array of per-node vertex position arrays.
        triangles (np.ndarray): Object array of per-node triangle index arrays.
        axes (list[Axis] | None): List of Axis metadata.
        vertex_normals (np.ndarray | None): Optional object array of per-node vertex
            normal arrays.
        triangle_normals (np.ndarray | None): Optional object array of per-node triangle
            normal arrays.
        vertices_missing (np.ndarray | None): Optional 1D boolean array marking nodes that
            do not have mesh data. Used as the canonical missing mask for the whole mesh.
        triangles_missing (np.ndarray | None): Optional 1D boolean array; if given along
            with `vertices_missing`, the two must match.
        vertex_normals_missing (np.ndarray | None): Optional 1D boolean array; if given
            along with `vertices_missing`, the two must match.
        triangle_normals_missing (np.ndarray | None): Optional 1D boolean array; if given
            along with `triangles_missing`, the two must match.

    Raises:
        ValueError: Must define exactly 3 space axes in order to have mesh data
        ValueError: Missing mask for mesh properties must match
        ValueError: Mesh vertices must be a 2D array with 3 columns
        ValueError: Mesh must have at least 3 vertices
        ValueError: Mesh triangles must be a 2D array with 3 columns
        ValueError: Mesh must have at least 1 triangle
        ValueError: Mesh triangle indices must be integers
        ValueError: Mesh triangle indices must be in bounds
        ValueError: Mesh triangles must reference 3 distinct vertices
        ValueError: Mesh vertex/triangle normals must match the shape of vertices/triangles
        ValueError: Mesh vertices/normals must be finite
    """
    spatial_dim = _spatial_dim(axes)
    if spatial_dim != 3:
        raise ValueError(
            f"Must define exactly 3 space axes in order to have mesh data, got {spatial_dim}"
        )

    for other_name, other_missing, ref_missing, ref_name in (
        ("triangles", triangles_missing, vertices_missing, "vertices"),
        ("vertex_normals", vertex_normals_missing, vertices_missing, "vertices"),
        ("triangle_normals", triangle_normals_missing, triangles_missing, "triangles"),
    ):
        if (
            other_missing is not None
            and ref_missing is not None
            and not np.array_equal(other_missing, ref_missing)
        ):
            raise ValueError(f"Missing mask for mesh '{other_name}' must match '{ref_name}'")

    missing = vertices_missing

    for i in range(len(vertices)):
        if missing is not None and missing[i]:
            continue

        verts = vertices[i]
        if verts.ndim != 2 or verts.shape[1] != 3:
            raise ValueError(
                f"Mesh vertices must be a 2D array with 3 columns, got shape {verts.shape} "
                f"at node index {i}"
            )
        if verts.shape[0] < 3:
            raise ValueError(
                f"Mesh must have at least 3 vertices, got {verts.shape[0]} at node index {i}"
            )
        if not np.all(np.isfinite(verts)):
            raise ValueError(
                f"Mesh vertices must be finite, got non-finite values at node index {i}"
            )

        tris = triangles[i]
        if tris.ndim != 2 or tris.shape[1] != 3:
            raise ValueError(
                f"Mesh triangles must be a 2D array with 3 columns, got shape {tris.shape} "
                f"at node index {i}"
            )
        if tris.shape[0] < 1:
            raise ValueError(f"Mesh must have at least 1 triangle, got 0 at node index {i}")
        if not np.issubdtype(tris.dtype, np.integer):
            raise ValueError(
                f"Mesh triangle indices must be integers, got dtype {tris.dtype} at node index {i}"
            )
        if tris.size > 0 and (tris.min() < 0 or tris.max() >= verts.shape[0]):
            raise ValueError(
                f"Mesh triangle indices must be in the range [0, {verts.shape[0]}) "
                f"at node index {i}"
            )
        sorted_tris = np.sort(tris, axis=1)
        degenerate = (sorted_tris[:, 0] == sorted_tris[:, 1]) | (
            sorted_tris[:, 1] == sorted_tris[:, 2]
        )
        if np.any(degenerate):
            raise ValueError(f"Mesh triangles must reference 3 distinct vertices at node index {i}")

        if vertex_normals is not None:
            vnorms = vertex_normals[i]
            if vnorms.shape != verts.shape:
                raise ValueError(
                    f"Mesh vertex normals must have the same shape as vertices, "
                    f"got {vnorms.shape} vs {verts.shape} at node index {i}"
                )
            if not np.all(np.isfinite(vnorms)):
                raise ValueError(
                    f"Mesh vertex normals must be finite, got non-finite values at node index {i}"
                )

        if triangle_normals is not None:
            tnorms = triangle_normals[i]
            if tnorms.shape != (tris.shape[0], 3):
                raise ValueError(
                    f"Mesh triangle normals must have shape {(tris.shape[0], 3)}, "
                    f"got {tnorms.shape} at node index {i}"
                )
            if not np.all(np.isfinite(tnorms)):
                raise ValueError(
                    f"Mesh triangle normals must be finite, got non-finite values at node index {i}"
                )
