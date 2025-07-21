from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    Protocol,
    TypeVar,
    overload,
)

import networkx as nx

from ..dict_representation import GraphDict
from ..geff_reader import read_to_dict
from ..metadata_schema import Axis, GeffMetadata
from ..networkx.io import _ingest_dict_nx
from .supported_backends import SupportedBackend

if TYPE_CHECKING:
    import networkx as nx

R = TypeVar("R", covariant=True)


class IngestFunc(Protocol[R]):
    def __call__(self, graph_dict: GraphDict, *args, **kwargs) -> tuple[R, GeffMetadata]: ...


def ingest_dict_dummy(graph_dict: GraphDict) -> tuple[int, GeffMetadata]:
    return 1, GeffMetadata(geff_version="0.3.0", directed=True, axes=[Axis(name="x")])


@overload
def get_ingest_func(
    backend: Literal[SupportedBackend.NETWORKX],
) -> IngestFunc[nx.Graph | nx.DiGraph]: ...


@overload
def get_ingest_func(backend: Literal[SupportedBackend.DUMMY]) -> IngestFunc[int]: ...


def get_ingest_func(backend: SupportedBackend) -> IngestFunc[Any]:
    match backend:
        case SupportedBackend.NETWORKX:
            ingest_func = _ingest_dict_nx
        case SupportedBackend.DUMMY:
            ingest_func = ingest_dict_dummy
        case _:
            raise ValueError
    return ingest_func


def read(
    path: Path | str,
    validate: bool = True,
    node_props: list[str] | None = None,
    edge_props: list[str] | None = None,
    ingest_func: IngestFunc[R] = _ingest_dict_nx,
    backend_kwargs: dict[str, Any] | None = None,
) -> tuple[R, GeffMetadata]:
    if backend_kwargs is None:
        backend_kwargs = {}
    graph_dict = read_to_dict(path, validate, node_props, edge_props)
    return ingest_func(graph_dict, **backend_kwargs)
