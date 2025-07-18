from pathlib import Path

import pytest
import zarr

from geff.metadata_schema import GeffMetadata
from geff.utils import validate
from geff.writer_helper import write_attrs


def test_write_attrs(tmp_path: Path) -> None:
    zpath = tmp_path / "test.zarr"
    z = zarr.open(zpath)

    write_attrs(
        group=z.require_group("nodes"),
        data=[
            (0, {"a": 1, "b": 2}),
            (127, {"a": 5}),
            (1, {"a": 6, "c": 7}),
        ],
        attr_names=["a", "b", "c"],
        position_attr="a",
    )

    write_attrs(
        group=z.require_group("edges"),
        data=[
            ((0, 127), {"score": 0.5}),
            ((127, 1), {}),
            ((1, 0), {"score": 0.7}),
        ],
        attr_names=["score"],
    )

    metadata = GeffMetadata(
        geff_version="0.1.0",
        directed=True,
        position_attr="a",
        roi_min=(0,),
        roi_max=(7,),
    )
    metadata.write(z)

    validate(zpath)


def test_write_attrs_empty(tmp_path: Path) -> None:
    zpath = tmp_path / "test.zarr"
    z = zarr.open(zpath)

    write_attrs(
        group=z.require_group("nodes"),
        data=[],
        attr_names=["a"],
    )

    write_attrs(
        group=z.require_group("edges"),
        data=[],
        attr_names=["score"],
    )

    metadata = GeffMetadata(
        geff_version="0.1.0",
        directed=True,
    )
    metadata.write(z)

    validate(zpath)


def test_write_attrs_invalid_group(tmp_path: Path) -> None:
    zpath = tmp_path / "test.zarr"
    z = zarr.open(zpath)

    with pytest.raises(ValueError, match="Group must be a 'nodes' or 'edges' group"):
        write_attrs(group=z, data=[], attr_names=["a"])
