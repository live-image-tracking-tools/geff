from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("geff")
except PackageNotFoundError:
    __version__ = "uninstalled"

from .metadata_schema import GeffMetadata
from .networkx.io import read_nx, write_nx
from .utils import validate

__all__ = ["GeffMetadata", "read_nx", "validate", "write_nx"]
