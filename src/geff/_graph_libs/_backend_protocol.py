from typing import Any, Protocol, TypeVar

from numpy.typing import NDArray

from geff._typing import PropDictNpArray
from geff.metadata import GeffMetadata

from ._graph_adapter import GraphAdapter

T = TypeVar("T")


class Backend(Protocol[T]):
    """
    A protocol that acts as a namespace for functions that allow for backend interoperability.
    """

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

    @staticmethod
    def graph_adapter(graph: T) -> GraphAdapter[T]: ...

    # TODO: add write
