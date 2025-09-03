from typing import TYPE_CHECKING, get_args

import numpy as np
import pytest

from geff._graph_libs._api_wrapper import SupportedBackend, get_backend, read
from geff.testing.data import create_mock_geff

if TYPE_CHECKING:
    from geff._graph_libs._backend_protocol import Backend

rx = pytest.importorskip("rustworkx")
sg = pytest.importorskip("spatial_graph")

node_id_dtypes = ["uint8", "uint16"]
node_axis_dtypes = [
    {"position": "double", "time": "double"},
    {"position": "int", "time": "int"},
]
extra_edge_props = [
    {"score": "float64", "color": "uint8"},
    {"score": "float32", "color": "int16"},
]


@pytest.mark.parametrize("node_id_dtype", node_id_dtypes)
@pytest.mark.parametrize("node_axis_dtypes", node_axis_dtypes)
@pytest.mark.parametrize("extra_edge_props", extra_edge_props)
@pytest.mark.parametrize("directed", [True, False])
@pytest.mark.parametrize("include_t", [True, False])
@pytest.mark.parametrize("include_z", [True, False])
@pytest.mark.parametrize("backend", get_args(SupportedBackend))
def test_read(
    node_id_dtype,
    node_axis_dtypes,
    extra_edge_props,
    directed,
    include_t,
    include_z,
    backend,
) -> None:
    backend_module: Backend = get_backend(backend)

    store, memory_geff = create_mock_geff(
        node_id_dtype,
        node_axis_dtypes,
        extra_edge_props=extra_edge_props,
        directed=directed,
        include_t=include_t,
        include_z=include_z,
    )

    graph, metadata = read(store, backend=backend)
    graph_adapter = backend_module.graph_adapter(graph)

    # nodes and edges correct
    assert {*graph_adapter.get_node_ids()} == {*memory_geff["node_ids"].tolist()}
    assert {*graph_adapter.get_edge_ids()} == {
        *[tuple(edges) for edges in memory_geff["edge_ids"].tolist()]
    }

    # check node properties are correct
    spatial_node_properties = ["y", "x"]
    if include_t:
        spatial_node_properties.append("t")
    if include_z:
        spatial_node_properties.append("z")
    for name in spatial_node_properties:
        np.testing.assert_array_equal(
            graph_adapter.get_node_prop(name, memory_geff["node_ids"].tolist(), metadata=metadata),
            memory_geff["node_props"][name]["values"],
        )

    for name, data in memory_geff["node_props"].items():
        values = data["values"]
        np.testing.assert_array_equal(
            graph_adapter.get_node_prop(name, memory_geff["node_ids"].tolist(), metadata=metadata),
            values,
        )

    # check edge properties are correct
    for name, data in memory_geff["edge_props"].items():
        values = data["values"]
        np.testing.assert_array_equal(
            graph_adapter.get_edge_prop(name, memory_geff["edge_ids"].tolist(), metadata),
            values,
        )


# TODO: test write
