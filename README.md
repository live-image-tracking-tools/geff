# Graph Exchange File Format (geff)
geff is a specification for a file format for **exchanging** spatial graph data. It is not intended to be mutable, editable, chunked, or optimized for use in an application setting.

geff is the specification of the file format, but the library also includes implementations for writing from and reading to Python in-memory graph data structures: networkx and spatial_graph. The library uses semantic versioning, where changes to the specification bump the major or minor versions, and bugfixes for the example implementations bump the patch version.