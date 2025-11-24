![](docs/images/GEFF_HorizontalLogo_RGB.png)

# Graph Exchange File Format 

<!--intro-start-->

[![License](https://img.shields.io/pypi/l/geff.svg?color=green)](https://github.com/live-image-tracking-tools/geff/raw/main/LICENSE)
[![geff PyPI](https://img.shields.io/pypi/v/geff?label=geff%20pypi&color=green)](https://pypi.org/project/geff)
[![geff Conda Version](https://img.shields.io/conda/vn/conda-forge/geff.svg)](https://anaconda.org/conda-forge/geff)
[![geff-spec PyPI](https://img.shields.io/pypi/v/geff-spec?label=geff-spec%20pypi&color=green)](https://pypi.org/project/geff-spec) 
[![geff-spec Conda Version](https://img.shields.io/conda/vn/conda-forge/geff-spec.svg)](https://anaconda.org/conda-forge/geff-spec)
[![Python Version](https://img.shields.io/pypi/pyversions/geff.svg?color=green)](https://python.org)
[![Test geff](https://github.com/live-image-tracking-tools/geff/actions/workflows/ci.yaml/badge.svg)](https://github.com/live-image-tracking-tools/geff/actions/workflows/ci.yaml)
[![Benchmarks](https://img.shields.io/endpoint?url=https://codspeed.io/badge.json)](https://codspeed.io/live-image-tracking-tools/geff)

GEFF is a specification for a file format for **exchanging** spatial graph data. It is not intended to be mutable, editable, chunked, or optimized for use in an application setting.

This repository contains two packages:
- `geff-spec` is the specification of GEFF metadata written with `pydantic` `BaseModels` which are exported to a json schema for use in other languages.
- `geff` is the python library that reads and writes GEFF files to and from several python in-memory graph data structures (`networkx`, `rustworkx` and `spatial-graph`).

Learn more in the [documentation](https://live-image-tracking-tools.github.io/geff/latest/) or check out the [source code](https://github.com/live-image-tracking-tools/geff).

## Installation

```
pip install geff
```
<!--intro-end-->
