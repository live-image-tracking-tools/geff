from collections.abc import Sequence
from typing import cast

import numpy as np
from numpy.typing import ArrayLike, NDArray
from zarr import Group


def serialize_vlen_property_data_as_dict(
    data: Sequence[ArrayLike | None],
) -> dict[str, NDArray | None]:
    """
    Serialize a sequence of vlen property data into a structured format as a dictionary.
    Args:
        data (Sequence[ArrayLike | None]): A sequence of property data, where each element can be
            a numpy array or None.
    Returns:
        dict[str, NDArray]: A dictionary with keys 'values', 'missing', and 'slices'.
    """
    values, missing, slices = serialize_vlen_property_data(data)
    return {
        "values": values,
        "missing": missing,
        "slices": slices,
    }


def serialize_vlen_property_data(
    data: Sequence[ArrayLike | None],
) -> tuple[NDArray, NDArray | None, NDArray]:
    """
    Serialize a sequence of property data into a structured format.
    Args:
        data (Sequence[ArrayLike | None]): A sequence of property data, where each element can be
            an ArrayLike object or None.
    Returns:
        tuple[NDArray, NDArray | None, NDArray]: A tuple containing:
            - 'values': a NDArray of the property values.
            - 'missing': a 1D array of booleans indicating missing values,
            - 'slices': a NDArray of slices indicating the start and end indices of each property
              in the values array.
            The return value will be a tuple of (values, missing, slices).
    """
    slices = []
    missing = []
    values = []
    offset = 0
    n_col = None
    for element in data:
        if element is None:
            slices.append((0, 0))
            missing.append(True)
        else:
            element = np.asarray(element, dtype=np.float32)
            if n_col is None:
                n_col = element.shape[1]
            elif element.shape[1] != n_col:
                raise ValueError(
                    "All elements must have the same number of columns: "
                    f"expected {n_col}, got {element.shape[1]}."
                )
            slices.append((offset, offset + element.shape[0]))
            missing.append(False)
            values.append(element)
            offset += element.shape[0]

    return (
        np.vstack(values),
        np.array(missing, dtype=bool) if missing else None,
        np.array(slices, dtype=np.uint64),
    )


def deserialize_vlen_property_data(
    vlen_props: Group | dict[str, NDArray],
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
    if "slices" not in vlen_props:
        raise ValueError(f"Group {vlen_props} does not contain 'slices'.")
    slices = cast("NDArray", vlen_props["slices"])
    values = cast("NDArray", vlen_props["values"])
    if "missing" in vlen_props:
        missing = cast("NDArray | None", vlen_props["missing"])
        if missing is not None and missing.shape[0] != slices.shape[0]:
            raise ValueError(
                f"Length of 'missing' ({missing.shape[0]}) does not match length of 'slices'"
                + f"({len(slices)})."
            )
    else:
        missing = None

    if index is not None:
        if index < 0 or index >= len(slices):
            raise IndexError(f"Index {index} out of bounds for property data.")
        if missing is not None and missing[index]:
            return None
        start, end = slices[index]
        return values[start:end]

    if missing is not None and np.any(missing):
        return [
            values[slice(start, end)] if not miss else None
            for (start, end), miss in zip(slices, missing, strict=False)
        ]

    return [values[slice(start, end)] for start, end in slices]
