from __future__ import annotations

import copy
import warnings
from collections.abc import Sequence  # noqa: TC003
from typing import TYPE_CHECKING, Any, Literal, TypeVar

import numpy as np
from pydantic import validate_call

from ._axis import Axis

# The next import is needed at runtime for Pydantic validation
from ._prop_metadata import PropMetadata
from ._schema import GEFF_VERSION, GeffMetadata

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ._mesh import Mesh
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
        metadata.geff_version = GEFF_VERSION
        metadata.directed = is_directed
        if axes is not None:
            metadata.axes = axes
    else:
        metadata = GeffMetadata(
            geff_version=GEFF_VERSION,
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
        If a key in props_md already exists in the properties metadata, only the
            dtype and varlength fields will be updated
    """
    metadata = copy.deepcopy(metadata)
    match c_type:
        case "node":
            existing_props = metadata.node_props_metadata
        case "edge":
            existing_props = metadata.edge_props_metadata

    md_dict = {}
    for prop in props_md:
        if prop.identifier in existing_props:
            existing_props[prop.identifier].dtype = prop.dtype
            existing_props[prop.identifier].varlength = prop.varlength
        else:
            md_dict[prop.identifier] = prop

    existing_props.update(md_dict)

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
        axis_scales ((Sequence[float | None] | None, optional)): The scale to apply to the
            spatial dims. Defaults to None.
        scaled_units (Sequence[str | None] | None, optional): The units of the spatial dims
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

    if axis_offset is not None and len(axis_offset) != len(axis_names):
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
        identifier (str): The property identifier/name
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
        raise TypeError(f"Expected dict of property data, got {prop_data}")
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


def _validate_prop_exists(
    label: str,
    prop_name: str,
    node_props_metadata: Mapping[str, PropMetadata],
) -> None:
    """Check that a property name referenced elsewhere in the metadata is a valid node property.

    Args:
        label (str): Description of what references `prop_name`, used verbatim at the start
            of the error message (e.g. "Sphere property", "Related object node_prop").
        prop_name (str): The node property name being referenced.
        node_props_metadata (Mapping[str, PropMetadata]): Metadata for node properties,
            keyed by property identifier.

    Raises:
        ValueError: If prop_name is not found in node_props_metadata.
    """
    if prop_name not in node_props_metadata:
        raise ValueError(f"{label} '{prop_name}' not found in node_props_metadata")


def _validate_mesh_metadata(
    mesh: Mesh,
    node_props_metadata: Mapping[str, PropMetadata],
    axes: list[Axis] | None,
) -> None:
    """Check that a Mesh's property names exist in node_props_metadata, and that any
    vertex_axes names refer to existing spatial axes.

    Args:
        mesh (Mesh): The Mesh metadata to validate.
        node_props_metadata (Mapping[str, PropMetadata]): Metadata for node properties,
            keyed by property identifier.
        axes (list[Axis] | None): List of Axis metadata.

    Raises:
        ValueError: If a mesh property name is not found in node_props_metadata.
        ValueError: If a vertex_axes name is not found in axes, or is not a spatial axis.
    """
    for field_name in ("vertices", "triangles", "vertex_normals", "triangle_normals"):
        prop_name = getattr(mesh, field_name)
        if prop_name is not None and prop_name not in node_props_metadata:
            raise ValueError(
                f"Mesh '{field_name}' property '{prop_name}' not found in node_props_metadata"
            )

    if mesh.vertex_axes is not None:
        ax_by_name = {ax.name: ax for ax in axes} if axes is not None else {}
        for name in mesh.vertex_axes:
            if name not in ax_by_name:
                raise ValueError(f"Mesh vertex_axes name '{name}' not found in axes")
            if ax_by_name[name].type != "space":
                raise ValueError(f"Mesh vertex_axes name '{name}' is not a spatial axis")


def validate_metadata(metadata: GeffMetadata) -> None:
    """Validate cross references between `GeffMetadata` fields and `node_props_metadata`.

    These checks only need the metadata object itself, not the underlying property arrays.
    They are not enforced eagerly on every `GeffMetadata` construction/assignment because some
    writers build up `node_props_metadata` incrementally: an initial, intentionally incomplete
    `GeffMetadata` is constructed first, and `node_props_metadata` is filled in afterward from
    the real property data (e.g. `write_arrays`). Call this explicitly once metadata is
    finalized, such as right before writing or right after reading.

    Args:
        metadata (GeffMetadata): The metadata to validate.

    Raises:
        ValueError: If a sphere/ellipsoid/polygon/mesh/tracklet/lineage/related-object property
            name is not found in `node_props_metadata`, or a mesh `vertex_axes` name is not a
            valid spatial axis.
    """
    if metadata.sphere is not None:
        _validate_prop_exists("Sphere property", metadata.sphere, metadata.node_props_metadata)
    if metadata.ellipsoid is not None:
        _validate_prop_exists(
            "Ellipsoid property", metadata.ellipsoid, metadata.node_props_metadata
        )
    if metadata.polygon is not None:
        _validate_prop_exists("Polygon property", metadata.polygon, metadata.node_props_metadata)

    if metadata.mesh is not None:
        _validate_mesh_metadata(metadata.mesh, metadata.node_props_metadata, metadata.axes)

    if metadata.track_node_props is not None:
        for key, prop_name in metadata.track_node_props.items():
            _validate_prop_exists(
                f"{key.capitalize()} property", prop_name, metadata.node_props_metadata
            )

    if metadata.related_objects is not None:
        for related_object in metadata.related_objects:
            if related_object.node_prop is not None:
                _validate_prop_exists(
                    "Related object node_prop",
                    related_object.node_prop,
                    metadata.node_props_metadata,
                )
            # Accessing label_prop always triggers its deprecation warning, even when None
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore", message="Deprecated in geff-spec v1.2.1 in favor of `node_prop`."
                )
                label_prop = related_object.label_prop
            if label_prop is not None:
                _validate_prop_exists(
                    "Related object label_prop", label_prop, metadata.node_props_metadata
                )
