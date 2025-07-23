from typing import Any, Literal, Protocol, TypeVar, overload

import networkx as nx
from zarr.storage import StoreLike

from geff.dict_representation import GraphDict
from geff.geff_reader import read_to_dict
from geff.metadata_schema import GeffMetadata
from geff.networkx.io import construct_nx

from .supported_backends import SupportedBackend

R = TypeVar("R", covariant=True)

# !!! Add new overloads for `read` and `get_construct_func` when a new backend is added !!!

# When the GRAPH_DICT option is removed from SupportedBackend enum this can be removed.
# Currently need 2 options for the overloads to work properly


class ConstructFunc(Protocol[R]):
    """A protocol for callables that convert a `GraphDict` to different backends."""

    def __call__(self, graph_dict: GraphDict, *args: Any, **kwargs: Any) -> R:
        """
        The callable must have this function signature.

        The callable must have the first argument `graph_dict`, it may have additional
        args and kwargs.

        Args:
            graph_dict (GraphDict): A graph representation of the GEFF data.
            *args (Any): Optional args for constructing the `graph_dict`.
            **kwargs (Any): Optional kwargs for constructing the `graph_dict`.
        """
        ...


# temporary dummy construct func
def construct_identity(graph_dict: GraphDict) -> GraphDict:
    """
    This functional is the identity.

    Args:
        graph_dict (GraphDict): A dictionary representation of the GEFF data.

    Returns:
        (GraphDict): A dictionary representation of the GEFF data.
    """
    return graph_dict


@overload
def get_construct_func(
    backend: Literal[SupportedBackend.NETWORKX],
) -> ConstructFunc[nx.Graph | nx.DiGraph]: ...


@overload
def get_construct_func(
    backend: Literal[SupportedBackend.GRAPH_DICT],
) -> ConstructFunc[GraphDict]: ...


def get_construct_func(backend: SupportedBackend) -> ConstructFunc[Any]:
    """
    Get the construct function for different backends.

    Args:
        backend (SupportedBackend): Flag for the chosen backend.

    Returns:
        ConstructFunc: A function to convert a `GraphDict` to the chosen backend.
    """
    match backend:
        case SupportedBackend.NETWORKX:
            return construct_nx
        case SupportedBackend.GRAPH_DICT:
            return construct_identity
        # Add cases for new backends, remember to add overloads
        case _:
            raise ValueError(f"Unsupported backend chosen: '{backend.value}'")


@overload
def read(
    store: StoreLike,
    validate: bool = True,
    node_props: list[str] | None = None,
    edge_props: list[str] | None = None,
    backend: Literal[SupportedBackend.NETWORKX] = SupportedBackend.NETWORKX,
    backend_kwargs: dict[str, Any] | None = None,
) -> tuple[nx.Graph | nx.DiGraph, GeffMetadata]: ...


@overload
def read(
    store: StoreLike,
    validate: bool,
    node_props: list[str] | None,
    edge_props: list[str] | None,
    backend: Literal[SupportedBackend.GRAPH_DICT],
    backend_kwargs: dict[str, Any] | None = None,
) -> tuple[GraphDict, GeffMetadata]: ...


def read(
    store: StoreLike,
    validate: bool = True,
    node_props: list[str] | None = None,
    edge_props: list[str] | None = None,
    # using Literal because mypy can't seem to narrow the enum type when chaining functions
    backend: Literal[
        SupportedBackend.NETWORKX,
        SupportedBackend.GRAPH_DICT,
    ] = SupportedBackend.NETWORKX,
    backend_kwargs: dict[str, Any] | None = None,
) -> tuple[Any, GeffMetadata]:
    """
    Read a GEFF to a chosen backend.

    Args:
        store (StoreLike): The path or zarr store to the root of the geff zarr, where
            the .attrs contains the geff  metadata.
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
        tuple[Any, GeffMetadata]: Graph object of the chosen backend, and the GEFF metadata.
    """
    construct_func = get_construct_func(backend)
    if backend_kwargs is None:
        backend_kwargs = {}
    graph_dict = read_to_dict(store, validate, node_props, edge_props)
    return construct_func(graph_dict, **backend_kwargs), graph_dict["metadata"]
