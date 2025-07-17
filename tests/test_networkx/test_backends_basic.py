import numpy as np

import geff

# NOTE: this may be subject to change with potential new reader/writer interfaces


# already tested in test_nx_basic.py module
# this test serves as a template for other backends
def test_networkx_read(path_w_expected_graph_attrs):
    path, graph_attrs = path_w_expected_graph_attrs

    graph = geff.read_nx(path)

    assert set(graph.nodes) == {*graph_attrs["nodes"].tolist()}
    assert set(graph.edges) == {
        *[tuple(edges) for edges in graph_attrs["edges"].tolist()]
    }
    for idx, node in enumerate(graph_attrs["nodes"]):
        np.testing.assert_array_equal(
            graph.nodes[node.item()]["pos"], graph_attrs["node_positions"][idx]
        )

    for idx, edge in enumerate(graph_attrs["edges"]):
        for name, values in graph_attrs["edge_attrs"].items():
            assert graph.edges[edge.tolist()][name] == values[idx].item()

    assert graph.graph["axis_names"] == graph_attrs["axis_names"]
    assert graph.graph["axis_units"] == graph_attrs["axis_units"]
