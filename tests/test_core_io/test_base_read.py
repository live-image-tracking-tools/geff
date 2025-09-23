import numpy as np
import pytest

from geff import GeffReader
from geff._graph_libs._networkx import NxBackend
from geff.core_io._base_read import read_to_memory
from geff.testing.data import create_mock_geff, create_simple_2d_geff
from geff.validate.data import ValidationConfig

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
def test_build_w_masked_nodes(
    node_id_dtype,
    node_axis_dtypes,
    extra_edge_props,
    directed,
) -> None:
    store, memory_geff = create_mock_geff(
        node_id_dtype=node_id_dtype,
        node_axis_dtypes=node_axis_dtypes,
        extra_edge_props=extra_edge_props,
        directed=directed,
    )

    file_reader = GeffReader(store)

    n_nodes = file_reader.nodes.shape[0]
    node_mask = np.zeros(n_nodes, dtype=bool)
    node_mask[: n_nodes // 2] = True  # mask half the nodes

    in_memory_geff = file_reader.build(node_mask=node_mask)

    # make sure nodes and edges are masked as expected
    np.testing.assert_array_equal(memory_geff["node_ids"][node_mask], in_memory_geff["node_ids"])

    # assert no edges that reference non existing nodes
    assert np.isin(in_memory_geff["node_ids"], in_memory_geff["edge_ids"]).all()

    # make sure graph dict can be ingested
    _ = NxBackend.construct(**in_memory_geff)


def test_load_prop_into_memory() -> None:
    store, memory_geff = create_mock_geff(
        node_id_dtype="uint8",
        node_axis_dtypes={"position": "double", "time": "uint8"},
        extra_edge_props={"score": "float64", "color": "str"},
        directed=True,
        include_varlength=True,
    )

    reader = GeffReader(store)
    for node_prop in ["z", "t", "var_length"]:
        zarr_prop = reader._read_prop(node_prop, prop_type="node")
        loaded_prop = reader._load_prop_to_memory(
            zarr_prop, mask=None, prop_metadata=reader.metadata.node_props_metadata[node_prop]
        )
        actual_values = loaded_prop["values"]
        actual_missing = loaded_prop["missing"]

        expected_values = memory_geff["node_props"][node_prop]["values"]
        expected_missing = memory_geff["node_props"][node_prop]["missing"]
        if node_prop == "var_length":
            for expected, actual in zip(expected_values, actual_values, strict=True):
                np.testing.assert_array_equal(expected, actual)
        else:
            np.testing.assert_array_equal(expected_values, actual_values)
        np.testing.assert_array_equal(expected_missing, actual_missing)

    for edge_prop in ["score", "color"]:
        zarr_prop = reader._read_prop(edge_prop, prop_type="edge")
        loaded_prop = reader._load_prop_to_memory(
            zarr_prop, mask=None, prop_metadata=reader.metadata.edge_props_metadata[edge_prop]
        )
        actual_values = loaded_prop["values"]
        actual_missing = loaded_prop["missing"]

        expected_values = memory_geff["edge_props"][edge_prop]["values"]
        expected_missing = memory_geff["edge_props"][edge_prop]["missing"]
        np.testing.assert_array_equal(expected_values, actual_values)
        np.testing.assert_array_equal(expected_missing, actual_missing)


@pytest.mark.parametrize("node_id_dtype", node_id_dtypes)
@pytest.mark.parametrize("node_axis_dtypes", node_axis_dtypes)
@pytest.mark.parametrize("extra_edge_props", extra_edge_props)
@pytest.mark.parametrize("directed", [True, False])
def test_build_w_masked_edges(
    node_id_dtype,
    node_axis_dtypes,
    extra_edge_props,
    directed,
) -> None:
    store, memory_geff = create_mock_geff(
        node_id_dtype=node_id_dtype,
        node_axis_dtypes=node_axis_dtypes,
        extra_edge_props=extra_edge_props,
        directed=directed,
    )
    file_reader = GeffReader(store)

    n_edges = file_reader.edges.shape[0]
    edge_mask = np.zeros(n_edges, dtype=bool)
    edge_mask[: n_edges // 2] = True  # mask half the edges

    in_memory_geff = file_reader.build(edge_mask=edge_mask)

    np.testing.assert_array_equal(memory_geff["edge_ids"][edge_mask], in_memory_geff["edge_ids"])

    # make sure graph dict can be ingested
    _ = NxBackend.construct(**in_memory_geff)


@pytest.mark.parametrize("node_id_dtype", node_id_dtypes)
@pytest.mark.parametrize("node_axis_dtypes", node_axis_dtypes)
@pytest.mark.parametrize("extra_edge_props", extra_edge_props)
@pytest.mark.parametrize("directed", [True, False])
def test_build_w_masked_nodes_edges(
    node_id_dtype,
    node_axis_dtypes,
    extra_edge_props,
    directed,
) -> None:
    store, memory_geff = create_mock_geff(
        node_id_dtype=node_id_dtype,
        node_axis_dtypes=node_axis_dtypes,
        extra_edge_props=extra_edge_props,
        directed=directed,
    )
    file_reader = GeffReader(store)

    n_nodes = file_reader.nodes.shape[0]
    node_mask = np.zeros(n_nodes, dtype=bool)
    node_mask[: n_nodes // 2] = True  # mask half the nodes

    n_edges = file_reader.edges.shape[0]
    edge_mask = np.zeros(n_edges, dtype=bool)
    edge_mask[: n_edges // 2] = True  # mask half the edges

    in_memory_geff = file_reader.build(node_mask=node_mask, edge_mask=edge_mask)

    # make sure nodes and edges are masked as expected
    np.testing.assert_array_equal(memory_geff["node_ids"][node_mask], in_memory_geff["node_ids"])

    # assert no edges that reference non existing nodes
    assert np.isin(in_memory_geff["node_ids"], in_memory_geff["edge_ids"]).all()

    # assert all the output edges are in the naively masked edges
    output_edges = in_memory_geff["edge_ids"]
    masked_edges = memory_geff["edge_ids"][edge_mask]
    # Adding a new axis allows comparing each element
    assert (output_edges[:, :, np.newaxis] == masked_edges).all(axis=1).any(axis=1).all()

    # make sure graph dict can be ingested
    _ = NxBackend.construct(**in_memory_geff)


def test_read_node_props() -> None:
    store, memory_geff = create_mock_geff(
        node_id_dtype="uint8",
        node_axis_dtypes={"position": "double", "time": "double"},
        extra_edge_props={"score": "float64", "color": "uint8"},
        directed=True,
        include_varlength=True,
    )

    file_reader = GeffReader(store)

    # make sure the node props are also masked
    n_nodes = file_reader.nodes.shape[0]
    node_mask = np.zeros(n_nodes, dtype=bool)
    node_mask[: n_nodes // 2] = True  # mask half the nodes

    in_memory_geff = file_reader.build(node_mask=node_mask)
    assert len(in_memory_geff["node_props"]) == 0

    file_reader.read_node_props(["t"])
    in_memory_geff = file_reader.build(node_mask=node_mask)
    assert "t" in in_memory_geff["node_props"]
    np.testing.assert_allclose(
        memory_geff["node_props"]["t"]["values"][node_mask],
        in_memory_geff["node_props"]["t"]["values"],
    )

    _ = NxBackend.construct(**in_memory_geff)


def test_read_edge_props() -> None:
    store, memory_geff = create_mock_geff(
        node_id_dtype="uint8",
        node_axis_dtypes={"position": "double", "time": "double"},
        extra_edge_props={"score": "float64", "color": "uint8"},
        directed=True,
    )

    file_reader = GeffReader(store)

    # make sure props are also masked
    n_edges = file_reader.edges.shape[0]
    edge_mask = np.zeros(n_edges, dtype=bool)
    edge_mask[: n_edges // 2] = True  # mask half the edges

    in_memory_geff = file_reader.build(edge_mask=edge_mask)
    assert len(in_memory_geff["edge_props"]) == 0

    file_reader.read_edge_props(["score"])
    in_memory_geff = file_reader.build(edge_mask=edge_mask)
    np.testing.assert_allclose(
        memory_geff["edge_props"]["score"]["values"][edge_mask],
        in_memory_geff["edge_props"]["score"]["values"],
    )

    _ = NxBackend.construct(**in_memory_geff)


def test_read_to_memory():
    # Mostly testing that conditionals run correctly since functionality is tested elsewhere
    store, attrs = create_simple_2d_geff()

    read_to_memory(store, structure_validation=True, data_validation=ValidationConfig())
