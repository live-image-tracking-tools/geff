from __future__ import annotations

import shutil
from functools import cache
from typing import TYPE_CHECKING, Any

import networkx as nx
import numpy as np
import pytest
import rustworkx as rx

import geff.networkx.io as geff_nx
import geff.rustworkx.io as geff_rx
from geff.utils import validate

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from pytest import TempPathFactory
    from pytest_benchmark.plugin import BenchmarkFixture


np.random.seed(42)  # for reproducibility


@cache
def node_data(n_nodes: int) -> dict[int, dict[str, float]]:
    """Returns a dict of {node_id -> tzyx_coord_dict}."""
    coords = np.random.uniform(size=(n_nodes, 4))
    return {n: dict(zip("tzyx", c, strict=True)) for n, c in enumerate(coords)}


@cache
def edge_data(n_nodes: int) -> dict[tuple[int, int], dict[str, Any]]:
    """Returns a dict of {(u, v) -> edge_data_dict}."""
    idx = np.arange(n_nodes)  # [0, 1, ..., n-1]
    u = np.repeat(idx, n_nodes)  # 0 0 ... 1 1 ...
    v = np.tile(idx, n_nodes)  # 0 1 ... 0 1 ...
    mask = u != v  # drop self-loops
    mask_sum = np.sum(mask)  # number of edges without self-loops
    return {
        (int(uu), int(vv)): {"float_prop": float(fp), "int_prop": int(ip)}
        for (uu, vv, fp, ip) in zip(
            u[mask],
            v[mask],
            np.random.uniform(size=mask_sum),
            np.arange(mask_sum, dtype=int),
            strict=True,
        )
    }


def create_nx_graph(num_nodes: int = 2000) -> nx.DiGraph:
    graph: nx.DiGraph[int] = nx.DiGraph()
    nodes, edges = node_data(num_nodes), edge_data(num_nodes)
    graph.add_nodes_from(nodes.items())
    graph.add_edges_from(((u, v, dd) for (u, v), dd in edges.items()))
    return graph


def create_rx_graph(num_nodes: int = 2000) -> rx.PyDiGraph:
    graph = rx.PyDiGraph()
    nodes, edges = node_data(num_nodes), edge_data(num_nodes)
    graph.add_nodes_from(nodes.items())
    graph.add_edges_from(((u, v, dd) for (u, v), dd in edges.items()))
    return graph


@pytest.fixture(scope="session")
def big_graph_path(tmp_path_factory: TempPathFactory) -> Path:
    tmp_path = tmp_path_factory.mktemp("data") / "test.zarr"
    geff_nx.write_nx(graph=create_nx_graph(), store=tmp_path, axis_names=["t", "z", "y", "x"])
    return tmp_path


@pytest.mark.parametrize(
    "create_func,write_func",
    [
        # (create_rx_graph, geff_rx.write_rx),  # there's a bug in write_rx
        (create_nx_graph, geff_nx.write_nx),
    ],
)
def test_bench_write(
    create_func: Callable, write_func: Callable, benchmark: BenchmarkFixture, tmp_path: Path
) -> None:
    path = tmp_path / "test_write.zarr"
    big_graph = create_func()
    benchmark.pedantic(
        write_func,
        kwargs={"graph": big_graph, "axis_names": ["t", "z", "y", "x"], "store": path},
        setup=lambda: shutil.rmtree(path, ignore_errors=True),  # delete previous zarr
    )


def test_bench_validate(benchmark: BenchmarkFixture, big_graph_path: Path) -> None:
    benchmark(validate, store=big_graph_path)


@pytest.mark.parametrize("read_func", [geff_nx.read_nx, geff_rx.read_rx])
def test_bench_read(
    read_func: Callable[[Path], Any], benchmark: BenchmarkFixture, big_graph_path: Path
) -> None:
    benchmark(read_func, big_graph_path, validate=False)
