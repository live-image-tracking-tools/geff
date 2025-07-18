from pathlib import Path
from typing import Any, Generic, Optional, TypedDict, TypeVar

import numpy as np
import zarr
from numpy.typing import NDArray
from typing_extensions import NotRequired

from . import utils
from .metadata_schema import GeffMetadata

T_Array = TypeVar("T_Array", bound=zarr.Array | NDArray)


# TODO: move dict defs to own module
# the typevar T_Array means that the arrays can either be numpy or zarr arrays
class PropDict(TypedDict, Generic[T_Array]):
    values: T_Array
    missing: NotRequired[T_Array]


# Intermediate dict format that can be injested to different backend types
class GraphDict(TypedDict):
    metadata: GeffMetadata
    nodes: NDArray[Any]
    edges: NDArray[Any]
    node_props: dict[str, PropDict[NDArray]]
    edge_props: dict[str, PropDict[NDArray]]


class FileReader:
    """
    File reader class that allows subset reading to an intermediate dict representation.

    The subsets can be a subset of node and edge properties, and a subset of nodes and
    edges.

    Example:
        >>> from pathlib import Path
        ... from geff.read_file import FileReader

        >>> path = Path("example/path")
        ... file_reader = FileReader(path)
        ... file_reader.read_node_prop("seg_id")
        ... # graph_dict will only have the node property "seg_id"
        ... graph_dict = file_reader.build()
        ... graph_dict

        >>> file_reader.read_node_prop("t")
        ... # Now graph dict will have two node properties: "seg_id" and "t"
        ... graph_dict = file_reader.build()

        >>> # Now graph_dict will only be a subset with nodes "t" < 5
        ... graph_dict = file_reader.build(file_reader.node_props["t"]["values"][:] < 5)
        ... graph_dict
    """

    def __init__(self, path: Path, validate: bool = True):
        if validate:
            utils.validate(path)
        self.group = zarr.open_group(path, mode="r")
        self.metadata = GeffMetadata.read(self.group)
        self.nodes = self.group["nodes/ids"]
        self.edges = self.group["edges/ids"]
        self.node_props: dict[str, PropDict[zarr.Array]] = {}
        self.edge_props: dict[str, PropDict[zarr.Array]] = {}

    def read_node_props(self, name: str):
        prop_group = zarr.open_group(self.group.store, path=f"nodes/props/{name}")
        prop_dict: PropDict = {"values": prop_group["values"]}
        if "missing" in prop_group.keys():
            prop_dict["missing"] = prop_group["missing"]
        self.node_props[name] = prop_dict

    def read_edge_props(self, name: str):
        prop_group = zarr.open_group(self.group.store, path=f"edges/props/{name}")
        prop_dict: PropDict = {"values": prop_group["values"]}
        if "missing" in prop_group.keys():
            prop_dict["missing"] = prop_group["missing"]
        self.node_props[name] = prop_dict

    def build(
        self,
        node_mask: Optional[NDArray[np.bool]] = None,
        edge_mask: Optional[NDArray[np.bool]] = None,
    ) -> GraphDict:
        nodes = np.array(
            self.nodes[node_mask.tolist() if node_mask is not None else ...]
        )
        node_props: dict[str, PropDict[NDArray]] = {}
        for name, props in self.node_props.items():
            node_props[name] = {
                "values": np.array(
                    props["values"][
                        node_mask.tolist() if node_mask is not None else ...
                    ]
                )
            }
            if "missing" in props:
                node_props[name]["missing"] = np.array(
                    props["missing"][
                        node_mask.tolist() if node_mask is not None else ...
                    ],
                    dtype=bool,
                )

        edges = np.array(self.edges[edge_mask.tolist() if edge_mask else ...])
        edge_props: dict[str, PropDict[NDArray]] = {}
        for name, props in self.edge_props.items():
            edge_props[name] = {
                "values": np.array(
                    props["values"][
                        edge_mask.tolist() if edge_mask is not None else ...
                    ]
                )
            }
            if "missing" in props:
                node_props[name]["missing"] = np.array(
                    props["missing"][
                        edge_mask.tolist() if edge_mask is not None else ...
                    ],
                    dtype=bool,
                )

        return {
            "metadata": self.metadata,
            "nodes": nodes,
            "node_props": node_props,
            "edges": edges,
            "edge_props": edge_props,
        }
