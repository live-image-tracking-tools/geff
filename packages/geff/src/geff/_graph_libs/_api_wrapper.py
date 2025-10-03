from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, TypeAlias, TypeVar, get_args, overload

from ._errors import MissingDependencyError

R = TypeVar("R", covariant=True)

if TYPE_CHECKING:
    import networkx as nx
    import rustworkx as rx
    import spatial_graph as sg
    from numpy.typing import NDArray
    from zarr.storage import StoreLike

    from geff._typing import PropDictNpArray
    from geff.validate.data import ValidationConfig
    from geff_spec import AxisType, GeffMetadata

    from ._backend_protocol import Backend

    NxGraph: TypeAlias = nx.Graph[Any] | nx.DiGraph[Any]
    RxGraph: TypeAlias = rx.PyGraph | rx.PyDiGraph
    SgGraph: TypeAlias = sg.SpatialGraph | sg.SpatialDiGraph
    SupportedGraphType: TypeAlias = NxGraph | RxGraph | SgGraph

SupportedBackend = Literal["networkx", "rustworkx", "spatial-graph"]

AVAILABLE_BACKENDS: list[Backend] = []


# This function will add available backends to the available backend list
# it has to be called after the definition of get_backends
def _import_available_backends() -> None:
    backends: tuple[SupportedBackend] = get_args(SupportedBackend)
    for backend in backends:
        try:
            AVAILABLE_BACKENDS.append(get_backend(backend))
        except MissingDependencyError:
            pass


# NOTE: overload get_backend for new backends by typing the return type as Backend[GraphType]
@overload
def get_backend(backend: Literal["networkx"]) -> Backend[NxGraph]: ...
@overload
def get_backend(backend: Literal["rustworkx"]) -> Backend[RxGraph]: ...
@overload
def get_backend(backend: Literal["spatial-graph"]) -> Backend[SgGraph]: ...
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


_import_available_backends()


# Used in the write function wrapper, where the backend should be determined from the graph type
def get_backend_from_graph_type(graph: SupportedGraphType) -> Backend[SupportedGraphType]:
    for backend_module in AVAILABLE_BACKENDS:
        if isinstance(graph, backend_module.GRAPH_TYPES):
            return backend_module
    raise TypeError(f"Unrecognized graph type '{type(graph)}'.")


# NOTE: when overloading read for a new backend, if additional arguments can be accepted, explicitly
# define them such as in the spatial-graph overload below, where position_attr has been added.
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
    structure_validation: bool = ...,
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
def read(
    store: StoreLike,
    structure_validation: bool = True,
    node_props: list[str] | None = None,
    edge_props: list[str] | None = None,
    data_validation: ValidationConfig | None = None,
    *,
    backend: SupportedBackend = "networkx",
    **backend_kwargs: Any,
) -> tuple[SupportedGraphType, GeffMetadata]:
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


@overload
def construct(
    metadata: GeffMetadata,
    node_ids: NDArray[Any],
    edge_ids: NDArray[Any],
    node_props: dict[str, PropDictNpArray],
    edge_props: dict[str, PropDictNpArray],
    *,
    backend: Literal["networkx"] = ...,
) -> NxGraph: ...
@overload
def construct(
    metadata: GeffMetadata,
    node_ids: NDArray[Any],
    edge_ids: NDArray[Any],
    node_props: dict[str, PropDictNpArray],
    edge_props: dict[str, PropDictNpArray],
    *,
    backend: Literal["rustworkx"],
) -> RxGraph: ...
@overload
def construct(
    metadata: GeffMetadata,
    node_ids: NDArray[Any],
    edge_ids: NDArray[Any],
    node_props: dict[str, PropDictNpArray],
    edge_props: dict[str, PropDictNpArray],
    *,
    backend: Literal["spatial-graph"],
    position_attr: str = "position",
) -> SgGraph: ...
def construct(
    metadata: GeffMetadata,
    node_ids: NDArray[Any],
    edge_ids: NDArray[Any],
    node_props: dict[str, PropDictNpArray],
    edge_props: dict[str, PropDictNpArray],
    *,
    backend: SupportedBackend = "networkx",
    **backend_kwargs: Any,
) -> SupportedGraphType:
    backend_io = get_backend(backend)
    return backend_io.construct(
        metadata, node_ids, edge_ids, node_props, edge_props, **backend_kwargs
    )


# rustworkx has an additional node_id_dict arg
@overload
def write(
    graph: RxGraph,
    store: StoreLike,
    metadata: GeffMetadata | None = ...,
    axis_names: list[str] | None = ...,
    axis_units: list[str | None] | None = ...,
    axis_types: list[AxisType | None] | None = ...,
    axis_scales: list[float | None] | None = ...,
    scaled_units: list[str | None] | None = ...,
    axis_offset: list[float | None] | None = ...,
    zarr_format: Literal[2, 3] = ...,
    structure_validation: bool = True,
    node_id_dict: dict[int, int] | None = ...,
) -> None:
    # TODO: what is best practice for overload docstrings, want to document node_id_dict
    """Write a rustworkx graph object to the geff file format.

    Args:
        graph (SupportedGraphType): An instance of a supported graph object.
        store (str | Path | zarr store): The path/str to the output zarr, or the store
            itself. Opens in append mode, so will only overwrite geff-controlled groups.
        metadata (GeffMetadata, optional): The original metadata of the graph.
            Defaults to None. If provided, will override the graph properties.
        axis_names (list[str], optional): The names of the spatial dims
            represented in position property. Defaults to None. Will override
            both value in graph properties and metadata if provided.
        axis_units (list[str | None], optional): The units of the spatial dims
            represented in position property. Defaults to None. Will override value
            both value in graph properties and metadata if provided.
        axis_types (list[Literal[AxisType] | None], optional): The types of the spatial dims
            represented in position property. Usually one of "time", "space", or "channel".
            Defaults to None. Will override both value in graph properties and metadata
            if provided.
        axis_scales (list[float | None] | None): The scale to apply to the spatial dims.
            Defaults to None.
        scaled_units (list[str | None] | None): The units of the spatial dims after scaling.
            Defaults to None.
        axis_offset (list[float | None] | None): Amount to offset an axis after applying
            scaling factor. Defaults to None.
        zarr_format (Literal[2, 3], optional): The version of zarr to write.
            Defaults to 2.
        structure_validation (bool): If True, runs structural validation and does not write
            a geff that is invalid. Defaults to True.
        node_id_dict (dict[int, int], optional): A dictionary mapping rx node indices to
            arbitrary indices. This allows custom node identifiers to be used in the geff file
            instead of rustworkx's internal indices. If None, uses rx indices directly.
    """
    ...


@overload
def write(
    graph: SupportedGraphType,
    store: StoreLike,
    metadata: GeffMetadata | None = ...,
    axis_names: list[str] | None = ...,
    axis_units: list[str | None] | None = ...,
    axis_types: list[AxisType | None] | None = ...,
    axis_scales: list[float | None] | None = ...,
    scaled_units: list[str | None] | None = ...,
    axis_offset: list[float | None] | None = ...,
    zarr_format: Literal[2, 3] = ...,
    structure_validation: bool = True,
    *args: Any,
    **kwargs: Any,
) -> None: ...
def write(
    graph: SupportedGraphType,
    store: StoreLike,
    metadata: GeffMetadata | None = None,
    axis_names: list[str] | None = None,
    axis_units: list[str | None] | None = None,
    axis_types: list[AxisType | None] | None = None,
    axis_scales: list[float | None] | None = None,
    scaled_units: list[str | None] | None = None,
    axis_offset: list[float | None] | None = None,
    zarr_format: Literal[2, 3] = 2,
    structure_validation: bool = True,
    *args: Any,
    **kwargs: Any,
) -> None:
    """Write a supported graph object to the geff file format.

    Args:
        graph (SupportedGraphType): An instance of a supported graph object.
        store (str | Path | zarr store): The path/str to the output zarr, or the store
            itself. Opens in append mode, so will only overwrite geff-controlled groups.
        metadata (GeffMetadata, optional): The original metadata of the graph.
            Defaults to None. If provided, will override the graph properties.
        axis_names (list[str], optional): The names of the spatial dims
            represented in position property. Defaults to None. Will override
            both value in graph properties and metadata if provided.
        axis_units (list[str | None], optional): The units of the spatial dims
            represented in position property. Defaults to None. Will override value
            both value in graph properties and metadata if provided.
        axis_types (list[Literal[AxisType] | None], optional): The types of the spatial dims
            represented in position property. Usually one of "time", "space", or "channel".
            Defaults to None. Will override both value in graph properties and metadata
            if provided.
        axis_scales (list[float | None] | None): The scale to apply to the spatial dims.
            Defaults to None.
        scaled_units (list[str | None] | None): The units of the spatial dims after scaling.
            Defaults to None.
        axis_offset (list[float | None] | None): Amount to offset an axis after applying
            scaling factor. Defaults to None.
        zarr_format (Literal[2, 3], optional): The version of zarr to write.
            Defaults to 2.
        structure_validation (bool): If True, runs structural validation and does not write
            a geff that is invalid. Defaults to True.
        *args (Any): Additional args that may be accepted by the backend when writing from a
            specific type of graph.
        **kwargs (Any): Additional kwargs that may be accepted by the backend when writing from a
            specific type of graph.
    """
    backend_io = get_backend_from_graph_type(graph)
    backend_io.write(
        graph,
        store,
        metadata,
        axis_names,
        axis_units,
        axis_types,
        axis_scales,
        scaled_units,
        axis_offset,
        zarr_format,
        structure_validation,
        *args,
        **kwargs,
    )
