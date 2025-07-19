# Geff specification

The graph exchange file format is `zarr` based. A graph is stored in a zarr group, which can have any name. This allows storing multiple `geff` graphs inside the same zarr root directory. A `geff` group is identified by the presence of a `geff_version` attribute in the `.zattrs`. Other `geff` metadata is also stored in the `.zattrs` file of the `geff` group. The `geff` group must contain a `nodes` group and an `edges` group.

`geff` graphs have the option to provide position as a special property. In this case, a `position_prop` must be specified in the `geff` metadata along with a `roi_min` and `roi_max`. If a `position_prop` is provided, every node must have a position value.

## Zarr specification

Currently, `geff` supports zarr specifications [2](https://zarr-specs.readthedocs.io/en/latest/v2/v2.0.html) and [3](https://zarr-specs.readthedocs.io/en/latest/v3/core/index.html). However, `geff` will default to writing specification 2 because graphs written to the zarr v3 spec will not be compatible with all applications. When zarr 3 is more fully adopted by other libraries and tools, we will move to a zarr spec 3 default.

## Geff metadata

{%
    include "schema/schema.html"
%}

## The `nodes` group
The nodes group will contain an `ids` array and a `props` group.

### The `ids` array
The `nodes\ids` array is a 1D array of node IDs of length `N` > 0, where `N` is the number of nodes in the graph. Node ids must be unique. Node IDs can have any type supported by zarr, but we recommend integer dtypes. For large graphs, `uint64` might be necessary to provide enough range for every node to have a unique ID. 

### The `props` group and `node property` groups
The `nodes\props` group will contain one or more `node property` groups, each with a `values` array and an optional `missing` array.

- `values` arrays can be any zarr supported dtype, and can be N-dimensional. The first dimension of the `values` array must have the same length as the node `ids` array, such that each row of the property `values` array stores the property for the node at that index in the ids array.
- The `missing` array is an optional, a one dimensional boolean array to support properties that are not present on all nodes. A 1 at an index in the `missing` array indicates that the `value` of that property for the node at that index is None, and the value in the `values` array at that index should be ignored. If the `missing` array is not present, that means that all nodes have values for the property.

!!! note
    When writing a graph with missing properties to the geff format, you must fill in a dummy value in the `values` array for the nodes that are missing the property, in order to keep the indices aligned with the node ids.

- The `position` group is a special node property group that must be present if a `position_prop` is set in the `geff` metadata and does not allow missing properties.
- The `seg_id` group is an optional, special node property group that stores the segmenatation label for each node. The `seg_id` values do not need to be unique, in case labels are repeated between time points. If the `seg_id` group is not present, it is assumed that the graph is not associated with a segmentation. 
<!-- Perhaps we just let the user specify the seg id property in the metadata instead? Then you can point it to the node ids if you wanted to -->

## The `edges` group
Similar to the `nodes` group, the `edges` group will contain an `ids` array and a `props` group. If there are no edges in the graph, the edge group is not created.

### The `ids` array
The `edges\ids` array is a 2D array with the same dtype as the `nodes\ids` array. It has shape `(2, E)`, where `E` is the number of edges in the graph. All elements in the `edges\ids` array must also be present in the `nodes\ids` array.
Each row represents an edge between two nodes. For directed graphs, the first column is the source nodes and the second column holds the target nodes. For undirected graphs, the order is arbitrary.
Edges should be unique (no multiple edges between the same two nodes) and edges from a node to itself are not supported.

### The `props` group and `edge property` groups
The `edges\props` group will contain zero or more `edge property` groups, each with a `values` array and an optional `missing` array.

- `values` arrays can be any zarr supported dtype, and can be N-dimensional. The first dimension of the `values` array must have the same length as the `edges\ids` array, such that each row of the property `values` array stores the property for the edge at that index in the ids array.
- The `missing` array is an optional, a one dimensional boolean array to support properties that are not present on all edges. A 1 at an index in the `missing` array indicates that the `value` of that property for the edge at that index is missing, and the value in the `values` array at that index should be ignored. If the `missing` array is not present, that means that all edges have values for the property.

If you do not have any edge properties, the `edges\props` group should still be present, but empty.

## Example file structure and metadata
Here is a schematic of the expected file structure.
``` python
/path/to.zarr
    /tracking_graph
	    .zattrs  # graph metadata with `geff_version`
	    nodes/
            ids  # shape: (N,)  dtype: uint64
            props/
                position/
                    values # shape: (N, 3) dtype: float16
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
