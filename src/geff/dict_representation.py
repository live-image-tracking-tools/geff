from typing import Any, Generic, Optional, TypedDict, TypeVar
from typing_extensions import NotRequired

import zarr
from numpy.typing import NDArray

from .metadata_schema import GeffMetadata

T_Array = TypeVar("T_Array", bound=zarr.Array | NDArray)


# TODO: move dict defs to own module
# the typevar T_Array means that the arrays can either be numpy or zarr arrays
class PropDict(TypedDict, Generic[T_Array]):
    values: T_Array
    missing: NotRequired[T_Array]


# Intermediate dict format that can be injested to different backend types
class GraphDict(TypedDict):
    metadata: GeffMetadata
    nodes: NDArray[Any]
    edges: NDArray[Any]
    node_props: dict[str, PropDict[NDArray]]
    edge_props: dict[str, PropDict[NDArray]]
