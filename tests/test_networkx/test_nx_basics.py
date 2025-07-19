import networkx as nx
import numpy as np
import pytest

import geff

node_dtypes = ["int8", "uint8", "int16", "uint16", "str"]
node_prop_dtypes = [
    {"position": "double"},
    {"position": "int"},
]
edge_prop_dtypes = [
    {"score": "float64", "color": "uint8"},
    {"score": "float32", "color": "int16"},
]

# TODO: mixed dtypes?


@pytest.mark.parametrize("node_dtype", node_dtypes)
@pytest.mark.parametrize("node_prop_dtypes", node_prop_dtypes)
@pytest.mark.parametrize("edge_prop_dtypes", edge_prop_dtypes)
@pytest.mark.parametrize("directed", [True, False])
def test_read_write_consistency(
    path_w_expected_graph_props,
    node_dtype,
    node_prop_dtypes,
    edge_prop_dtypes,
    directed,
):
    path, graph_props = path_w_expected_graph_props(
        node_dtype, node_prop_dtypes, edge_prop_dtypes, directed
    )

    graph, metadata = geff.read_nx(path)

    assert set(graph.nodes) == {*graph_props["nodes"].tolist()}
    assert set(graph.edges) == {*[tuple(edges) for edges in graph_props["edges"].tolist()]}
    for idx, node in enumerate(graph_props["nodes"]):
        # TODO: test other dimensions
        np.testing.assert_array_equal(graph.nodes[node.item()]["t"], graph_props["t"][idx])

    for idx, edge in enumerate(graph_props["edges"]):
        for name, values in graph_props["edge_props"].items():
            assert graph.edges[edge.tolist()][name] == values[idx].item()

    # TODO: test metadata
    # assert graph.graph["axis_names"] == graph_props["axis_names"]
    # assert graph.graph["axis_units"] == graph_props["axis_units"]


@pytest.mark.parametrize("node_dtype", node_dtypes)
@pytest.mark.parametrize("node_prop_dtypes", node_prop_dtypes)
@pytest.mark.parametrize("edge_prop_dtypes", edge_prop_dtypes)
@pytest.mark.parametrize("directed", [True, False])
def test_read_write_no_spatial(tmp_path, node_dtype, node_prop_dtypes, edge_prop_dtypes, directed):
    graph = nx.DiGraph() if directed else nx.Graph()

    nodes = np.array([10, 2, 127, 4, 5], dtype=node_dtype)
    props = np.array([4, 9, 10, 2, 8], dtype=node_prop_dtypes["position"])
    for node, pos in zip(nodes, props):
        graph.add_node(node.item(), attr=pos)

    edges = np.array(
        [
            [10, 2],
            [2, 127],
            [2, 4],
            [4, 5],
        ],
        dtype=node_dtype,
    )
    scores = np.array([0.1, 0.2, 0.3, 0.4], dtype=edge_prop_dtypes["score"])
    colors = np.array([1, 2, 3, 4], dtype=edge_prop_dtypes["color"])
    for edge, score, color in zip(edges, scores, colors):
        graph.add_edge(*edge.tolist(), score=score.item(), color=color.item())

    path = tmp_path / "rw_consistency.zarr/graph"

    geff.write_nx(graph, path, axis_names=[])

    compare, metadata = geff.read_nx(path)

    assert set(graph.nodes) == set(compare.nodes)
    assert set(graph.edges) == set(compare.edges)
    for node in nodes:
        assert graph.nodes[node.item()]["attr"] == compare.nodes[node.item()]["attr"]

    for edge in edges:
        assert graph.edges[edge.tolist()]["score"] == compare.edges[edge.tolist()]["score"]
        assert graph.edges[edge.tolist()]["color"] == compare.edges[edge.tolist()]["color"]


def test_write_empty_graph(tmp_path):
    graph = nx.DiGraph()
    geff.write_nx(graph, axis_names=["t", "y", "x"], path=tmp_path / "empty.zarr")


def test_write_nx_with_metadata(tmp_path):
    """Test write_nx with explicit metadata parameter"""
    from geff.metadata_schema import GeffMetadata, axes_from_lists

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
    metadata = GeffMetadata(geff_version="0.3.0", directed=False, axes=axes)

    path = tmp_path / "metadata_test.zarr"
    geff.write_nx(graph, path, metadata=metadata)

    # Read it back and verify metadata is preserved
    read_graph, read_metadata = geff.read_nx(path)

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


def test_write_nx_metadata_override_precedence(tmp_path, caplog):
    """Test that explicit axis parameters override metadata"""
    from geff.metadata_schema import GeffMetadata, axes_from_lists

    graph = nx.Graph()
    graph.add_node(1, x=1.0, y=2.0, z=3.0)
    graph.add_node(2, x=4.0, y=5.0, z=6.0)

    # Create metadata with one set of axes
    axes = axes_from_lists(
        axis_names=["x", "y"],
        axis_units=["micrometer", "micrometer"],
        axis_types=["space", "space"],
    )
    metadata = GeffMetadata(geff_version="0.3.0", directed=False, axes=axes)

    path = tmp_path / "override_test.zarr"

    # Should log warning when both metadata and axis lists are provided
    with caplog.at_level("WARNING"):
        geff.write_nx(
            graph,
            path,
            metadata=metadata,
            axis_names=["x", "y", "z"],  # Override with different axes
            axis_units=["meter", "meter", "meter"],
            axis_types=["space", "space", "space"],
        )
        assert len(caplog.records) == 1
        assert "Both axis lists and metadata provided" in caplog.records[0].message

    # Verify that axis lists took precedence
    read_graph, read_metadata = geff.read_nx(path)
    assert len(read_metadata.axes) == 3
    axis_names = [axis.name for axis in read_metadata.axes]
    axis_units = [axis.unit for axis in read_metadata.axes]
    axis_types = [axis.type for axis in read_metadata.axes]
    assert axis_names == ["x", "y", "z"]
    assert axis_units == ["meter", "meter", "meter"]
    assert axis_types == ["space", "space", "space"]


def test_write_nx_partial_axis_lists_fallback(tmp_path):
    """Test that providing partial axis lists uses graph properties for missing values"""
    graph = nx.Graph()
    graph.add_node(1, x=1.0, y=2.0)

    # Set some graph properties to test fallback behavior
    graph.graph["axis_names"] = ["x", "y"]
    graph.graph["axis_units"] = ["micrometer", "micrometer"]
    graph.graph["axis_types"] = ["space", "space"]

    path = tmp_path / "partial_fallback.zarr"

    # Providing only axis_names should fallback to graph properties for units and types
    geff.write_nx(graph, path, axis_names=["x", "y"])

    read_graph, read_metadata = geff.read_nx(path)
    assert len(read_metadata.axes) == 2
    axis_names = [axis.name for axis in read_metadata.axes]
    axis_units = [axis.unit for axis in read_metadata.axes]
    axis_types = [axis.type for axis in read_metadata.axes]
    assert axis_names == ["x", "y"]
    assert axis_units == ["micrometer", "micrometer"]  # From graph properties
    assert axis_types == ["space", "space"]  # From graph properties


def test_write_nx_graph_properties_fallback(tmp_path):
    """Test that graph properties are used as fallback when no metadata or axis lists provided"""
    graph = nx.Graph()
    graph.add_node(1, t=1.0, x=2.0)
    graph.add_node(2, t=2.0, x=3.0)

    # Set axis information in graph properties
    graph.graph["axis_names"] = ["t", "x"]
    graph.graph["axis_units"] = ["second", "micrometer"]
    graph.graph["axis_types"] = ["time", "space"]

    path = tmp_path / "graph_props.zarr"
    geff.write_nx(graph, path)  # No metadata or axis lists provided

    # Verify graph properties were used
    read_graph, read_metadata = geff.read_nx(path)
    assert len(read_metadata.axes) == 2
    axis_names = [axis.name for axis in read_metadata.axes]
    axis_units = [axis.unit for axis in read_metadata.axes]
    axis_types = [axis.type for axis in read_metadata.axes]
    assert axis_names == ["t", "x"]
    assert axis_units == ["second", "micrometer"]
    assert axis_types == ["time", "space"]
