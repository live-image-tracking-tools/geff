from __future__ import annotations

import copy
import warnings
from collections.abc import Sequence  # noqa: TC003
from typing import TYPE_CHECKING, Any, Literal, TypeVar

import numpy as np
from pydantic import validate_call

import geff
from geff.metadata import GeffMetadata, PropMetadata

from ._axis import Axis

if TYPE_CHECKING:
    T = TypeVar("T")
    from geff._typing import PropDictNpArray


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


@validate_call
def create_or_update_props_metadata(
    metadata: GeffMetadata,
    props_md: Sequence[PropMetadata],
    c_type: Literal["node", "edge"],
) -> GeffMetadata:
    """Create new props metadata or update existing metadata with new props metadata.

    Args:
        metadata (GeffMetadata): Existing metadata object
        props_md (Sequence[PropMetadata]): The props metadata to add to the metadata.
        c_type (Literal["node", "edge"]): The type of the props metadata.

    Returns:
        GeffMetadata object with updated props metadata.

    Warning:
        If a key in props_md already exists in the properties metadata, it will be overwritten.
    """
    metadata = copy.deepcopy(metadata)
    md_dict = {prop.identifier: prop for prop in props_md}
    match c_type:
        case "node":
            md_to_update = metadata.node_props_metadata
        case "edge":
            md_to_update = metadata.edge_props_metadata

    if md_to_update is None:
        md_to_update = md_dict
    else:
        md_to_update.update(md_dict)

    match c_type:
        case "node":
            metadata.node_props_metadata = md_to_update
        case "edge":
            metadata.edge_props_metadata = md_to_update

    return metadata


def axes_from_lists(
    axis_names: Sequence[str] | None = None,
    axis_units: Sequence[str | None] | None = None,
    axis_types: Sequence[str | None] | None = None,
    roi_min: Sequence[float | None] | None = None,
    roi_max: Sequence[float | None] | None = None,
) -> list[Axis]:
    """Create a list of Axes objects from lists of axis names, units, types, mins,
    and maxes. If axis_names is None, there are no spatial axes and the list will
    be empty. Nones for all other arguments will omit them from the axes.

    All provided arguments must have the same length. If an argument should not be specified
    for a single property, use None.

    Args:
        axis_names (list[str] | None, optional): Names of properties for spatiotemporal
            axes. Defaults to None.
        axis_units (list[str | None] | None, optional): Units corresponding to named properties.
            Defaults to None.
        axis_types (list[str | None] | None, optional): Axis type for each property.
            Choose from "space", "time", "channel". Defaults to None.
        roi_min (list[float | None] | None, optional): Minimum value for each property.
            Defaults to None.
        roi_max (list[float | None] | None, optional): Maximum value for each property.
            Defaults to None.

    Returns:
        list[Axis]:
    """
    axes: list[Axis] = []
    if axis_names is None:
        return axes

    dims = len(axis_names)
    if axis_types is not None:
        assert len(axis_types) == dims, (
            "The number of axis types has to match the number of axis names"
        )

    if axis_units is not None:
        assert len(axis_units) == dims, (
            "The number of axis types has to match the number of axis names"
        )

    for i in range(len(axis_names)):
        axes.append(
            Axis(
                name=axis_names[i],
                type=axis_types[i] if axis_types is not None else None,
                unit=axis_units[i] if axis_units is not None else None,
                min=roi_min[i] if roi_min is not None else None,
                max=roi_max[i] if roi_max is not None else None,
            )
        )
    return axes


def create_prop_metadata(
    identifier: str,
    prop_data: PropDictNpArray,
    unit: str | None = None,
    name: str | None = None,
    description: str | None = None,
) -> PropMetadata:
    """Create PropMetadata from property data.

    Automatically detects dtype and varlength from the provided data.

    Args:
        identifier: The property identifier/name
        prop_data: Either InMemoryNormalProp (dict with values/missing) or
                  InMemoryVarLenProp (sequence of arrays with None values)
        unit: Optional unit for the property
        name: Optional human-friendly name for the property
        description: Optional description for the property

    Returns:
        PropMetadata object with inferred dtype and varlength settings

    Raises:
        ValueError: If var length array has mixed dtype
    """
    # Check if this is a variable length property (sequence of arrays)

    if not isinstance(prop_data, dict):
        raise ValueError(f"Expected dict of property data, got {prop_data}")
    values = prop_data["values"]
    if not np.issubdtype(values.dtype, np.object_):
        # normal property case
        varlength = False
        dtype = values.dtype

    else:
        # variable length property case
        varlength = True
        dtype = values[0].dtype
        # check that all arrays have the same dtype while we are here
        for array in values:
            if array.dtype != dtype:
                raise ValueError(
                    "Object array containing variable length properties has two "
                    f"dtypes: {dtype, array.dtype}"
                )

    return PropMetadata(
        identifier=identifier,
        dtype=str(dtype),
        varlength=varlength,
        unit=unit,
        name=name,
        description=description,
    )
