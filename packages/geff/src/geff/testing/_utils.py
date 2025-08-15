import warnings

import networkx as nx
import networkx.algorithms.isomorphism as iso
from zarr.storage import StoreLike

from geff import _path
from geff.core_io._utils import expect_array, expect_group, open_storelike
from geff.validate.structure import validate_structure


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


def check_equiv_geff(store_a: StoreLike, store_b: StoreLike) -> None:
    """This function compares two geffs, typically a starting fixture geff with
    the output of an implementation.

    This tests focuses on maintaining shape and dtype consistency. It does not
    assert element wise equality. store_a is assumed to be the "correct" geff.

    Missing arrays are not required to be present in both a and b because we allow
    missing arrays where all values are present. We raise a warning if we see this.

    Args:
        store_a (str | Path | zarr store): str/Path/store for a geff zarr
        store_b (str | Path | zarr store): str/Path/store for a second geff zarr
    """

    # Run validation first so that we don't hit issues with basic structure
    validate_structure(store_a)
    validate_structure(store_b)

    for graph_group in [_path.NODES, _path.EDGES]:
        ga = expect_group(open_storelike(store_a), graph_group)
        gb = expect_group(open_storelike(store_b), graph_group)

        # Check ids
        ids_a = expect_array(ga, _path.IDS)
        ids_b = expect_array(gb, _path.IDS)
        if (a_shape := ids_a.shape) != (b_shape := ids_b.shape):
            raise ValueError(f"{graph_group} ids shape: a {a_shape} does not match b {b_shape}")

        # Check that properties in each geff are the same
        a_props = set(expect_group(ga, _path.PROPS))
        b_props = set(expect_group(gb, _path.PROPS))
        if a_props != b_props:
            raise ValueError(
                f"{graph_group} properties: a ({a_props}) does not match b ({b_props})"
            )

        # Check shape and dtype of each prop
        for prop in a_props:
            a_missing = "missing" in expect_group(ga, f"{_path.PROPS}/{prop}")
            b_missing = "missing" in expect_group(gb, f"{_path.PROPS}/{prop}")
            if a_missing != b_missing:
                warnings.warn(
                    f"one {graph_group}/{_path.PROPS}/{prop} contains missing "
                    "but the other does not. This may be correct but should be verified.",
                    stacklevel=2,
                )

                # Note: don't need to check missing shape because validation forces it to be
                # the same shape as values

                # Note: don't need to check missing dtype because validation forces it to be bool

            a_values = expect_array(ga, f"{_path.PROPS}/{prop}/{_path.VALUES}")
            b_values = expect_array(gb, f"{_path.PROPS}/{prop}/{_path.VALUES}")
            if (a_shape := a_values.shape) != (b_shape := b_values.shape):
                raise ValueError(
                    f"{graph_group}/{_path.PROPS}/{prop}/{_path.VALUES} shape: "
                    f"a {a_shape} does not match b {b_shape}"
                )
            if (a_dtype := a_values.dtype) != (b_dtype := b_values.dtype):
                raise ValueError(
                    f"{graph_group}/{_path.PROPS}/{prop}/{_path.VALUES} dtype: "
                    f"a {a_dtype} does not match b {b_dtype}"
                )
