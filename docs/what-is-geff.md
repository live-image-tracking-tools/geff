# What is geff?

`geff` is a graph exchange file format that seeks to fulfill the following needs:

- Provide a storage/exchange format for graphs and optional segmentation
- Provide a common API with reference implementations for use in other projects

## Design Decisions and Assumptions

- Raw image data is not included in the `geff` spec. However, to keep nodes linked to segmentation labels, support for specifying the seg_id of each node in a standard way, along with the path to the segmentation, are included in the `spec`.
- Since `geff` is an exchange format, we do not provide support for searching or filtering.
- We do not provide support for editing or changing the graph on the fly.
- In order to support efficient reading/writing, we assume the graph can fit into memory.