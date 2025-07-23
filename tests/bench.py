import shutil
from itertools import product
from pathlib import Path

import networkx as nx
import numpy as np
import pytest

import geff.networkx.io as geff_nx
import geff.rustworkx.io as geff_rx
from geff.utils import validate

ROUNDS = 3
N_NODES = 2000


@pytest.fixture(scope="session")
def big_graph():
    graph = nx.DiGraph()

    nodes = np.arange(N_NODES)  # int
    positions = np.random.uniform(size=(N_NODES, 4))  # float
    for node, pos in zip(nodes, positions, strict=False):
        t, z, y, x = pos.tolist()
        graph.add_node(node.item(), t=t, z=z, y=y, x=x)

    float_prop = np.random.uniform(size=(N_NODES * N_NODES))
    int_prop = np.arange(N_NODES * N_NODES)
    for i, (source, target) in enumerate(product(nodes, nodes)):
        if source != target:
            graph.add_edge(source, target, float_prop=float_prop[i], int_prop=int_prop[i])

    print("N nodes", len(graph.nodes))
    print("N edges", len(graph.edges))

    return graph


@pytest.fixture(scope="session")
def big_graph_path(tmpdir_factory, big_graph):
    tmp_path = Path(tmpdir_factory.mktemp("data").join("test.zarr"))
    geff_nx.write_nx(graph=big_graph, store=tmp_path, axis_names=["t", "z", "y", "x"])
    return tmp_path


def test_write(benchmark, tmp_path, big_graph):
    path = tmp_path / "test_write.zarr"

    benchmark.pedantic(
        geff_nx.write_nx,
        kwargs={"graph": big_graph, "axis_names": ["t", "z", "y", "x"], "store": path},
        rounds=ROUNDS,
        setup=lambda: shutil.rmtree(path, ignore_errors=True),  # delete previous zarr
    )


def test_validate(benchmark, big_graph_path):
    benchmark.pedantic(validate, kwargs={"store": big_graph_path}, rounds=ROUNDS)


@pytest.mark.parametrize("read_func", [geff_nx.read_nx, geff_rx.read_rx])
def test_read(read_func, benchmark, big_graph_path):
    benchmark.pedantic(
        read_func, kwargs={"store": big_graph_path, "validate": False}, rounds=ROUNDS
    )
