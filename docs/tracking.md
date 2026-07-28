# Tracking graph standards

While GEFFs can store any graphs, many of our core users are concerned with tracking cells in microscopy imagery.
Therefore, we provide special support and standardization for exchanging tracking GEFFs, or GEFFs that contain tracking outputs.

## Tracklet and lineage ID properties
Often when analyzing and visualizing tracking outputs, we assign IDs based on identity over time.
The geff specification supports specifying and validating optional node properties representing **tracklet** and **lineage** IDs.

- **Tracklet**: A simple path of connected nodes where the initiating node has any incoming degree and outgoing degree at most 1 and the terminating node has incoming degree at most 1 and any outgoing degree, and other nodes along the path have in/out degree of 1. Each tracklet must contain the maximal set of connected nodes that match this definition - no sub-tracklets.
- **Lineage**: a weakly connected component of the graph

The `tracklet` and `lineage` properties specified in the `track_node_props` section of the specification point to node properties that contain tracklet IDs or lineage IDs - each node in a tracklet/lineage has the same ID, and all nodes not in the same tracklet/lineage have different IDs. 

By providing and enforcing a definition of tracklet and lineage, and ensuring tracklet and lineage IDs can be exchanged rather than requiring them to be recomputed, we can ensure consistency of downstream analyses on the tracks across different tools.

### GEFFception for tracking

In order to store properties that apply to an entire tracklet or lineage as opposed to an individual node or edge, we recommend [geffception](./geffception.md). GEFFception allows for hierarchical nesting of geffs. 

In the example illustrated below, there are three levels of nested geffs.

```
core.geff/
    tracklet.geff/
        lineage.geff/
```

`core.geff` contains 12 nodes and 11 edges. Nodes have the property `tracklet_id` which corresponds to the ids of nodes in `tracklet.geff`. `core.geff` contains the following metadata and graph structure shown below:

```jsonc
"related_objects": [
    {
        "type": "geff",
        "path": "tracklet.geff",
        "node_prop": "tracklet_id"
    }
]
```

```
    a1(tracklet_id=1)
    |
    a2(tracklet_id=1)
    |
    +--------------------------+
    |                          |
    b1(tracklet_id=2)          c1(tracklet_id=3)
    |                          |
    b2(tracklet_id=2)          c2(tracklet_id=3)
                               +--------------------------+
                               |                          |
                               d1(tracklet_id=4)          e1(tracklet_id=5)
                               |                          |
                               d2(tracklet_id=4)          e2(tracklet_id=5)
                               |                          |
                               d3(tracklet_id=4)          e3(tracklet_id=5)
```

`tracklet.geff` contains 5 nodes and 4 edges. The nodes and their ids correspond to the tracklets in `core.geff`. Additionally, the nodes have the property `lineage_id` which corresponds to the node ids in `lineage.geff`. `tracklet.geff` contains the following metadata and graph structure shown below:

```jsonc
"related_objects": [
    {
        "type": "geff",
        "path": "lineage.geff",
        "node_prop": "lineage_id"
    }
]
```

```
a(id=1, lineage_id=1)
|
+----------------------+
|                      |
b(id=2, lineage_id=1)  c(id=3, lineage_id=1)
                       +----------------------+
                       |                      |
                       d(id=4, lineage_id=1)  e(id=5, lineage_id=1)
```

Finally, `lineage.geff` contains a single node whose id maps to the `lineage_id` property in `tracklet.geff`.

```
track_1(id=1)
```




<!--  TODO: provide example graphs with valid and invalid annotations -->
