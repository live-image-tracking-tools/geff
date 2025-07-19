from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("geff")
except PackageNotFoundError:
    __version__ = "uninstalled"

from .metadata_schema import GeffMetadata
from .networkx.io import read_nx, write_nx
from .utils import validate


def __getattr__(name: str):
    if name == "read_sg":
        try:
            from .spatial_graph.io import read_sg

            return read_sg
        except ImportError as e:
            raise ImportError("install with geff[spatial_graph] to use read_sg") from e
    if name == "write_sg":
        try:
            from .spatial_graph.io import write_sg

            return write_sg
        except ImportError as e:
            raise ImportError("install with geff[spatial_graph] to use read_sg") from e
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = ["GeffMetadata", "read_nx", "read_sg", "validate", "write_nx", "write_sg"]
