from __future__ import annotations

import sys

import pytest

# only run this file if benchmarks are requested, or running directly
if all(x not in {"--codspeed", "--benchmark", "tests/test_bench.py"} for x in sys.argv):
    pytest.skip("use --benchmark to run benchmark", allow_module_level=True)

import atexit
import shutil
import tempfile
from functools import cache
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Any

import networkx as nx
import numpy as np

import geff
from geff.utils import validate

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from pytest_codspeed.plugin import BenchmarkFixture


np.random.seed(42)  # for reproducibility

# ###########################   Utils   ##################################


@cache
def node_data(n_nodes: int) -> Mapping[int, dict[str, float]]:
    """Returns a dict of {node_id -> tzyx_coord_dict}."""
    coords = np.random.uniform(size=(n_nodes, 4))
    nodes = {n: dict(zip("tzyx", c, strict=True)) for n, c in enumerate(coords)}
    return MappingProxyType(nodes)


@cache
def edge_data(n_nodes: int) -> Mapping[tuple[int, int], dict[str, Any]]:
    """Returns a dict of {(u, v) -> edge_data_dict}."""
    idx = np.arange(n_nodes)  # [0, 1, ..., n-1]
    u = np.repeat(idx, n_nodes)  # 0 0 ... 1 1 ...
    v = np.tile(idx, n_nodes)  # 0 1 ... 0 1 ...
    mask = u != v  # drop self-loops
    mask_sum = np.sum(mask)  # number of edges without self-loops
    edges = {
        (int(uu), int(vv)): {"float_prop": float(fp), "int_prop": int(ip)}
        for (uu, vv, fp, ip) in zip(
            u[mask],
            v[mask],
            np.random.uniform(size=mask_sum),
            np.arange(mask_sum, dtype=int),
            strict=True,
        )
    }
    return MappingProxyType(edges)


def create_nx_graph(num_nodes: int) -> nx.DiGraph:
    graph: nx.DiGraph[int] = nx.DiGraph()
    nodes, edges = node_data(num_nodes), edge_data(num_nodes)
    graph.add_nodes_from(nodes.items())
    graph.add_edges_from(((u, v, dd) for (u, v), dd in edges.items()))
    return graph


@cache
def graph_file_path(num_nodes: int) -> Path:
    tmp_dir = tempfile.mkdtemp(suffix=".zarr")
    atexit.register(shutil.rmtree, tmp_dir, ignore_errors=True)
    geff.write_nx(graph=create_nx_graph(num_nodes), store=tmp_dir, axis_names=["t", "z", "y", "x"])
    return Path(tmp_dir)


# ###########################   TESTS   ##################################

READ_PATH: Mapping[Callable, Callable[[Path], tuple[Any, Any]]] = {
    geff.read_nx: lambda path: geff.read_nx(path, validate=False),
    geff.read_rx: lambda path: geff.read_rx(path, validate=False),
    geff.read_sg: lambda path: geff.read_sg(path, validate=False),
}


@pytest.mark.parametrize("nodes", [500])
@pytest.mark.parametrize("write_func", [geff.write_nx, geff.write_rx, geff.write_sg])
def test_bench_write(
    write_func: Callable, benchmark: BenchmarkFixture, tmp_path: Path, nodes: int
) -> None:
    path = tmp_path / "test_write.zarr"
    read_func = getattr(geff, f"read_{write_func.__name__.split('_')[1]}")
    graph = read_func(graph_file_path(nodes))[0]
    benchmark.pedantic(
        write_func,
        kwargs={"graph": graph, "axis_names": ["t", "z", "y", "x"], "store": path},
        setup=lambda **__: shutil.rmtree(path, ignore_errors=True),  # delete previous zarr
    )


@pytest.mark.parametrize("nodes", [500])
def test_bench_validate(benchmark: BenchmarkFixture, nodes: int) -> None:
    graph_path = graph_file_path(nodes)
    benchmark(validate, store=graph_path)


@pytest.mark.parametrize("nodes", [500])
@pytest.mark.parametrize("read_func", [geff.read_nx, geff.read_rx, geff.read_sg])
def test_bench_read(read_func: Callable, benchmark: BenchmarkFixture, nodes: int) -> None:
    graph_path = graph_file_path(nodes)
    benchmark(read_func, graph_path, validate=False)
