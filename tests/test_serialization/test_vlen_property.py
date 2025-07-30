from collections.abc import Sequence
from typing import cast

import numpy as np
import pytest
import zarr
import zarr.storage
from numpy.typing import ArrayLike, NDArray

from geff.serialization import (
    deserialize_vlen_property_data,
    serialize_vlen_property_data,
    serialize_vlen_property_data_as_dict,
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
        serialized = serialize_vlen_property_data_as_dict(polygons, dtype=np.float32)
        assert "values" in serialized
        assert "missing" in serialized
        assert "data" in serialized
        assert cast("NDArray", serialized["values"]).dtype == np.int64
        assert cast("NDArray", serialized["missing"]).dtype == np.bool_
        assert cast("NDArray", serialized["data"]).dtype == np.float32

    def test_serialize_polygons(self, polygons: Sequence[ArrayLike]):
        serialized = serialize_vlen_property_data(polygons)
        assert len(serialized) == 3
        assert serialized[0].dtype == np.int64  # values
        assert cast("NDArray", serialized[1]).dtype == np.bool_  # missing
        assert serialized[2].dtype == np.float32  # data

    def test_deserialize_polygons_as_dict(self, polygons):
        serialized = serialize_vlen_property_data_as_dict(polygons)
        deserialized = deserialize_vlen_property_data(serialized)
        assert len(deserialized) == len(polygons)
        for orig, des in zip(polygons, deserialized, strict=False):
            np.testing.assert_array_equal(orig, des)

    def test_deserialize_polygons_as(self, polygons):
        serialized = serialize_vlen_property_data(polygons)
        store = zarr.storage.MemoryStore()
        group = zarr.group(store, overwrite=True)
        group["values"] = serialized[0]
        group["missing"] = serialized[1]
        group["data"] = serialized[2]
        deserialized = deserialize_vlen_property_data(group)
        assert len(deserialized) == len(polygons)
        for orig, des in zip(polygons, deserialized, strict=False):
            np.testing.assert_array_equal(orig, des)
