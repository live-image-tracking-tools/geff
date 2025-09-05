from typing import Any, Literal, Protocol, TypeVar

from numpy.typing import NDArray
from zarr.storage import StoreLike

from geff._typing import PropDictNpArray
from geff.core_io._base_read import read_to_memory
from geff.metadata import GeffMetadata
from geff.validate.data import ValidationConfig

from ._graph_adapter import GraphAdapter

T = TypeVar("T")


class Backend(Protocol[T]):
    """
    A protocol that acts as a namespace for functions that allow for backend interoperability.
    """

    @property
    def GRAPH_TYPES(self) -> tuple[type[T], ...]: ...

    @staticmethod
    def construct(
        metadata: GeffMetadata,
        node_ids: NDArray[Any],
        edge_ids: NDArray[Any],
        node_props: dict[str, PropDictNpArray],
        edge_props: dict[str, PropDictNpArray],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """
        Construct a backend graph object from GEFF data.

        Args:
            metadata (GeffMetadata): The metadata of the graph.
            node_ids (NDArray[Any]): An array containing the node ids. Must have same dtype as
                edge_ids.
            edge_ids (NDArray[Any]): An array containing the edge ids. Must have same dtype
                as node_ids.
            node_props (dict[str, PropDictNpArray]): A dictionary
                from node property names to (values, missing) arrays, which should have same
                length as node_ids. Spatial graph does not support missing attributes, so the
                missing arrays should be None or all False. If present, the missing arrays are
                ignored with warning
            edge_props (dict[str, PropDictNpArray]): A dictionary
                from edge property names to (values, missing) arrays, which should have same
                length as edge_ids. Spatial graph does not support missing attributes, so the
                missing arrays should be None or all False. If present, the missing array is ignored
                with warning.
            *args (Any): Additional positional arguments used for construction.
            **kwargs (Any): Additional keyword arguments used for construction.

        Returns:
            graph (T): The graph object.
        """
        ...

    @classmethod
    def read(
        cls,
        store: StoreLike,
        structure_validation: bool = True,
        node_props: list[str] | None = None,
        edge_props: list[str] | None = None,
        data_validation: ValidationConfig | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> tuple[T, GeffMetadata]:
        """
        Read a GEFF to a chosen backend graph instance.

        Args:
            store (StoreLike): The path or zarr store to the root of the geff zarr, where
                the .attrs contains the geff  metadata.
            structure_validation (bool, optional): Flag indicating whether to perform validation
                on the geff file before loading into memory. If set to False and there are format
                issues, will likely fail with a cryptic error. Defaults to True.
            node_props (list of str, optional): The names of the node properties to load,
                if None all properties will be loaded, defaults to None.
            edge_props (list of str, optional): The names of the edge properties to load,
                if None all properties will be loaded, defaults to None.
            data_validation (ValidationConfig, optional): Optional configuration for which
                optional types of data to validate. Each option defaults to False.
            *args (Any): Additional args that may be accepted by the backend when reading the
                data.
            **kwargs (Any): Additional kwargs that may be accepted by the backend when reading the
                data.

        Returns:
            tuple[Any, GeffMetadata]: Graph object of the chosen backend, and the GEFF metadata.
        """
        in_memory_geff = read_to_memory(
            store, structure_validation, node_props, edge_props, data_validation
        )
        return cls.construct(**in_memory_geff, **kwargs), in_memory_geff["metadata"]

    @staticmethod
    def write(
        graph: T,
        store: StoreLike,
        metadata: GeffMetadata | None = None,
        axis_names: list[str] | None = None,
        axis_units: list[str | None] | None = None,
        axis_types: list[str | None] | None = None,
        zarr_format: Literal[2, 3] = 2,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Write a supported graph object to the geff file format.

        Args:
            graph (T): An instance of a supported graph object.
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
            axis_types (list[str | None], optional): The types of the spatial dims
                represented in position property. Usually one of "time", "space", or "channel".
                Defaults to None. Will override both value in graph properties and metadata
                if provided.
            zarr_format (Literal[2, 3], optional): The version of zarr to write.
                Defaults to 2.
            *args (Any): Additional args that may be accepted by the backend when writing from a
                specific type of graph.
            **kwargs (Any): Additional kwargs that may be accepted by the backend when writing from
                a specific type of graph.
        """
        ...

    @staticmethod
    def graph_adapter(graph: T) -> GraphAdapter[T]:
        """
        Wrap a graph in a GraphAdapter for a unified API for accessing data.

        Args:
            graph (T): An instance of a supported graph object.

        Returns:
            GraphAdapter[T]
        """
        ...
