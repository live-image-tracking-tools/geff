import abc
from typing import Any, Sequence

import numpy as np
import zarr
from numpy.typing import ArrayLike


class BaseWriterHelper(abc.ABC):
    """
    Base class for writing geff attributes to a zarr group.

    Important:
        This function does not create the `ids` attribute.

    Args:
        group: The zarr group to write the attribute to.
        position_attr: The name of the position attribute.

    Raises:
        ValueError: If the group is not a 'nodes' or 'edges' group.
    """

    def __init__(self, group: zarr.Group, position_attr: str | None):
        if group.name not in ["/nodes", "/edges"]:
            raise ValueError(f"Group must be a 'nodes' or 'edges' group. Found {group.name}")

        self._group = group
        self._position_attr = position_attr

    @abc.abstractmethod
    def _data_dict_iterator(self) -> Sequence[tuple[Any, dict[str, Any]]]:
        """
        Methods to iterate over the data dictionary to be written.
        Must match the index ordering
        """

    @abc.abstractmethod
    def _attr_names(self) -> list[str]:
        """
        Methods to iterate over the attribute names to be written.
        """

    def write_attrs(self) -> None:
        """
        Write the attributes to the zarr group.
        """
        seen_position = False
        for name in self._attr_names():
            values = []
            missing = []

            if self._position_attr is None:
                is_position = False
            else:
                is_position = name == self._position_attr
                seen_position |= is_position

            for key, data_dict in self._data_dict_iterator():
                if name in data_dict:
                    values.append(data_dict[name])
                    missing.append(False)
                else:
                    values.append(0)  # this fails to non-scalar attributes
                    missing.append(True)
                    if is_position:
                        raise ValueError(f"Element '{key}' does not have position attribute")

            self._write_geff_attr(
                attr_name=name,
                values=values,
                missing=missing,
                is_position=is_position,
            )

        if self._position_attr is not None and not seen_position:
            raise ValueError(
                f"Position attribute ('{self._position_attr}') not found in {self._attr_names()}"
            )

    def _write_geff_attr(
        self,
        attr_name: str,
        values: ArrayLike,
        missing: ArrayLike,
        is_position: bool,
    ) -> None:
        """
        Write a geff attribute to a zarr group.

        Args:
            group: The zarr group to write the attribute to.
            attr_name: The name of the attribute to write.
            values: The values of the attribute to write.
            missing: The missing values of the attribute to write.
            is_position: Whether the attribute is a position attribute.

        Raises:
            ValueError: If the group is not a 'nodes' or 'edges' group.
        """
        self._group[f"attrs/{attr_name}/values"] = np.asarray(values)

        if not is_position:
            self._group[f"attrs/{attr_name}/missing"] = np.asarray(missing, dtype=bool)
