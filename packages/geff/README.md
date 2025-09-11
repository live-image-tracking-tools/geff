![](../../docs/images/GEFF_HorizontalLogo_RGB.png)

# Graph Exchange File Format 

[![License](https://img.shields.io/pypi/l/geff.svg?color=green)](https://github.com/live-image-tracking-tools/geff/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/geff.svg?color=green)](https://pypi.org/project/geff)
[![Python Version](https://img.shields.io/pypi/pyversions/geff.svg?color=green)](https://python.org)
[![Test geff](https://github.com/live-image-tracking-tools/geff/actions/workflows/ci.yaml/badge.svg)](https://github.com/live-image-tracking-tools/geff/actions/workflows/ci.yaml)
[![Benchmarks](https://img.shields.io/endpoint?url=https://codspeed.io/badge.json)](https://codspeed.io/live-image-tracking-tools/geff)

GEFF is a specification for a file format for **exchanging** spatial graph data. It is not intended to be mutable, editable, chunked, or optimized for use in an application setting.

The geff python library also includes implementations for writing from and reading to three different Python in-memory graph data structures (`networkx`, `rustworkx` and `spatial-graph`). The library uses semantic versioning, where changes to the specification bump the major or minor versions, and bugfixes for the example implementation bumps the patch version.

Learn more in the [documentation](https://live-image-tracking-tools.github.io/geff/latest/) or check out the [source code](https://github.com/live-image-tracking-tools/geff).

## Installation

```
pip install geff
```
