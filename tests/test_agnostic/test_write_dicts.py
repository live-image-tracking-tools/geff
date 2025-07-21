import pytest
from geff.write_dicts import write_dicts, dict_props_to_arr
import numpy as np


@pytest.fixture
def data():
    data = [
        (0, {"num": 1, "str": "category"}),
        (127, {"num": 5, "str_arr": ["test", "string"]}),
        (1, {"num": 6, "num_arr": [1, 2]}),
    ]
    return data


@pytest.mark.parametrize(
    ("data_type", "expected"),
    [
        ("num", ([1, 5, 6], None)),
        ("str", (["category", "", ""], [0, 1, 1])),
        ("num_arr", ([[1, 2], [1, 2], [1, 2]], [1, 1, 0])),
        ("str_arr", ([["test", "string"], ["test", "string"], ["test", "string"]], [1, 0, 1])),
    ],
)
def test_dict_prop_to_arr(data, data_type, expected):
    props_dict = dict_props_to_arr(data, [data_type])
    print(props_dict)
    values, missing = props_dict[data_type]
    ex_values, ex_missing = expected
    ex_values = np.array(ex_values)
    ex_missing = np.array(ex_missing, dtype=bool) if ex_missing is not None else None

    np.testing.assert_array_equal(missing, ex_missing)
    np.testing.assert_array_equal(values, ex_values)


# TODO: test write_dicts (it is pretty solidly covered by networkx and write_array tests,
# so I'm okay merging without, but we should do it when we have time)
