import pytest
import zarr

try:
    import pandas as pd

    from geff.convert._dataframe import geff_to_csv, geff_to_dataframes
except ImportError:
    pytest.skip("geff[pandas] not installed", allow_module_level=True)

import os

import numpy as np
import pytest

from geff import _path
from geff.testing.data import create_mock_geff, create_simple_2d_geff, create_simple_3d_geff


class Test_geff_to_dataframes:
    def test_3d_geff(self):
        store, memory_geff = create_simple_3d_geff()
        node_df, edge_df = geff_to_dataframes(store)

        # Check node ids
        assert node_df["id"].dtype == memory_geff["node_ids"].dtype
        assert all(node_df["id"].to_numpy() == memory_geff["node_ids"])

        # Check edge ids
        assert edge_df["source"].dtype == memory_geff["edge_ids"].dtype
        assert edge_df["target"].dtype == memory_geff["edge_ids"].dtype
        assert all(edge_df["source"].to_numpy() == memory_geff["edge_ids"][:, 0])
        assert all(edge_df["target"].to_numpy() == memory_geff["edge_ids"][:, 1])

        # Check props which in this case are all 1d
        for df, props in [
            (node_df, memory_geff["node_props"]),
            (edge_df, memory_geff["edge_props"]),
        ]:
            for name, prop in props.items():
                assert df[name].dtype == prop["values"].dtype
                assert all(df[name].to_numpy() == prop["values"])

    def test_2d_prop(self):
        # Create data with a 2d node attribute
        n_nodes = 5
        special_prop = np.ones((n_nodes, 2))
        prop_name = "2d_prop"
        store, memory_geff = create_mock_geff(
            num_nodes=n_nodes,
            node_id_dtype="uint",
            node_axis_dtypes={"position": "float64", "time": "float64"},
            directed=True,
            extra_node_props={prop_name: special_prop},
        )
        df, _ = geff_to_dataframes(store)

        for i in range(2):
            assert df[f"{prop_name}_{i}"].dtype == special_prop.dtype
            assert all(df[f"{prop_name}_{i}"].to_numpy() == special_prop[:, i])

    def test_3d_prop(self):
        # Create data with a 3d node attribute
        n_nodes = 5
        special_prop = np.ones((n_nodes, 2, 2))
        prop_name = "3d_prop"
        store, memory_geff = create_mock_geff(
            num_nodes=n_nodes,
            node_id_dtype="uint",
            node_axis_dtypes={"position": "float64", "time": "float64"},
            directed=True,
            extra_node_props={prop_name: special_prop},
        )

        # More than 3d triggers warning and skips that prop
        with pytest.raises(
            UserWarning, match="will not be exported to csv with more than 2 dimensions"
        ):
            df, _ = geff_to_dataframes(store)

            assert set(df.columns) == {"t", "z", "x", "y"}

    def test_no_nodes(self):
        store, memory_geff = create_simple_3d_geff(num_nodes=0)
        node_df, edge_df = geff_to_dataframes(store)

        assert isinstance(node_df, pd.DataFrame)
        assert isinstance(edge_df, pd.DataFrame)
        assert len(node_df) == 0
        assert len(edge_df) == 0

    def test_no_edges(self):
        store, memory_geff = create_simple_3d_geff(num_edges=0)
        node_df, edge_df = geff_to_dataframes(store)

        assert isinstance(edge_df, pd.DataFrame)
        assert len(edge_df) == 0

    def test_missing(self):
        num_edges = 10
        store, memory_geff = create_simple_2d_geff(num_edges=num_edges)
        z = zarr.open(store)

        # Missing array exists but is all False, e.g. nothing missing
        missing = np.array([False] * num_edges)
        z[f"{_path.EDGE_PROPS}/score/{_path.MISSING}"] = missing  # pyright: ignore[reportArgumentType]
        node_df, edge_df = geff_to_dataframes(store)
        # No missing so shouldn't be any nans in values
        assert not any(edge_df["score"].isna())

        # Missing array with some values missing
        n_missing = 4
        missing = np.array([True] * n_missing + [False] * (num_edges - n_missing))
        z[f"{_path.EDGE_PROPS}/score/{_path.MISSING}"] = missing  # pyright: ignore[reportArgumentType]
        node_df, edge_df = geff_to_dataframes(store)
        # Number of nans should match number missing
        assert np.count_nonzero(edge_df["score"].isna()) == n_missing


class Test_geff_to_csv:
    def test_outpath_no_suffix(self, tmp_path):
        store, memory_geff = create_simple_3d_geff()
        out_path = tmp_path / "dataframe"
        geff_to_csv(store, out_path)

        node_path = str(out_path) + "-nodes.csv"
        edge_path = str(out_path) + "-edges.csv"

        # Check that files exist
        assert os.path.exists(node_path)
        assert os.path.exists(edge_path)

        # Check shape of dataframe, details tested in geff_to_dataframe
        node_df = pd.read_csv(node_path, index_col=0)
        assert len(node_df) == memory_geff["node_ids"].shape[0]
        assert len(node_df.columns) == 1 + len(memory_geff["node_props"].keys())

        edge_df = pd.read_csv(edge_path, index_col=0)
        assert len(edge_df) == memory_geff["edge_ids"].shape[0]
        assert len(edge_df.columns) == 2 + len(memory_geff["edge_props"].keys())

    def test_outpath_with_suffix(self, tmp_path):
        store, memory_geff = create_simple_3d_geff()
        out_path = tmp_path / "dataframe.csv"
        geff_to_csv(store, out_path)

        node_path = str(out_path.with_suffix("")) + "-nodes.csv"
        edge_path = str(out_path.with_suffix("")) + "-edges.csv"

        # Check that files exist
        assert os.path.exists(node_path)
        assert os.path.exists(edge_path)

    def test_no_nodes(self, tmp_path):
        store, memory_geff = create_simple_3d_geff(num_nodes=0)
        out_path = tmp_path / "dataframe"
        geff_to_csv(store, out_path)

        node_path = str(out_path) + "-nodes.csv"
        edge_path = str(out_path) + "-edges.csv"

        # Check that files exist
        assert os.path.exists(node_path)
        assert os.path.exists(edge_path)

        # Check that node file is empty
        node_df = pd.read_csv(node_path, index_col=0)
        assert len(node_df) == memory_geff["node_ids"].shape[0]

    def test_no_edges(self, tmp_path):
        store, memory_geff = create_simple_3d_geff(num_edges=0)
        out_path = tmp_path / "dataframe"
        geff_to_csv(store, out_path)

        node_path = str(out_path) + "-nodes.csv"
        edge_path = str(out_path) + "-edges.csv"

        # Check that files exist
        assert os.path.exists(node_path)
        assert os.path.exists(edge_path)

        # Check that node file is empty
        edge_df = pd.read_csv(edge_path, index_col=0)
        assert len(edge_df) == memory_geff["edge_ids"].shape[0]
