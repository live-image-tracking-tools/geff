from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
import zarr

import geff

if TYPE_CHECKING:
    import rustworkx as rx

from geff.metadata_schema import GeffMetadata


def write_rx(
    graph: "rx.PyGraph",
    path: str | Path,
    node_id_dict: dict[int, int] | None = None,
    position_attr: str | None = None,
    axis_names: list[str] | None = None,
    axis_units: list[str] | None = None,
    zarr_format: int = 2,
    validate: bool = True,
) -> None:
    """
    Write a rustworkx graph to the geff file format
    """


def _set_attribute_values(
    rx_attrs: list[dict],
    group: zarr.Group,
) -> None:
    """Add attributes in-place to a networkx graph's nodes or edges."""
    arange = np.arange(len(rx_attrs))

    for name in group.keys():
        attrs = group[f"{name}/values"][...].tolist()

        try:
            missing = group[f"{name}/missing"][...]
            current_indices = arange[~missing]
        except KeyError:
            current_indices = arange

        for idx in current_indices.tolist():
            rx_attrs[idx][name] = attrs[idx]


def read_rx(
    path: Path | str,
    validate: bool = True,
) -> tuple["rx.PyGraph", dict[int, int]]:
    """
    Read a geff file into a rustworkx graph.
    Metadata attributes will be stored in the graph attributes
    and can be accessed via `G.attrs[key]` where G is a rustworkx graph.

    Args:
        path: Path to the geff file.
        validate: Whether to validate the geff file.

    Returns:
        A tuple containing the rustworkx graph and a dictionary mapping node ids to rx ids.
        The rx ids are 0-indexed.
    """
    try:
        import rustworkx as rx

    except ImportError as e:
        raise ImportError(
            "rustworkx is not installed. Please install it with `pip install rustworkx`."
        ) from e

    path = Path(path)

    if validate:
        geff.utils.validate(path)

    group = zarr.open(path, mode="r")
    metadata = GeffMetadata.read(group)

    graph = rx.PyDiGraph() if metadata.directed else rx.PyGraph()
    graph.attrs = metadata.model_dump()

    node_ids = group["nodes/ids"][...].tolist()

    # adding nodes with empty dicts to initialize the attributes
    # these dict are populated in `_set_attribute_values`
    node_attrs: list[dict[str, Any]] = [{} for _ in node_ids]
    rx_node_ids = graph.add_nodes_from(node_attrs)

    to_rx_id_map = dict(zip(node_ids, rx_node_ids))

    _set_attribute_values(node_attrs, group["nodes/attrs"])

    if "edges" in group.group_keys():
        edge_ids = group["edges/ids"][...].tolist()
        # and same as node_attrs, initialize the attributes with empty dicts
        edge_attrs: list[dict[str, Any]] = [{} for _ in range(len(edge_ids))]

        # converting node ids (arbitrary index) to rx ids (0-indexed)
        edges = [
            (to_rx_id_map[i], to_rx_id_map[j], attr) for (i, j), attr in zip(edge_ids, edge_attrs)
        ]
        graph.add_edges_from(edges)

        if "edges/attrs" in group:
            _set_attribute_values(edge_attrs, group["edges/attrs"])

    return graph, to_rx_id_map


if __name__ == "__main__":
    path = "/Users/jordao.bragantini/Data/geff/Fluo-N3DL-DRO.zarr/01/tracks"
    graph, to_rx_id_map = read_rx(path)
    print(graph.num_nodes())
    print(graph.num_edges())
