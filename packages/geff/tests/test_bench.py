from __future__ import annotations

import sys

import pytest

# only run this file if benchmarks are requested, or running directly
if all(
    x not in {"--codspeed", "--benchmark", "packages/geff/tests/test_bench.py"} for x in sys.argv
):
    pytest.skip("use --benchmark to run benchmark", allow_module_level=True)

import atexit
import shutil
import tempfile
from functools import cache
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, get_args

import networkx as nx
import numpy as np

import geff
from geff._graph_libs._api_wrapper import SupportedBackend, get_backend

if TYPE_CHECKING:
    from collections.abc import Mapping

    from pytest_codspeed.plugin import BenchmarkFixture


np.random.seed(42)  # for reproducibility

# ###########################   Utils   ##################################

BACKEND_STRINGS: tuple[SupportedBackend] = get_args(SupportedBackend)


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
    geff.write(graph=create_nx_graph(num_nodes), store=tmp_dir, axis_names=["t", "z", "y", "x"])
    return Path(tmp_dir)


# ###########################   TESTS   ##################################

# to keep consistency before api refac
WRITE_TEST_IDS: dict[SupportedBackend, str] = {
    "networkx": "write_nx",
    "rustworkx": "write_rx",
    "spatial-graph": "write_sg",
}


@pytest.mark.parametrize("nodes", [500])
@pytest.mark.parametrize(
    "backend",
    BACKEND_STRINGS,
    # to keep consistency before api refac
    ids=[WRITE_TEST_IDS[backend] for backend in BACKEND_STRINGS],
)
def test_bench_write(
    backend: SupportedBackend, benchmark: BenchmarkFixture, tmp_path: Path, nodes: int
) -> None:
    path = tmp_path / "test_write.zarr"
    backend_io = get_backend(backend)
    write_func = backend_io.write
    read_func = backend_io.read
    graph = read_func(graph_file_path(nodes))[0]
    benchmark.pedantic(
        write_func,
        kwargs={"graph": graph, "axis_names": ["t", "z", "y", "x"], "store": path},
        setup=lambda **__: shutil.rmtree(path, ignore_errors=True),  # delete previous zarr
    )


@pytest.mark.parametrize("nodes", [500])
def test_bench_validate(benchmark: BenchmarkFixture, nodes: int) -> None:
    graph_path = graph_file_path(nodes)
    benchmark(geff.validate_structure, store=graph_path)


# to keep consistency before api refac
READ_TEST_IDS: dict[SupportedBackend, str] = {
    "networkx": "read_nx",
    "rustworkx": "read_rx",
    "spatial-graph": "read_sg",
}


@pytest.mark.parametrize("nodes", [500])
@pytest.mark.parametrize(
    "backend",
    BACKEND_STRINGS,
    # to keep consistency before api refac
    ids=[READ_TEST_IDS[backend] for backend in BACKEND_STRINGS],
)
def test_bench_read(backend: SupportedBackend, benchmark: BenchmarkFixture, nodes: int) -> None:
    read_func = get_backend(backend).read
    graph_path = graph_file_path(nodes)
    benchmark(read_func, graph_path, structure_validation=False)
