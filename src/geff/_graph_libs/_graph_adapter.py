from collections.abc import Sequence
from typing import Any, Protocol, TypeVar

from numpy.typing import NDArray

from geff.metadata import GeffMetadata

T = TypeVar("T", covariant=True)


class GraphAdapter(Protocol[T]):
    def __init__(self, graph: T) -> None: ...

    def get_node_ids(self) -> Sequence[Any]:
        """
        Get the node ids of the graph.

        Returns:
            node_ids (Sequence[Any]): The node ids.
        """
        ...

    def get_edge_ids(self) -> Sequence[tuple[Any, Any]]:
        """
        Get the edges of the graph.

        Returns:
            edge_ids (Sequence[tuple[Any, Any]]): Pairs of node ids that represent edges..
        """
        ...

    def get_node_prop(
        self, name: str, nodes: Sequence[Any], metadata: GeffMetadata
    ) -> NDArray[Any]:
        """
        Get a property of the nodes as a numpy array.

        Args:
            name (str): The name of the node property.
            nodes (Sequence[Any]): A sequence of node ids; this determines the order of the property
                array.
            metadata (GeffMetadata): The GEFF metadata.

        Returns:
            numpy.ndarray: The values of the selected property as a numpy array.
        """
        ...

    def get_edge_prop(
        self,
        name: str,
        edges: Sequence[tuple[Any, Any]],
        metadata: GeffMetadata,
    ) -> NDArray[Any]:
        """
        Get a property of the edges as a numpy array.

        Args:
            name (str): The name of the edge property.
            edges (Sequence[Any]): A sequence of tuples of node ids, representing the edges; this
                determines the order of the property array.
            metadata (GeffMetadata): The GEFF metadata.

        Returns:
            numpy.ndarray: The values of the selected property as a numpy array.
        """
        ...

    # TODO: add get roi?
