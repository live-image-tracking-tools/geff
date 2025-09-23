from __future__ import annotations

import copy
from typing import TYPE_CHECKING

import numpy as np
import zarr

from geff import _path
from geff.core_io._utils import expect_array, expect_group, open_storelike, remove_tilde
from geff.validate.data import ValidationConfig, validate_data
from geff.validate.structure import validate_structure
from geff_spec import GeffMetadata, PropMetadata

from ._serialization import deserialize_vlen_property_data

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Literal

    from numpy.typing import NDArray
    from zarr.storage import StoreLike

    from geff._typing import InMemoryGeff, PropDictNpArray, ZarrPropDict


class GeffReader:
    """File reader class that allows subset reading to an intermediate dict representation.

    The subsets can be a subset of node and edge properties, and a subset of nodes and
    edges.

    Example:
    ```
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

    >>> in_memory_geff = file_reader.build(file_reader.node_props["t"]["values"][:] < 5)
    ... # Now in_memory_geff will only be a subset with nodes "t" < 5
    ... in_memory_geff
    ```
    """

    def __init__(self, source: StoreLike, validate: bool = True) -> None:
        """
        File reader class that allows subset reading to an intermediate dict representation.

        Args:
            source (str | Path | zarr.store): Either a str/path to the root of the geff zarr
                (where the .attrs contains the geff metadata), or a zarr store object
            validate (bool, optional): Flag indicating whether to perform validation on the
                geff file before loading into memory. If set to False and there are
                format issues, will likely fail with a cryptic error. Defaults to True.
        """
        source = remove_tilde(source)

        if validate:
            validate_structure(source)
        self.group = open_storelike(source)
        self.metadata = GeffMetadata.read(source)
        self.nodes = zarr.open_array(source, path=_path.NODE_IDS, mode="r")
        self.edges = zarr.open_array(source, path=_path.EDGE_IDS, mode="r")
        self.node_props: dict[str, ZarrPropDict] = {}
        self.edge_props: dict[str, ZarrPropDict] = {}

        # get node properties names
        nodes_group = expect_group(self.group, _path.NODES)
        if _path.PROPS in nodes_group.keys():
            node_props_group = zarr.open_group(self.group.store, path=_path.NODE_PROPS, mode="r")
            self.node_prop_names: list[str] = [*node_props_group.group_keys()]
        else:
            self.node_prop_names = []

        # get edge property names
        edges_group = expect_group(self.group, _path.EDGES)
        if _path.PROPS in edges_group.keys():
            edge_props_group = zarr.open_group(self.group.store, path=_path.EDGE_PROPS, mode="r")
            self.edge_prop_names: list[str] = [*edge_props_group.group_keys()]
        else:
            self.edge_prop_names = []

    def read_node_props(self, names: Iterable[str] | None = None) -> None:
        """
        Read the node property with the name `name` from a GEFF.

        If no names are specified, then all properties will be loaded

        Call `build` to get the output `InMemoryGeff` with the loaded properties.

        Args:
            names (iterable of str, optional): The names of the node properties to load. If
                None all node properties will be loaded.
        """
        if names is None:
            names = self.node_prop_names

        for name in names:
            self.node_props[name] = self._read_prop(name, "node")

    def read_edge_props(self, names: Iterable[str] | None = None) -> None:
        """
        Read the edge property with the name `name` from a GEFF.

        If no names are specified, then all properties will be loaded

        Call `build` to get the output `InMemoryGeff` with the loaded properties.

        Args:
            names (iterable of str, optional): The names of the edge properties to load. If
                None all node properties will be loaded.
        """
        if names is None:
            names = self.edge_prop_names

        for name in names:
            self.edge_props[name] = self._read_prop(name, "edge")

    def _read_prop(self, name: str, prop_type: Literal["node", "edge"]) -> ZarrPropDict:
        """Read a property into a zarr property dictionary

        Args:
            name (str): The name of the property to read
            prop_type (Literal["node", "edge"]): Either `node` or `edge`

        Returns:
            ZarrPropDict: A dictionary with "values" "missing" and optionally "data" arrays
                holding the zarr arrays for a property.
        """
        group_path = (
            f"{_path.NODE_PROPS}/{name}" if prop_type == "node" else f"{_path.EDGE_PROPS}/{name}"
        )
        prop_group = zarr.open_group(self.group.store, path=group_path, mode="r")
        values = expect_array(prop_group, _path.VALUES, prop_type)
        prop_dict: ZarrPropDict = {_path.VALUES: values}
        if _path.MISSING in prop_group.keys():
            missing = expect_array(prop_group, _path.MISSING, prop_type)
            prop_dict[_path.MISSING] = missing

        if _path.DATA in prop_group.keys():
            prop_dict[_path.DATA] = expect_array(prop_group, _path.DATA, prop_type)
        return prop_dict

    def _load_prop_to_memory(
        self, zarr_prop: ZarrPropDict, mask: NDArray[np.bool_] | None, prop_metadata: PropMetadata
    ) -> PropDictNpArray:
        """Load a zarr property dictionary into memory, including deserialization.

        Has option to only load a subset of the nodes or edges by providing a mask.

        Args:
            zarr_prop (ZarrPropDict): The zarr property dictionary to load and deserialize.
            mask (NDArray[np.bool_] | None): A mask to use to only include a subset of the elements.
                Can be None, which loads all the elements to memory.
            prop_metadata (PropMetadata): The metadata of the given property.

        Raises:
            ValueError: If the property is varlength and no `data` array is provided.

        Returns:
            PropDictNpArray: The property loaded into memory as "values" and "missing" arrays.
        """
        dtype = np.dtype(prop_metadata.dtype)
        values_dtype = np.uint64 if prop_metadata.varlength else dtype
        values = np.array(
            zarr_prop[_path.VALUES][mask.tolist() if mask is not None else ...],
            dtype=values_dtype,
        )
        if _path.MISSING in zarr_prop:
            missing = np.array(
                zarr_prop[_path.MISSING][mask.tolist() if mask is not None else ...],
                dtype=bool,
            )
        else:
            missing = None
        if _path.DATA in zarr_prop:
            data = np.array(
                zarr_prop[_path.DATA][mask.tolist() if mask is not None else ...],
                dtype=dtype,
            )
        else:
            data = None

        in_memory_dict: PropDictNpArray
        if prop_metadata.varlength:
            if data is None:
                raise ValueError(
                    f"Property {prop_metadata.identifier} metadata is varlength but no "
                    "serialized data was found in GEFF zarr"
                )
            in_memory_dict = deserialize_vlen_property_data(values, missing, data)
        else:
            in_memory_dict = {
                "values": values,
                "missing": missing,
            }
        return in_memory_dict

    def build(
        self,
        node_mask: NDArray[np.bool_] | None = None,
        edge_mask: NDArray[np.bool_] | None = None,
    ) -> InMemoryGeff:
        """
        Build an `InMemoryGeff` by loading the data from a GEFF zarr.

        A set of nodes and edges can be selected using `node_mask` and `edge_mask`.

        Args:
            node_mask (np.ndarray of bool): A boolean numpy array to mask build a graph
                of a subset of nodes, where `node_mask` is equal to True. It must be a 1D
                array of length number of nodes.
            edge_mask (np.ndarray of bool): A boolean numpy array to mask build a graph
                of a subset of edge, where `edge_mask` is equal to True. It must be a 1D
                array of length number of edges.
        Returns:
            InMemoryGeff: A dictionary of in memory numpy arrays representing the graph.
        """
        nodes = np.array(self.nodes[node_mask.tolist() if node_mask is not None else ...])
        node_props: dict[str, PropDictNpArray] = {}
        for name, props in self.node_props.items():
            prop_metadata = self.metadata.node_props_metadata[name]
            node_props[name] = self._load_prop_to_memory(props, node_mask, prop_metadata)

        # remove edges if any of it's nodes has been masked
        edges = np.array(self.edges[:])
        if node_mask is not None:
            edge_mask_removed_nodes = np.isin(edges, nodes).all(axis=1)
            if edge_mask is not None:
                edge_mask = np.logical_and(edge_mask, edge_mask_removed_nodes)
            else:
                edge_mask = edge_mask_removed_nodes  # type: ignore[assignment]
        edges = edges[edge_mask if edge_mask is not None else ...]

        edge_props: dict[str, PropDictNpArray] = {}
        for name, props in self.edge_props.items():
            prop_metadata = self.metadata.edge_props_metadata[name]
            edge_props[name] = self._load_prop_to_memory(props, edge_mask, prop_metadata)

        # we have to remove the unused properties from the props_metadata
        output_metadata = copy.deepcopy(self.metadata)

        all_node_props = self.metadata.node_props_metadata.keys()
        for prop in all_node_props:
            if prop not in self.node_props.keys():
                del output_metadata.node_props_metadata[prop]

        all_edge_props = self.metadata.edge_props_metadata.keys()
        for prop in all_edge_props:
            if prop not in self.edge_props.keys():
                del output_metadata.edge_props_metadata[prop]

        return {
            "metadata": output_metadata,
            "node_ids": nodes,
            "node_props": node_props,
            "edge_ids": edges,
            "edge_props": edge_props,
        }


# NOTE: if different FileReaders exist in the future a `file_reader` argument can be
#   added to this function to select between them.
def read_to_memory(
    source: StoreLike,
    structure_validation: bool = True,
    node_props: Iterable[str] | None = None,
    edge_props: Iterable[str] | None = None,
    data_validation: ValidationConfig | None = None,
) -> InMemoryGeff:
    """
    Read a GEFF zarr file to into memory as a series of numpy arrays in a dictionary.

    A subset of node and edge properties can be selected with the `node_props` and
    `edge_props` argument.

    Args:
        source (str | Path | zarr store): Either a path to the root of the geff zarr
            (where the .attrs contains the geff metadata), or a zarr store object
        structure_validation (bool, optional): Flag indicating whether to perform metadata/structure
            validation on the geff file before loading into memory. If set to False and
            there are format issues, will likely fail with a cryptic error. Defaults to True.
        data_validation (ValidationConfig, optional): Optional configuration for which
            optional types of data to validate. Each option defaults to False.
        node_props (iterable of str, optional): The names of the node properties to load,
            if None all properties will be loaded, defaults to None.
        edge_props (iterable of str, optional): The names of the edge properties to load,
            if None all properties will be loaded, defaults to None.

    Returns:
        A InMemoryGeff object containing the graph as a TypeDict of in memory numpy arrays
        (metadata, node_ids, edge_ids, node_props, edge_props)
    """

    file_reader = GeffReader(source, structure_validation)

    file_reader.read_node_props(node_props)
    file_reader.read_edge_props(edge_props)
    in_memory_geff = file_reader.build()

    if data_validation is not None:
        validate_data(config=data_validation, memory_geff=in_memory_geff)

    return in_memory_geff
