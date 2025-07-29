from collections.abc import Sequence
from typing import cast

import numpy as np
import zarr
from numpy.typing import NDArray
from zarr import Array
from zarr.storage import StoreLike

from geff.metadata_schema import GeffMetadata
from geff.serialization import deserialize_vlen_property_data
from geff.typing import InMemoryGeff, PropDictNpArray, PropDictSequence, PropDictZArray

from . import utils


class GeffReader:
    """
    File reader class that allows subset reading to an intermediate dict representation.

    The subsets can be a subset of node and edge properties, and a subset of nodes and
    edges.

    Example:
        >>> from pathlib import Path
        ... from geff.file_reader import FileReader

        >>> path = Path("example/path")
        ... file_reader = FileReader(path)
        ... file_reader.read_node_prop("seg_id")
        ... # in_memory_geff will only have the node property "seg_id"
        ... in_memory_geff = file_reader.build()
        ... in_memory_geff

        >>> file_reader.read_node_prop("t")
        ... # Now graph dict will have two node properties: "seg_id" and "t"
        ... in_memory_geff = file_reader.build()
        ... in_memory_geff

        >>> # Now in_memory_geff will only be a subset with nodes "t" < 5
        ... in_memory_geff = file_reader.build(file_reader.node_props["t"]["values"][:] < 5)
        ... in_memory_geff
    """

    def __init__(self, source: StoreLike, validate: bool = True):
        """
        File reader class that allows subset reading to an intermediate dict representation.

        Args:
            source (str | Path | zarr.store): Either a str/path to the root of the geff zarr
                (where the .attrs contains the geff metadata), or a zarr store object
            validate (bool, optional): Flag indicating whether to perform validation on the
                geff file before loading into memory. If set to False and there are
                format issues, will likely fail with a cryptic error. Defaults to True.
        """
        source = utils.remove_tilde(source)

        if validate:
            utils.validate(source)
        self.group = zarr.open_group(source, mode="r")
        self.metadata = GeffMetadata.read(self.group)
        self.nodes = zarr.open_array(source, path="nodes/ids", mode="r")
        self.edges = zarr.open_array(source, path="edges/ids", mode="r")
        self.node_props: dict[str, PropDictZArray | PropDictSequence] = {}
        self.edge_props: dict[str, PropDictZArray | PropDictSequence] = {}
        nodes_group: zarr.Group = cast("zarr.Group", self.group["nodes"])
        edges_group: zarr.Group = cast("zarr.Group", self.group["edges"])

        # get node properties names
        if "props" in nodes_group.keys():
            node_props_group = zarr.open_group(self.group.store, path="nodes/props", mode="r")
            self.node_prop_names: list[str] = [*node_props_group.group_keys()]
        else:
            self.node_prop_names = []

        # get edge property names
        if "props" in edges_group.keys():
            edge_props_group = zarr.open_group(self.group.store, path="edges/props", mode="r")
            self.edge_prop_names: list[str] = [*edge_props_group.group_keys()]
        else:
            self.edge_prop_names = []

        # get vlen node properties names
        if "vlen_props" in nodes_group.keys():
            vlen_node_props_group = zarr.open_group(
                self.group.store, path="nodes/vlen_props", mode="r"
            )
            self.vlen_node_prop_names: list[str] = [*vlen_node_props_group.group_keys()]
        else:
            self.vlen_node_prop_names = []

        # get vlen edge properties names
        if "vlen_props" in edges_group.keys():
            vlen_edge_props_group = zarr.open_group(
                self.group.store, path="edges/vlen_props", mode="r"
            )
            self.vlen_edge_prop_names: list[str] = [*vlen_edge_props_group.group_keys()]
        else:
            self.vlen_edge_prop_names = []

    def read_node_props(self, names: list[str] | None = None):
        """
        Read the node property with the name `name` from a GEFF.

        If no names are specified, then all properties will be loaded

        Call `build` to get the output `InMemoryGeff` with the loaded properties.

        Args:
            names (lists of str, optional): The names of the node properties to load. If
            None all node properties will be loaded.
        """
        if names is None:
            names = self.node_prop_names

        for name in names:
            prop_group = zarr.open_group(self.group.store, path=f"nodes/props/{name}", mode="r")
            prop_values = zarr.open_array(
                self.group.store, path=f"nodes/props/{name}/values", mode="r"
            )
            prop_dict: PropDictZArray = {"values": prop_values}
            if "missing" in prop_group.keys():
                prop_missing = zarr.open_array(
                    self.group.store, path=f"nodes/props/{name}/missing", mode="r"
                )
                prop_dict["missing"] = prop_missing
            self.node_props[name] = prop_dict

    def read_edge_props(self, names: list[str] | None = None):
        """
        Read the edge property with the name `name` from a GEFF.

        If no names are specified, then all properties will be loaded

        Call `build` to get the output `InMemoryGeff` with the loaded properties.

        Args:
            names (lists of str, optional): The names of the edge properties to load. If
            None all node properties will be loaded.
        """
        if names is None:
            names = self.edge_prop_names

        for name in names:
            prop_group = zarr.open_group(self.group.store, path=f"edges/props/{name}", mode="r")
            prop_dict: PropDictZArray = {"values": cast("Array", prop_group["values"])}
            if "missing" in prop_group.keys():
                prop_dict["missing"] = cast("Array", prop_group["missing"])
            self.edge_props[name] = prop_dict

    def read_vlen_node_props(self, names: list[str] | None = None):
        """
        Read the vlen node property with the name `name` from a GEFF.

        If no names are specified, then all properties will be loaded

        Call `build` to get the output `InMemoryGeff` with the loaded properties.

        Args:
            names (lists of str, optional): The names of the vlen node properties
            to load. If None all node properties will be loaded.
        """
        if names is None:
            names = self.vlen_node_prop_names

        for name in names:
            prop_group = zarr.open_group(
                self.group.store, path=f"nodes/vlen_props/{name}", mode="r"
            )
            prop_values = deserialize_vlen_property_data(prop_group)
            prop_dict: PropDictSequence = {"values": prop_values}
            if "missing" in prop_group.keys():
                prop_dict["missing"] = cast("Array", prop_group["missing"])
            self.node_props[name] = prop_dict

    def read_vlen_edge_props(self, names: list[str] | None = None):
        """
        Read the vlen edge property with the name `name` from a GEFF.

        If no names are specified, then all properties will be loaded

        Call `build` to get the output `InMemoryGeff` with the loaded properties.

        Args:
            names (lists of str, optional): The names of the vlen edge properties
            to load. If None all edge properties will be loaded.
        """
        if names is None:
            names = self.vlen_edge_prop_names

        for name in names:
            prop_group = zarr.open_group(
                self.group.store, path=f"edges/vlen_props/{name}", mode="r"
            )
            prop_dict: PropDictSequence = {
                "values": cast("Sequence", deserialize_vlen_property_data(prop_group))
            }
            if "missing" in prop_group.keys():
                prop_dict["missing"] = cast("Array", prop_group["missing"])
            self.edge_props[name] = prop_dict

    def build(
        self,
        node_mask: NDArray[bool] | None = None,
        edge_mask: NDArray[bool] | None = None,
    ) -> InMemoryGeff:
        """
        Build an `InMemoryGeff` by loading the data from a GEFF zarr.

        A set of nodes and edges can be selected using `node_mask` and `edge_mask`.

        Args:
            node_mask (NDArray of bool): A boolean numpy array to mask build a graph
            of a subset of nodes, where `node_mask` is equal to True. It must be a 1D
            array of length number of nodes.
            edge_mask (NDArray of bool): A boolean numpy array to mask build a graph
            of a subset of edge, where `edge_mask` is equal to True. It must be a 1D
            array of length number of edges.
        Returns:
            InMemoryGeff: A dictionary of in memory numpy arrays representing the graph.
        """
        nodes = np.array(self.nodes[node_mask.tolist() if node_mask is not None else ...])
        node_props: dict[str, PropDictNpArray | PropDictSequence] = {}
        for name, props in self.node_props.items():
            masked_values: NDArray | Sequence | None = None
            if isinstance(props["values"], Sequence):
                masked_values = (
                    [
                        val
                        for val, mask in zip(props["values"], node_mask.tolist(), strict=False)
                        if mask
                    ]
                    if node_mask is not None
                    else props["values"]
                )
            else:
                masked_values = cast("NDArray", props["values"])[
                    node_mask.tolist() if node_mask is not None else ...
                ]
            if name in self.vlen_node_prop_names:
                node_props[name] = {"values": cast("Sequence", masked_values)}
            else:
                node_props[name] = {"values": cast("NDArray", np.array(masked_values))}

            if "missing" in props:
                node_masked_missing: NDArray[np.bool] | None = None
                node_masked_missing = cast("NDArray", props["missing"])[
                    node_mask.tolist() if node_mask is not None else ...
                ]
                cast("PropDictNpArray", node_props[name])["missing"] = np.array(
                    node_masked_missing,
                    dtype=bool,
                )

        # remove edges if any of it's nodes has been masked
        edges = np.array(self.edges[:])
        if node_mask is not None:
            edge_mask_removed_nodes = np.isin(edges, nodes).all(axis=1)
            if edge_mask is not None:
                edge_mask = np.logical_and(edge_mask, edge_mask_removed_nodes)
            else:
                edge_mask = cast("NDArray", edge_mask_removed_nodes)
        edges = edges[edge_mask if edge_mask is not None else ...]

        edge_props: dict[str, PropDictNpArray | PropDictSequence] = {}
        for name, props in self.edge_props.items():
            if isinstance(props["values"], Sequence):
                masked_values = (
                    [
                        val
                        for val, mask in zip(props["values"], edge_mask.tolist(), strict=False)
                        if mask
                    ]
                    if edge_mask is not None
                    else props["values"]
                )
            else:
                masked_values = cast("NDArray", props["values"])[
                    edge_mask.tolist() if edge_mask is not None else ...
                ]
            if name in self.vlen_edge_prop_names:
                edge_props[name] = {"values": cast("Sequence", masked_values)}
            else:
                edge_props[name] = {"values": cast("NDArray", np.array(masked_values))}
            if "missing" in props:
                edge_masked_missing: Sequence | NDArray[np.bool] | None = None
                edge_masked_missing = cast("NDArray", props["missing"])[
                    edge_mask.tolist() if edge_mask is not None else ...
                ]
                cast("PropDictNpArray", edge_props[name])["missing"] = np.array(
                    edge_masked_missing,
                    dtype=bool,
                )

        return {
            "metadata": self.metadata,
            "node_ids": nodes,
            "node_props": node_props,
            "edge_ids": edges,
            "edge_props": edge_props,
        }


# NOTE: if different FileReaders exist in the future a `file_reader` argument can be
#   added to this function to select between them.
def read_to_memory(
    source: StoreLike,
    validate: bool = True,
    node_props: list[str] | None = None,
    edge_props: list[str] | None = None,
) -> InMemoryGeff:
    """
    Read a GEFF zarr file to into memory as a series of numpy arrays in a dictionary.

    A subset of node and edge properties can be selected with the `node_props` and
    `edge_props` argument.

    Args:
        source (str | Path | zarr store): Either a path to the root of the geff zarr
            (where the .attrs contains the geff metadata), or a zarr store object
        validate (bool, optional): Flag indicating whether to perform validation on the
            geff file before loading into memory. If set to False and there are
            format issues, will likely fail with a cryptic error. Defaults to True.
        node_props (list of str, optional): The names of the node properties to load,
            if None all properties will be loaded, defaults to None.
        edge_props (list of str, optional): The names of the edge properties to load,
            if None all properties will be loaded, defaults to None.

    Returns:
        A InMemoryGeff object containing the graph as a TypeDict of in memory numpy arrays
        (metadata, node_ids, edge_ids, node_props, edge_props)
    """

    file_reader = GeffReader(source, validate)

    file_reader.read_node_props(node_props)
    file_reader.read_edge_props(edge_props)
    file_reader.read_vlen_node_props(node_props)
    file_reader.read_vlen_edge_props(edge_props)

    in_memory_geff = file_reader.build()
    return in_memory_geff
