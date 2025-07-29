from enum import Enum


class SupportedBackend(str, Enum):
    """
    An enum containing all the backends that the `geff` API supports.

    Attributes:
        NETWORKX (str): Flag for the `networkx` backend.
    """

    NETWORKX = "networkx"
    RUSTWORKX = "rustworkx"
    SPATIAL_GRAPH = "spatial_graph"
