from collections.abc import Sequence
from typing import cast, overload

import numpy as np
from numpy.typing import ArrayLike, NDArray
from zarr import Group


def serialize_vlen_property_data_as_dict(
    prop_data: Sequence[ArrayLike | None],
    dtype: type = np.float32,
) -> dict[str, NDArray | None]:
    """
    Serialize a sequence of vlen property data into a structured format as a dictionary.
    Args:
        prop_data (Sequence[ArrayLike | None]): A sequence of property data, where each element
            can be a numpy array or None.
        dtype (type): The data type to use for the values array. Default is np.float32.
    Returns:
        dict[str, NDArray]: A dictionary with keys 'values', 'missing', and 'data'.
    """
    values, missing, data = serialize_vlen_property_data(prop_data, dtype=dtype)
    return {
        "values": values,
        "missing": missing,
        "data": data,
    }


def serialize_vlen_property_data(
    prop_data: Sequence[ArrayLike | None],
    dtype: type = np.float32,
) -> tuple[NDArray, NDArray | None, NDArray]:
    """
    Serialize a sequence of property data into a structured format.
    Args:
        prop_data (Sequence[ArrayLike | None]): A sequence of property data, where each element can
            be an ArrayLike object or None.
        dtype (type): The data type to use for the values array. Default is np.float32.
    Returns:
        tuple[NDArray, NDArray | None, NDArray]: A tuple containing:
            - 'values': a NDArray of data indicating the offset indices and shapes of each property
              in the values array.
            - 'missing': a 1D NArray of booleans indicating missing values,
            - 'data': a 1D NDArray of data that contains the serialized property data.
            The return value will be a tuple of (values, missing, data).
    """
    values = []
    missing = []
    data = []
    offset = 0
    ndim = None

    # Determine the number of dimensions
    for element in prop_data:
        if element is not None:
            element = np.asarray(element, dtype=dtype)
            if ndim is None:
                ndim = element.ndim
            elif element.ndim != ndim:
                raise ValueError(
                    "All elements must have the same number of dimensions: "
                    f"expected {ndim}, got {element.ndim}."
                )

    # Convert elements to arrays and build the values, missing, and data arrays
    for element in prop_data:
        if element is None:
            values.append((offset,) + (0,) * ndim if ndim is not None else ())
            missing.append(True)
        else:
            element = np.asarray(element, dtype=dtype)
            values.append((offset, *element.shape))
            missing.append(False)
            data.append(element)
            offset += np.asarray(element.shape).prod()

    return (
        np.asarray(values, dtype=np.int64),
        np.array(missing, dtype=bool) if missing else None,
        np.concatenate([d.ravel() for d in data]) if data else np.array([], dtype=dtype),
    )


def _deserialize_vlen_array(
    values: NDArray,
    missing: NDArray | None,
    data: NDArray,
    index: int,
) -> NDArray | None:
    """
    Deserialize a variable-length array from the data and values arrays.

    Args:
        values (NDArray): The AND array containing the offset indices and shapes of
            each property. (e.g., [[offset, shape_dim0, shape_dim1], ...]).
            expected shape is (N, ndim + 1) where N is the number of nodes or edges.
        missing (NDArray): The 1D array indicating missing values. expected shape is (N,).
        data (NDArray): The 1D array containing the serialized property data.
            expected shape is (total_data_length,).
        index (int): The index of the property to deserialize.

    Returns:
        NDArray: The deserialized variable-length array.
    """
    if index < 0 or index >= values.shape[0]:
        raise IndexError(f"Index {index} out of bounds for property data.")
    if missing is not None and missing[index]:
        return None
    offset = values[index][0]
    shape = values[index][1:]
    return data[offset : offset + np.prod(shape)].reshape(shape)


@overload
def deserialize_vlen_property_data(
    vlen_props: Group | dict[str, NDArray | None],
    index: int,
) -> NDArray | None: ...


@overload
def deserialize_vlen_property_data(
    vlen_props: Group | dict[str, NDArray | None],
    index: None = None,
) -> Sequence[NDArray | None]: ...


def deserialize_vlen_property_data(
    vlen_props: Group | dict[str, NDArray | None],
    index: int | None = None,
) -> NDArray | Sequence[NDArray | None] | None:
    """
    Get deserialized vlen property data for a specific property name.

    Args:
        vlen_props (Group | dict[str, NDArray]): The Zarr group or dictionary containing the
            serialized data.
        index (int | None): The index of the property to retrieve. If None, returns all properties.

    Returns:
        NDArray | Sequence[NDArray | None] | None: The deserialized vlen property data, or None if
            the indexed item is missing.
    """
    if "values" not in vlen_props:
        raise ValueError(f"Group {vlen_props} does not contain 'values'.")
    if "data" not in vlen_props:
        raise ValueError(f"Group {vlen_props} does not contain 'data'.")
    data = cast("NDArray", vlen_props["data"])
    values = cast("NDArray", vlen_props["values"])
    if "missing" in vlen_props:
        missing = cast("NDArray | None", vlen_props["missing"])
        if missing is not None and missing.shape[0] != values.shape[0]:
            raise ValueError(
                f"Length of 'missing' ({missing.shape[0]}) does not match length of 'values'"
                + f"({values.shape[0]})."
            )
    else:
        missing = None

    if index is not None:
        return _deserialize_vlen_array(values, missing, data, index)

    return [_deserialize_vlen_array(values, missing, data, i) for i in range(values.shape[0])]
