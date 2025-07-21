import numpy as np
import pytest

from geff.geff_reader import GeffReader
from geff.networkx.io import _ingest_dict_nx
from geff.testing.data import create_memory_mock_geff

node_id_dtypes = ["int8", "uint8", "int16", "uint16"]
node_prop_dtypes = [
    {"position": "double", "time": "double"},
    {"position": "int", "time": "int"},
]
edge_prop_dtypes = [
    {"score": "float64", "color": "uint8"},
    {"score": "float32", "color": "int16"},
]


@pytest.mark.parametrize("node_id_dtype", node_id_dtypes)
@pytest.mark.parametrize("node_prop_dtypes", node_prop_dtypes)
@pytest.mark.parametrize("edge_prop_dtypes", edge_prop_dtypes)
@pytest.mark.parametrize("directed", [True, False])
def test_build_w_masked_nodes(
    node_id_dtype,
    node_prop_dtypes,
    edge_prop_dtypes,
    directed,
):
    store, graph_props = create_memory_mock_geff(
        node_id_dtype, node_prop_dtypes, edge_prop_dtypes, directed
    )

    file_reader = GeffReader(store)

    n_nodes = file_reader.nodes.shape[0]
    node_mask = np.zeros(n_nodes, dtype=bool)
    node_mask[: n_nodes // 2] = True  # mask half the nodes

    graph_dict = file_reader.build(node_mask=node_mask)

    # make sure nodes and edges are masked as expected
    np.testing.assert_array_equal(graph_props["nodes"][node_mask], graph_dict["nodes"])

    # assert no edges that reference non existing nodes
    assert np.isin(graph_dict["nodes"], graph_dict["edges"]).all()

    # make sure graph dict can be ingested
    _ = _ingest_dict_nx(graph_dict)


@pytest.mark.parametrize("node_id_dtype", node_id_dtypes)
@pytest.mark.parametrize("node_prop_dtypes", node_prop_dtypes)
@pytest.mark.parametrize("edge_prop_dtypes", edge_prop_dtypes)
@pytest.mark.parametrize("directed", [True, False])
def test_build_w_masked_edges(
    node_id_dtype,
    node_prop_dtypes,
    edge_prop_dtypes,
    directed,
):
    store, graph_props = create_memory_mock_geff(
        node_id_dtype, node_prop_dtypes, edge_prop_dtypes, directed
    )
    file_reader = GeffReader(store)

    n_edges = file_reader.edges.shape[0]
    edge_mask = np.zeros(n_edges, dtype=bool)
    edge_mask[: n_edges // 2] = True  # mask half the edges

    graph_dict = file_reader.build(edge_mask=edge_mask)

    np.testing.assert_array_equal(graph_props["edges"][edge_mask], graph_dict["edges"])

    # make sure graph dict can be ingested
    _ = _ingest_dict_nx(graph_dict)


@pytest.mark.parametrize("node_id_dtype", node_id_dtypes)
@pytest.mark.parametrize("node_prop_dtypes", node_prop_dtypes)
@pytest.mark.parametrize("edge_prop_dtypes", edge_prop_dtypes)
@pytest.mark.parametrize("directed", [True, False])
def test_build_w_masked_nodes_edges(
    node_id_dtype,
    node_prop_dtypes,
    edge_prop_dtypes,
    directed,
):
    store, graph_props = create_memory_mock_geff(
        node_id_dtype, node_prop_dtypes, edge_prop_dtypes, directed
    )
    file_reader = GeffReader(store)

    n_nodes = file_reader.nodes.shape[0]
    node_mask = np.zeros(n_nodes, dtype=bool)
    node_mask[: n_nodes // 2] = True  # mask half the nodes

    n_edges = file_reader.edges.shape[0]
    edge_mask = np.zeros(n_edges, dtype=bool)
    edge_mask[: n_edges // 2] = True  # mask half the edges

    graph_dict = file_reader.build(node_mask=node_mask, edge_mask=edge_mask)

    # make sure nodes and edges are masked as expected
    np.testing.assert_array_equal(graph_props["nodes"][node_mask], graph_dict["nodes"])

    # assert no edges that reference non existing nodes
    assert np.isin(graph_dict["nodes"], graph_dict["edges"]).all()

    # assert all the output edges are in the naively masked edges
    output_edges = graph_dict["edges"]
    masked_edges = graph_props["edges"][edge_mask]
    # Adding a new axis allows comparing each element
    assert (output_edges[:, :, np.newaxis] == masked_edges).all(axis=1).any(axis=1).all()

    # make sure graph dict can be ingested
    _ = _ingest_dict_nx(graph_dict)


def test_read_node_props():
    store, graph_props = create_memory_mock_geff(
        node_id_dtype="uint8",
        node_prop_dtypes={"position": "double", "time": "double"},
        edge_prop_dtypes={"score": "float64", "color": "uint8"},
        directed=True,
    )

    file_reader = GeffReader(store)

    # make sure the node props are also masked
    n_nodes = file_reader.nodes.shape[0]
    node_mask = np.zeros(n_nodes, dtype=bool)
    node_mask[: n_nodes // 2] = True  # mask half the nodes

    graph_dict = file_reader.build(node_mask=node_mask)
    assert len(graph_dict["node_props"]) == 0

    file_reader.read_node_props("t")
    graph_dict = file_reader.build(node_mask=node_mask)
    assert "t" in graph_dict["node_props"]
    np.testing.assert_allclose(
        graph_props["t"][node_mask],
        graph_dict["node_props"]["t"]["values"],
    )

    _ = _ingest_dict_nx(graph_dict)


def test_read_edge_props():
    store, graph_props = create_memory_mock_geff(
        node_id_dtype="uint8",
        node_prop_dtypes={"position": "double", "time": "double"},
        edge_prop_dtypes={"score": "float64", "color": "uint8"},
        directed=True,
    )

    file_reader = GeffReader(store)

    # make sure props are also masked
    n_edges = file_reader.edges.shape[0]
    edge_mask = np.zeros(n_edges, dtype=bool)
    edge_mask[: n_edges // 2] = True  # mask half the edges

    graph_dict = file_reader.build(edge_mask=edge_mask)
    assert len(graph_dict["edge_props"]) == 0

    file_reader.read_edge_props(["score"])
    graph_dict = file_reader.build(edge_mask=edge_mask)
    np.testing.assert_allclose(
        graph_props["edge_props"]["score"][edge_mask],
        graph_dict["edge_props"]["score"]["values"],
    )

    _ = _ingest_dict_nx(graph_dict)
