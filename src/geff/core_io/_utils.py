from __future__ import annotations

import os
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


# -----------------------------------------------------------------------------#
# helpers
# -----------------------------------------------------------------------------#


def expect_array(parent: zarr.Group, key: str, parent_name: str) -> zarr.Array:
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


def setup_zarr_group(store: StoreLike, zarr_format: Literal[2, 3] = 2) -> zarr.Group:
    """Set up and return a zarr group for writing.

    Args:
        store: The zarr store path or object
        zarr_format: The zarr format version to use

    Returns:
        The opened zarr group
    """
    store = remove_tilde(store)

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
