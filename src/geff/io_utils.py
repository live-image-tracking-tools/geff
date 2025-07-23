import copy
import warnings
from collections.abc import Callable
from typing import Any, Literal, Protocol

import numpy as np
import zarr

import geff
from geff.metadata_schema import GeffMetadata
from geff.utils import remove_tilde


class GraphProtocol(Protocol):
    """Protocol for graph objects that can be used with shared I/O utilities."""

    def num_nodes(self) -> int:
        """Return the number of nodes in the graph."""
        ...

    def nodes(self) -> Any:
        """Return nodes with data."""
        ...


def get_graph_existing_metadata(
    metadata: GeffMetadata | None = None,
    axis_names: list[str] | None = None,
    axis_units: list[str | None] | None = None,
    axis_types: list[str | None] | None = None,
) -> tuple[list[str] | None, list[str | None] | None, list[str | None] | None]:
    """Get the existing metadata from a graph.

    If axis lists are provided, they will override the graph properties and metadata.
    If metadata is provided, it will override the graph properties.
    If neither are provided, the graph properties will be used.

    Args:
        metadata: The metadata of the graph. Defaults to None.
        axis_names: The names of the spatial dims. Defaults to None.
        axis_units: The units of the spatial dims. Defaults to None.
        axis_types: The types of the spatial dims. Defaults to None.

    Returns:
        tuple[list[str] | None, list[str | None] | None, list[str | None] | None]:
            A tuple with the names of the spatial dims, the units of the spatial dims,
            and the types of the spatial dims. None if not provided.
    """
    lists_provided = any(x is not None for x in [axis_names, axis_units, axis_types])
    metadata_provided = metadata is not None

    if lists_provided and metadata_provided:
        warnings.warn(
            "Both axis lists and metadata provided. Overriding metadata with axis lists.",
            stacklevel=2,
        )

    # If any axis lists is not provided, fallback to metadata if provided
    if metadata is not None and metadata.axes is not None:
        # the x = x or y is a python idiom for setting x to y if x is None, otherwise x
        axis_names = axis_names or [axis.name for axis in metadata.axes]
        axis_units = axis_units or [axis.unit for axis in metadata.axes]
        axis_types = axis_types or [axis.type for axis in metadata.axes]

    return axis_names, axis_units, axis_types


def setup_zarr_group(store: Any, zarr_format: Literal[2, 3] = 2) -> zarr.Group:
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


def create_or_update_metadata(
    metadata: GeffMetadata | None,
    is_directed: bool,
    axes: Any,
) -> GeffMetadata:
    """Create new metadata or update existing metadata with axes, version, and directedness.

    Args:
        metadata: Existing metadata object or None
        is_directed: Whether the graph is directed
        axes: The axes object to set

    Returns:
        Updated or new GeffMetadata object
    """
    if metadata is not None:
        metadata = copy.deepcopy(metadata)
        metadata.geff_version = geff.__version__
        metadata.directed = is_directed
        metadata.axes = axes
    else:
        metadata = GeffMetadata(
            geff_version=geff.__version__,
            directed=is_directed,
            axes=axes,
        )
    return metadata


def calculate_roi_from_nodes(
    nodes_iter: Any,
    axis_names: list[str],
    node_accessor_func: Callable,
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

    return tuple(_min.tolist()), tuple(_max.tolist())  # type: ignore
