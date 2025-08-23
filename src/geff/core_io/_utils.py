from __future__ import annotations

import os
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, TypeVar

import numpy as np
import zarr

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping

    from zarr.storage import StoreLike

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
            if hasattr(group, "_zarr_format") and group._zarr_format == 3:
                return 3
            elif hasattr(group, "_zarr_format") and group._zarr_format == 2:
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


def calculate_roi_from_nodes(
    nodes_iter: Iterable[T],
    axis_names: list[str],
    node_accessor_func: Callable[[T], Mapping[str, Any]],
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Calculate ROI (region of interest) from graph nodes.

    Args:
        nodes_iter: Iterator over graph nodes
        axis_names: Names of the spatial axes
        node_accessor_func: Function to extract node data from each node

    Returns:
        tuple[tuple[float, ...], tuple[float, ...]]: Min and max values for each axis
    """
    _min = None
    _max = None
    for node in nodes_iter:
        node_data = node_accessor_func(node)

        try:
            pos = np.array([node_data[name] for name in axis_names])
        except KeyError as e:
            missing_names = {name for name in axis_names if name not in node_data}
            raise ValueError(f"Spatiotemporal properties {missing_names} not found in node") from e

        if _min is None or _max is None:
            _min = pos
            _max = pos
        else:
            _min = np.min([_min, pos], axis=0)
            _max = np.max([_max, pos], axis=0)

    if _min is None or _max is None:
        raise ValueError("No nodes found to calculate ROI")

    return tuple(_min.tolist()), tuple(_max.tolist())
