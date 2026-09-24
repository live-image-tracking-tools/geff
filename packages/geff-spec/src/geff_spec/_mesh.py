from pydantic import BaseModel, Field


class Mesh(BaseModel):
    """TODO"""

    vertices: str = Field(..., description="Name of the node property that contains mesh vertices")
    triangles: str = Field(
        ..., description="Name of the node property that contains mesh triangles"
    )
    vertex_normals: str | None = Field(
        default=None, description="Name of the node property that contains vertex normals"
    )
    triangle_normals: str | None = Field(
        default=None, description="Name of the node property that contains triangle normals"
    )
    vertex_axes: list[str] = Field(
        ..., description="List that specifies the axis order used in mesh properties"
    )
