from __future__ import annotations

import os
import shutil
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Literal, TypeVar

import numpy as np
import zarr

from geff import _path

if TYPE_CHECKING:
    from collections.abc import Sequence

    from numpy.typing import ArrayLike
    from zarr.storage import StoreLike

    from geff._typing import PropDictNpArray

    T = TypeVar("T")

from urllib.parse import urlparse


def is_remote_url(path: str) -> bool:
    """Returns True if the path is a remote URL (http, https, ftp, sftp), otherwise False.

    Parameters
    ----------
    path : str
        path to a local or remote resource

    Returns
    -------
    bool
        True if the path is a remote URL, False otherwise
    """
    parsed = urlparse(path)
    return parsed.scheme in ("http", "https", "ftp", "sftp")


def remove_tilde(store: StoreLike) -> StoreLike:
    """
    Remove tilde from a store path/str, because zarr (3?) will not recognize
        the tilde and write the zarr in the wrong directory.

    Args:
        store (str | Path | zarr store): The store to remove the tilde from

    Returns:
        StoreLike: The store with the tilde removed
    """
    if isinstance(store, str | Path):
        store_str = str(store)
        if "~" in store_str:
            store = os.path.expanduser(store_str)
    return store


def open_storelike(store: StoreLike) -> zarr.Group:
    """Opens a StoreLike input as a zarr group

    Args:
        store (str | Path | zarr store): str/Path/store for a geff zarr

    Raises:
        FileNotFoundError: Path does not exist
        ValueError: store must be a zarr StoreLike

    Returns:
        zarr.Group: Opened zarr group
    """
    # Check if path exists for string/Path inputs
    if isinstance(store, str | Path):
        store_path = Path(store)
        if not is_remote_url(str(store_path)) and not store_path.exists():
            raise FileNotFoundError(f"Path does not exist: {store}")

    # Check for zarr spec v3 files being opened with zarr python v2 and warn if so
    if zarr.__version__.startswith("2"):
        spec_version = _detect_zarr_spec_version(store)
        if spec_version == 3:
            warnings.warn(
                "Attempting to open a zarr spec v3 file with zarr-python v2. "
                "This may cause compatibility issues. Consider upgrading to zarr-python v3 "
                "or recreating the file with zarr spec v2.",
                UserWarning,
                stacklevel=2,
            )

    # Open the zarr group from the store
    try:
        graph_group = zarr.open_group(store, mode="r")
    except Exception as e:
        raise ValueError(f"store must be a zarr StoreLike: {e}") from e

    return graph_group


# -----------------------------------------------------------------------------#
# helpers
# -----------------------------------------------------------------------------#


def expect_array(parent: zarr.Group, key: str, parent_name: str = "array") -> zarr.Array:
    """Return an array in the parent group with the given key, or raise ValueError."""
    arr = parent.get(key)
    if not isinstance(arr, zarr.Array):
        raise ValueError(f"{parent_name!r} group must contain an {key!r} array")
    return arr


def expect_group(parent: zarr.Group, key: str, parent_name: str = "graph") -> zarr.Group:
    """Return a group in the parent group with the given key, or raise ValueError."""
    grp = parent.get(key)
    if not isinstance(grp, zarr.Group):
        raise ValueError(f"{parent_name!r} group must contain a group named {key!r}")
    return grp


def _detect_zarr_spec_version(store: StoreLike) -> int | None:
    """Detect the zarr specification version of an existing zarr store.

    Args:
        store: The zarr store path or object

    Returns:
        int | None: The zarr spec version (2 or 3) if detectable, None if unknown
    """
    try:
        if isinstance(store, str | Path):
            store_path = Path(store)
            # Check for zarr v3 indicator: zarr.json instead of .zarray/.zgroup
            if (store_path / "zarr.json").exists():
                return 3
            # Check for zarr v2 indicators
            elif (store_path / ".zgroup").exists() or (store_path / ".zarray").exists():
                return 2
        else:
            # For store objects, try to detect based on metadata
            group = zarr.open_group(store, mode="r")
            # In zarr v3, metadata is stored differently
            if group.metadata.zarr_format == 3:  # pyright: ignore
                return 3
            elif group.metadata.zarr_format == 2:  # pyright: ignore
                return 2
    except Exception:
        # If we can't detect, return None
        pass

    return None


def setup_zarr_group(store: StoreLike, zarr_format: Literal[2, 3] = 2) -> zarr.Group:
    """Set up and return a zarr group for writing.

    Args:
        store: The zarr store path or object
        zarr_format: The zarr format version to use

    Returns:
        The opened zarr group
    """
    store = remove_tilde(store)

    # Check for trying to write zarr spec v3 with zarr python v2 and warn if so
    if zarr_format == 3 and zarr.__version__.startswith("2"):
        warnings.warn(
            "Requesting zarr spec v3 with zarr-python v2. "
            "zarr-python v2 does not support spec v3. "
            "Ignoring zarr_format=3 and writing zarr spec v2 instead. "
            "Consider upgrading to zarr-python v3 to write zarr spec v3 files.",
            UserWarning,
            stacklevel=2,
        )

    # open/create zarr container
    if zarr.__version__.startswith("3"):
        return zarr.open_group(store, mode="a", zarr_format=zarr_format)
    else:
        return zarr.open_group(store, mode="a")


def _get_common_type_dims(arr_seq: Sequence[ArrayLike | None]) -> tuple[np.dtype, int]:
    """Get a common dtype and number of dimensions that will work for all elements.

    Will use native numpy casting to unify all the dtypes, and will take the maximum
    number of dimensions of the elements. Nones are ignored.

    Args:
        arr_seq (Sequence[ArrayLike | None]): A sequence of array-like elements and Nones
            to infer the dtype and number of dimensions for.

    Raises:
        ValueError: If the elements do not have any shared dtype that can be cast to safely.

    Returns:
        tuple[np.dtype, int]: A dtype that all non-None elements can be cast to, and the
            maximum number of dimensions of any non-None element
    """
    ndim = None
    dtype = None

    for arr in arr_seq:
        if arr is None:
            continue
        element = np.asarray(arr)
        if ndim is None:
            ndim = element.ndim
            dtype = element.dtype
        else:
            ndim = max(element.ndim, ndim)
            if np.can_cast(dtype, element.dtype):
                dtype = np.promote_types(dtype, element.dtype)
            else:
                raise ValueError(
                    "All elements must have compatible dtypes. Cannot"
                    f"cast {dtype} and {element.dtype}."
                )

    if dtype is None or ndim is None:
        warnings.warn(
            "Variable length property sequence does not have any non-None elements - "
            "using ndim=1 and dtype=int64",
            stacklevel=2,
        )
        dtype = np.dtype("int64")
        ndim = 1
    return dtype, ndim


def construct_var_len_props(arr_seq: Sequence[ArrayLike | None]) -> PropDictNpArray:
    """Converts a sequence of array like and None objects into a geff._typing.PropDictNpArray

    Creates a missing array with the indices of the None objects. Converts each element of
    the sequence into a numpy array. Prepends dummy dimensions to each element to ensure
    all elements have the same number of dimensions. Casts all arrays into a common dtype
    (if there is one). Turns the sequence into a numpy array with dtype object.

    Args:
        arr_seq (Sequence[ArrayLike | None]): A sequence of properties, with one entry
            per node or edge. Missing values are indicated by None entries.

    Returns:
        PropDictNpArray: A standardized version of the input properties where all entries
            are numpy arrays contained in an object array.
    """
    values_arr = np.empty(shape=(len(arr_seq),), dtype=np.object_)
    missing_arr = np.zeros(shape=(len(arr_seq),), dtype=np.bool_)

    dtype, ndim = _get_common_type_dims(arr_seq)

    for i, arr in enumerate(arr_seq):
        if arr is None:
            missing_arr[i] = 1
            empty_shape = tuple(0 for _ in range(ndim))
            default_val = np.empty(shape=empty_shape, dtype=dtype)
            values_arr[i] = default_val
        else:
            element = np.asarray(arr, dtype=dtype)
            # prepend dummy axes if needed
            while element.ndim < ndim:
                element = np.expand_dims(element, axis=0)
            values_arr[i] = element
    return {"values": values_arr, "missing": missing_arr if missing_arr.any() else None}


def delete_geff(store: StoreLike, zarr_format: Literal[2, 3] = 2) -> None:
    """Delete a geff after writing

    Tries to handle multiple StoreLike inputs and avoids deleting non-geff contents
    in the store

    Args:
        store (StoreLike): StoreLike geff that should be deleted
        zarr_format (Literal[2, 3], optional): Zarr format used to write input store. Defaults to 2.
    """
    root = setup_zarr_group(store, zarr_format=zarr_format)

    # Delete node and edge groups
    del root[_path.NODES]
    del root[_path.EDGES]

    # If the root is empty, try to delete the root zarr
    if len(list(root.keys())) == 0:
        # Handle Path or str storelike
        if isinstance(store, Path) or isinstance(store, str):
            shutil.rmtree(store)
        else:
            # Try to get a valid path from the store
            try:
                path = store.path  # type: ignore
                if os.path.exists(path):
                    shutil.rmtree(path)
            except AttributeError:
                warnings.warn(
                    "Cannot delete root zarr directory, but geff contents have been deleted",
                    stacklevel=2,
                )
                del root.attrs["geff"]
    else:
        warnings.warn(
            "Found non-geff members in zarr. Exiting without deleting root zarr.", stacklevel=2
        )
        # Delete geff metadata from attrs
        del root.attrs["geff"]
