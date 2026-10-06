from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

    from geff_spec import GeffMetadata, PropMetadata


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
        ValueError: If a sphere/ellipsoid/polygon/tracklet/lineage/related-object property
            name is not found in `node_props_metadata`.
    """
    if metadata.sphere is not None:
        _validate_prop_exists("Sphere property", metadata.sphere, metadata.node_props_metadata)
    if metadata.ellipsoid is not None:
        _validate_prop_exists(
            "Ellipsoid property", metadata.ellipsoid, metadata.node_props_metadata
        )
    if metadata.polygon is not None:
        _validate_prop_exists("Polygon property", metadata.polygon, metadata.node_props_metadata)

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
