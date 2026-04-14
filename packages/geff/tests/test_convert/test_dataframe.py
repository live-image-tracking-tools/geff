import pytest
import zarr

try:
    import pandas as pd

    from geff.convert._dataframe import (
        _dataframes_to_memory_geff,
        csv_to_geff,
        geff_to_csv,
        geff_to_dataframes,
    )
except ImportError:
    pytest.skip("geff[pandas] not installed", allow_module_level=True)

import os

import numpy as np
import pytest

from geff import _path
from geff.core_io._base_read import read_to_memory
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
        store, _memory_geff = create_mock_geff(
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
        store, _memory_geff = create_mock_geff(
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
        store, _memory_geff = create_simple_3d_geff(num_nodes=0)
        node_df, edge_df = geff_to_dataframes(store)

        assert isinstance(node_df, pd.DataFrame)
        assert isinstance(edge_df, pd.DataFrame)
        assert len(node_df) == 0
        assert len(edge_df) == 0

    def test_no_edges(self):
        store, _memory_geff = create_simple_3d_geff(num_edges=0)
        _, edge_df = geff_to_dataframes(store)

        assert isinstance(edge_df, pd.DataFrame)
        assert len(edge_df) == 0

    def test_missing(self):
        num_edges = 10
        store, _memory_geff = create_simple_2d_geff(num_edges=num_edges)
        z = zarr.open(store)

        # Missing array exists but is all False, e.g. nothing missing
        missing = np.array([False] * num_edges)
        z[f"{_path.EDGE_PROPS}/score/{_path.MISSING}"] = missing  # pyright: ignore[reportArgumentType]
        _, edge_df = geff_to_dataframes(store)
        # No missing so shouldn't be any nans in values
        assert not any(edge_df["score"].isna())

        # Missing array with some values missing
        n_missing = 4
        missing = np.array([True] * n_missing + [False] * (num_edges - n_missing))
        z[f"{_path.EDGE_PROPS}/score/{_path.MISSING}"] = missing  # pyright: ignore[reportArgumentType]
        _, edge_df = geff_to_dataframes(store)
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
        store, _memory_geff = create_simple_3d_geff()
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

    def test_overwrite(self, tmp_path):
        store, _ = create_simple_3d_geff()
        out_path = tmp_path / "dataframe.csv"
        geff_to_csv(store, out_path)

        store_2d, _ = create_simple_2d_geff()

        # Fails if overwrite false
        with pytest.raises(FileExistsError, match="File exists:"):
            geff_to_csv(store_2d, out_path)

        geff_to_csv(store_2d, out_path, overwrite=True)
        df = pd.read_csv(str(out_path.with_suffix("")) + "-nodes.csv")
        assert "z" not in df.columns


@pytest.fixture()
def sample_dataframes():
    """Node and edge DataFrames covering multiple dtypes and missing values."""
    node_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "x": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "label": ["a", "b", "c", "d", "e", "f"],
            "flag": pd.array([True, False, pd.NA, True, False, True], dtype=pd.BooleanDtype()),
            "score": [10.0, np.nan, 30.0, 40.0, 50.0, 60.0],
        }
    )
    edge_df = pd.DataFrame(
        {
            "source": [0, 1, 2, 3],
            "target": [1, 2, 3, 4],
            "weight": [0.1, 0.2, 0.3, 0.4],
        }
    )
    return node_df, edge_df


@pytest.fixture()
def expected_memory_geff():
    """Manually constructed expected InMemoryGeff for the sample DataFrames."""
    return {
        "node_ids": np.array([0, 1, 2, 3, 4, 5], dtype=np.uint8),
        "edge_ids": np.array([[0, 1], [1, 2], [2, 3], [3, 4]], dtype=np.uint8),
        "node_props": {
            "x": {
                "values": np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0]),
                "missing": None,
            },
            "label": {
                "values": np.array(["a", "b", "c", "d", "e", "f"]),
                "missing": None,
            },
            "flag": {
                "values": np.array([True, False, False, True, False, True]),
                "missing": np.array([False, False, True, False, False, False]),
            },
            "score": {
                "values": np.array([10.0, 0.0, 30.0, 40.0, 50.0, 60.0]),
                "missing": np.array([False, True, False, False, False, False]),
            },
        },
        "edge_props": {
            "weight": {
                "values": np.array([0.1, 0.2, 0.3, 0.4]),
                "missing": None,
            },
        },
    }


class Test_dataframes_to_geff:
    def test_missing_node_id_column(self):
        """Should raise ValueError when node_df is missing the ID column."""
        node_df = pd.DataFrame({"x": [1.0, 2.0]})
        edge_df = pd.DataFrame({"source": pd.Series(dtype=int), "target": pd.Series(dtype=int)})

        with pytest.raises(ValueError, match="node_df must contain a 'id' column"):
            _dataframes_to_memory_geff(node_df, edge_df)

    def test_missing_edge_columns(self):
        """Should raise ValueError when edge_df is missing source/target columns."""
        node_df = pd.DataFrame({"id": [0, 1]})
        edge_df = pd.DataFrame({"src": [0], "tgt": [1]})

        with pytest.raises(ValueError, match="edge_df must contain"):
            _dataframes_to_memory_geff(node_df, edge_df)

    def test_empty_dataframes(self):
        """Empty DataFrames should produce valid InMemoryGeff with empty arrays."""
        node_df = pd.DataFrame({"id": pd.Series(dtype=int)})
        edge_df = pd.DataFrame({"source": pd.Series(dtype=int), "target": pd.Series(dtype=int)})

        result = _dataframes_to_memory_geff(node_df, edge_df)

        assert result["node_ids"].shape == (0,)
        assert result["edge_ids"].shape == (0, 2)
        assert result["node_props"] == {}
        assert result["edge_props"] == {}

    def test_all_edge_cases(self, sample_dataframes, expected_memory_geff):
        """Manually constructed input DataFrames produce expected InMemoryGeff."""
        node_df, edge_df = sample_dataframes
        result = _dataframes_to_memory_geff(node_df, edge_df, directed=True)
        expected = expected_memory_geff

        assert result["metadata"].directed is True

        np.testing.assert_array_equal(result["node_ids"], expected["node_ids"])
        assert result["node_ids"].dtype == expected["node_ids"].dtype

        np.testing.assert_array_equal(result["edge_ids"], expected["edge_ids"])
        assert result["edge_ids"].dtype == expected["edge_ids"].dtype

        assert set(result["node_props"].keys()) == set(expected["node_props"].keys())
        for name in expected["node_props"]:
            np.testing.assert_array_equal(
                result["node_props"][name]["values"],
                expected["node_props"][name]["values"],
            )
            assert (
                result["node_props"][name]["values"].dtype
                == expected["node_props"][name]["values"].dtype
            )
            if expected["node_props"][name]["missing"] is None:
                assert result["node_props"][name]["missing"] is None
            else:
                np.testing.assert_array_equal(
                    result["node_props"][name]["missing"],
                    expected["node_props"][name]["missing"],
                )

        assert set(result["edge_props"].keys()) == set(expected["edge_props"].keys())
        for name in expected["edge_props"]:
            np.testing.assert_array_equal(
                result["edge_props"][name]["values"],
                expected["edge_props"][name]["values"],
            )
            assert (
                result["edge_props"][name]["values"].dtype
                == expected["edge_props"][name]["values"].dtype
            )
            if expected["edge_props"][name]["missing"] is None:
                assert result["edge_props"][name]["missing"] is None
            else:
                np.testing.assert_array_equal(
                    result["edge_props"][name]["missing"],
                    expected["edge_props"][name]["missing"],
                )


class Test_csv_to_geff:
    def test_end_to_end(self, tmp_path, sample_dataframes, expected_memory_geff):
        """CSV files with an Unnamed: column should produce correct geff on disk."""
        node_df, edge_df = sample_dataframes

        # Write CSVs with a pandas-style index column (Unnamed: 0)
        node_df.to_csv(tmp_path / "nodes.csv")
        edge_df.to_csv(tmp_path / "edges.csv")

        store_path = str(tmp_path / "output.zarr")
        csv_to_geff(tmp_path / "nodes.csv", tmp_path / "edges.csv", store_path, directed=True)

        result = read_to_memory(store_path)
        expected = expected_memory_geff

        np.testing.assert_array_equal(result["node_ids"], expected["node_ids"])
        np.testing.assert_array_equal(result["edge_ids"], expected["edge_ids"])

        for name in expected["node_props"]:
            np.testing.assert_array_equal(
                result["node_props"][name]["values"],
                expected["node_props"][name]["values"],
            )
            if expected["node_props"][name]["missing"] is None:
                assert result["node_props"][name]["missing"] is None
            else:
                np.testing.assert_array_equal(
                    result["node_props"][name]["missing"],
                    expected["node_props"][name]["missing"],
                )

        for name in expected["edge_props"]:
            np.testing.assert_array_equal(
                result["edge_props"][name]["values"],
                expected["edge_props"][name]["values"],
            )
            if expected["edge_props"][name]["missing"] is None:
                assert result["edge_props"][name]["missing"] is None
            else:
                np.testing.assert_array_equal(
                    result["edge_props"][name]["missing"],
                    expected["edge_props"][name]["missing"],
                )

        # Unnamed: column must have been filtered out
        assert all(not k.startswith("Unnamed:") for k in result["node_props"])
        assert all(not k.startswith("Unnamed:") for k in result["edge_props"])
