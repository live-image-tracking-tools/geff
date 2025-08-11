import networkx as nx
import networkx.algorithms.isomorphism as iso


def nx_is_equal(g1: nx.Graph, g2: nx.Graph) -> bool:
    """Utility function to check that two Network graphs are perfectly identical.

    It checks that the graphs are isomorphic, and that their graph,
    nodes and edges attributes are all identical.

    Args:
        g1 (nx.Graph): The first graph to compare.
        g2 (nx.Graph): The second graph to compare.

    Returns:
        bool: True if the graphs are identical, False otherwise.
    """
    edges_attr = list({k for (n1, n2, d) in g2.edges.data() for k in d})
    edges_default = len(edges_attr) * [0]
    em = iso.categorical_edge_match(edges_attr, edges_default)
    nodes_attr = list({k for (n, d) in g2.nodes.data() for k in d})
    nodes_default = len(nodes_attr) * [0]
    nm = iso.categorical_node_match(nodes_attr, nodes_default)

    same_nodes = same_edges = False
    if not g1.nodes.data() and not g2.nodes.data():
        same_nodes = True
    elif len(g1.nodes.data()) != len(g2.nodes.data()):
        same_nodes = False
    else:
        for data1, data2 in zip(sorted(g1.nodes.data()), sorted(g2.nodes.data()), strict=False):
            n1, attr1 = data1
            n2, attr2 = data2
            if sorted(attr1) == sorted(attr2) and n1 == n2:
                same_nodes = True
            else:
                same_nodes = False

    if not g1.edges.data() and not g2.edges.data():
        same_edges = True
    elif len(g1.edges.data()) != len(g2.edges.data()):
        same_edges = False
    else:
        for data1, data2 in zip(sorted(g1.edges.data()), sorted(g2.edges.data()), strict=False):
            n11, n12, attr1 = data1
            n21, n22, attr2 = data2
            if sorted(attr1) == sorted(attr2) and sorted((n11, n12)) == sorted((n21, n22)):
                same_edges = True
            else:
                same_edges = False

    if (
        nx.is_isomorphic(g1, g2, edge_match=em, node_match=nm)
        and g1.graph == g2.graph
        and same_nodes
        and same_edges
    ):
        return True
    else:
        return False
