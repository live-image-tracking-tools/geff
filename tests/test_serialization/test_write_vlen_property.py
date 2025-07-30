from pathlib import Path

import numpy as np
import pytest

from geff.metadata_schema import GeffMetadata
from geff.write_dicts import dict_vlen_props_to_arr, write_dicts


@pytest.fixture
def data():
    data = [
        (
            0,
            {
                "polygon": None,
            },
        ),
        (
            127,
            {
                "polygon": [
                    [11, 13],
                    [111, 113],
                    [22, 246],
                ],
            },
        ),
        (
            1,
            {
                "polygon": [
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
                ],
            },
        ),
        (
            2,
            {
                "polygon": None,
            },
        ),
    ]
    return data


@pytest.mark.parametrize(
    ("expected"),
    [
        (
            np.array(
                [
                    [0, 0, 0],
                    [0, 3, 2],
                    [6, 14, 2],
                    [34, 0, 0],
                ]
            ),
            np.array(
                [
                    True,
                    False,
                    False,
                    True,
                ]
            ),
            np.array(
                [
                    [11, 13],
                    [111, 113],
                    [22, 246],
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
            ),
        )
    ],
)
def test_dict_prop_to_arr(data, expected):
    props_dict = dict_vlen_props_to_arr(data, ["polygon"])
    assert props_dict["polygon"] is not None
    assert isinstance(props_dict["polygon"], tuple)
    assert len(props_dict["polygon"]) == 3
    values, missing, data = props_dict["polygon"]
    ex_values, ex_missing, ex_data = expected
    ex_values = np.array(ex_values)
    ex_missing = np.array(ex_missing, dtype=bool) if ex_missing is not None else None
    ex_data = np.array(ex_data).ravel() if ex_data is not None else None

    np.testing.assert_array_equal(missing, ex_missing)
    np.testing.assert_array_equal(values, ex_values)
    np.testing.assert_array_equal(data, ex_data)


def test_write_dicts(tmp_path, data):
    zarr_path = Path(tmp_path) / "test.zarr"
    write_dicts(
        zarr_path,
        data,
        [],
        [],
        [],
        node_vlen_prop_names=["polygon"],
    )
    meta = GeffMetadata(
        geff_version="0.0.1",
        directed=True,
        axes=[
            {"name": "test"},
            {
                "name": "complete",
                "type": "space",
                "unit": "micrometer",
                "min": 0,
                "max": 10,
            },
        ],
        extra=True,
    )
    meta.write("test.zarr/tracks")


# TODO: test write_dicts (it is pretty solidly covered by networkx and write_array tests,
# so I'm okay merging without, but we should do it when we have time)
