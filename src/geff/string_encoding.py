from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import NDArray

    from geff._typing import PropDictNpArray


def encode_string_data(data: PropDictNpArray) -> tuple[NDArray, NDArray | None, NDArray]:
    """Encode a string array into a data array, values array, and missing array

    Args:
        data (PropDictNpArray): A 2d numpy array representing a list of strings, one per
            node or edge, potentially with empty strings appended at the end to make it
            non-ragged, along with a 1D missing array.

    Raises:
        TypeError: If the input values are not a string array

    Returns:
        tuple[NDArray, NDArray | None, NDArray]: new values, missing, and data arrays
            to write to the props group
    """
    str_values = data["values"]
    missing = data["missing"]
    if not str_values.dtype.kind == "U":
        raise TypeError("Cannot encode non-string array")

    encoded_data = np.array("".join([str(row) for row in str_values]).encode("utf-8"))
    shapes = np.asarray(tuple(len(s) for s in str_values), dtype=np.int64)
    offsets = np.concatenate(([0], np.cumsum(shapes[:-1])))
    new_values = np.vstack((offsets, shapes)).T
    return new_values, missing, encoded_data


def decode_string_data(
    values: NDArray, missing: NDArray[np.bool_] | None, data: NDArray
) -> PropDictNpArray:
    """Turns encoded string values back into a native python string array of values

    Args:
        values (NDArray): The values array containing the offset indices and shapes of
            each property. (e.g., [[offset, shape_dim0,], ...]).
            expected shape is (N, 2) where N is the number of nodes or edges.
        missing (NDArray[np.bool_] | None): The 1D array indicating missing values, or
            None if no values are missing.
        data (NDArray): The 1D byte array containing the serialized property data.
            expected shape is (total_data_length,).
    Raises:
        TypeError: If the data array is not a byte array

    Returns:
        PropDictNpArray: The values and missing arrays representing the string values
            for each node/edge as native python strings in a numpy string array
    """
    if not data.dtype.kind == "S":
        raise TypeError("Cannot decode non-bytes array")
    decoded_data = data.tobytes().decode("utf-8")
    str_values = []
    for i in range(len(values)):
        offset = values[i][0]
        shape = values[i][1:]
        size = shape.prod()
        str_val = decoded_data[offset : offset + size]
        str_values.append(str_val)
    new_values = np.array(str_values)
    return {"values": new_values, "missing": missing}
