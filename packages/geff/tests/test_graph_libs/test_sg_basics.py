import numpy as np
import pytest
import zarr
import zarr.storage

from geff import _path
from geff.testing.data import create_mock_geff
from geff.validate.structure import validate_structure

sg = pytest.importorskip("spatial_graph")
from geff._graph_libs._spatial_graph import SgBackend  # noqa: E402

node_dtypes = ["uint8", "uint16"]
node_attr_dtypes = [
    {"position": "double", "time": "double"},
    {"position": "int", "time": "int"},
]
extra_edge_props = [
    {"score": "float64", "color": "uint8"},
    {"score": "float32", "color": "int16"},
]


@pytest.mark.parametrize("node_dtype", node_dtypes)
@pytest.mark.parametrize("node_attr_dtypes", node_attr_dtypes)
@pytest.mark.parametrize("extra_edge_props", extra_edge_props)
@pytest.mark.parametrize("directed", [True, False])
def test_read_write_consistency(
    node_dtype,
    node_attr_dtypes,
    extra_edge_props,
    directed,
) -> None:
    store, memory_geff = create_mock_geff(
        node_id_dtype=node_dtype,
        node_axis_dtypes=node_attr_dtypes,
        extra_edge_props=extra_edge_props,
        directed=directed,
    )
    # with pytest.warns(UserWarning, match="Potential missing values for attr"):
    # TODO: make sure test data has missing values, otherwise this warning will
    # not be triggered
    graph, _ = SgBackend.read(store, position_attr="pos")

    np.testing.assert_array_equal(np.sort(graph.nodes), np.sort(memory_geff["node_ids"]))
    np.testing.assert_array_equal(np.sort(graph.edges), np.sort(memory_geff["edge_ids"]))

    for idx, node in enumerate(memory_geff["node_ids"]):
        np.testing.assert_array_equal(
            graph.node_attrs[node].pos,
            np.array([memory_geff["node_props"][d]["values"][idx] for d in ["t", "z", "y", "x"]]),
        )

    for idx, edge in enumerate(memory_geff["edge_ids"]):
        for name, data in memory_geff["edge_props"].items():
            assert getattr(graph.edge_attrs[edge], name) == data["values"][idx].item()


def test_write_empty_graph() -> None:
    create_graph = getattr(sg, "create_graph", sg.SpatialGraph)
    graph = create_graph(
        ndims=3,
        node_dtype="uint64",
        node_attr_dtypes={"pos": "float32[3]"},
        edge_attr_dtypes={},
        position_attr="pos",
    )

    store = zarr.storage.MemoryStore()
    SgBackend.write(graph, store=store, axis_names=[])
    validate_structure(store)

    z = zarr.open(store)
    assert z[_path.NODE_IDS].shape[0] == 0
