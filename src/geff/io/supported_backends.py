from enum import Enum


class SupportedBackend(str, Enum):
    NETWORKX = "networkx"
    DUMMY = "dummy"
