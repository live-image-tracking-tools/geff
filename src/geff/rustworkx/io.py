import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
import zarr

import geff

if TYPE_CHECKING:
    import rustworkx as rx  # noqa: TC004

from geff.metadata_schema import GeffMetadata
from geff.writer_helper import write_props


def write_rx(
    graph: "rx.PyGraph",
    path: str | Path,
    node_id_dict: dict[int, int] | None = None,
    position_prop: str | None = None,
    axis_names: list[str] | None = None,
    axis_units: list[str] | None = None,
    zarr_format: int = 2,
    validate: bool = True,
) -> None:
    """
    Write a rustworkx graph to the geff file format

    Args:
        graph: The rustworkx graph to write.
        path: The path to the geff file.
        node_id_dict: A dictionary mapping rx node indices to arbitrary indices.
        position_prop: The property name to use for the position.
        axis_names: The names of the axes.
        axis_units: The units of the axes.
        zarr_format: The zarr format to use.
        validate: Whether to validate the geff file.
    """
    if graph.num_nodes() == 0:
        warnings.warn(f"Graph is empty - not writing anything to {path}", stacklevel=2)
        return

    # open/create zarr container
    if zarr.__version__.startswith("3"):
        group = zarr.open(path, mode="a", zarr_format=zarr_format)
    else:
        group = zarr.open(path, mode="a")

    if node_id_dict is None:
        node_data = list(zip(graph.node_indices(), graph.nodes()))
    else:
        node_data = [(node_id_dict[i], d) for i, d in zip(graph.node_indices(), graph.nodes())]

    write_props(
        group=group.require_group("nodes"),
        data=node_data,
        prop_names=list({k for _, data in node_data for k in data}),
        position_prop=position_prop,
    )
    del node_data

    if node_id_dict is None:
        edge_data = [((u, v), data) for u, v, data in graph.weighted_edge_list()]
    else:
        edge_data = [
            ((node_id_dict[u], node_id_dict[v]), data) for u, v, data in graph.weighted_edge_list()
        ]

    write_props(
        group=group.require_group("edges"),
        data=edge_data,
        prop_names=list({k for _, data in edge_data for k in data}),
    )
    del edge_data

    # TODO: roi and other stuff
    # write metadata

    metadata = GeffMetadata(
        geff_version=geff.__version__,
        directed=isinstance(graph, rx.PyDiGraph),
        roi_min=None,  # FIXME
        roi_max=None,  # FIXME
        position_prop=position_prop,
        axis_names=axis_names if axis_names is not None else graph.attrs.get("axis_names", None),
        axis_units=axis_units if axis_units is not None else graph.attrs.get("axis_units", None),
    )
    metadata.write(group)


def _set_properties_values(
    rx_props: list[dict],
    group: zarr.Group,
) -> None:
    """Add properties in-place to a rustworkx graph's nodes or edges."""
    arange = np.arange(len(rx_props))

    for name in group.keys():
        props = group[f"{name}/values"][...].tolist()

        try:
            missing = group[f"{name}/missing"][...]
            current_indices = arange[~missing]
        except KeyError:
            current_indices = arange

        for idx in current_indices.tolist():
            rx_props[idx][name] = props[idx]


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

    # adding nodes with empty dicts to initialize the properties
    # these dict are populated in `_set_properties_values`
    node_props: list[dict[str, Any]] = [{} for _ in node_ids]
    rx_node_ids = graph.add_nodes_from(node_props)

    to_rx_id_map = dict(zip(node_ids, rx_node_ids))

    _set_properties_values(node_props, group["nodes/props"])

    if "edges" in group.group_keys():
        edge_ids = group["edges/ids"][...].tolist()
        # and same as node_props, initialize the properties with empty dicts
        edge_props: list[dict[str, Any]] = [{} for _ in range(len(edge_ids))]

        # converting node ids (arbitrary index) to rx ids (0-indexed)
        edges = [
            (to_rx_id_map[i], to_rx_id_map[j], attr) for (i, j), attr in zip(edge_ids, edge_props)
        ]
        graph.add_edges_from(edges)

        if "edges/props" in group:
            _set_properties_values(edge_props, group["edges/props"])

    return graph, to_rx_id_map


if __name__ == "__main__":
    path = "/Users/jordao.bragantini/Data/geff/Fluo-N3DL-DRO.zarr/01/tracks"
    graph, to_rx_id_map = read_rx(path)
    print(graph.num_nodes())
    print(graph.num_edges())
