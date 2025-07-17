from typing import Any, Sequence

import numpy as np
import zarr
from numpy.typing import ArrayLike


class BaseWriterHelper:
    """
    Base class for writing geff attributes to a zarr group.

    Important:
        This function does not create the `ids` attribute.

    Args:
        data: A sequence of (id, data) pairs. For example, graph.nodes(data=True) for networkx
        position_attr: The name of the position attribute.

    Raises:
        ValueError: If the group is not a 'nodes' or 'edges' group.
    """

    def __init__(self, data: Sequence[tuple[Any, dict[str, Any]]], position_attr: str | None):
        self._data = data
        self._position_attr = position_attr

    def _attr_names(self) -> list[str]:
        return list({k for _, data in self._data for k in data})

    def write_attrs(self, group: zarr.Group) -> None:
        """
        Write the attributes to the zarr group.

        Args:
            group: The zarr group to write the attribute to.
        """
        # sanity check if the user is writing to the correct group (e.g. not `attrs` directly)
        if group.name not in ["/nodes", "/edges"]:
            raise ValueError(f"Group must be a 'nodes' or 'edges' group. Found {group.name}")

        ids = [idx for idx, _ in self._data]

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

        seen_position = False
        for name in self._attr_names():
            values = []
            missing = []

            if self._position_attr is None:
                is_position = False
            else:
                is_position = name == self._position_attr
                seen_position |= is_position

            # iterate over the data and checks for missing content
            for key, data_dict in self._data:
                if name in data_dict:
                    values.append(data_dict[name])
                    missing.append(False)
                else:
                    values.append(0)  # this fails to non-scalar attributes
                    missing.append(True)
                    if is_position:
                        raise ValueError(f"Element '{key}' does not have position attribute")

            self._write_geff_attr(
                group=group,
                attr_name=name,
                values=values,
                missing=missing,
                is_position=is_position,
            )

        if self._position_attr is not None and not seen_position:
            raise ValueError(
                f"Position attribute ('{self._position_attr}') not found in {self._attr_names()}"
            )

    @staticmethod
    def _write_geff_attr(
        group: zarr.Group,
        attr_name: str,
        values: ArrayLike,
        missing: ArrayLike,
        is_position: bool,
    ) -> None:
        """
        Write a geff attribute to a zarr group.

        Args:
            group: The zarr group to write the attribute to (e.g. `nodes` or `edges`)
            attr_name: The name of the attribute to write.
            values: The values of the attribute to write.
            missing: The missing values of the attribute to write.
            is_position: Whether the attribute is a position attribute.

        Raises:
            ValueError: If the group is not a 'nodes' or 'edges' group.
        """
        group[f"attrs/{attr_name}/values"] = np.asarray(values)

        if not is_position:
            group[f"attrs/{attr_name}/missing"] = np.asarray(missing, dtype=bool)
