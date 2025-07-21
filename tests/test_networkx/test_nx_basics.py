import networkx as nx
import numpy as np
import pytest

import geff
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

# TODO: mixed dtypes?


@pytest.mark.parametrize("node_id_dtype", node_id_dtypes)
@pytest.mark.parametrize("node_prop_dtypes", node_prop_dtypes)
@pytest.mark.parametrize("edge_prop_dtypes", edge_prop_dtypes)
@pytest.mark.parametrize("directed", [True, False])
@pytest.mark.parametrize("include_t", [True, False])
@pytest.mark.parametrize("include_z", [True, False])
def test_read_write_consistency(
    node_id_dtype,
    node_prop_dtypes,
    edge_prop_dtypes,
    directed,
    include_t,
    include_z,
):
    store, graph_props = create_memory_mock_geff(
        node_id_dtype,
        node_prop_dtypes,
        edge_prop_dtypes,
        directed=directed,
        include_t=include_t,
        include_z=include_z,
    )

    graph, _ = geff.read_nx(store)

    assert set(graph.nodes) == {*graph_props["nodes"].tolist()}
    assert set(graph.edges) == {*[tuple(edges) for edges in graph_props["edges"].tolist()]}
    for idx, node in enumerate(graph_props["nodes"]):
        if include_t and len(graph_props["t"]) > 0:
            np.testing.assert_array_equal(graph.nodes[node.item()]["t"], graph_props["t"][idx])
        if include_z and len(graph_props["z"]) > 0:
            np.testing.assert_array_equal(graph.nodes[node.item()]["z"], graph_props["z"][idx])
        # TODO: test other dimensions

    for idx, edge in enumerate(graph_props["edges"]):
        for name, values in graph_props["edge_props"].items():
            assert graph.edges[edge.tolist()][name] == values[idx].item()

    # TODO: test metadata
    # assert graph.graph["axis_names"] == graph_props["axis_names"]
    # assert graph.graph["axis_units"] == graph_props["axis_units"]


@pytest.mark.parametrize("node_id_dtype", node_id_dtypes)
@pytest.mark.parametrize("node_prop_dtypes", node_prop_dtypes)
@pytest.mark.parametrize("edge_prop_dtypes", edge_prop_dtypes)
@pytest.mark.parametrize("directed", [True, False])
def test_read_write_no_spatial(
    tmp_path, node_id_dtype, node_prop_dtypes, edge_prop_dtypes, directed
):
    graph = nx.DiGraph() if directed else nx.Graph()

    nodes = np.array([10, 2, 127, 4, 5], dtype=node_id_dtype)
    props = np.array([4, 9, 10, 2, 8], dtype=node_prop_dtypes["position"])
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
    scores = np.array([0.1, 0.2, 0.3, 0.4], dtype=edge_prop_dtypes["score"])
    colors = np.array([1, 2, 3, 4], dtype=edge_prop_dtypes["color"])
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


def test_write_empty_graph(tmp_path):
    graph = nx.DiGraph()
    geff.write_nx(graph, axis_names=["t", "y", "x"], store=tmp_path / "empty.zarr")


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


def test_write_nx_metadata_override_precedence(tmp_path):
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


def test_create_simple_2d_geff():
    """Test the create_simple_2d_geff convenience function"""
    from geff.testing.data import create_simple_2d_geff

    # Test with defaults
    store, _ = create_simple_2d_geff()

    # Verify it creates a valid geff store
    graph, metadata = geff.read_nx(store)

    # Check basic properties
    assert len(graph.nodes) == 10  # default num_nodes
    assert len(graph.edges) == 15  # default num_edges
    assert not graph.is_directed()  # default directed=False

    # Check spatial dimensions (2D should have x, y, t but not z)
    for node in graph.nodes:
        node_data = graph.nodes[node]
        assert "x" in node_data
        assert "y" in node_data
        assert "t" in node_data
        assert "z" not in node_data  # 2D doesn't include z

    # Check metadata
    assert not metadata.directed
    axis_names = [axis.name for axis in metadata.axes]
    assert "x" in axis_names
    assert "y" in axis_names
    assert "t" in axis_names
    assert "z" not in axis_names


def test_create_simple_3d_geff():
    """Test the create_simple_3d_geff convenience function"""
    from geff.testing.data import create_simple_3d_geff

    # Test with defaults
    store, props = create_simple_3d_geff()

    # Verify it creates a valid geff store
    graph, metadata = geff.read_nx(store)

    # Check basic properties
    assert len(graph.nodes) == 10  # default num_nodes
    assert len(graph.edges) == 15  # default num_edges
    assert not graph.is_directed()  # default directed=False

    # Check spatial dimensions (3D should have x, y, z, t)
    for node in graph.nodes:
        node_data = graph.nodes[node]
        assert "x" in node_data
        assert "y" in node_data
        assert "z" in node_data  # 3D includes z
        assert "t" in node_data

    # Check metadata
    assert not metadata.directed
    axis_names = [axis.name for axis in metadata.axes]
    assert "x" in axis_names
    assert "y" in axis_names
    assert "z" in axis_names  # 3D includes z
    assert "t" in axis_names


def test_simple_geff_edge_properties():
    """Test that the simple functions create graphs with proper edge properties"""
    from geff.testing.data import create_simple_2d_geff, create_simple_3d_geff

    # Test 2D
    store_2d, _ = create_simple_2d_geff()
    graph_2d, _ = geff.read_nx(store_2d)

    # Check that edges have the expected properties
    for edge in graph_2d.edges:
        edge_data = graph_2d.edges[edge]
        assert "score" in edge_data
        assert "color" in edge_data
        assert isinstance(edge_data["score"], float | np.floating)
        assert isinstance(edge_data["color"], int | np.integer)

    # Test 3D
    store_3d, _ = create_simple_3d_geff()
    graph_3d, _ = geff.read_nx(store_3d)

    # Check that edges have the expected properties
    for edge in graph_3d.edges:
        edge_data = graph_3d.edges[edge]
        assert "score" in edge_data
        assert "color" in edge_data
        assert isinstance(edge_data["score"], float | np.floating)
        assert isinstance(edge_data["color"], int | np.integer)


def test_create_memory_mock_geff_with_extra_node_props():
    """Test create_memory_mock_geff with extra node properties"""
    from geff.testing.data import create_memory_mock_geff

    # Test with various extra node properties
    extra_node_props = [
        {"label": "str", "confidence": "float64"},
        {"category": "int8", "priority": "uint16"},
        {"status": "str", "weight": "float32"},
    ]

    store, _ = create_memory_mock_geff(
        node_id_dtype="int",
        node_prop_dtypes={"position": "float64", "time": "float64"},
        edge_prop_dtypes={"score": "float64", "color": "int"},
        directed=False,
        num_nodes=5,
        num_edges=4,
        extra_node_props=extra_node_props,
    )

    # Verify the graph was created correctly
    graph, _ = geff.read_nx(store)

    # Check that extra node properties are present
    for node in graph.nodes:
        node_data = graph.nodes[node]
        # Check that all extra properties are present
        assert "label" in node_data
        assert "confidence" in node_data
        assert "category" in node_data
        assert "priority" in node_data
        assert "status" in node_data
        assert "weight" in node_data

        # Check data types
        assert isinstance(node_data["label"], str)
        assert isinstance(node_data["confidence"], float | np.floating)
        assert isinstance(node_data["category"], int | np.integer)
        assert isinstance(node_data["priority"], int | np.integer)
        assert isinstance(node_data["status"], str)
        assert isinstance(node_data["weight"], float | np.floating)

    # Check that the properties match the expected patterns
    for i, node in enumerate(sorted(graph.nodes)):
        node_data = graph.nodes[node]
        assert node_data["label"] == f"label_{i}"
        assert node_data["status"] == f"status_{i}"
        assert node_data["category"] == i
        assert node_data["priority"] == i


def test_create_memory_mock_geff_with_no_extra_node_props():
    """Test create_memory_mock_geff with no extra node properties"""
    from geff.testing.data import create_memory_mock_geff

    store, graph_props = create_memory_mock_geff(
        node_id_dtype="int",
        node_prop_dtypes={"position": "float64", "time": "float64"},
        edge_prop_dtypes={"score": "float64", "color": "int"},
        directed=False,
        num_nodes=5,
        num_edges=4,
        extra_node_props=None,  # Explicitly None
    )

    # Verify the graph was created correctly
    graph, metadata = geff.read_nx(store)

    # Check that no extra node properties are present
    for node in graph.nodes:
        node_data = graph.nodes[node]
        # Should only have spatial properties, not extra ones
        extra_props = {"label", "confidence", "category", "priority", "status", "weight"}

        for prop in extra_props:
            assert prop not in node_data


def test_create_memory_mock_geff_extra_node_props_validation():
    """Test validation of extra_node_props parameter"""
    from geff.testing.data import create_memory_mock_geff

    # Test with invalid input types
    with pytest.raises(ValueError, match="extra_node_props must be a list"):
        create_memory_mock_geff(
            node_id_dtype="int",
            node_prop_dtypes={"position": "float64", "time": "float64"},
            edge_prop_dtypes={"score": "float64", "color": "int"},
            directed=False,
            extra_node_props="not_a_list",  # Should be a list
        )

    with pytest.raises(ValueError, match="extra_node_props\\[0\\] must be a dict"):
        create_memory_mock_geff(
            node_id_dtype="int",
            node_prop_dtypes={"position": "float64", "time": "float64"},
            edge_prop_dtypes={"score": "float64", "color": "int"},
            directed=False,
            extra_node_props=["not_a_dict"],  # Should be a list of dicts
        )

    with pytest.raises(ValueError, match="extra_node_props\\[0\\] keys must be strings"):
        create_memory_mock_geff(
            node_id_dtype="int",
            node_prop_dtypes={"position": "float64", "time": "float64"},
            edge_prop_dtypes={"score": "float64", "color": "int"},
            directed=False,
            extra_node_props=[{123: "str"}],  # Key should be string
        )

    with pytest.raises(
        ValueError, match="extra_node_props\\[0\\]\\[label\\] must be a string dtype"
    ):
        create_memory_mock_geff(
            node_id_dtype="int",
            node_prop_dtypes={"position": "float64", "time": "float64"},
            edge_prop_dtypes={"score": "float64", "color": "int"},
            directed=False,
            extra_node_props=[{"label": 123}],  # Value should be string dtype
        )

    with pytest.raises(ValueError, match="dtype 'invalid_dtype' not supported"):
        create_memory_mock_geff(
            node_id_dtype="int",
            node_prop_dtypes={"position": "float64", "time": "float64"},
            edge_prop_dtypes={"score": "float64", "color": "int"},
            directed=False,
            extra_node_props=[{"label": "invalid_dtype"}],  # Invalid dtype
        )


def test_create_memory_mock_geff_extra_node_props_different_dtypes():
    """Test extra node properties with different data types"""
    from geff.testing.data import create_memory_mock_geff

    # Test all supported dtypes
    extra_node_props = [
        {"str_prop": "str"},
        {"int_prop": "int"},
        {"int8_prop": "int8"},
        {"uint8_prop": "uint8"},
        {"int16_prop": "int16"},
        {"uint16_prop": "uint16"},
        {"float32_prop": "float32"},
        {"float64_prop": "float64"},
    ]

    store, graph_props = create_memory_mock_geff(
        node_id_dtype="int",
        node_prop_dtypes={"position": "float64", "time": "float64"},
        edge_prop_dtypes={"score": "float64", "color": "int"},
        directed=False,
        num_nodes=3,
        num_edges=2,
        extra_node_props=extra_node_props,
    )

    # Verify the graph was created correctly
    graph, metadata = geff.read_nx(store)

    # Check that all properties are present with correct types
    for node in graph.nodes:
        node_data = graph.nodes[node]

        # String properties
        assert "str_prop" in node_data
        assert isinstance(node_data["str_prop"], str)

        # Integer properties
        for prop_name in ["int_prop", "int8_prop", "uint8_prop", "int16_prop", "uint16_prop"]:
            assert prop_name in node_data
            assert isinstance(node_data[prop_name], int | np.integer)

        # Float properties
        for prop_name in ["float32_prop", "float64_prop"]:
            assert prop_name in node_data
            assert isinstance(node_data[prop_name], float | np.floating)


def test_create_dummy_graph_props_extra_node_props():
    """Test create_dummy_graph_props with extra node properties"""
    from geff.testing.data import create_dummy_graph_props

    extra_node_props = [
        {"label": "str", "confidence": "float64"},
        {"category": "int8"},
    ]

    graph_props = create_dummy_graph_props(
        node_id_dtype="int",
        node_prop_dtypes={"position": "float64", "time": "float64"},
        edge_prop_dtypes={"score": "float64", "color": "int"},
        directed=False,
        num_nodes=5,
        num_edges=4,
        extra_node_props=extra_node_props,
    )

    # Check that extra_node_props_dict contains the expected properties
    extra_props = graph_props["extra_node_props"]
    assert "label" in extra_props
    assert "confidence" in extra_props
    assert "category" in extra_props

    # Check data types and values
    assert extra_props["label"].dtype.kind == "U"  # Unicode string
    assert extra_props["confidence"].dtype == "float64"
    assert extra_props["category"].dtype == "int8"

    # Check that arrays have the correct length
    assert len(extra_props["label"]) == 5
    assert len(extra_props["confidence"]) == 5
    assert len(extra_props["category"]) == 5

    # Check that string properties follow the expected pattern
    for i in range(5):
        assert extra_props["label"][i] == f"label_{i}"
        assert extra_props["category"][i] == i
