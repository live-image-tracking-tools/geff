from __future__ import annotations

from importlib.util import find_spec
from typing import TYPE_CHECKING, Any, Literal, TypeAlias, TypeVar, get_args, overload

R = TypeVar("R", covariant=True)

if TYPE_CHECKING:
    import networkx as nx
    import rustworkx as rx
    import spatial_graph as sg
    from zarr.storage import StoreLike

    from geff.metadata._schema import GeffMetadata
    from geff.validate.data import ValidationConfig

    from ._backend_protocol import Backend

    NxGraph: TypeAlias = nx.Graph | nx.DiGraph
    RxGraph: TypeAlias = rx.PyGraph | rx.PyDiGraph
    SgGraph: TypeAlias = sg.SpatialGraph | sg.SpatialDiGraph
    SupportedGraphType: TypeAlias = NxGraph | RxGraph | SgGraph

SupportedBackend = Literal["networkx", "rustworkx", "spatial-graph"]


# A dictionary to map between supported backend literals and the correct type
# Used in the get_backend_from_type function below
BACKEND_TYPE_MAP: dict[SupportedBackend, tuple[type[SupportedGraphType], ...]]


# Used in the write function wrapper, where the backend should be determined from the graph type
def get_backend_from_graph_type(graph: SupportedGraphType) -> Backend:
    for backend, graph_type in BACKEND_TYPE_MAP.items():
        if isinstance(graph, graph_type):
            return get_backend(backend)
    raise TypeError(f"Unrecognized graph type '{type(graph)}'.")


@overload
def get_backend(backend: Literal["networkx"]) -> Backend[NxGraph]: ...


@overload
def get_backend(
    backend: Literal["rustworkx"],
) -> Backend[RxGraph]: ...


@overload
def get_backend(
    backend: Literal["spatial-graph"],
) -> Backend[SgGraph]: ...


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


# Only installed backends will be added to the backend type map
def _create_backend_type_map() -> dict[SupportedBackend, tuple[type[SupportedGraphType], ...]]:
    mapping: dict[SupportedBackend, tuple[type[SupportedGraphType], ...]] = {}
    backends: tuple[SupportedBackend] = get_args(SupportedBackend)
    for backend in backends:
        if find_spec(backend) is not None:
            backend_io = get_backend(backend)
            mapping[backend] = backend_io.GRAPH_TYPES
    return mapping


BACKEND_TYPE_MAP = _create_backend_type_map()


@overload
def read(
    store: StoreLike,
    structure_validation: bool = ...,
    node_props: list[str] | None = ...,
    edge_props: list[str] | None = ...,
    data_validation: ValidationConfig | None = ...,
    *,
    backend: Literal["networkx"] = "networkx",
) -> tuple[NxGraph, GeffMetadata]: ...


@overload
def read(
    store: StoreLike,
    structure_validation: bool,
    node_props: list[str] | None = ...,
    edge_props: list[str] | None = ...,
    data_validation: ValidationConfig | None = ...,
    *,
    backend: Literal["rustworkx"],
) -> tuple[RxGraph, GeffMetadata]: ...


@overload
def read(
    store: StoreLike,
    structure_validation: bool = ...,
    node_props: list[str] | None = ...,
    edge_props: list[str] | None = ...,
    data_validation: ValidationConfig | None = ...,
    *,
    backend: Literal["spatial-graph"],
    position_attr: str = "position",
) -> tuple[SgGraph, GeffMetadata]: ...


# NOTE: when overloading read for a new backend, if additional arguments can be accepted, explicitly
# define them such as in the spatial-graph overload above, where position_attr has been added.


def read(
    store: StoreLike,
    structure_validation: bool = True,
    node_props: list[str] | None = None,
    edge_props: list[str] | None = None,
    data_validation: ValidationConfig | None = None,
    *,
    backend: SupportedBackend = "networkx",
    **backend_kwargs: Any,
) -> tuple[Any, GeffMetadata]:
    """
    Read a GEFF to a chosen backend.

    Args:
        store (StoreLike): The path or zarr store to the root of the geff zarr, where
            the .attrs contains the geff  metadata.
        structure_validation (bool, optional): Flag indicating whether to perform validation on the
            geff file before loading into memory. If set to False and there are
            format issues, will likely fail with a cryptic error. Defaults to True.
        node_props (list of str, optional): The names of the node properties to load,
            if None all properties will be loaded, defaults to None.
        edge_props (list of str, optional): The names of the edge properties to load,
            if None all properties will be loaded, defaults to None.
        backend ({"networkx", "rustworkx", "spatial-graph"}): Flag for the chosen backend, default
            is "networkx".
        data_validation (ValidationConfig, optional): Optional configuration for which
            optional types of data to validate. Each option defaults to False.
        backend_kwargs (Any): Additional kwargs that may be accepted by
            the backend when reading the data.

    Returns:
        tuple[Any, GeffMetadata]: Graph object of the chosen backend, and the GEFF metadata.
    """
    backend_io = get_backend(backend)
    return backend_io.read(
        store,
        structure_validation,
        node_props,
        edge_props,
        data_validation,
        **backend_kwargs,
    )


# rustworkx has an additional nod_id_dict arg
@overload
def write(
    graph: rx.PyGraph | rx.PyDiGraph,
    store: StoreLike,
    metadata: GeffMetadata | None = None,
    axis_names: list[str] | None = None,
    axis_units: list[str | None] | None = None,
    axis_types: list[str | None] | None = None,
    zarr_format: Literal[2, 3] = 2,
    node_id_dict: dict[int, int] | None = None,
) -> None: ...


@overload
def write(
    graph: SupportedGraphType,
    store: StoreLike,
    metadata: GeffMetadata | None = None,
    axis_names: list[str] | None = None,
    axis_units: list[str | None] | None = None,
    axis_types: list[str | None] | None = None,
    zarr_format: Literal[2, 3] = 2,
    *args: Any,
    **kwargs: Any,
) -> None: ...


def write(
    graph: SupportedGraphType,
    store: StoreLike,
    metadata: GeffMetadata | None = None,
    axis_names: list[str] | None = None,
    axis_units: list[str | None] | None = None,
    axis_types: list[str | None] | None = None,
    zarr_format: Literal[2, 3] = 2,
    *args: Any,
    **kwargs: Any,
) -> None:
    backend_io = get_backend_from_graph_type(graph)
    backend_io.write(
        graph,
        store,
        metadata,
        axis_names,
        axis_units,
        axis_types,
        zarr_format,
        *args,
        **kwargs,
    )
