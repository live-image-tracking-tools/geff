import warnings

import pytest

from geff.validate.metadata import _validate_prop_exists, validate_metadata
from geff_spec import GeffMetadata, PropMetadata, RelatedObject


class Test_validate_prop_exists:
    def test_found(self):
        node_props_metadata = {"radius": PropMetadata(identifier="radius", dtype="float64")}
        _validate_prop_exists("Sphere property", "radius", node_props_metadata)

    def test_not_found(self):
        node_props_metadata = {"radius": PropMetadata(identifier="radius", dtype="float64")}
        with pytest.raises(
            ValueError, match=r"Sphere property 'nope' not found in node_props_metadata"
        ):
            _validate_prop_exists("Sphere property", "nope", node_props_metadata)


class Test_validate_metadata:
    def _meta(self, **kwargs) -> GeffMetadata:
        base = {
            "geff_version": "0.0.1",
            "directed": True,
            "edge_props_metadata": {},
            "node_props_metadata": {},
        }
        base.update(kwargs)
        return GeffMetadata(**base)

    def test_valid_sphere(self):
        meta = self._meta(
            node_props_metadata={"radius": PropMetadata(identifier="radius", dtype="float64")},
            sphere="radius",
        )
        validate_metadata(meta)

    def test_sphere_not_found(self):
        meta = self._meta(sphere="nope")
        with pytest.raises(
            ValueError, match=r"Sphere property 'nope' not found in node_props_metadata"
        ):
            validate_metadata(meta)

    def test_ellipsoid_not_found(self):
        meta = self._meta(ellipsoid="nope")
        with pytest.raises(
            ValueError, match=r"Ellipsoid property 'nope' not found in node_props_metadata"
        ):
            validate_metadata(meta)

    def test_polygon_not_found(self):
        meta = self._meta(polygon="nope")
        with pytest.raises(
            ValueError, match=r"Polygon property 'nope' not found in node_props_metadata"
        ):
            validate_metadata(meta)

    def test_track_node_props_not_found(self):
        meta = self._meta(track_node_props={"tracklet": "nope"})
        with pytest.raises(
            ValueError, match=r"Tracklet property 'nope' not found in node_props_metadata"
        ):
            validate_metadata(meta)

        meta = self._meta(track_node_props={"lineage": "nope"})
        with pytest.raises(
            ValueError, match=r"Lineage property 'nope' not found in node_props_metadata"
        ):
            validate_metadata(meta)

    def test_related_object_node_prop_not_found(self):
        meta = self._meta(
            related_objects=[RelatedObject(type="labels", path="seg/", node_prop="nope")]
        )
        with pytest.raises(
            ValueError, match=r"Related object node_prop 'nope' not found in node_props_metadata"
        ):
            validate_metadata(meta)

    def test_related_object_label_prop_not_found(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            meta = self._meta(
                related_objects=[RelatedObject(type="labels", path="seg/", label_prop="nope")]
            )
        with pytest.raises(
            ValueError, match=r"Related object label_prop 'nope' not found in node_props_metadata"
        ):
            validate_metadata(meta)

    def test_valid_full_metadata(self):
        meta = self._meta(
            node_props_metadata={
                "radius": PropMetadata(identifier="radius", dtype="float64"),
                "seg_id": PropMetadata(identifier="seg_id", dtype="int64"),
                "tracklet": PropMetadata(identifier="tracklet", dtype="int64"),
            },
            sphere="radius",
            track_node_props={"tracklet": "tracklet"},
            related_objects=[RelatedObject(type="labels", path="seg/", node_prop="seg_id")],
        )
        validate_metadata(meta)
