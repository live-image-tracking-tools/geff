# Tips and Tricks

## Loading a subset of a GEFF

Using a lower level component ([`GeffReader`][geff.GeffReader]) of the `geff` API, it is possible to load a subset of a graph based on a mask that is applied either to nodes or edges. 

### Loading a subset of properties

```python
from geff import GeffReader, construct


# Open the geff file without reading any data into memory
geff_reader = GeffReader(path)

# Print names of available node/edge properties
print(reader.node_prop_names, reader.edge_prop_names)
# >>> (['t', 'x', 'y', 'label', 'score'] ['color', 'score'])

geff_reader.read_node_props(['t', 'x', 'y'])
# By default all edge properties will be loaded
geff_reader.read_edge_props()

# Read the data of the geff into memory including only properties that have been loaded
in_memory_geff = geff_reader.build()

# Construct a graph representation of the data with the backend of your choice
graph = construct(**in_memory_geff, backend="networkx")
# Nodes will contain the attributes t, x, and y
# Edges will contain the attributes color and score
```

### Filtering based on nodes

```python
from geff import GeffReader, construct


# Open the geff file without reading any data into memory
geff_reader = GeffReader(path)
# Load edge and node properties
geff_reader.read_node_props()
geff_reader.read_edge_props()
# Access the property values, load it into memory as a numpy and then create the mask
node_mask = file_reader.node_props["t"]["values"][:] < 5

# Read the data of the geff into memory using the mask to filter which nodes to load
in_memory_geff = geff_reader.build(node_mask=node_mask)

# Construct a graph representation of the data with the backend of your choice
graph = construct(**in_memory_geff, backend="networkx")
```

### Filtering based on edges

!!! note

    When loading a GEFF using an edge mask, by default all nodes will be loaded even if they are not contained within an unmasked edge. However `GeffReader.build` can take both a node and edge mask if constructed by the user.

```python
from geff import GeffReader, construct


# Open the geff file without reading any data into memory
geff_reader = GeffReader(path)
# Load edge and node properties
geff_reader.read_node_props()
geff_reader.read_edge_props()
# Access the property values, load it into memory as a numpy and then create the mask
edge_mask = file_reader.edge_props["score"]["values"][:] < 0.5

# Read the data of the geff into memory using the mask to filter which edges to load
in_memory_geff = geff_reader.build(edge_mask=edge_mask)

# Construct a graph representation of the data with the backend of your choice
graph = construct(**in_memory_geff, backend="networkx")
```