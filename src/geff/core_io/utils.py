from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

import zarr

if TYPE_CHECKING:
    from zarr.storage import StoreLike

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
