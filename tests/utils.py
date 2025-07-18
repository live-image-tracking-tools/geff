import zarr


def check_equiv_geff(path_a, path_b):
    """This function compares two geffs, typically a starting fixture geff with
    the output of an implementation.

    This tests focuses on maintaining shape and dtype consistency. It does not
    assert element wise equality. path_a is assumed to be the "correct" geff.

    Args:
        path_a (str): Path to first zarr geff group
        path_b (str): Path to second zarr geff group
    """

    za = zarr.open(path_a)
    zb = zarr.open(path_b)

    for graph_group in ["nodes", "edges"]:
        ga = za[graph_group]
        gb = zb[graph_group]

        # Check ids
        assert ga["ids"].shape == gb["ids"].shape
        assert ga["ids"].dtype == gb["ids"].dtype

        # Check that properties in each geff are the same
        assert set(ga["props"]) == set(gb["props"])

        # Check shape and dtype of each prop
        for prop in ga["props"]:
            assert ga["props"][prop].shape == gb["props"][prop].shape
            assert ga["props"][prop].dtype == gb["props"][prop].dtype
