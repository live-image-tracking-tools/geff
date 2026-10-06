from pydantic import BaseModel, Field


class Mesh(BaseModel):
    """
    The `Mesh` schema specifies the node properties that together define a triangular surface
    mesh associated with each node, giving the node a 3D shape. Each field below names a
    `node property` (a key into `node_props_metadata` and the `nodes\\props` group) rather than
    storing the mesh data itself.

    Vertex positions are defined relative to the spatial position of the node, in the same way
    as `polygon` points. Nodes are not required to have the same number of vertices or triangles,
    so the `vertices` and `triangles` properties (and `vertex_normals`/`triangle_normals`, if
    present) are typically written as variable length properties (see the "Variable length
    properties" section of the Specification).

    For a single node:

    - `vertices` is a `(V, D)` array, where `V` is the number of vertices for that node's mesh
      and `D` is the number of spatial dimensions (3 for surface meshes). Row `i` gives the
      position of vertex `i` relative to the node.
    - `triangles` is a `(T, 3)` integer array, where `T` is the number of triangular faces. Each
      row holds the indices of three vertices (into that same node's `vertices` array) that form
      one face. Index values must therefore be valid local indices into `vertices`, i.e. in the
      range `[0, V)`.
    - `vertex_normals`, if present, is a `(V, D)` array aligned row-for-row with `vertices`,
      giving a normal vector per vertex.
    - `triangle_normals`, if present, is a `(T, D)` array aligned row-for-row with `triangles`,
      giving a normal vector per face.

    Surface meshes are only used for 3D shapes.
    """

    vertices: str = Field(
        ...,
        description="Name of the node property that contains the mesh vertices, as a "
        "`(V, D)` array per node where `V` is the number of vertices and `D` is the number of "
        "spatial dimensions. Vertex positions are defined relative to the spatial position of "
        "the associated node.",
    )
    triangles: str = Field(
        ...,
        description="Name of the node property that contains the mesh triangles, as a `(T, 3)` "
        "integer array per node. Each row contains the indices of the three vertices (into the "
        "same node's `vertices` array) that make up one triangular face.",
    )
    vertex_normals: str | None = Field(
        default=None,
        description="Optional name of the node property that contains the mesh vertex normals, "
        "as a `(V, D)` array per node aligned row-for-row with the `vertices` property.",
    )
    triangle_normals: str | None = Field(
        default=None,
        description="Optional name of the node property that contains the mesh triangle "
        "(face) normals, as a `(T, D)` array per node aligned row-for-row with the "
        "`triangles` property.",
    )
    vertex_axes: list[str] | None = Field(
        default=None,
        description="Optional list of axis names specifying the order of the spatial "
        "dimensions (columns) used in the `vertices` (and, if present, `vertex_normals`) "
        "arrays, when that order differs from the default. Names must match `name` values in "
        "the `GeffMetadata.axes` list. If not specified, the default is the order of the "
        "spatial-type axes as they appear in `GeffMetadata.axes`.",
    )
