from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("geff")
except PackageNotFoundError:
    __version__ = "uninstalled"

from .metadata_schema import GeffMetadata
from .networkx.io import read_nx, write_nx
from .rustworkx.io import read_rx
from .utils import validate

__all__ = ["GeffMetadata", "read_nx", "read_rx", "validate", "write_nx"]
