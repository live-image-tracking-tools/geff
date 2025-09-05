from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Sequence

    from numpy.typing import ArrayLike

    from geff._typing import InMemoryGeff
    from geff.metadata._schema import GeffMetadata


def has_valid_seg_id(memory_geff: InMemoryGeff, seg_id: str = "seg_id") -> tuple[bool, list[str]]:
    """
    Validate that all nodes in the geff have a property 'seg_id', that is of type integer.

    Args:
        memory_geff (InMemoryGeff): An InMemoryGeff to check for seg_id
        seg_id (str): the key to the dataset storing the segmentation value.

    Returns:
        tuple (bool, list[str])
        True if the checks passed, False if validation failed due to missing data or
        non-integer seg_ids.
        A list of encountered errors.
    """

    errors: list[str] = []

    # check that 'seg_id' property is present in the nodes group
    if seg_id not in memory_geff["node_props"]:
        errors.append("Missing seg_id property in Zarr store")
        return False, errors

    seg_ids = memory_geff["node_props"][seg_id]["values"]
    # Check that seg_id array is of integer type
    if not np.issubdtype(seg_ids.dtype, np.integer):
        errors.append(f"'seg_id' array has non-integer dtype: {seg_ids.dtype}")
        return False, errors

    # Check for no missing seg ids
    missing = memory_geff["node_props"][seg_id]["missing"]
    if missing is not None and any(missing):
        errors.append("Mismatch in number of node IDs and seg_ids.")
        return False, errors

    return len(errors) == 0, errors


def axes_match_seg_dims(
    memory_geff: InMemoryGeff,
    segmentation: ArrayLike,
) -> tuple[bool, list[str]]:
    """Validate that geff axes metadata have the same number of dimensions as the
    segmentation data.

    Args:
        memory_geff (InMemoryGeff): An InMemoryGeff to validate
        segmentation (ArrayLike): a 3D or 4D segmentation array (t, (z), y, x).

    Returns:
        tuple (bool, list[str])
        True if all checks passed
        False if the store does not provide metadata or if the number of dimensions in the
        metadata does not match that of the segmentation.
        A list of length 0 or 1 with the encountered error, if any.
    """

    errors: list[str] = []
    axes = memory_geff["metadata"].axes

    if axes:
        return np.asanyarray(segmentation).ndim == len(axes), errors
    else:
        errors.append("No axes metadata found in this geff.")
        return False, errors


def graph_is_in_seg_bounds(
    memory_geff: InMemoryGeff,
    segmentation: ArrayLike,
    scale: Sequence[float] | None = None,
) -> tuple[bool, list[str]]:
    """Validate that geff axes metadata have the same number of dimensions as the
    segmentation data.

    Args:
        memory_geff (InMemoryGeff): An InMemoryGeff to validate
        segmentation (ArrayLike): a 3D or 4D segmentation array (t, (z), y, x).
        scale (tuple[float] | list[float] | None = None): optional scaling tuple, with the
            same length as the number of dimensions in the segmentation data.

    Returns:
        tuple (bool, list[str])
        True if all checks passed
        False if the store does not provide metadata, if the provided scale tuple does not
            have the same length as the number of dimensions in the segmentation, if the
            number of dimensions in the metadata does not match that of the segmentation,
            or if the (scaled) graph data is not within the segmentation bounds.
        A list of length 0 or 1 with the encountered error, if any.
    """

    errors: list[str] = []
    axes = memory_geff["metadata"].axes

    segmentation = np.asanyarray(segmentation)
    seg_shape = segmentation.shape

    if scale is None:
        scale = [1.0] * segmentation.ndim

    if len(scale) != segmentation.ndim:
        errors.append(
            f"Length of scale factor list ({len(scale)} does not match with the number "
            f"of dimensions in the segmentation ({segmentation.ndim})"
        )
        return False, errors

    if axes:
        for i, ax in enumerate(axes):
            max_bound = ax.max
            if max_bound:
                if seg_shape[i] * scale[i] <= max_bound:
                    errors.append(
                        f"Graph axis {i} is out of bounds with value {max_bound} in "
                        f"segmentation axis size {seg_shape[i]} and scale factor "
                        f"{scale[i]}"
                    )
                    return False, errors
            else:
                errors.append("No axis 'max' value found in this geff metadata.")
                return False, errors
        return True, errors
    else:
        errors.append("No axes metadata found in this geff.")
        return False, errors


def has_seg_ids_at_time_points(
    segmentation: ArrayLike,
    time_points: Sequence[int],
    seg_ids: Sequence[int],
    metadata: GeffMetadata | None = None,
) -> tuple[bool, list[str]]:
    """
    Validates that labels with given seg_ids exist at time points t. If a store is
    provided, the time axis will be identified by the metadata using the 'type' key. If
    this is not possible, it is assumed that time is on axis 0.

    Args:
        segmentation (ArrayLike): a 3D or 4D segmentation array (t, (z), y, x).
        time_points (Sequence[int]): Sequence of time points to check.
        seg_ids (Sequence[int]): Sequence of seg_ids to check.
        metadata (GeffMetadata): If provided, it will attempt to read the axis order from the
            metadata. Otherwise, it is assumed that the dimension order is t(z)yx.

    Returns:
        tuple (bool, list[str])
        True if all seg_ids are present at their respective time points, False if an
        Index error is encountered or if there are any missing labels.
        A list of encountered errors (can be of length 1 when returning early).
    """

    errors: list[str] = []
    time_index = 0
    if metadata is not None:
        # load the axes metadata to extract the axes order. If it is not present, assume
        # that time is the first axes.
        axes = metadata.axes

        # check the metadata to see if an alternative time index is provided there.
        if axes:
            time_indices = [axes.index(ax) for ax in axes if ax.type == "time"]
            if len(time_indices) == 1:
                time_index = time_indices[0]

    # Create dictionary to map multiple seg_ids to the same time point.
    seg_id_group = defaultdict(list)
    for t, seg_id in zip(time_points, seg_ids, strict=False):
        seg_id_group[t].append(seg_id)

    # Loop over all time points, collect the label values, and check if the seg_ids are
    # present
    missing = defaultdict(list)
    for t in time_points:
        try:
            labels = np.unique(np.take(segmentation, indices=t, axis=time_index))
        except IndexError as e:
            errors.append(f"Time point {t} is out of bounds: {e}")
            return False, errors

        label_set = set(labels.tolist())
        for seg_id in seg_id_group[t]:
            if seg_id not in label_set:
                errors.append(f"Missing seg_id {seg_id} at time {t}")
                missing[t].append(seg_id)

    if len(missing) > 0:
        return False, errors
    return True, errors


def has_seg_ids_at_coords(
    segmentation: ArrayLike,
    coords: Sequence[Sequence[int]],
    seg_ids: Sequence[int],
    scale: Sequence[float] | None = None,
) -> tuple[bool, list[str]]:
    """
    Validates that the pixels at given coordinates in the segmentation have a value equal
      to the provided seg_ids.

    Args:
        segmentation (ArrayLike): a 3D or 4D segmentation array (t, (z), y, x).
        coords (Sequence[Sequence[int]]): Sequence of t(z)yx coordinates, should have the
            same order as the segmentation dimensions.
        seg_ids (Sequence[int]): Sequence of corresponding seg_ids to check.
        scale (Sequence[float] | None = None): optional scaling tuple, with the same
            length as the number of dimensions in the segmentation data.

    Returns:
        tuple[bool, list[str]]:
        True if all checks pass, False if an error was encountered or if there is no
        match.
        A list of encountered errors (can be of length 1 when returning early).

    """

    errors: list[str] = []
    if not len(coords) == len(seg_ids):
        errors.append("Coordinate list must have the same length as the list of seg_ids to test.")
        return False, errors

    segmentation = np.asanyarray(segmentation)
    if scale is None:
        scale = [1.0] * segmentation.ndim

    if len(scale) != segmentation.ndim:
        errors.append(
            f"Length of scale factor list ({len(scale)} does not match with the number "
            f"of dimensions in the segmentation ({segmentation.ndim})"
        )
        return False, errors

    missing = {}
    for coord, seg_id in zip(coords, seg_ids, strict=False):
        try:
            scaled_coord = [int(c * s) for c, s in zip(coord, scale, strict=True)]
            value = segmentation[tuple(scaled_coord)]
        except IndexError:
            errors.append(
                f"Coords {coord} are out of bounds for segmentation data with shape"
                f"{segmentation.shape} and scale factors {scale}"
            )
            return False, errors

        if value != seg_id:
            missing[seg_id] = coords

    if len(missing) > 0:
        return False, errors
    return True, errors
