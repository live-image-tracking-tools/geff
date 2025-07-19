from typing import Any, Sequence

import numpy as np
import zarr


def write_props(
    group: zarr.Group,
    data: Sequence[tuple[Any, dict[str, Any]]],
    prop_names: Sequence[str],
    axis_names: list[str] | None = None,
) -> None:
    """
    Write the properties to the zarr group.

    Args:
        group: The zarr group to write the property to (e.g. `nodes` or `edges`)
        data: A sequence of (id, data) pairs. For example, graph.nodes(data=True) for networkx
        prop_names: The names of the properties to write.
        node_dtype: The numpy dtype to use for the node and edge ID datasets.
        axis_names: The name of the spatiotemporal properties

    Raises:
        ValueError: If the group is not a 'nodes' or 'edges' group.
    """
    # sanity check if the user is writing to the correct group (e.g. not `props` directly)
    if group.name not in ["/nodes", "/edges"]:
        raise ValueError(f"Group must be a 'nodes' or 'edges' group. Found {group.name}")

    ids = [idx for idx, _ in data]

    if len(ids) > 0:
        group["ids"] = np.asarray(ids)
    # special corner cases where the graph is empty the ids must still have the
    # correct dimension (N,) for nodes, (N, 2) for edges
    elif group.name == "/nodes":
        group["ids"] = np.empty((0,), dtype=np.int64)
    elif group.name == "/edges":
        group["ids"] = np.empty((0, 2), dtype=np.int64)
    else:
        raise ValueError(f"Invalid group name: {group.name}")

    if axis_names is None:
        seen_axes = None
    else:
        seen_axes = [
            False,
        ] * len(axis_names)

    for name in prop_names:
        values = []
        missing = []

        if axis_names is None:
            is_position = False
        else:
            is_position = name in axis_names
            if is_position:
                seen_axes[axis_names.index(name)] = True  # type: ignore

        # iterate over the data and checks for missing content
        for key, data_dict in data:
            if name in data_dict:
                values.append(data_dict[name])
                missing.append(False)
            else:
                values.append(0)  # this fails to non-scalar properties
                missing.append(True)
                if is_position:
                    raise ValueError(f"Element '{key}' does not have position property")
        group[f"props/{name}/values"] = np.asarray(values)

        if not is_position:
            group[f"props/{name}/missing"] = np.asarray(missing, dtype=bool)

    if axis_names is not None and len(ids) > 0 and False in seen_axes:  # type: ignore
        missing_idx = seen_axes.index(False)  # type: ignore
        raise ValueError(f"Spatiotemporal property ('{axis_names[missing_idx]}') not found")
