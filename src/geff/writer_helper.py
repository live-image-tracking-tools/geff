from typing import Any, Sequence

import numpy as np
import zarr


def write_props(
    group: zarr.Group,
    data: Sequence[tuple[Any, dict[str, Any]]],
    prop_names: Sequence[str],
    node_dtype: np.typing.DTypeLike,
    position_prop: str | None = None,
) -> None:
    """
    Write the properties to the zarr group.

    Args:
        group: The zarr group to write the property to (e.g. `nodes` or `edges`)
        data: A sequence of (id, data) pairs. For example, graph.nodes(data=True) for networkx
        prop_names: The names of the properties to write.
        node_dtype: The numpy dtype to use for the node and edge ID datasets.
        position_prop: The name of the position property.

    Raises:
        ValueError: If the group is not a 'nodes' or 'edges' group.
    """
    # sanity check if the user is writing to the correct group (e.g. not `props` directly)
    if group.name not in ["/nodes", "/edges"]:
        raise ValueError(f"Group must be a 'nodes' or 'edges' group. Found {group.name}")

    ids = [idx for idx, _ in data]

    if len(ids) > 0:
        group["ids"] = np.asarray(ids, dtype=node_dtype)
    # special corner cases where the graph is empty the ids must still have the
    # correct dimension (N,) for nodes, (N, 2) for edges
    elif group.name == "/nodes":
        group["ids"] = np.empty((0,), dtype=np.int64)
    elif group.name == "/edges":
        group["ids"] = np.empty((0, 2), dtype=np.int64)
    else:
        raise ValueError(f"Invalid group name: {group.name}")

    seen_position = False
    for name in prop_names:
        values = []
        missing = []

        if position_prop is None:
            is_position = False
        else:
            is_position = name == position_prop
            seen_position |= is_position

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

    if position_prop is not None and not seen_position:
        raise ValueError(f"Position property ('{position_prop}') not found in {prop_names}")
