from importlib.metadata import PackageNotFoundError, version

try:
    __version__: str = version("geff")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "uninstalled"

from geff_spec import GeffMetadata

from ._graph_libs._api_wrapper import construct, read, write
from .core_io._base_read import GeffReader
from .validate.structure import validate_structure

__all__ = [
    "GeffMetadata",
    "GeffReader",
    "construct",
    "read",
    "validate_structure",
    "write",
]
