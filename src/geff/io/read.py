from pathlib import Path
from typing import Any, Literal, Protocol, TypeVar, overload

import networkx as nx

from geff.dict_representation import GraphDict
from geff.geff_reader import read_to_dict
from geff.metadata_schema import GeffMetadata
from geff.networkx.io import _ingest_dict_nx

from .supported_backends import SupportedBackend

R = TypeVar("R", covariant=True)


class IngestFunc(Protocol[R]):
    """A protocol for callables that ingest a `GraphDict` to different backends."""

    def __call__(self, graph_dict: GraphDict, *args: Any, **kwargs: Any) -> tuple[R, GeffMetadata]:
        """
        The callable must have this function signature.

        The callable must have the first argument `graph_dict`, it may have additional
        args and kwargs.

        Args:
            graph_dict (GraphDict): A graph representation of the GEFF data.
            *args (Any): Optional args for ingesting the `graph_dict`.
            **kwargs (Any): Optional kwargs for ingesting the `graph_dict`.
        """
        ...


# !!! When a new backend is added new overloads for `read` should be added !!!


# When the GRAPH_DICT option is removed from SupportedBackend enum this can be removed.
# Currently need 2 options for the overloads to work properly
def ingest_graph_dict(graph_dict: GraphDict) -> tuple[GraphDict, GeffMetadata]:
    """
    This functional is essentially the identity.

    Args:
        graph_dict (GraphDict): A graph representation of the GEFF data.
    """
    return graph_dict, graph_dict["metadata"]


def get_ingest_func(backend: SupportedBackend) -> IngestFunc[Any]:
    """
    Get the ingest function for different backends.

    Args:
        backend (SupportedBackend): Flag for the chosen backend.

    Returns:
        IngestFunc: A function to ingest a `GraphDict` to the chosen backend.
    """
    match backend:
        case SupportedBackend.NETWORKX:
            return _ingest_dict_nx
        case SupportedBackend.GRAPH_DICT:
            return ingest_graph_dict
        # Add cases for new backends, remember to add overloads
        case _:
            raise ValueError(f"Unsupported backend chosen: '{backend.value}'")


@overload
def read(
    path: Path | str,
    validate: bool = True,
    node_props: list[str] | None = None,
    edge_props: list[str] | None = None,
    backend: Literal[SupportedBackend.NETWORKX] = SupportedBackend.NETWORKX,
    backend_kwargs: dict[str, Any] | None = None,
) -> tuple[nx.Graph | nx.DiGraph, GeffMetadata]: ...


@overload
def read(
    path: Path | str,
    validate: bool,
    node_props: list[str] | None,
    edge_props: list[str] | None,
    backend: Literal[SupportedBackend.GRAPH_DICT],
    backend_kwargs: dict[str, Any] | None = None,
) -> tuple[GraphDict, GeffMetadata]: ...


def read(
    path: Path | str,
    validate: bool = True,
    node_props: list[str] | None = None,
    edge_props: list[str] | None = None,
    backend: SupportedBackend = SupportedBackend.NETWORKX,
    backend_kwargs: dict[str, Any] | None = None,
) -> tuple[Any, GeffMetadata]:
    """
    Read a GEFF to a chosen backend.

    Args:
        path (Path | str): The path to the root of the geff zarr, where the .attrs contains
            the geff  metadata
        validate (bool, optional): Flag indicating whether to perform validation on the
            geff file before loading into memory. If set to False and there are
            format issues, will likely fail with a cryptic error. Defaults to True.
        node_props (list of str, optional): The names of the node properties to load,
            if None all properties will be loaded, defaults to None.
        edge_props (list of str, optional): The names of the edge properties to load,
            if None all properties will be loaded, defaults to None.
        backend (SupportedBackend): Flag for the chosen backend, default is "networkx".
        backend_kwargs (dict of {str: Any}): Additional kwargs that may be accepted by
            the backend when reading the data.

    Returns:
        graph (Any): Graph object of the chosen backend.
        metadata (GeffMetadata): The GEFF metadata.
    """
    ingest_func = get_ingest_func(backend)
    if backend_kwargs is None:
        backend_kwargs = {}
    graph_dict = read_to_dict(path, validate, node_props, edge_props)
    return ingest_func(graph_dict, **backend_kwargs)
