from typing import Literal, TypedDict, Any, Mapping
from pathlib import Path

import pytest
import numpy as np
from numpy.typing import NDArray
import networkx as nx

import geff

DTypeStr = Literal[
    "double", "int", "int8", "uint8", "int16", "uint16", "float32", "float64"
]
Axes = Literal["t", "z", "y", "x"]


class GraphAttrs(TypedDict):
    nodes: NDArray[Any]
    edges: NDArray[Any]
    node_positions: NDArray[Any]
    extra_node_attrs: dict[str, NDArray[Any]]
    edge_attrs: dict[str, NDArray[Any]]
    directed: bool
    axis_names: tuple[Axes, ...]
    axis_units: tuple[str, ...]


class ExampleNodeAttrs(TypedDict):
    position: DTypeStr


class ExampleEdgeAttrs(TypedDict):
    score: DTypeStr
    color: DTypeStr


def create_dummy_graph_attrs(
    node_dtype: DTypeStr,
    node_attr_dtypes: ExampleNodeAttrs,
    edge_attr_dtypes: ExampleEdgeAttrs,
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
        dtype=node_attr_dtypes["position"],
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
    scores = np.array([0.1, 0.2, 0.3, 0.4], dtype=edge_attr_dtypes["score"])
    colors = np.array([1, 2, 3, 4], dtype=edge_attr_dtypes["color"])

    return {
        "nodes": nodes,
        "edges": edges,
        "node_positions": positions,
        "extra_node_attrs": {},
        "edge_attrs": {"score": scores, "color": colors},
        "directed": directed,
        "axis_names": axis_names,
        "axis_units": axis_units,
    }


@pytest.fixture()
def path_w_expected_graph_attrs(tmp_path) -> tuple[Path, GraphAttrs]:
    """
    Fixture to a geff graph path saved on disk with the expected graph attributes.

    Returns:
    Path
        Path to the example graph.
    GraphAttrs
        The expected graph attributes in a dictionary.
    """

    directed = True
    graph_attrs = create_dummy_graph_attrs(
        node_dtype="int8",
        node_attr_dtypes={"position": "double"},
        edge_attr_dtypes={"score": "float64", "color": "uint8"},
        directed=directed,
    )

    # TODO: write zarr from scratch to remove test dependency on networkx backend?
    # write graph with networkx api
    graph = nx.DiGraph() if directed else nx.Graph()

    for idx, node in enumerate(graph_attrs["nodes"]):
        attrs = {
            name: attr_array[idx]
            for name, attr_array in graph_attrs["extra_node_attrs"].items()
        }
        graph.add_node(node, pos=graph_attrs["node_positions"][idx], **attrs)

    for idx, edge in enumerate(graph_attrs["edges"]):
        attrs = {
            name: attr_array[idx]
            for name, attr_array in graph_attrs["edge_attrs"].items()
        }
        graph.add_edge(*edge.tolist(), **attrs)

    path = tmp_path / "rw_consistency.zarr/graph"

    geff.write_nx(
        graph,
        path,
        position_attr="pos",
        axis_names=list(graph_attrs["axis_names"]),
        axis_units=list(graph_attrs["axis_units"]),
    )

    return path, graph_attrs
