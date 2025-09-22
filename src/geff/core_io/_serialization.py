import numpy as np
from numpy.typing import NDArray

from geff._typing import PropDictNpArray


def serialize_vlen_property_data(
    prop_dict: PropDictNpArray,
) -> tuple[NDArray, NDArray | None, NDArray]:
    """
    Serialize a sequence of property data into a structured format.
    Args:
        prop_dict (PropDictNpArray): Variable length properties to be serialized. The values
            array must have dtype np.object_, and each numpy array inside the object array
            should have the same ndim and dtype. You can use `construct_var_len_props` to
            convert properties into this standardized format.

    Returns:
        tuple[NDArray, NDArray | None, NDArray]: A tuple containing:
            - 'values': a NDArray of data indicating the offset indices and shapes of each property
              in the values array.
            - 'missing': a 1D NArray of booleans indicating missing values,
            - 'data': a 1D NDArray of data that contains the serialized property data.
            The return value will be a tuple of (values, missing, data).
    """
    values = prop_dict["values"]
    missing = prop_dict["missing"]
    encoded_values = []
    data = []
    offset = 0

    dtype = None
    ndim = None

    # Elements should already be numpy arrays of numpy arrays with dtypes
    for element in values:
        if not isinstance(element, np.ndarray):
            raise ValueError(
                "For variable length properties, each node/edge property must be a "
                f"numpy array, got {type(element)}. Try using `construct_var_len_props` "
                "helper function to standardize the properties."
            )
        if ndim is None:
            ndim = element.ndim
        elif element.ndim != ndim:
            raise ValueError(
                "For variable length properties, each node/edge property must have the "
                "same number of dimensions. Try using `construct_var_len_props` helper "
                "function to standardize the properties."
            )
        if dtype is None:
            dtype = element.dtype
        elif element.dtype != dtype:
            raise ValueError(
                "For variable length properties, each node/edge property must have the "
                "same number of dtype. Try using `construct_var_len_props` helper function "
                "to standardize the properties."
            )
        encoded_values.append((offset, *element.shape))
        data.append(element.ravel())
        offset += np.asarray(element.shape).prod()

    return (
        np.asarray(encoded_values, dtype=np.uint64),
        missing,
        np.concatenate(data) if len(data) > 0 else np.array([], dtype="int64"),
    )


def _deserialize_vlen_value(
    values: NDArray,
    data: NDArray,
    index: int,
) -> NDArray:
    """
    Deserialize one variable-length array value from the data and values arrays.

    Args:
        values (NDArray): The NDArray containing the offset indices and shapes of
            each property. (e.g., [[offset, shape_dim0, shape_dim1], ...]).
            expected shape is (N, ndim + 1) where N is the number of nodes or edges.
        data (NDArray): The 1D array containing the serialized property data.
            expected shape is (total_data_length,).
        index (int): The index of the property to deserialize.

    Returns:
        NDArray: The deserialized variable-length value.
    """
    if index < 0 or index >= values.shape[0]:
        raise IndexError(f"Index {index} out of bounds for property data.")
    # TODO: we could use the missing values to make an empty array, but it messes
    # up consistency if you had an array before writing
    offset = values[index][0]
    shape = values[index][1:]
    return data[offset : offset + np.prod(shape)].reshape(shape)


def deserialize_vlen_property_data(
    values: NDArray,
    missing: NDArray[np.bool_] | None,
    data: NDArray,
) -> PropDictNpArray:
    """
    Deserialize variable length property data, turning it into a normal in-memory property.

    Args:
        values (NDArray): The values array containing the offset indices and shapes of
            each property. (e.g., [[offset, shape_dim0, shape_dim1], ...]).
            expected shape is (N, ndim + 1) where N is the number of nodes or edges.
        missing (NDArray[np.bool_] | None): The 1D array indicating missing values, or
            None if no values are missing.
        data (NDArray): The 1D array containing the serialized property data.
            expected shape is (total_data_length,).

    Returns:
        PropDictNpArray: The deserialized property data, where values is a numpy
            array of type object containing other numpy arrays.
    """
    decoded_values = np.empty(shape=(len(values),), dtype=np.object_)
    for i in range(values.shape[0]):
        decoded_values[i] = _deserialize_vlen_value(values, data, i)
    return {"values": decoded_values, "missing": missing}
