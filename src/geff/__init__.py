from importlib.metadata import PackageNotFoundError, version
from typing import TYPE_CHECKING, Any

try:
    __version__: str = version("geff")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "uninstalled"

from ._graph_libs._api_wrapper import read
from ._graph_libs._networkx import read_nx, write_nx
from .core_io._base_read import GeffReader
from .metadata._schema import GeffMetadata
from .validate.structure import validate_structure

if TYPE_CHECKING:
    from geff._graph_libs._rustworkx import read_rx, write_rx
    from geff._graph_libs._spatial_graph import read_sg, write_sg


__all__ = [
    "GeffMetadata",
    "GeffReader",
    "read",
    "read_nx",
    "read_rx",
    "read_sg",
    "validate_structure",
    "write_nx",
    "write_rx",
    "write_sg",
]


def __getattr__(name: str) -> Any:
    if name in ("read_rx", "write_rx"):
        from geff._graph_libs import _rustworkx

        return getattr(_rustworkx, name)
    if name in ("read_sg", "write_sg"):
        from geff._graph_libs import _spatial_graph

        return getattr(_spatial_graph, name)

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
