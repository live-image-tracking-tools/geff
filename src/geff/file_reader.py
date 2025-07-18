from typing import TypedDict, Any, Optional, Generic, TypeVar
from typing_extensions import NotRequired
from pathlib import Path

import zarr
import numpy as np
from numpy.typing import NDArray

from .metadata_schema import GeffMetadata
from . import utils

T_Array = TypeVar("T_Array", bound=zarr.Array | NDArray)


# TODO: move dict defs to own module
class AttrDict(TypedDict, Generic[T_Array]):
    values: T_Array
    missing: NotRequired[T_Array]


# Itermediate dict format that can be injested to different backend types
class GraphDict(TypedDict):
    metadata: GeffMetadata
    nodes: NDArray[Any]
    edges: NDArray[Any]
    node_attrs: dict[str, AttrDict[NDArray]]
    edge_attrs: dict[str, AttrDict[NDArray]]


class FileReader:
    """
    File reader class that allows subset reading to an intermediate dict representation.

    The subsets can be a subset of node and edge attributes, and a subset of nodes and
    edges.

    Example:
        >>> from pathlib import Path
        ... from geff.read_file import FileReader

        >>> path = Path("example/path")
        ... file_reader = FileReader(path)
        ... file_reader.read_node_attr("seg_id")
        ... # graph_dict will only have the node attribute "seg_id"
        ... graph_dict = file_reader.build()
        ... graph_dict

        >>> file_reader.read_node_attr("t")
        ... # Now graph dict will have two node attributes: "seg_id" and "t"
        ... graph_dict = file_reader.build()

        >>> # Now graph_dict will only be a subset with nodes "t" < 5
        ... graph_dict = file_reader.build(file_reader.node_attrs["t"]["values"][:] < 5)
        ... graph_dict
    """

    def __init__(self, path: Path, validate: bool = True):
        if validate:
            utils.validate(path)
        self.group = zarr.open_group(path, mode="r")
        self.metadata = GeffMetadata.read(self.group)
        self.nodes = self.group["nodes/ids"]
        self.edges = self.group["edges/ids"]
        self.node_attrs: dict[str, AttrDict[zarr.Array]] = {}
        self.edge_attrs: dict[str, AttrDict[zarr.Array]] = {}

    def read_node_attr(self, name: str):
        attr_group = zarr.open_group(self.group.store, path=f"nodes/attrs/{name}")
        attr_dict: AttrDict = {"values": attr_group["values"]}
        if "missing" in attr_group.keys():
            attr_dict["missing"] = attr_group["missing"]
        self.node_attrs[name] = attr_dict

    def read_edge_attr(self, name: str):
        attr_group = zarr.open_group(self.group.store, path=f"edges/attrs/{name}")
        attr_dict: AttrDict = {"values": attr_group["values"]}
        if "missing" in attr_group.keys():
            attr_dict["missing"] = attr_group["missing"]
        self.node_attrs[name] = attr_dict

    def build(
        self,
        node_mask: Optional[NDArray[np.bool]] = None,
        edge_mask: Optional[NDArray[np.bool]] = None,
    ) -> GraphDict:

        nodes = np.array(
            self.nodes[node_mask.tolist() if node_mask is not None else ...]
        )
        node_attrs: dict[str, AttrDict[NDArray]] = {}
        for name, attrs in self.node_attrs.items():
            node_attrs[name] = {
                "values": np.array(
                    attrs["values"][
                        node_mask.tolist() if node_mask is not None else ...
                    ]
                )
            }
            if "missing" in attrs:
                node_attrs[name]["missing"] = np.array(
                    attrs["missing"][
                        node_mask.tolist() if node_mask is not None else ...
                    ],
                    dtype=bool,
                )

        edges = np.array(self.edges[edge_mask.tolist() if edge_mask else ...])
        edge_attrs: dict[str, AttrDict[NDArray]] = {}
        for name, attrs in self.edge_attrs.items():
            edge_attrs[name] = {
                "values": np.array(
                    attrs["values"][
                        edge_mask.tolist() if edge_mask is not None else ...
                    ]
                )
            }
            if "missing" in attrs:
                node_attrs[name]["missing"] = np.array(
                    attrs["missing"][
                        edge_mask.tolist() if edge_mask is not None else ...
                    ],
                    dtype=bool,
                )

        return {
            "metadata": self.metadata,
            "nodes": nodes,
            "node_attrs": node_attrs,
            "edges": edges,
            "edge_attrs": edge_attrs,
        }
