import numpy as np
import zarr
from numpy.typing import ArrayLike


def write_geff_attr(
    group: zarr.Group,
    attr_name: str,
    values: ArrayLike,
    missing: ArrayLike | None = None,
) -> None:
    """
    Write a geff attribute to a zarr group.

    Args:
        group: The zarr group to write the attribute to.
        attr_name: The name of the attribute to write.
        values: The values of the attribute to write.
        missing: The missing values of the attribute to write.

    Raises:
        ValueError: If the group is not a 'nodes' or 'edges' group.
    """

    if group.name not in ["nodes", "edges"]:
        raise ValueError("Group must be a 'nodes' or 'edges' group")

    group[f"{group.name}/attrs/{attr_name}/values"] = np.asarray(values)

    if missing is not None:
        group[f"attrs/{attr_name}/missing"] = np.asarray(missing, astype=bool)
