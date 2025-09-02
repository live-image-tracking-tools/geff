from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, TypeVar, overload

from geff.core_io._base_read import read_to_memory

R = TypeVar("R", covariant=True)

if TYPE_CHECKING:
    import networkx as nx
    import rustworkx as rx
    import spatial_graph as sg
    from zarr.storage import StoreLike

    from geff.metadata._schema import GeffMetadata

    from ._backend_protocol import Backend

SupportedBackend = Literal["networkx", "rustworkx", "spatial-graph"]


@overload
def get_backend(backend: Literal["networkx"]) -> Backend[nx.Graph | nx.DiGraph]: ...


@overload
def get_backend(
    backend: Literal["rustworkx"],
) -> Backend[rx.PyGraph | rx.PyDiGraph]: ...


@overload
def get_backend(
    backend: Literal["spatial-graph"],
) -> Backend[sg.SpatialGraph | sg.SpatialDiGraph]: ...


# NOTE: overload get_backend for new backends by typing the return type as Backend[GraphType]


def get_backend(backend: SupportedBackend) -> Backend:
    """
    Get a specified backend io module.

    Args:
        backend (SupportedBackend): Flag for the chosen backend.

    Returns:
        Backend: A module for reading and writing GEFF data to and from the specified backend.
    """
    match backend:
        case "networkx":
            from geff._graph_libs._networkx import NxBackend

            return NxBackend()
        case "rustworkx":
            from geff._graph_libs._rustworkx import RxBackend

            return RxBackend()
        case "spatial-graph":
            from geff._graph_libs._spatial_graph import SgBackend

            return SgBackend()
        # Add cases for new backends, remember to add overloads
        case _:
            raise ValueError(f"Unsupported backend chosen: '{backend}'")


@overload
def read(
    store: StoreLike,
    validate: bool = True,
    node_props: list[str] | None = None,
    edge_props: list[str] | None = None,
    backend: Literal["networkx"] = "networkx",
) -> tuple[nx.Graph | nx.DiGraph, GeffMetadata]: ...


@overload
def read(
    store: StoreLike,
    validate: bool = ...,
    node_props: list[str] | None = ...,
    edge_props: list[str] | None = ...,
    *,
    backend: Literal["rustworkx"],
) -> tuple[rx.PyGraph | rx.PyDiGraph, GeffMetadata]: ...


@overload
def read(
    store: StoreLike,
    validate: bool = ...,
    node_props: list[str] | None = ...,
    edge_props: list[str] | None = ...,
    *,
    backend: Literal["spatial-graph"],
    position_attr: str = "position",
) -> tuple[sg.SpatialGraph | sg.SpatialDiGraph, GeffMetadata]: ...


# NOTE: when overloading read for a new backend, if additional arguments can be accepted, explicitly
# define them such as in the spatial-graph overload above, where position_attr has been added.


def read(
    store: StoreLike,
    validate: bool = True,
    node_props: list[str] | None = None,
    edge_props: list[str] | None = None,
    backend: SupportedBackend = "networkx",
    **backend_kwargs: Any,
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
        backend ({"networkx", "rustworkx", "spatial-graph"}): Flag for the chosen backend, default
            is "networkx".
        backend_kwargs (Any): Additional kwargs that may be accepted by
            the backend when reading the data.

    Returns:
        tuple[Any, GeffMetadata]: Graph object of the chosen backend, and the GEFF metadata.
    """
    backend_io = get_backend(backend)
    in_memory_geff = read_to_memory(store, validate, node_props, edge_props)
    return (
        backend_io.construct(**in_memory_geff, **backend_kwargs),
        in_memory_geff["metadata"],
    )
