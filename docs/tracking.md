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

<!--  TODO: provide example graphs with valid and invalid annotations -->
