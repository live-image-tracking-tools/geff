from typing import TYPE_CHECKING, get_args

import networkx as nx
import numpy as np
import pytest
import zarr

from geff import construct, read, write
from geff._graph_libs._api_wrapper import SupportedBackend, get_backend
from geff._graph_libs._backend_protocol import GraphAdapter
from geff._graph_libs._networkx import NxBackend
from geff._typing import InMemoryGeff
from geff.core_io import read_to_memory
from geff.testing.data import create_empty_geff, create_mock_geff, create_simple_3d_geff

if TYPE_CHECKING:
    from geff._graph_libs._backend_protocol import Backend


rx = pytest.importorskip("rustworkx")
sg = pytest.importorskip("spatial_graph")


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


PROP_DTYPES = ["float64", "uint8", "float32", "int16"]
ID_DTYPES = ["int8", "uint16"]
AXIS_DTYPES = {"position": "double", "time": "int"}


@pytest.mark.parametrize("node_id_dtype", ID_DTYPES, ids=["nid_" + dtype for dtype in ID_DTYPES])
@pytest.mark.parametrize("directed", [True, False], ids=["direct", "!direct"])
@pytest.mark.parametrize("include_t", [True, False], ids=["t", "!t"])
@pytest.mark.parametrize("include_spatial", [True, False], ids=["xyz", "!xyz"])
@pytest.mark.parametrize("backend", get_args(SupportedBackend))
class Test_api_wrapper:
    def test_read(
        self,
        node_id_dtype,
        directed,
        include_t,
        include_spatial,
        backend,
    ) -> None:
        if include_spatial is False and backend == "spatial-graph":
            pytest.skip("Non-spatial graphs not supported by spatial-graph")
        backend_module: Backend = get_backend(backend)

        extra_props = {dtype: dtype for dtype in PROP_DTYPES}
        if backend != "spatial-graph":
            extra_props["str"] = "str"

        store, memory_geff = create_mock_geff(
            node_id_dtype,
            AXIS_DTYPES,
            extra_node_props=extra_props,
            extra_edge_props=extra_props,
            directed=directed,
            include_t=include_t,
            include_x=include_spatial,
            include_y=include_spatial,
            include_z=include_spatial,
            include_varlength=backend != "spatial-graph",
            include_missing=backend != "spatial-graph",
        )

        graph, metadata = read(store, backend=backend)
        graph_adapter = backend_module.graph_adapter(graph)

        _assert_graph_equal_to_geff(graph_adapter, memory_geff)

    def test_construct(
        self,
        node_id_dtype,
        directed,
        include_t,
        include_spatial,
        backend,
    ) -> None:
        backend_module: Backend = get_backend(backend)

        extra_props = {dtype: dtype for dtype in PROP_DTYPES}
        if backend != "spatial-graph":
            extra_props["str"] = "str"

        store, memory_geff = create_mock_geff(
            node_id_dtype,
            AXIS_DTYPES,
            extra_node_props=extra_props,
            extra_edge_props=extra_props,
            directed=directed,
            include_t=include_t,
            include_x=include_spatial,
            include_y=include_spatial,
            include_z=include_spatial,
            include_varlength=backend != "spatial-graph",
            include_missing=backend != "spatial-graph",
        )

        in_memory_geff = read_to_memory(store)
        if all([include_spatial is False, include_t is False, backend == "spatial-graph"]):
            with pytest.raises(
                ValueError,
                match="Cannot construct a non-empty SpatialGraph from a geff without axes",
            ):
                graph = construct(**in_memory_geff, backend=backend)
        else:
            graph = construct(**in_memory_geff, backend=backend)
            graph_adapter = backend_module.graph_adapter(graph)

            _assert_graph_equal_to_geff(graph_adapter, memory_geff)

    def test_write(
        self,
        tmp_path,
        node_id_dtype,
        directed,
        include_t,
        include_spatial,
        backend,
    ) -> None:
        if include_spatial is False and backend == "spatial-graph":
            pytest.skip("Non-spatial graphs not supported by spatial-graph")
        backend_module: Backend = get_backend(backend)

        extra_props = {dtype: dtype for dtype in PROP_DTYPES}
        if backend != "spatial-graph":
            extra_props["str"] = "str"

        store, memory_geff = create_mock_geff(
            node_id_dtype,
            AXIS_DTYPES,
            extra_node_props=extra_props,
            extra_edge_props=extra_props,
            directed=directed,
            include_t=include_t,
            include_x=include_spatial,
            include_y=include_spatial,
            include_z=include_spatial,
            include_varlength=backend != "spatial-graph",
            include_missing=backend != "spatial-graph",
        )

        # this will create a graph instance of the backend type
        original_graph = backend_module.construct(**memory_geff)

        # Add extra values to metadata
        metadata = memory_geff["metadata"]
        metadata.extra = {"foo": "bar", "bar": {"baz": "qux"}}

        # write with unified write function
        path_store = tmp_path / "test_path.zarr"
        write(original_graph, path_store, memory_geff["metadata"])

        # read with the NxBackend to see if the graph is the same
        graph, metadata = NxBackend.read(path_store)
        graph_adapter = NxBackend.graph_adapter(graph)

        _assert_graph_equal_to_geff(graph_adapter, memory_geff)
        assert metadata.extra["foo"] == "bar"
        assert metadata.extra["bar"]["baz"] == "qux"


@pytest.mark.parametrize("backend", get_args(SupportedBackend))
class Test_api_wrapper_simple:  # tests that only need backend parametrization
    def test_write_axis_lists_override_metadata(self, tmp_path, backend):
        backend_module: Backend = get_backend(backend)
        store, memory_geff = create_simple_3d_geff()

        # this will create a graph instance of the backend type
        original_graph = backend_module.construct(**memory_geff)

        # write with unified write function
        path_store = tmp_path / "test_path.zarr"
        axis_names = ["x", "y"]
        axis_units = ["meter", "meter"]
        axis_types = ["space", "space"]
        if backend == "spatial-graph":
            # Cannot change the number of axes in sg graph without modifying position attribute
            with pytest.raises(
                ValueError,
                match="Cannot write a SpatialGraph with ndims .* "
                "and a different number of axes (.*)",
            ):
                backend_module.write(
                    original_graph,
                    path_store,
                    metadata=memory_geff["metadata"],
                    axis_names=axis_names,
                    axis_units=axis_units,
                    axis_types=axis_types,
                )
        else:
            backend_module.write(
                original_graph,
                path_store,
                metadata=memory_geff["metadata"],
                axis_names=axis_names,
                axis_units=axis_units,
                axis_types=axis_types,
            )

            new_mem_geff = read_to_memory(path_store)
            metadata = new_mem_geff["metadata"]
            assert metadata.axes is not None
            assert len(metadata.axes) == 2
            assert axis_names == [axis.name for axis in metadata.axes]
            assert axis_units == [axis.unit for axis in metadata.axes]
            assert axis_types == [axis.type for axis in metadata.axes]

    def test_write_read_different_stores(self, tmp_path, backend):
        stores = [
            tmp_path / "test_path.zarr",  # Path object
            str(tmp_path / "test_string.zarr"),  # string path
            zarr.storage.MemoryStore(),
        ]

        backend_module: Backend = get_backend(backend)
        _, memory_geff = create_simple_3d_geff()

        # this will create a graph instance of the backend type
        original_graph = backend_module.construct(**memory_geff)
        adpt_og_graph = backend_module.graph_adapter(original_graph)

        # Write to store type
        for store in stores:
            backend_module.write(original_graph, store, memory_geff["metadata"])
            new_graph = backend_module.graph_adapter(backend_module.read(store)[0])
            assert adpt_og_graph.get_node_ids() == new_graph.get_node_ids()
            assert adpt_og_graph.get_edge_ids() == new_graph.get_edge_ids()


@pytest.mark.parametrize("backend", get_args(SupportedBackend))
class Test_empty_graph:
    def test_read(self, backend):
        backend_module: Backend = get_backend(backend)

        store, memory_geff = create_empty_geff()

        graph, metadata = read(store, backend=backend)
        graph_adapter = backend_module.graph_adapter(graph)

        _assert_graph_equal_to_geff(graph_adapter, memory_geff)

    def test_construct(self, backend):
        backend_module: Backend = get_backend(backend)

        store, memory_geff = create_empty_geff()

        in_memory_geff = read_to_memory(store)
        graph = construct(**in_memory_geff, backend=backend)
        graph_adapter = backend_module.graph_adapter(graph)

        _assert_graph_equal_to_geff(graph_adapter, memory_geff)

    def test_write(self, tmp_path, backend):
        if backend == "networkx":
            original_graph = nx.Graph()
        elif backend == "rustworkx":
            original_graph = rx.PyGraph()
        elif backend == "spatial-graph":
            create_graph = getattr(sg, "create_graph", sg.SpatialGraph)
            original_graph = create_graph(
                ndims=1,
                node_dtype="uint64",
                node_attr_dtypes={"pos": "float32[1]"},
                edge_attr_dtypes={},
                position_attr="pos",
            )
        else:
            raise NotImplementedError(
                f"Backend {backend} not tested in Test_empty_graph.test_write"
            )

        # write with unified write function
        path_store = tmp_path / "test_path.zarr"
        write(original_graph, path_store)

        # check that graph is empty after loading to in memory geff
        mem_geff = read_to_memory(path_store)
        assert len(mem_geff["node_ids"]) == 0
        assert len(mem_geff["edge_ids"]) == 0
        assert mem_geff["node_props"] == {}
        assert mem_geff["edge_props"] == {}
