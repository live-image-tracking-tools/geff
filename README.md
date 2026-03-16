![](docs/images/GEFF_HorizontalLogo_RGB.png)

# Graph Exchange File Format 

<!--intro-start-->

[![License](https://img.shields.io/pypi/l/geff.svg?color=green)](https://github.com/live-image-tracking-tools/geff/raw/main/LICENSE)
[![geff PyPI](https://img.shields.io/pypi/v/geff?label=geff%20pypi&color=green)](https://pypi.org/project/geff)
[![geff Conda Version](https://img.shields.io/conda/vn/conda-forge/geff?label=geff%20conda-forge)](https://anaconda.org/conda-forge/geff)
[![geff-spec PyPI](https://img.shields.io/pypi/v/geff-spec?label=geff-spec%20pypi&color=green)](https://pypi.org/project/geff-spec) 
[![geff-spec Conda Version](https://img.shields.io/conda/vn/conda-forge/geff-spec?label=geff-spec%20conda-forge)](https://anaconda.org/conda-forge/geff-spec)
[![Python Version](https://img.shields.io/pypi/pyversions/geff.svg?color=green)](https://python.org)
[![Test geff](https://github.com/live-image-tracking-tools/geff/actions/workflows/ci.yaml/badge.svg)](https://github.com/live-image-tracking-tools/geff/actions/workflows/ci.yaml)
[![Benchmarks](https://img.shields.io/endpoint?url=https://codspeed.io/badge.json)](https://codspeed.io/live-image-tracking-tools/geff)

GEFF is a specification for a file format for **exchanging** spatial graph data. It is not intended to be mutable, editable, chunked, or optimized for use in an application setting.

This repository contains two packages:
- `geff-spec` is the specification of GEFF metadata written with [`pydantic`](https://docs.pydantic.dev/latest/) `BaseModels` which are exported to a json schema for use in other languages.
- `geff` is the python library that reads and writes GEFF files to and from several python in-memory graph data structures ([`networkx`](https://networkx.org/en/), [`rustworkx`](https://www.rustworkx.org/) and [`spatial-graph`](https://funkelab.github.io/spatial_graph/)).

Learn more in the [documentation](https://live-image-tracking-tools.github.io/geff/latest/) or check out the [source code](https://github.com/live-image-tracking-tools/geff).

## Installation

```
pip install geff
```
or
```
conda install conda-forge::geff
```

## Quick Start

For this example, we will use a simple [`networkx`](https://networkx.org/en/) graph, but `geff` can write graphs created with [`networkx`](https://networkx.org/en/), [`rustworkx`](https://www.rustworkx.org/) and [`spatial-graph`](https://funkelab.github.io/spatial_graph/).

```python
import networkx as nx

# Create a simple networkx graph with 10 nodes connected sequentially
node_ids = range(10)
nodes = []
for t, node in enumerate(node_ids):
    # Each node has an attribute "t"
    nodes.append((node, {"t": t}))

edges = []
for i in range(len(node_ids) - 1):
    # Each edge has an attribute "color"
    edges.append((node_ids[i], node_ids[i + 1], {"color": "red"}))

graph = nx.DiGraph()
graph.add_nodes_from(nodes)
graph.add_edges_from(edges)
```

The simplest `geff` requires only a graph.
```python
from geff import write, read

write(
    graph,
    "simple.geff",
    zarr_format=2  # 2 or 3
)

read_graph = read(
    "simple.geff",
    backend="networkx"  # or "spatial-graph" or "rustworkx"
)
```

Basic metadata about spatial-temporal axes can be included in the write function call. Additional metadata defined in the `geff-spec` can be included by creating a `GeffMetadata` object.
```python
write(
    graph,
    "simple-metadata.geff",
    axis_names=["t"],
    axis_units=["second"],
    axis_types=["time"]
)
```
<!--intro-end-->
