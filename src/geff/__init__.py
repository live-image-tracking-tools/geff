from importlib.metadata import PackageNotFoundError, version
from typing import TYPE_CHECKING, Any

try:
    __version__: str = version("geff")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "uninstalled"

from .graph_libs._networkx import read_nx, write_nx
from .metadata_schema import GeffMetadata
from .utils import validate

if TYPE_CHECKING:
    from geff.graph_libs._rustworkx import read_rx, write_rx
    from geff.spatial_graph.io import read_sg, write_sg


__all__ = [
    "GeffMetadata",
    "read_nx",
    "read_rx",
    "read_sg",
    "validate",
    "write_nx",
    "write_rx",
    "write_sg",
]


def __getattr__(name: str) -> Any:
    if name in ("read_rx", "write_rx"):
        from geff.graph_libs import _rustworkx

        return getattr(_rustworkx, name)
    if name in ("read_sg", "write_sg"):
        from geff.spatial_graph import io

        return getattr(io, name)

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
