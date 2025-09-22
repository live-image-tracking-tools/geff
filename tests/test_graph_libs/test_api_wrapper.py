from typing import TYPE_CHECKING, get_args

import numpy as np
import pytest

from geff import construct, read, write
from geff._graph_libs._api_wrapper import SupportedBackend, get_backend
from geff._graph_libs._backend_protocol import GraphAdapter
from geff._graph_libs._networkx import NxBackend
from geff._typing import InMemoryGeff
from geff.core_io import read_to_memory
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
    {},
]


# assert that all the data in the graph are equal to those in the memory geff it was created from
def _assert_graph_equal_to_geff(
    graph_adapter: GraphAdapter,
    memory_geff: InMemoryGeff,
):
    metadata = memory_geff["metadata"]

    # nodes and edges correct
    assert {*graph_adapter.get_node_ids()} == {*memory_geff["node_ids"].tolist()}
    assert {*graph_adapter.get_edge_ids()} == {
        *[tuple(edges) for edges in memory_geff["edge_ids"].tolist()]
    }

    for name, data in memory_geff["node_props"].items():
        values = data["values"]
        missing = data["missing"]
        if missing is None:
            missing = np.zeros(shape=(values.shape[0],), dtype=bool)
        nodes = memory_geff["node_ids"]
        for node, expected_val, expected_missing in zip(nodes, values, missing, strict=True):
            actual_missing = not graph_adapter.has_node_prop(name, node, metadata)
            assert actual_missing == expected_missing

            if not expected_missing:
                actual_val = graph_adapter.get_node_prop(name, node, metadata=metadata)
                if isinstance(actual_val, np.ndarray):
                    np.testing.assert_array_equal(expected_val, actual_val)
                else:
                    assert expected_val == actual_val

    # check edge properties are correct
    for name, data in memory_geff["edge_props"].items():
        values = data["values"]
        missing = data["missing"]
        if missing is None:
            missing = np.zeros(shape=(values.shape[0],), dtype=bool)

        edges = memory_geff["edge_ids"]
        for edge, expected_val, expected_missing in zip(edges, values, missing, strict=True):
            actual_missing = not graph_adapter.has_edge_prop(name, edge, metadata)
            assert actual_missing == expected_missing
            if not expected_missing:
                actual_val = graph_adapter.get_edge_prop(name, edge, metadata)
                if isinstance(actual_val, np.ndarray):
                    np.testing.assert_array_equal(expected_val, actual_val)
                else:
                    assert expected_val == actual_val


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
        extra_node_props={
            "label": "str" if backend != "spatial-graph" else "int",
            "score": "float32",
            "sub_id": "int",
        },
        extra_edge_props=extra_edge_props,
        directed=directed,
        include_t=include_t,
        include_z=include_z,
        include_varlength=backend != "spatial-graph",
    )

    graph, metadata = read(store, backend=backend)
    graph_adapter = backend_module.graph_adapter(graph)

    _assert_graph_equal_to_geff(graph_adapter, memory_geff)


@pytest.mark.parametrize("node_id_dtype", node_id_dtypes)
@pytest.mark.parametrize("node_axis_dtypes", node_axis_dtypes)
@pytest.mark.parametrize("extra_edge_props", extra_edge_props)
@pytest.mark.parametrize("directed", [True, False])
@pytest.mark.parametrize("include_t", [True, False])
@pytest.mark.parametrize("include_z", [True, False])
@pytest.mark.parametrize("backend", get_args(SupportedBackend))
def test_construct(
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
        extra_node_props={
            "label": "str" if backend != "spatial-graph" else "int",
            "score": "float32",
            "sub_id": "int",
        },
        extra_edge_props=extra_edge_props,
        directed=directed,
        include_t=include_t,
        include_z=include_z,
        include_varlength=backend != "spatial-graph",
    )

    in_memory_geff = read_to_memory(store)
    graph = construct(**in_memory_geff, backend=backend)
    graph_adapter = backend_module.graph_adapter(graph)

    _assert_graph_equal_to_geff(graph_adapter, memory_geff)


@pytest.mark.parametrize("node_id_dtype", node_id_dtypes)
@pytest.mark.parametrize("node_axis_dtypes", node_axis_dtypes)
@pytest.mark.parametrize("extra_edge_props", extra_edge_props)
@pytest.mark.parametrize("directed", [True, False])
@pytest.mark.parametrize("include_t", [True, False])
@pytest.mark.parametrize("include_z", [True, False])
@pytest.mark.parametrize("backend", get_args(SupportedBackend))
def test_write(
    tmp_path,
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
        extra_node_props={
            "label": "str" if backend != "spatial-graph" else "int",
            "score": "float32",
            "sub_id": "int",
        },
        extra_edge_props=extra_edge_props,
        directed=directed,
        include_t=include_t,
        include_z=include_z,
        include_varlength=backend != "spatial-graph",
    )

    # this will create a graph instance of the backend type
    original_graph = backend_module.construct(**memory_geff)

    # write with unified write function
    path_store = tmp_path / "test_path.zarr"
    write(original_graph, path_store, memory_geff["metadata"])

    # read with the NxBackend to see if the graph is the same
    graph, metadata = NxBackend.read(path_store)
    graph_adapter = NxBackend.graph_adapter(graph)

    _assert_graph_equal_to_geff(graph_adapter, memory_geff)

    # TODO: test metadata
