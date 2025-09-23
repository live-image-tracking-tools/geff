from collections.abc import Sequence
from typing import Any, Protocol, TypeVar

from geff_spec import GeffMetadata

T = TypeVar("T", covariant=True)


class GraphAdapter(Protocol[T]):
    def __init__(self, graph: T) -> None: ...

    def get_node_ids(self) -> Sequence[int]:
        """
        Get the node ids of the graph.

        Returns:
            node_ids (Sequence[int]): The node ids.
        """
        ...

    def get_edge_ids(self) -> Sequence[tuple[int, int]]:
        """
        Get the edges of the graph.

        Returns:
            edge_ids (Sequence[tuple[int, int]]): Pairs of node ids that represent edges.
        """
        ...

    def has_node_prop(self, name: str, node: int, metadata: GeffMetadata) -> bool:
        """Determine if the given node has a property value or not

        Args:
            name (str): The name of the node property.
            node (int): A node id to get the property for
            metadata (GeffMetadata): The GEFF metadata.

        Returns:
            bool: True if the node has the property, and False otherwise
        """
        ...

    def get_node_prop(self, name: str, node: int, metadata: GeffMetadata) -> Any:
        """
        Get a property of a specific node

        Args:
            name (str): The name of the node property.
            node (int): A node id to get the property for
            metadata (GeffMetadata): The GEFF metadata.

        Returns:
            Any: The value of the selected property for the given node
        """
        ...

    def has_edge_prop(
        self,
        name: str,
        edge: tuple[int, int],
        metadata: GeffMetadata,
    ) -> bool:
        """
        Determine if an edge has a specific property

        Args:
            name (str): The name of the edge property.
            edge (tuple[int,int]): A tuple of node ids representing an edge.
            metadata (GeffMetadata): The GEFF metadata.

        Returns:
            bool: True if the edge does have the property, false otherwise.
        """
        ...

    def get_edge_prop(
        self,
        name: str,
        edge: tuple[int, int],
        metadata: GeffMetadata,
    ) -> Any:
        """
        Get a property of a specific edge

        Args:
            name (str): The name of the edge property.
            edge (tuple[int, int]): A tuple of node ids representing an edge
            metadata (GeffMetadata): The GEFF metadata.

        Returns:
            Any: The value of the selected property for a specific edge.
        """
        ...

    # TODO: add get roi?
