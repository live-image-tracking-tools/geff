from typing import Any, TypedDict

import numpy as np
import zarr
from numpy.typing import NDArray
from typing_extensions import NotRequired

from .metadata_schema import GeffMetadata

# From python 3.11 TypeDicts can also inherit from Generic
# While python 3.10 is support two PropDicts for NDArray and zarr.Array are defined
#
# # implementation with Generic for python 3.11
# from typing import TypeVar, Generic
#
# # the typevar T_Array means that the arrays can either be numpy or zarr arrays
# T_Array = TypeVar("T_Array", bound=zarr.Array | NDArray)
#
# class PropDict(TypedDict, Generic[T_Array]):
#     values: T_Array
#     missing: NotRequired[T_Array]


class PropDictNpArray(TypedDict):
    values: NDArray[Any]
    missing: NotRequired[NDArray[np.bool]]


class PropDictZArray(TypedDict):
    values: zarr.Array
    missing: NotRequired[zarr.Array]
    dtype: NotRequired[str]


# Intermediate dict format that can be injested to different backend types
class GraphDict(TypedDict):
    metadata: GeffMetadata
    nodes: NDArray[Any]
    edges: NDArray[Any]
    node_props: dict[str, PropDictNpArray]
    edge_props: dict[str, PropDictNpArray]
