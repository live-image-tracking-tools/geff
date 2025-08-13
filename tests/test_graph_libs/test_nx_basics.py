import networkx as nx
import numpy as np
import pytest
import zarr

import geff
from geff.metadata._schema import GeffMetadata, _axes_from_lists
from geff.testing.data import create_memory_mock_geff

node_id_dtypes = ["int8", "uint8", "int16", "uint16"]
node_axis_dtypes = [
    {"position": "double", "time": "double"},
    {"position": "int", "time": "int"},
]
extra_edge_props = [
    {"score": "float64", "color": "uint8"},
    {"score": "float32", "color": "int16"},
]

# TODO: mixed dtypes?


@pytest.mark.parametrize("node_id_dtype", node_id_dtypes)
@pytest.mark.parametrize("node_axis_dtypes", node_axis_dtypes)
@pytest.mark.parametrize("extra_edge_props", extra_edge_props)
@pytest.mark.parametrize("directed", [True, False])
@pytest.mark.parametrize("include_t", [True, False])
@pytest.mark.parametrize("include_z", [True, False])
def test_read_write_consistency(
    tmp_path,
    node_id_dtype,
    node_axis_dtypes,
    extra_edge_props,
    directed,
    include_t,
    include_z,
) -> None:
    store, graph_props = create_memory_mock_geff(
        node_id_dtype,
        node_axis_dtypes,
        extra_edge_props=extra_edge_props,
        directed=directed,
        include_t=include_t,
        include_z=include_z,
    )

    graph, _ = geff.read_nx(store)

    # Check that in memory representation is consistent with what we expected to have from fixture
    assert set(graph.nodes) == {*graph_props["nodes"].tolist()}
    assert set(graph.edges) == {*[tuple(edges) for edges in graph_props["edges"].tolist()]}
    for idx, node in enumerate(graph_props["nodes"]):
        if include_t and len(graph_props["t"]) > 0:
            np.testing.assert_array_equal(graph.nodes[node.item()]["t"], graph_props["t"][idx])
        if include_z and len(graph_props["z"]) > 0:
            np.testing.assert_array_equal(graph.nodes[node.item()]["z"], graph_props["z"][idx])
        # TODO: test other dimensions

    for idx, edge in enumerate(graph_props["edges"]):
        for name, values in graph_props["extra_edge_props"].items():
            assert graph.edges[edge.tolist()][name] == values[idx].item()

    # TODO: test metadata
    # assert graph.graph["axis_names"] == graph_props["axis_names"]
    # assert graph.graph["axis_units"] == graph_props["axis_units"]


@pytest.mark.parametrize("node_id_dtype", node_id_dtypes)
@pytest.mark.parametrize("node_axis_dtypes", node_axis_dtypes)
@pytest.mark.parametrize("extra_edge_props", extra_edge_props)
@pytest.mark.parametrize("directed", [True, False])
def test_read_write_no_spatial(
    tmp_path, node_id_dtype, node_axis_dtypes, extra_edge_props, directed
) -> None:
    graph = nx.DiGraph() if directed else nx.Graph()

    nodes = np.array([10, 2, 127, 4, 5], dtype=node_id_dtype)
    props = np.array([4, 9, 10, 2, 8], dtype=node_axis_dtypes["position"])
    for node, pos in zip(nodes, props, strict=False):
        graph.add_node(node.item(), attr=pos)

    edges = np.array(
        [
            [10, 2],
            [2, 127],
            [2, 4],
            [4, 5],
        ],
        dtype=node_id_dtype,
    )
    scores = np.array([0.1, 0.2, 0.3, 0.4], dtype=extra_edge_props["score"])
    colors = np.array([1, 2, 3, 4], dtype=extra_edge_props["color"])
    for edge, score, color in zip(edges, scores, colors, strict=False):
        graph.add_edge(*edge.tolist(), score=score.item(), color=color.item())

    path = tmp_path / "rw_consistency.zarr/graph"

    geff.write_nx(graph, path, axis_names=[])

    compare, _ = geff.read_nx(path)

    assert set(graph.nodes) == set(compare.nodes)
    assert set(graph.edges) == set(compare.edges)
    for node in nodes.tolist():
        assert graph.nodes[node]["attr"] == compare.nodes[node]["attr"]

    for edge in edges:
        assert graph.edges[edge.tolist()]["score"] == compare.edges[edge.tolist()]["score"]
        assert graph.edges[edge.tolist()]["color"] == compare.edges[edge.tolist()]["color"]


def test_write_empty_graph(tmp_path) -> None:
    graph = nx.DiGraph()
    geff.write_nx(graph, axis_names=["t", "y", "x"], store=tmp_path / "empty.zarr")


def test_write_nx_with_metadata(tmp_path) -> None:
    """Test write_nx with explicit metadata parameter"""

    graph = nx.Graph()
    graph.add_node(1, x=1.0, y=2.0)
    graph.add_node(2, x=3.0, y=4.0)
    graph.add_edge(1, 2, weight=0.5)

    # Create metadata object
    axes = _axes_from_lists(
        axis_names=["x", "y"],
        axis_units=["micrometer", "micrometer"],
        axis_types=["space", "space"],
        roi_min=(1.0, 2.0),
        roi_max=(3.0, 4.0),
    )
    metadata = GeffMetadata(geff_version="0.3.0", directed=False, axes=axes)

    path = tmp_path / "metadata_test.zarr"
    geff.write_nx(graph, path, metadata=metadata)

    # Read it back and verify metadata is preserved
    _, read_metadata = geff.read_nx(path)

    assert not read_metadata.directed
    assert len(read_metadata.axes) == 2
    assert read_metadata.axes[0].name == "x"
    assert read_metadata.axes[1].name == "y"
    assert read_metadata.axes[0].unit == "micrometer"
    assert read_metadata.axes[1].unit == "micrometer"
    assert read_metadata.axes[0].type == "space"
    assert read_metadata.axes[1].type == "space"
    assert read_metadata.axes[0].min == 1.0 and read_metadata.axes[0].max == 3.0
    assert read_metadata.axes[1].min == 2.0 and read_metadata.axes[1].max == 4.0


def test_write_nx_metadata_extra_properties(tmp_path) -> None:
    graph = nx.Graph()
    graph.add_node(1, x=1.0, y=2.0)
    graph.add_node(2, x=3.0, y=4.0)
    graph.add_edge(1, 2, weight=0.5)

    axes = _axes_from_lists(
        axis_names=["x", "y"],
        axis_units=["micrometer", "micrometer"],
        axis_types=["space", "space"],
    )
    metadata = GeffMetadata(
        geff_version="0.3.0",
        directed=False,
        axes=axes,
        extra={"foo": "bar", "bar": {"baz": "qux"}},
    )
    path = tmp_path / "extra_properties_test.zarr"

    geff.write_nx(graph, path, metadata=metadata)
    _, compare = geff.read_nx(path)
    assert compare.extra["foo"] == "bar"
    assert compare.extra["bar"]["baz"] == "qux"


def test_write_nx_metadata_override_precedence(tmp_path) -> None:
    """Test that explicit axis parameters override metadata"""
    graph = nx.Graph()
    graph.add_node(1, x=1.0, y=2.0, z=3.0)
    graph.add_node(2, x=4.0, y=5.0, z=6.0)

    # Create metadata with one set of axes
    axes = _axes_from_lists(
        axis_names=["x", "y"],
        axis_units=["micrometer", "micrometer"],
        axis_types=["space", "space"],
    )
    metadata = GeffMetadata(geff_version="0.3.0", directed=False, axes=axes)

    path = tmp_path / "override_test.zarr"

    # Should log warning when both metadata and axis lists are provided
    with pytest.warns(UserWarning):
        geff.write_nx(
            graph,
            store=path,
            metadata=metadata,
            axis_names=["x", "y", "z"],  # Override with different axes
            axis_units=["meter", "meter", "meter"],
            axis_types=["space", "space", "space"],
        )

    # Verify that axis lists took precedence
    _, read_metadata = geff.read_nx(path)
    assert len(read_metadata.axes) == 3
    axis_names = [axis.name for axis in read_metadata.axes]
    axis_units = [axis.unit for axis in read_metadata.axes]
    axis_types = [axis.type for axis in read_metadata.axes]
    assert axis_names == ["x", "y", "z"]
    assert axis_units == ["meter", "meter", "meter"]
    assert axis_types == ["space", "space", "space"]


def test_write_nx_different_store_types(tmp_path) -> None:
    """Test write_nx with different store types: path, string, and zarr.store"""

    # Create a simple test graph
    graph = nx.Graph()
    graph.add_node(1, x=1.0, y=2.0)
    graph.add_node(2, x=3.0, y=4.0)
    graph.add_edge(1, 2, weight=0.5)

    # Test 1: Path object
    path_store = tmp_path / "test_path.zarr"
    geff.write_nx(graph, path_store, axis_names=["x", "y"])

    # Verify it was written correctly
    graph_read, _ = geff.read_nx(path_store)
    assert len(graph_read.nodes) == 2
    assert len(graph_read.edges) == 1
    assert (1, 2) in graph_read.edges

    # Test 2: String path
    string_store = str(tmp_path / "test_string.zarr")
    geff.write_nx(graph, string_store, axis_names=["x", "y"])

    # Verify it was written correctly
    graph_read, _ = geff.read_nx(string_store)
    assert len(graph_read.nodes) == 2
    assert len(graph_read.edges) == 1
    assert (1, 2) in graph_read.edges

    # Test 3: Zarr MemoryStore
    memory_store = zarr.storage.MemoryStore()
    geff.write_nx(graph, memory_store, axis_names=["x", "y"])

    # Verify it was written correctly
    graph_read, _ = geff.read_nx(memory_store)
    assert len(graph_read.nodes) == 2
    assert len(graph_read.edges) == 1
    assert (1, 2) in graph_read.edges
