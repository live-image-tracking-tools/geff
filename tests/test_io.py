from typing import TYPE_CHECKING, get_args

import numpy as np
import pytest

from geff.io import SupportedBackend, read
from geff.io.read import get_backend
from geff.testing.data import create_memory_mock_geff

if TYPE_CHECKING:
    from geff.backend_protocol import Backend

rx = pytest.importorskip("rustworkx")
sg = pytest.importorskip("spatial_graph")

node_id_dtypes = ["int8", "uint8", "int16", "uint16"]
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

    store, graph_props = create_memory_mock_geff(
        node_id_dtype,
        node_axis_dtypes,
        extra_edge_props=extra_edge_props,
        directed=directed,
        include_t=include_t,
        include_z=include_z,
    )

    graph, metadata = read(store, backend=backend)

    assert isinstance(graph, backend_module.GRAPH_TYPES)

    # nodes and edges correct
    assert {*backend_module.get_node_ids(graph)} == {*graph_props["nodes"].tolist()}
    assert {*backend_module.get_edge_ids(graph)} == {
        *[tuple(edges) for edges in graph_props["edges"].tolist()]
    }

    # check node properties are correct
    spatial_node_properties = ["y", "x"]
    if include_t:
        spatial_node_properties.append("t")
    if include_z:
        spatial_node_properties.append("z")
    for name in spatial_node_properties:
        np.testing.assert_array_equal(
            backend_module.get_node_prop(
                graph, name, graph_props["nodes"].tolist(), metadata=metadata
            ),
            graph_props[name],
        )
    for name, values in graph_props["extra_node_props"].items():
        np.testing.assert_array_equal(
            backend_module.get_node_prop(
                graph, name, graph_props["nodes"].tolist(), metadata=metadata
            ),
            values,
        )
    # check edge properties are correct
    for name, values in graph_props["extra_edge_props"].items():
        np.testing.assert_array_equal(
            backend_module.get_edge_prop(graph, name, graph_props["edges"].tolist(), metadata),
            values,
        )
