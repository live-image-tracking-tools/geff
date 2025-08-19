from collections.abc import Sequence
from typing import Any, Protocol, TypeVar

from numpy.typing import NDArray

from geff.metadata_schema import GeffMetadata
from geff.typing import PropDictNpArray

T = TypeVar("T")


class Backend(Protocol[T]):
    """
    A protocol that acts as a namespace for functions that allow for backend interoperability.
    """

    @property
    def GRAPH_TYPES(self) -> tuple[type[T], ...]:
        """The expected backend types."""
        ...

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
    def get_node_ids(graph: T) -> Sequence[Any]:
        """
        Get the node ids of the graph.

        Args:
            graph (T): The graph object.

        Returns:
            node_ids (Sequence[Any]): The node ids.
        """
        ...

    @staticmethod
    def get_edge_ids(graph: T) -> Sequence[tuple[Any, Any]]:
        """
        Get the edges of the graph.

        Args:
            graph (T): The graph object.

        Returns:
            edge_ids (Sequence[tuple[Any, Any]]): Pairs of node ids that represent edges..
        """
        ...

    @staticmethod
    def get_node_prop(
        graph: T, name: str, nodes: Sequence[Any], metadata: GeffMetadata
    ) -> NDArray[Any]:
        """
        Get a property of the nodes as a numpy array.

        Args:
            graph (T): The graph object.
            name (str): The name of the node property.
            nodes (Sequence[Any]): A sequence of node ids; this determines the order of the property
                array.
            metadata (GeffMetadata): The GEFF metadata.

        Returns:
            numpy.ndarray: The values of the selected property as a numpy array.
        """
        ...

    @staticmethod
    def get_edge_prop(
        graph: T, name: str, edges: Sequence[tuple[Any, Any]], metadata: GeffMetadata
    ) -> NDArray[Any]:
        """
        Get a property of the edges as a numpy array.

        Args:
            graph (T): The graph object.
            name (str): The name of the edge property.
            edges (Sequence[Any]): A sequence of tuples of node ids, representing the edges; this
                determines the order of the property array.
            metadata (GeffMetadata): The GEFF metadata.

        Returns:
            numpy.ndarray: The values of the selected property as a numpy array.
        """
        ...

    # TODO: add
    # - get_roi
    # - write
