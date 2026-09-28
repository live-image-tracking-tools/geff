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

geff_reader.read_node_props(["t", "x", "y"])
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

## Relative Paths

Relative paths need to be defined for [RelatedObjects](geff_spec.RelatedObject) including [geffception](./geffception.md). The source object for the relative path is the geff directory.

```python
from pathlib import Path

geff_source = Path("/path/to/graph.geff")
```

If the target of the `RelatedObject` is another geff, the path should point to the geff directory of the related geff.

```python
from pathlib import Path

target = Path("graph.geff/lineage.geff")
rel_path = target.relative_to(source, walk_up=True)
print(rel_path)
# 'lineage.geff'
```

A geff containing tracking data may be located within a larger zarr that contains the source imaging data and segmentation labels as illustrated below. In this case, the relative path will point to a directory 

```
/path/to/big.zarr
    zarr.json
    images/
        zarr.json
    labels/
        zarr.json
    tracks.geff/
        zarr.json
```

```python
from pathlib import Path

source_geff = Path("/path/to/big.zarr/tracks.geff")
labels = Path("/path/to/big.zarr/labels")
images = Path("/path/to/big.zarr/images")

rel_labels = labels.relative_to(source_geff, walk_up=True)
print(rel_labels)
# '../labels'

rel_images = images.relative_to(source_geff, walk_up=True)
print(rel_images)
# '../images'
```

### OME-Zarr and Multiscale data

Related objects that follow OME-Zarr conventions and may contain multiscale data should point to the lowest level zarr group that contains the multiscale arrays.

```
/path/to/data/
    zarr.json
    raw.ome.zarr/ ...
    deconv.ome.zarr/
        zarr.json
        0/ # image multiscales
        1/
        labels/
            zarr.json
            nucleus/
                zarr.json
                0/ # segmentation multiscales
                1/
        tracks/
            nucleus.geff/
                zarr.json
```

```python
from pathlib import Path

deconv = Path("/path/to/data/deconv.ome.zarr")
nuc_labels = Path("/path/to/data/deconv.ome.zarr/labels/nucleus")
geff = Path("/path/to/data/deconv.ome.zarr/tracks/nucleus.geff")

image_rel_path = deconv.relative_to(geff, walk_up=True)
print(image_rel_path)
# '../..'

labels_rel_path = nuc_labels.relative_to(geff, walk_up=True)
print(labels_rel_path)
# '../../labels/nucleus'
```