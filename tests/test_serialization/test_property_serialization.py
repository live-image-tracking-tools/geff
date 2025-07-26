from collections.abc import Sequence

import numpy as np
import pytest
import zarr
from numpy.typing import ArrayLike

from geff.serialization import (
    get_deserialized_property_data,
    serialize_property_data,
    serialize_property_data_as_dict,
)


@pytest.fixture
def polygons():
    triangle = [
        [11, 13],
        [111, 113],
        [22, 246],
    ]

    person = [
        [505, 60],
        [402, 71],
        [383, 42],
        [251, 95],
        [212, 59],
        [131, 137],
        [126, 187],
        [191, 204],
        [171, 248],
        [211, 260],
        [273, 243],
        [264, 225],
        [430, 173],
        [512, 160],
    ]

    building = [
        [310, 382],
        [229, 381],
        [209, 401],
        [221, 411],
        [258, 411],
        [300, 412],
        [306, 435],
        [268, 434],
        [265, 454],
        [298, 461],
        [307, 461],
        [307, 507],
        [349, 510],
        [352, 369],
        [330, 366],
        [330, 366],
    ]
    return [None, triangle, person, building]


class TestSerialization:
    """Test validation of polygon properties."""

    def test_serialize_polygons_as_dict(self, polygons: Sequence[ArrayLike]):
        serialized = serialize_property_data_as_dict(polygons)
        assert "values" in serialized
        assert "missing" in serialized
        assert "slices" in serialized
        assert serialized["values"].dtype == np.float32
        assert serialized["missing"].dtype == np.bool_
        assert serialized["slices"].dtype == np.uint64

    def test_serialize_polygons(self, polygons: Sequence[ArrayLike]):
        serialized = serialize_property_data(polygons)
        assert len(serialized) == 3
        assert serialized[0].dtype == np.float32  # values
        assert serialized[1].dtype == np.bool_  # missing
        assert serialized[2].dtype == np.uint64  # slices

    def test_deserialize_polygons_as_dict(self, polygons):
        serialized = serialize_property_data_as_dict(polygons)
        deserialized = get_deserialized_property_data(serialized)
        assert len(deserialized) == len(polygons)
        for orig, des in zip(polygons, deserialized, strict=False):
            np.testing.assert_array_equal(orig, des)

    def test_deserialize_polygons_as(self, polygons):
        serialized = serialize_property_data(polygons)
        store = zarr.storage.MemoryStore()
        group = zarr.group(store, overwrite=True)
        group["values"] = serialized[0]
        group["missing"] = serialized[1]
        group["slices"] = serialized[2]
        deserialized = get_deserialized_property_data(group)
        assert len(deserialized) == len(polygons)
        for orig, des in zip(polygons, deserialized, strict=False):
            np.testing.assert_array_equal(orig, des)
