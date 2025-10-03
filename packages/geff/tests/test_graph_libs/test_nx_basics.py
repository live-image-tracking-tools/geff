import networkx as nx
import numpy as np
import pytest
import zarr

from geff._graph_libs._networkx import NxBackend
from geff.testing.data import create_mock_geff
from geff_spec import GeffMetadata
from geff_spec.utils import axes_from_lists

node_id_dtypes = ["uint8", "uint16"]
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
def test_read_consistency(
    tmp_path,
    node_id_dtype,
    node_axis_dtypes,
    extra_edge_props,
    directed,
    include_t,
    include_z,
) -> None:
    store, memory_geff = create_mock_geff(
        node_id_dtype,
        node_axis_dtypes,
        extra_edge_props=extra_edge_props,
        directed=directed,
        include_t=include_t,
        include_z=include_z,
    )

    graph, _ = NxBackend.read(store)

    # Check that in memory representation is consistent with what we expected to have from fixture
    assert set(graph.nodes) == {*memory_geff["node_ids"].tolist()}
    assert set(graph.edges) == {*[tuple(edges) for edges in memory_geff["edge_ids"].tolist()]}
    for idx, node in enumerate(memory_geff["node_ids"]):
        if include_t and len(memory_geff["node_props"]["t"]["values"]) > 0:
            np.testing.assert_array_equal(
                graph.nodes[node.item()]["t"], memory_geff["node_props"]["t"]["values"][idx]
            )
        if include_z and len(memory_geff["node_props"]["z"]["values"]) > 0:
            np.testing.assert_array_equal(
                graph.nodes[node.item()]["z"], memory_geff["node_props"]["z"]["values"][idx]
            )
        # TODO: test other dimensions

    for idx, edge in enumerate(memory_geff["edge_ids"]):
        for name, data in memory_geff["edge_props"].items():
            values = data["values"]
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

    NxBackend.write(graph, path, axis_names=[])

    compare, _ = NxBackend.read(path)

    assert set(graph.nodes) == set(compare.nodes)
    assert set(graph.edges) == set(compare.edges)
    for node in nodes.tolist():
        assert graph.nodes[node]["attr"] == compare.nodes[node]["attr"]

    for edge in edges:
        assert graph.edges[edge.tolist()]["score"] == compare.edges[edge.tolist()]["score"]
        assert graph.edges[edge.tolist()]["color"] == compare.edges[edge.tolist()]["color"]


def test_write_empty_graph(tmp_path) -> None:
    graph = nx.DiGraph()
    NxBackend.write(graph, store=tmp_path / "empty.zarr")


def test_write_nx_with_metadata(tmp_path) -> None:
    """Test write_nx with explicit metadata parameter"""

    graph = nx.Graph()
    graph.add_node(1, x=1.0, y=2.0)
    graph.add_node(2, x=3.0, y=4.0)
    graph.add_edge(1, 2, weight=0.5)

    # Create metadata object
    axes = axes_from_lists(
        axis_names=["x", "y"],
        axis_units=["micrometer", "micrometer"],
        axis_types=["space", "space"],
        roi_min=(1.0, 2.0),
        roi_max=(3.0, 4.0),
    )
    metadata = GeffMetadata(
        geff_version="0.3.0",
        directed=False,
        axes=axes,
        node_props_metadata={},
        edge_props_metadata={},
    )

    path = tmp_path / "metadata_test.zarr"
    NxBackend.write(graph, path, metadata=metadata)

    # Read it back and verify metadata is preserved
    _, read_metadata = NxBackend.read(path)

    assert not read_metadata.directed
    assert read_metadata.axes is not None
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

    axes = axes_from_lists(
        axis_names=["x", "y"],
        axis_units=["micrometer", "micrometer"],
        axis_types=["space", "space"],
    )
    metadata = GeffMetadata(
        geff_version="0.3.0",
        directed=False,
        axes=axes,
        extra={"foo": "bar", "bar": {"baz": "qux"}},
        node_props_metadata={},
        edge_props_metadata={},
    )
    path = tmp_path / "extra_properties_test.zarr"

    NxBackend.write(graph, path, metadata=metadata)
    _, compare = NxBackend.read(path)
    assert compare.extra["foo"] == "bar"
    assert compare.extra["bar"]["baz"] == "qux"


def test_write_nx_metadata_override_precedence(tmp_path) -> None:
    """Test that explicit axis parameters override metadata"""
    graph = nx.Graph()
    graph.add_node(1, x=1.0, y=2.0, z=3.0)
    graph.add_node(2, x=4.0, y=5.0, z=6.0)

    # Create metadata with one set of axes
    axes = axes_from_lists(
        axis_names=["x", "y"],
        axis_units=["micrometer", "micrometer"],
        axis_types=["space", "space"],
    )
    metadata = GeffMetadata(
        geff_version="0.3.0",
        directed=False,
        axes=axes,
        node_props_metadata={},
        edge_props_metadata={},
    )

    path = tmp_path / "override_test.zarr"

    NxBackend.write(
        graph,
        store=path,
        metadata=metadata,
        axis_names=["x", "y", "z"],  # Override with different axes
        axis_units=["meter", "meter", "meter"],
        axis_types=["space", "space", "space"],
    )

    # Verify that axis lists took precedence
    _, read_metadata = NxBackend.read(path)
    assert read_metadata.axes is not None
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
    NxBackend.write(graph, path_store, axis_names=["x", "y"])

    # Verify it was written correctly
    graph_read, _ = NxBackend.read(path_store)
    assert len(graph_read.nodes) == 2
    assert len(graph_read.edges) == 1
    assert (1, 2) in graph_read.edges

    # Test 2: String path
    string_store = str(tmp_path / "test_string.zarr")
    NxBackend.write(graph, string_store, axis_names=["x", "y"])

    # Verify it was written correctly
    graph_read, _ = NxBackend.read(string_store)
    assert len(graph_read.nodes) == 2
    assert len(graph_read.edges) == 1
    assert (1, 2) in graph_read.edges

    # Test 3: Zarr MemoryStore
    memory_store = zarr.storage.MemoryStore()
    NxBackend.write(graph, memory_store, axis_names=["x", "y"])

    # Verify it was written correctly
    graph_read, _ = NxBackend.read(memory_store)
    assert len(graph_read.nodes) == 2
    assert len(graph_read.edges) == 1
    assert (1, 2) in graph_read.edges
