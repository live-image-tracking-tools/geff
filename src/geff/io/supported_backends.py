from enum import Enum


class SupportedBackend(str, Enum):
    """
    An enum containing all the backends that the `geff` API supports.

    Attributes:
        NETWORKX (str): Flag for the `networkx` backend.
    """

    NETWORKX = "networkx"
    # GRAPH_DICT can be removed when another backend is added, it is currently needed for overloads
    GRAPH_DICT = "graph_dict"
