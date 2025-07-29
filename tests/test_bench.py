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
import rustworkx as rx
import spatial_graph as sg

import geff.networkx.io as geff_nx
import geff.rustworkx.io as geff_rx
import geff.spatial_graph.io as geff_sg
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


def create_rx_graph(num_nodes: int) -> rx.PyDiGraph:
    graph = rx.PyDiGraph()
    nodes, edges = node_data(num_nodes), edge_data(num_nodes)
    graph.add_nodes_from(nodes.values())
    graph.add_edges_from(((u, v, dd) for (u, v), dd in edges.items()))
    return graph


def create_sg_graph(num_nodes: int) -> sg.SpatialDiGraph:
    nodes, edges = node_data(num_nodes), edge_data(num_nodes)
    # Construct arrays of properties
    node_ids, positions = [], []
    for nid, attrs in nodes.items():
        positions.append([attrs["t"], attrs["z"], attrs["y"], attrs["x"]])
        node_ids.append(nid)
    node_ids = np.array(node_ids)
    positions = np.array(positions)

    edge_ids, float_prop, int_prop = [], [], []
    for eid, attrs in edges.items():
        edge_ids.append(eid)
        float_prop.append(attrs["float_prop"])
        int_prop.append(attrs["int_prop"])
    edge_ids = np.array(edge_ids)
    float_prop = np.array(float_prop)
    int_prop = np.array(int_prop)

    create_graph = getattr(sg, "create_graph", sg.SpatialGraph)
    graph = create_graph(
        ndims=4,
        node_dtype="int64",
        node_attr_dtypes={"position": "float64[4]"},
        edge_attr_dtypes={"float_prop": "float64", "int_prop": "int64"},
        position_attr="position",
        directed=True,
    )
    graph.add_nodes(node_ids, position=positions)
    graph.add_edges(edge_ids, float_prop=float_prop, int_prop=int_prop)

    return graph


@cache
def graph_file_path(num_nodes: int) -> Path:
    tmp_dir = tempfile.mkdtemp(suffix=".zarr")
    atexit.register(shutil.rmtree, tmp_dir, ignore_errors=True)
    geff_nx.write_nx(
        graph=create_nx_graph(num_nodes), store=tmp_dir, axis_names=["t", "z", "y", "x"]
    )
    return Path(tmp_dir)


CREATE_FUNCS: Mapping[Callable, Callable[[int], Any]] = {
    geff_nx.write_nx: create_nx_graph,
    geff_rx.write_rx: create_rx_graph,
    geff_sg.write_sg: create_sg_graph,
}

# ###########################   TESTS   ##################################


@pytest.mark.parametrize("nodes", [500])
@pytest.mark.parametrize("write_func", [geff_nx.write_nx, geff_rx.write_rx, geff_sg.write_sg])
def test_bench_write(
    write_func: Callable, benchmark: BenchmarkFixture, tmp_path: Path, nodes: int
) -> None:
    path = tmp_path / "test_write.zarr"
    big_graph = CREATE_FUNCS[write_func](nodes)
    benchmark.pedantic(
        write_func,
        kwargs={"graph": big_graph, "axis_names": ["t", "z", "y", "x"], "store": path},
        setup=lambda **__: shutil.rmtree(path, ignore_errors=True),  # delete previous zarr
    )


@pytest.mark.parametrize("nodes", [500])
def test_bench_validate(benchmark: BenchmarkFixture, nodes: int) -> None:
    big_graph_path = graph_file_path(nodes)
    benchmark(validate, store=big_graph_path)


@pytest.mark.parametrize("nodes", [500])
@pytest.mark.parametrize("read_func", [geff_nx.read_nx, geff_rx.read_rx, geff_sg.read_sg])
def test_bench_read(read_func: Callable, benchmark: BenchmarkFixture, nodes: int) -> None:
    big_graph_path = graph_file_path(nodes)
    benchmark(read_func, big_graph_path, validate=False)
