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
    ) -> tuple[T, GeffMetadata]: ...

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
    ) -> None: ...

    @staticmethod
    def graph_adapter(graph: T) -> GraphAdapter[T]: ...


class BaseBackend(Backend[T]):
    @classmethod
    def read(
        cls,
        store: StoreLike,
        structure_validation: bool = True,
        node_props: list[str] | None = None,
        edge_props: list[str] | None = None,
        data_validation: ValidationConfig | None = None,
        **kwargs: Any,
    ) -> tuple[T, GeffMetadata]:
        in_memory_geff = read_to_memory(
            store, structure_validation, node_props, edge_props, data_validation
        )
        return cls.construct(**in_memory_geff, **kwargs), in_memory_geff["metadata"]
