from typing import Any, Literal, Protocol, TypeVar

from numpy.typing import NDArray
from zarr.storage import StoreLike

from geff._typing import PropDictNpArray
from geff.core_io._base_read import read_to_memory
from geff.validate.data import ValidationConfig
from geff_spec import AxisType, GeffMetadata

from ._graph_adapter import GraphAdapter

T = TypeVar("T")


# NOTE: see _api_wrapper.py read/write/construct functions for docstrings
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
    ) -> T: ...

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
        axis_types: list[AxisType | None] | None = None,
        axis_scales: list[float | None] | None = None,
        scaled_units: list[str | None] | None = None,
        axis_offset: list[float | None] | None = None,
        zarr_format: Literal[2, 3] = 2,
        structure_validation: bool = True,
        *args: Any,
        **kwargs: Any,
    ) -> None: ...

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
