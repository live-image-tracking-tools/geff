# TODO: update to test the new writer helper functions
# def test_write_props(tmp_path: Path) -> None:
#     zpath = tmp_path / "test.zarr"
#     z = zarr.open(zpath)

# write_props(
#     group=z.require_group("nodes"),
#     data=[
#         (0, {"a": 1, "b": 2}),
#         (127, {"a": 5}),
#         (1, {"a": 6, "c": 7}),
#     ],
#     prop_names=["a", "b", "c"],
#     axis_names=["a"],
# )

# write_props(
#     group=z.require_group("edges"),
#     data=[
#         ((0, 127), {"score": 0.5}),
#         ((127, 1), {}),
#         ((1, 0), {"score": 0.7}),
#     ],
#     prop_names=["score"],
# )
# axes = axes_from_lists(
#     axis_names=["x"],
#     roi_min=(0,),
#     roi_max=(7,),
# )
# metadata = GeffMetadata(
#     geff_version="0.1.0",
#     directed=True,
#     axes=axes,
# )
# metadata.write(z)

#     validate(zpath)


# def test_write_props_empty(tmp_path: Path) -> None:
#     zpath = tmp_path / "test.zarr"
#     z = zarr.open(zpath)

# write_props(
#     group=z.require_group("nodes"),
#     data=[],
#     prop_names=["a"],
# )

# write_props(
#     group=z.require_group("edges"),
#     data=[],
#     prop_names=["score"],
# )

#     metadata = GeffMetadata(
#         geff_version="0.1.0",
#         directed=True,
#     )
#     metadata.write(z)

#     validate(zpath)

#     assert z["nodes/ids"].shape == (0,)
#     assert z["edges/ids"].shape == (0, 2)


# def test_write_props_invalid_group(tmp_path: Path) -> None:
#     zpath = tmp_path / "test.zarr"
#     z = zarr.open(zpath)

# with pytest.raises(ValueError, match="Group must be a 'nodes' or 'edges' group"):
#     write_props(group=z, data=[], prop_names=["a"])
