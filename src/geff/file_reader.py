from pathlib import Path

import numpy as np
import zarr
from numpy.typing import NDArray

from . import utils
from .dict_representation import GraphDict, PropDictNpArray, PropDictZArray
from .metadata_schema import GeffMetadata


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
        """
        File reader class that allows subset reading to an intermediate dict representation.

        Args:
            path (Path | str): The path to the root of the geff zarr, where the .attrs contains
                the geff  metadata
            validate (bool, optional): Flag indicating whether to perform validation on the
                geff file before loading into memory. If set to False and there are
                format issues, will likely fail with a cryptic error. Defaults to True.
        """
        if validate:
            utils.validate(path)
        self.group = zarr.open_group(path, mode="r")
        self.metadata = GeffMetadata.read(self.group)
        self.nodes = self.group["nodes/ids"]
        self.edges = self.group["edges/ids"]
        self.node_props: dict[str, PropDictZArray] = {}
        self.edge_props: dict[str, PropDictZArray] = {}

        node_props_group = zarr.open_group(self.group.store, path="nodes/props", mode="r")
        self.node_prop_names: list[str] = [*node_props_group.group_keys()]

        edge_props_group = zarr.open_group(self.group.store, path="edges/props", mode="r")
        self.edge_prop_names: list[str] = [*edge_props_group.group_keys()]

    def read_node_props(self, name: str):
        """
        Read the node property with the name `name` from a GEFF.

        Call `build` to get the output `GraphDict` with the loaded properties.

        Args:
            name (str): The name of the node property.
        """
        prop_group = zarr.open_group(self.group.store, path=f"nodes/props/{name}", mode="r")
        prop_dict: PropDictZArray = {"values": prop_group["values"]}
        if "missing" in prop_group.keys():
            prop_dict["missing"] = prop_group["missing"]
        self.node_props[name] = prop_dict

    def read_edge_props(self, name: str):
        """
        Read the edge property with the name `name` from a GEFF.

        Call `build` to get the output `GraphDict` with the loaded properties.

        Args:
            name (str): The name of the edge property.
        """
        prop_group = zarr.open_group(self.group.store, path=f"edges/props/{name}", mode="r")
        prop_dict: PropDictZArray = {"values": prop_group["values"]}
        if "missing" in prop_group.keys():
            prop_dict["missing"] = prop_group["missing"]
        self.edge_props[name] = prop_dict

    def build(
        self,
        node_mask: NDArray[np.bool] | None = None,
        edge_mask: NDArray[np.bool] | None = None,
    ) -> GraphDict:
        """
        Build a `GraphDict` from a GEFF.

        A set of nodes and edges can be selected using `node_mask` and `edge_mask`.

        Args:
            node_mask (np.ndarray of bool): A boolean numpy array to mask build a graph
            of a subset of nodes, where `node_mask` is equal to True. It must be a 1D
            array of length number of nodes.
            edge_mask (np.ndarray of bool): A boolean numpy array to mask build a graph
            of a subset of edge, where `edge_mask` is equal to True. It must be a 1D
            array of length number of edges.
        Returns:
            GraphDict: A graph represented in graph dict format.
        """
        nodes = np.array(self.nodes[node_mask.tolist() if node_mask is not None else ...])
        node_props: dict[str, PropDictNpArray] = {}
        for name, props in self.node_props.items():
            node_props[name] = {
                "values": np.array(
                    props["values"][node_mask.tolist() if node_mask is not None else ...]
                )
            }
            if "missing" in props:
                node_props[name]["missing"] = np.array(
                    props["missing"][node_mask.tolist() if node_mask is not None else ...],
                    dtype=bool,
                )

        edges = np.array(self.edges[edge_mask.tolist() if edge_mask else ...])
        edge_props: dict[str, PropDictNpArray] = {}
        for name, props in self.edge_props.items():
            edge_props[name] = {
                "values": np.array(
                    props["values"][edge_mask.tolist() if edge_mask is not None else ...]
                )
            }
            if "missing" in props:
                edge_props[name]["missing"] = np.array(
                    props["missing"][edge_mask.tolist() if edge_mask is not None else ...],
                    dtype=bool,
                )

        return {
            "metadata": self.metadata,
            "nodes": nodes,
            "node_props": node_props,
            "edges": edges,
            "edge_props": edge_props,
        }
