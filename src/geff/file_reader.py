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
        ... graph_dict

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

        if "props" in self.group["edges"].keys():
            edge_props_group = zarr.open_group(self.group.store, path="edges/props", mode="r")
            self.edge_prop_names: list[str] = [*edge_props_group.group_keys()]
        else:
            self.edge_prop_names = []

    def read_node_props(self, names: list[str] | None = None):
        """
        Read the node property with the name `name` from a GEFF.

        Call `build` to get the output `GraphDict` with the loaded properties.

        Args:
            names (lists of str, optional): The names of the node properties to load. If
            None all node properties will be loaded.
        """
        if names is None:
            names = self.node_prop_names

        for name in names:
            prop_group = zarr.open_group(self.group.store, path=f"nodes/props/{name}", mode="r")
            prop_dict: PropDictZArray = {"values": prop_group["values"]}
            if "missing" in prop_group.keys():
                prop_dict["missing"] = prop_group["missing"]
            self.node_props[name] = prop_dict

    def read_edge_props(self, names: list[str] | None = None):
        """
        Read the edge property with the name `name` from a GEFF.

        Call `build` to get the output `GraphDict` with the loaded properties.

        Args:
            names (lists of str, optional): The names of the edge properties to load. If
            None all node properties will be loaded.
        """
        if names is None:
            names = self.edge_prop_names

        for name in names:
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

        # remove edges if any of it's nodes has been masked
        edges = self.edges[:]
        if node_mask is not None:
            edge_mask_removed_nodes = np.isin(edges, nodes).all(axis=1)
            if edge_mask is not None:
                edge_mask = np.logical_and(edge_mask, edge_mask_removed_nodes)
            else:
                edge_mask = edge_mask_removed_nodes
        edges = edges[edge_mask if edge_mask is not None else ...]

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


# NOTE: if different FileReaders exist in the future a `file_reader` argument can be
#   added to this function to select between them.
def read_to_dict(
    path: Path | str,
    validate: bool = True,
    node_props: list[str] | None = None,
    edge_props: list[str] | None = None,
) -> GraphDict:
    """
    Read a GEFF zarr file to a dictionary representation.

    A subset of node and edge properties can be selected with the `node_props` and
    `edge_props` argument.

    Args:
        path (Path | str): The path to the root of the geff zarr, where the .attrs contains
            the geff  metadata
        validate (bool, optional): Flag indicating whether to perform validation on the
            geff file before loading into memory. If set to False and there are
            format issues, will likely fail with a cryptic error. Defaults to True.
        node_props (list of str, optional): The names of the node properties to load,
            if None all properties will be loaded, defaults to None.
        edge_props (list of str, optional): The names of the edge properties to load,
            if None all properties will be loaded, defaults to None.

    Returns:
        A networkx graph containing the graph that was stored in the geff file format
    """
    if isinstance(path, str):
        path = Path(path)
    path = path.expanduser()
    file_reader = FileReader(path, validate)

    file_reader.read_node_props(node_props)
    file_reader.read_edge_props(edge_props)

    graph_dict = file_reader.build()
    return graph_dict
