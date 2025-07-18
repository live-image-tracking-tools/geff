# Geff specification

The graph exchange file format is `zarr` based. A graph is stored in a zarr group, which can have any name. This allows storing multiple `geff` graphs inside the same zarr root directory. A `geff` group is identified by the presence of a `geff_version` attribute in the `.zattrs`. Other `geff` metadata is also stored in the `.zattrs` file of the `geff` group. The `geff` group must contain a `nodes` group and an `edges` group (albeit both can be empty). `geff` graphs have the option to provide properties for `nodes` and `edges`.

## Zarr specification

Currently, `geff` supports zarr specifications [2](https://zarr-specs.readthedocs.io/en/latest/v2/v2.0.html) and [3](https://zarr-specs.readthedocs.io/en/latest/v3/core/index.html). However, `geff` will default to writing specification 2 because graphs written to the zarr v3 spec will not be compatible with all applications. When zarr 3 is more fully adopted by other libraries and tools, we will move to a zarr spec 3 default.

## Geff metadata

{%
    include "schema/schema.html"
%}

## The `nodes` group
The nodes group will contain an `ids` array and optionally a `props` group. In the minimal case of an empty graph, the `ids` array can be empty. 

### The `ids` array
The `nodes\ids` array is a 1D array of node IDs of length `N` >= 0, where `N` is the number of nodes in the graph. Node ids must be unique. Node IDs can have any type supported by zarr (except floats), but we recommend integer dtypes. For large graphs, `uint64` might be necessary to provide enough range for every node to have a unique ID. 

### The `props` group and `node property` groups
The `nodes\props` group is optional and will contain one or more `node property` groups, each with a `values` array and an optional `missing` array.

- `values` arrays can be any zarr supported dtype, and can be N-dimensional. The first dimension of the `values` array must have the same length as the node `ids` array, such that each row of the property `values` array stores the property for the node at that index in the ids array.
- The `missing` array is an optional, a one dimensional boolean array to support properties that are not present on all nodes. A `1` at an index in the `missing` array indicates that the `value` of that property for the node at that index is None, and the value in the `values` array at that index should be ignored. If the `missing` array is not present, that means that all nodes have values for the property.

-  Position and time are special properties. When used, an `axes` must be specified in the `geff` metadata, which is a list of dictionaries. Each dictionary represents one property, and requires `name`, and optionally `type`, `unit`, `min`, and `max` (see example below), following the [some-zarr](https://ngff.openmicroscopy.org/0.5/index.html#axes-md) specifications.

!!! note:
When writing a graph with missing properties to the geff format, you must fill in a dummy value in the `values` array for the nodes that are missing the property, in order to keep the indices aligned with the node ids. **[TEUN: IS THIS STILL TRUE???]**

## The `edges` group
Similar to the `nodes` group, the `edges` group will contain an `ids` array and an optional `props` group. If there are no edges in the graph, the edge group and `ids` array have to be present, but can be empty. 

### The `ids` array
The `edges\ids` array is a 2D array with the same dtype as the `nodes\ids` array. It has shape `(2, E)`, where `E` is the number of edges in the graph. All elements in the `edges\ids` array must also be present in the `nodes\ids` array.
Each row represents an edge between two nodes. For directed graphs, the first column is the source nodes and the second column holds the target nodes. For undirected graphs, the order is arbitrary.
Edges should be unique (no multiple edges between the same two nodes) and edges from a node to itself are not supported.

### The `props` group and `edge property` groups
The `edges\props` group will contain zero or more `edge property` groups, each with a `values` array and an optional `missing` array.

- `values` arrays can be any zarr supported dtype, and can be N-dimensional. The first dimension of the `values` array must have the same length as the `edges\ids` array, such that each row of the property `values` array stores the property for the edge at that index in the ids array.
- The `missing` array is an optional, a one dimensional boolean array to support properties that are not present on all edges. A `1` at an index in the `missing` array indicates that the `value` of that property for the edge at that index is missing, and the value in the `values` array at that index should be ignored. If the `missing` array is not present, that means that all edges have values for the property.

The `edges/props` is optional. If you do not have any edge properties, the `edges\props` can be absent. 

## Example file structure and metadata
Here is a schematic of the expected file structure.
``` python
/path/to.zarr
    /tracking_graph
	    .zattrs  # graph metadata with `geff_version`
	    nodes/
            ids  # shape: (N,)  dtype: uint64
            props/
                t/
                    values # shape: (N,) dtype: uint16
                z/
                    values # shape: (N,) dtype: float32
                y/
                    values # shape: (N,) dtype: float32
                x/
                    values # shape: (N,) dtype: float32
                color/
                    values # shape: (N, 4) dtype: float16
                    missing # shape: (N,) dtype: bool
	    edges/
            ids  # shape: (E, 2) dtype: uint64
            props/
                distance/
                    values # shape: (E,) dtype: float16
                score/
                    values # shape: (E,) dtype: float16
                    missing # shape: (E,) dtype: bool
    # optional:
    /segmentation 
    
    # unspecified, but totally okay:
    /raw 
```
This is a geff metadata zattrs file that matches the above example structure.
```json
# /path/to.zarr/tracking_graph/.zattrs
{
    "geff": {
        "axis_names": [ # optional
            "z",
            "y",
            "x"
        ],
        "axis_units": [ # optional
            "um",
            "um",
            "um"
        ],
        "directed": true,
        "geff_version": "0.1.3.dev4+gd5d1132.d20250616",
        "position_prop": "position",
        "roi_max": [ # Required if position_prop is specified
            4398.1,
            1877.7,
            2152.3
        ],
        "roi_min": [ # Required if position_prop is specified
            1523.368197,
            81.667,
            764.42
        ],
    }
    ... # custom other things are allowed and ignored by geff
}
```
