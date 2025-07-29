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
    """
    A prop dictionary which has the keys "values" and optionally "missing", stored as numpy arrays.

    "values" is a numpy array of any type, "missing" is a numpy array of bools.
    """

    values: NDArray[Any]
    missing: NotRequired[NDArray[bool]]


class PropDictZArray(TypedDict):
    """
    A prop dictionary which has the keys "values" and optionally "missing", stored as zarr arrays.
    """

    values: zarr.Array
    missing: NotRequired[zarr.Array]


# Intermediate dict format that can be constructed to different backend types
class InMemoryGeff(TypedDict):
    """
    Geff data loaded into memory as numpy arrays.
    """

    metadata: GeffMetadata
    node_ids: NDArray[Any]
    edge_ids: NDArray[Any]
    node_props: dict[str, PropDictNpArray]
    edge_props: dict[str, PropDictNpArray]
