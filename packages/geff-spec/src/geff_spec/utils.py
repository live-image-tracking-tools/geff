from __future__ import annotations

import copy
import warnings
from collections.abc import Sequence  # noqa: TC003
from typing import TYPE_CHECKING, Any, Literal, TypeVar

import numpy as np
from pydantic import validate_call

import geff

from ._axis import Axis

# The next import is needed at runtime for Pydantic validation
from ._prop_metadata import PropMetadata
from ._schema import GeffMetadata

if TYPE_CHECKING:
    from ._valid_values import AxisType

    T = TypeVar("T")
    from geff._typing import PropDictNpArray


def update_metadata_axes(
    metadata: GeffMetadata,
    axis_names: list[str],
    axis_units: list[str | None] | None = None,
    axis_types: list[Literal[AxisType] | None] | None = None,
    axis_scales: list[float | None] | None = None,
    scaled_units: list[str | None] | None = None,
    axis_offset: list[float | None] | None = None,
) -> GeffMetadata:
    """Update the axis names, units, and types in a geff metadata object.
    Overrides any existing axes.

    If axis lists are provided, they will override the graph properties and metadata.
    If metadata is provided, it will override the graph properties.
    If neither are provided, the graph properties will be used.

    Args:
        metadata (GeffMetadata): The metadata of the graph.
        axis_names (list[str]): The names of the spatial dims.
        axis_units (list[str | None] | None): The units of the spatial dims. Defaults to None.
        axis_types (list[Literal[AxisType] | None] | None): The types of the spatial dims.
            Defaults to None.
        axis_scales (list[float | None] | None): The scale to apply to the spatial dims.
            Defaults to None.
        scaled_units (list[str | None] | None): The units of the spatial dims after scaling.
            Defaults to None.
        axis_offset (list[float | None] | None): Amount to offset an axis after applying
            scaling factor. Defaults to None.

    Returns:
        GeffMetadata: A new metadata object with updated axes.
    """

    new_meta = metadata.model_copy()
    axes = axes_from_lists(
        axis_names=axis_names,
        axis_types=axis_types,
        axis_units=axis_units,
        axis_scales=axis_scales,
        scaled_units=scaled_units,
        axis_offset=axis_offset,
    )
    new_meta.axes = axes
    return new_meta


def compute_and_add_axis_min_max(
    metadata: GeffMetadata, node_props: dict[str, PropDictNpArray]
) -> GeffMetadata:
    """Create a new metadata object with the min and max values for each axis added.

    Args:
        metadata (GeffMetadata): The metadata to update with the min and max axis values.
        node_props (dict[str, PropDictNpArray]): The node props to compute the min and
            max from

    Returns:
        GeffMetadata: A new metadata object with the min and max updated.
    """
    new_meta = metadata.model_copy()
    if new_meta.axes is None:
        return new_meta
    new_axes = []
    for axis in new_meta.axes:
        if axis.name not in node_props:
            raise ValueError(
                f"Spatiotemporal property '{axis.name}' not found in node properties:"
                f"\n{node_props.keys()}"
            )
        prop = node_props[axis.name]
        values = prop["values"]
        if len(values) == 0:
            new_axes.append(axis)
            continue
        missing = prop["missing"]
        if missing is not None:
            values = values[np.logical_not(missing)]
        axis.min = np.min(values).item()
        axis.max = np.max(values).item()
        new_axes.append(axis)
    new_meta.axes = new_axes
    return new_meta


def create_or_update_metadata(
    metadata: GeffMetadata | None,
    is_directed: bool,
    axes: Any = None,
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
        if axes is not None:
            metadata.axes = axes
    else:
        metadata = GeffMetadata(
            geff_version=geff.__version__,
            directed=is_directed,
            axes=axes,
            node_props_metadata={},
            edge_props_metadata={},
        )
    return metadata


@validate_call
def add_or_update_props_metadata(
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
            metadata.node_props_metadata.update(md_dict)
        case "edge":
            metadata.edge_props_metadata.update(md_dict)

    return metadata


def axes_from_lists(
    axis_names: Sequence[str] | None = None,
    axis_units: Sequence[str | None] | None = None,
    axis_types: Sequence[Literal[AxisType] | None] | None = None,
    axis_scales: Sequence[float | None] | None = None,
    scaled_units: Sequence[str | None] | None = None,
    axis_offset: Sequence[float | None] | None = None,
    roi_min: Sequence[float | None] | None = None,
    roi_max: Sequence[float | None] | None = None,
) -> list[Axis]:
    """Create a list of Axes objects from lists of axis names, units, types, mins,
    and maxes. If axis_names is None, there are no spatial axes and the list will
    be empty. Nones for all other arguments will omit them from the axes.

    All provided arguments must have the same length. If an argument should not be specified
    for a single property, use None.

    Args:
        axis_names (Sequence[str] | None, optional): Names of properties for spatiotemporal
            axes. Defaults to None.
        axis_units (Sequence[str | None] | None, optional): Units corresponding to named properties.
            Defaults to None.
        axis_types (Sequence[Literal[AxisType] | None] | None, optional): Axis type for each
            property. Choose from "space", "time", "channel". Defaults to None.
        axis_scales((Sequence[float | None] | None, optional)): The scale to apply to the
            spatial dims. Defaults to None.
        scaled_units(Sequence[str | None] | None, optional): The units of the spatial dims
            after scaling. Defaults to None.
        axis_offset (list[float | None] | None): Amount to offset an axis after applying
            scaling factor. Defaults to None.
        roi_min (Sequence[float | None] | None, optional): Minimum value for each property.
            Defaults to None.
        roi_max (Sequence[float | None] | None, optional): Maximum value for each property.
            Defaults to None.

    Returns:
        list[Axis]: A list of axes objects, one per entry in axis_names
    """
    axes: list[Axis] = []
    if axis_names is None:
        return axes

    if axis_units is not None and len(axis_units) != len(axis_names):
        raise ValueError(
            f"Axis units {axis_units} does not have same length as axis names {axis_names}"
        )
    if axis_types is not None and len(axis_types) != len(axis_names):
        raise ValueError(
            f"Axis types {axis_types} does not have same length as axis names {axis_names}"
        )
    if axis_scales is not None and len(axis_scales) != len(axis_names):
        raise ValueError(
            f"Axis scales {axis_scales} does not have same length as axis names {axis_names}"
        )
    if scaled_units is not None and len(scaled_units) != len(axis_names):
        raise ValueError(
            f"Scaled units {scaled_units} does not have same length as axis names {axis_names}"
        )

    if axis_offset is not None and len(axis_offset) != len(axis_offset):
        raise ValueError(
            f"Axis offset {axis_offset} does not have same length as axis names {axis_names}"
        )

    for i in range(len(axis_names)):
        axes.append(
            Axis(
                name=axis_names[i],
                type=axis_types[i] if axis_types is not None else None,
                unit=axis_units[i] if axis_units is not None else None,
                scale=axis_scales[i] if axis_scales is not None else None,
                scaled_unit=scaled_units[i] if scaled_units is not None else None,
                offset=axis_offset[i] if axis_offset is not None else None,
                min=roi_min[i] if roi_min is not None else None,
                max=roi_max[i] if roi_max is not None else None,
            )
        )
    return axes


def create_props_metadata(
    identifier: str,
    prop_data: PropDictNpArray,
    unit: str | None = None,
    name: str | None = None,
    description: str | None = None,
) -> PropMetadata:
    """Create PropMetadata from property data.

    Automatically detects dtype and varlength from the provided data.
    If dtype is float16, upcasts to float32 with warning.

    Args:
        identifier(str): The property identifier/name
        prop_data (PropDictNpArray): The property to generate metadata for
        unit (str): Optional unit for the property
        name (str): Optional human-friendly name for the property
        description (str): Optional description for the property

    Returns:
        PropMetadata object with inferred dtype and varlength settings

    Raises:
        ValueError: If var length array has mixed dtype
    """
    # Check if this is a variable length property (sequence of arrays)
    if not isinstance(prop_data, dict):
        raise ValueError(f"Expected dict of property data, got {prop_data}")
    values = prop_data["values"]
    if np.issubdtype(values.dtype, np.float16):
        warnings.warn(
            "Dtype float16 is being upcast to float32 for Java compatibility", stacklevel=2
        )
        values = values.astype(np.float32)
        prop_data["values"] = values

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
        dtype=dtype,  # pyright: ignore
        varlength=varlength,
        unit=unit,
        name=name,
        description=description,
    )
