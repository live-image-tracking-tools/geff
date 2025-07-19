from pathlib import Path
from typing import Any, Callable, Literal, TypedDict

import networkx as nx
import numpy as np
import pytest
from numpy.typing import NDArray

import geff

DTypeStr = Literal["double", "int", "int8", "uint8", "int16", "uint16", "float32", "float64", "str"]
Axes = Literal["t", "z", "y", "x"]


class GraphAttrs(TypedDict):
    nodes: NDArray[Any]
    edges: NDArray[Any]
    node_positions: NDArray[Any]
    extra_node_props: dict[str, NDArray[Any]]
    edge_props: dict[str, NDArray[Any]]
    directed: bool
    axis_names: tuple[Axes, ...]
    axis_units: tuple[str, ...]


class ExampleNodeProps(TypedDict):
    position: DTypeStr


class ExampleEdgeProps(TypedDict):
    score: DTypeStr
    color: DTypeStr


def create_dummy_graph_props(
    node_dtype: DTypeStr,
    node_prop_dtypes: ExampleNodeProps,
    edge_prop_dtypes: ExampleEdgeProps,
    directed: bool,
) -> GraphAttrs:
    axis_names = ("t", "z", "y", "x")
    axis_units = ("s", "nm", "nm", "nm")
    nodes = np.array([10, 2, 127, 4, 5], dtype=node_dtype)
    positions = np.array(
        [
            [0.1, 0.5, 100.0, 1.0],
            [0.2, 0.4, 200.0, 0.1],
            [0.3, 0.3, 300.0, 0.1],
            [0.4, 0.2, 400.0, 0.1],
            [0.5, 0.1, 500.0, 0.1],
        ],
        dtype=node_prop_dtypes["position"],
    )

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

    ignored_attrs = {
        "foo": np.empty(len(nodes), dtype=node_dtype).tolist(),
        "bar": np.empty(len(edges), dtype=node_dtype).tolist(),
    }

    return {
        "nodes": nodes,
        "edges": edges,
        "node_positions": positions,
        "extra_node_props": {},
        "edge_props": {"score": scores, "color": colors},
        "directed": directed,
        "axis_names": axis_names,
        "axis_units": axis_units,
        "ignored_attrs": ignored_attrs,
    }


# Using a fixture instead of a function so the tmp_path fixture is automatically passed
# Implemented as a closure where tmp_path is the bound variable
@pytest.fixture
def path_w_expected_graph_props(
    tmp_path,
) -> Callable[[DTypeStr, ExampleNodeProps, ExampleEdgeProps, bool], tuple[Path, GraphAttrs]]:
    def func(
        node_dtype: DTypeStr,
        node_prop_dtypes: ExampleNodeProps,
        edge_prop_dtypes: ExampleEdgeProps,
        directed: bool,
    ) -> tuple[Path, GraphAttrs]:
        """
        Fixture to a geff graph path saved on disk with the expected graph properties.

        Returns:
        Path
            Path to the example graph.
        GraphAttrs
            The expected graph properties in a dictionary.
        """

        directed = True
        graph_props = create_dummy_graph_props(
            node_dtype=node_dtype,
            node_prop_dtypes=node_prop_dtypes,
            edge_prop_dtypes=edge_prop_dtypes,
            directed=directed,
        )

        # write graph with networkx api
        graph = nx.DiGraph() if directed else nx.Graph()

        for idx, node in enumerate(graph_props["nodes"]):
            props = {
                name: prop_array[idx]
                for name, prop_array in graph_props["extra_node_props"].items()
            }
            graph.add_node(node, pos=graph_props["node_positions"][idx], **props)

        for idx, edge in enumerate(graph_props["edges"]):
            props = {
                name: prop_array[idx] for name, prop_array in graph_props["edge_props"].items()
            }
            graph.add_edge(*edge.tolist(), **props)

        graph.graph["ignored_attrs"] = graph_props.get("ignored_attrs", {})

        path = tmp_path / "rw_consistency.zarr/graph"

        geff.write_nx(
            graph,
            path,
            position_prop="pos",
            axis_names=list(graph_props["axis_names"]),
            axis_units=list(graph_props["axis_units"]),
        )

        return path, graph_props

    return func
