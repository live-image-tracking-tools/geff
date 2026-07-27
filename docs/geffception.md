# Geffception

The GEFF specification supports hierarchical nesting of GEFF files. This is particularly useful in the context of cell tracking where some properties may be computed for an entire tracklet or lineage as opposed to for an individual node or edge. For a complete example of a tracking graph that uses geffception to store tracklet and lineage properties, see [the tracking docs](./tracking.md).

In the example illustrated below, `tracking_graph.geff` contains nodes with the properties `track_id`, `t`, `y`, and `x` and edges with the property `distance`. Within the folder structure of `tracking_graph.geff` is `lineage.geff`. The `GeffMetadata` of `tracking_graph.geff` points to `lineage.geff` as a related object whose node ids correspond to the `track_id` property of nodes in `tracking_graph.geff`.

```python
/path/to.zarr
    tracking_graph.geff/
        .zattrs # graph metadata with `geff_version` and RelatedObject metadata for lineage.geff
        nodes/ 
            ids # shape: (N,) dtype: uint64
            props/
                track_id/
                    values # shape: (N,) dtype: uint16
                t/
                    values # shape: (N,) dtype: uint16
                y/
                    values # shape: (N,) dtype: float32
                x/
                    values # shape: (N,) dtype: float32
        edges/
            ids # shape: (E, 2) dtype: uint64
            props/
                distance/
                    values # shape: (E,) dtype: float32
        lineage.geff/
            .zattrs # geff metadata
            nodes/
                ids # shape: (L,) dtype: uint64
                props/
                    track_displacement/
                        values # shape: (L,) dtype: float32
            edges/
                ids # shape: (0,) dytpe: uint64
```

```jsonc
// /path/to.zarr/tracking_graph.geff/.zattrs
{
    "geff": {
        "directed": true,
        "geff_version": "1.2.0.1.1",
        "axes": [
            { 
                "name": "t", 
                "type": "time",
                "unit": "second", 
                "min": 0, 
                "max": 125 
            },
            {
                "name": "x",
                "type": "space",
                "unit": "micrometer",
                "min": 764.42,
                "max": 2152.3
            },
            {
                "name": "y",
                "type": "space",
                "unit": "micrometer",
                "min": 81.667,
                "max": 1877.7
            }
        ],
        "node_props_metadata": {
            "track_id": {
                "identifier": "track_id",
                "dtype": "uint16",
                "varlength": false
            },
            "t": {
                "identifier": "t",
                "dtype": "uint16",
                "varlength": false,
                "unit": "second"
            },
            "y": {
                "identifier": "y",
                "dtype": "float32",
                "varlength": false,
                "unit": "micrometer"
            },
            "x": {
                "identifier": "x",
                "dtype": "float32",
                "varlength": false,
                "unit": "micrometer"
            }
        },
        "edge_props_metadata": {
            "distance": {
                "identifier": "distance",
                "dtype": "float32",
                "varlength": false
            }
        },
        "track_node_props": {
            "lineage": "track_id"
        },
        "related_objects": [
            {
                "type": "geff",
                "path": "lineage.geff",
                "node_prop": "track_id"
            }
        ]
    }
}
```

```jsonc
// /path/to.zarr/tracking_graph.geff/lineage.geff/.zattrs
{
    "geff": {
        "directed": true,
        "geff_version": "1.2.0.1.1",
        "node_props_metadata": {
            "track_displacement": {
                "identifier": "track_displacement",
                "dtype": "float32",
                "varlength": false
            }
        },
        "edge_props_metadata": {}
    }
}
```