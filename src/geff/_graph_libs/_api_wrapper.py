from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, Protocol, TypeVar, overload

from geff._graph_libs._networkx import construct_nx
from geff.core_io._base_read import read_to_memory

R = TypeVar("R", covariant=True)

if TYPE_CHECKING:
    import networkx as nx
    import rustworkx as rx
    import spatial_graph as sg
    from numpy.typing import NDArray
    from zarr.storage import StoreLike

    from geff._typing import PropDictNpArray
    from geff.metadata._schema import GeffMetadata
    from geff.validate.data import ValidationConfig

SupportedBackend = Literal["networkx", "rustworkx", "spatial-graph"]


class ConstructFunc(Protocol[R]):
    """A protocol for callables that construct a graph from GEFF data."""

    def __call__(
        self,
        metadata: GeffMetadata,
        node_ids: NDArray[Any],
        edge_ids: NDArray[Any],
        node_props: dict[str, PropDictNpArray],
        edge_props: dict[str, PropDictNpArray],
        *args: Any,
        **kwargs: Any,
    ) -> R:
        """
        The callable must have this function signature.

        The callable must have the first argument `in_memory_geff`, it may have additional
        args and kwargs.

        Args:
            metadata (GeffMetadata): The metadata of the graph.
            node_ids (np.ndarray): An array containing the node ids. Must have same dtype as
                edge_ids.
            edge_ids (np.ndarray): An array containing the edge ids. Must have same dtype
                as node_ids.
            node_props (dict[str, tuple[np.ndarray, np.ndarray | None]] | None): A dictionary
                from node property names to (values, missing) arrays, which should have same
                length as node_ids.
            edge_props (dict[str, tuple[np.ndarray, np.ndarray | None]] | None): A dictionary
                from edge property names to (values, missing) arrays, which should have same
                length as edge_ids.
            *args (Any): Optional args for constructing the `in_memory_geff`.
            **kwargs (Any): Optional kwargs for constructing the `in_memory_geff`.

        Returns:
            A graph object instance for a particular backend.
        """
        ...


@overload
def get_construct_func(
    backend: Literal["networkx"],
) -> ConstructFunc[nx.Graph | nx.DiGraph]: ...


@overload
def get_construct_func(
    backend: Literal["rustworkx"],
) -> ConstructFunc[rx.PyGraph | rx.PyDiGraph]: ...


@overload
def get_construct_func(
    backend: Literal["spatial-graph"],
) -> ConstructFunc[sg.SpatialGraph | sg.SpatialDiGraph]: ...


def get_construct_func(backend: SupportedBackend) -> ConstructFunc[Any]:
    """
    Get the construct function for different backends.

    Args:
        backend (SupportedBackend): Flag for the chosen backend.

    Returns:
        ConstructFunc: A function that construct a graph from GEFF data.
    """
    match backend:
        case "networkx":
            return construct_nx
        case "rustworkx":
            from geff._graph_libs._rustworkx import construct_rx

            return construct_rx
        case "spatial-graph":
            from geff._graph_libs._spatial_graph import construct_sg

            return construct_sg
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
    validate_data: bool = False,
    validate_opt_data: ValidationConfig | None = None,
) -> tuple[nx.Graph | nx.DiGraph, GeffMetadata]: ...


@overload
def read(
    store: StoreLike,
    validate: bool,
    node_props: list[str] | None,
    edge_props: list[str] | None,
    backend: Literal["rustworkx"],
    validate_data: bool = False,
    validate_opt_data: ValidationConfig | None = None,
) -> tuple[rx.PyGraph | rx.PyDiGraph, GeffMetadata]: ...


@overload
def read(
    store: StoreLike,
    validate: bool,
    node_props: list[str] | None,
    edge_props: list[str] | None,
    backend: Literal["spatial-graph"],
    validate_data: bool = False,
    validate_opt_data: ValidationConfig | None = None,
    *,
    position_attr: str = "position",
) -> tuple[sg.SpatialGraph | sg.SpatialDiGraph, GeffMetadata]: ...


def read(
    store: StoreLike,
    validate: bool = True,
    node_props: list[str] | None = None,
    edge_props: list[str] | None = None,
    backend: SupportedBackend = "networkx",
    validate_data: bool = False,
    validate_opt_data: ValidationConfig | None = None,
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
        validate_data (bool, optional): Flag indicating whether to perform validation on the
            underlying data of the geff, e.g. edges. Defaults to False.
        validate_opt_data (ValidationConfig, optional): Optional configuration for which
            optional types of data to validate
        backend_kwargs (Any): Additional kwargs that may be accepted by
            the backend when reading the data.

    Returns:
        tuple[Any, GeffMetadata]: Graph object of the chosen backend, and the GEFF metadata.
    """
    construct_func = get_construct_func(backend)
    in_memory_geff = read_to_memory(
        store, validate, node_props, edge_props, validate_data, validate_opt_data
    )
    return (
        construct_func(**in_memory_geff, **backend_kwargs),
        in_memory_geff["metadata"],
    )
