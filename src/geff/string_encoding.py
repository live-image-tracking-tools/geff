from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from geff._typing import PropDictNpArray, VarLenPropDictNpArray


def encode_string_data(data: PropDictNpArray) -> VarLenPropDictNpArray:
    """Encode a string array into a data array, values array, and missing array

    Args:
        data (PropDictNpArray): A 2d numpy array representing a list of strings, one per
            node or edge, potentially with empty strings appended at the end to make it
            non-ragged, along with a 1D missing array.

    Raises:
        TypeError: If the input values are not a string array

    Returns:
        VarLenPropDictNpArray: new data, values, and missing array to write to the props group
    """
    str_values = data["values"]
    missing = data["missing"]
    if not str_values.dtype.kind == "U":
        raise TypeError("Cannot encode non-string array")
    # TODO: Warn here or outside? Or no warn because it's now expected?
    # warnings.warn(
    #     f"Property '{data}' is a string array. Automatically casting it to bytes",
    #     stacklevel=2,
    # )

    encoded_data = np.array("".join([str(row) for row in str_values]).encode("utf-8"))
    shapes = np.asarray(tuple(len(s) for s in str_values), dtype=np.int64)
    offsets = np.concatenate(([0], np.cumsum(shapes[:-1])))
    new_values = np.vstack((offsets, shapes)).T
    return {"values": new_values, "missing": missing, "data": encoded_data}


def decode_string_data(data: VarLenPropDictNpArray) -> PropDictNpArray:
    """Turns encoded string values back into a native python string array of values

    Args:
        data (VarLenPropDictNpArray): The values, data, and missing arrays read from disk
            containing encoded string values of varying lengths

    Raises:
        TypeError: If the data array is not a byte array

    Returns:
        PropDictNpArray: The values and missing arrays representing the string values
            for each node/edge as native python strings in a numpy string array
    """
    encoded_data = data["data"]
    if not encoded_data.dtype.kind == "S":
        raise TypeError("Cannot decode non-bytes array")
    decoded_data = encoded_data.tobytes().decode("utf-8")
    offset_shape = data["values"]
    missing = data["missing"]
    str_values = []
    for i in range(len(offset_shape)):
        offset = offset_shape[i][0]
        shape = offset_shape[i][1:]
        size = shape.prod()
        str_val = decoded_data[offset : offset + size]
        str_values.append(str_val)
    new_values = np.array(str_values)
    return {"values": new_values, "missing": missing}
