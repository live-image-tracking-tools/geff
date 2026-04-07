try:
    import pandas as pd
except ImportError as e:
    raise ImportError("Please install with geff[pandas] to use this module.") from e

import warnings
from pathlib import Path
from typing import Literal

import numpy as np
from zarr.storage import StoreLike

from geff._typing import InMemoryGeff, PropDictNpArray
from geff.core_io._base_read import read_to_memory
from geff.core_io._base_write import write_arrays
from geff.core_io._utils import construct_props
from geff_spec.utils import (
    add_or_update_props_metadata,
    create_or_update_metadata,
    create_props_metadata,
)


def geff_to_dataframes(
    store: StoreLike,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Convert a GEFF store to a pandas DataFrame.

    Properties with more than 2 dimensions cannot be converted and will be skipped.
    Properties with two dimensions where the second dimension is > 1 will be unpacked
    into separate columns with the name "{prop_name}_{dim_index}"

    Args:
        store (StoreLike): The store to convert.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: The nodes and edges dataframes.
    """
    memory_geff = read_to_memory(store)
    dataframes = []

    # Construct dictionaries to convert to dataframes
    for data_type in ["node", "edge"]:
        df_dict = {}

        # Extract ids
        if data_type == "node":
            df_dict["id"] = memory_geff["node_ids"]
        else:
            df_dict["source"] = memory_geff["edge_ids"][:, 0]
            df_dict["target"] = memory_geff["edge_ids"][:, 1]

        # Conditional necessary to making typing happy :/
        if data_type == "node":
            props = memory_geff["node_props"]
        else:
            props = memory_geff["edge_props"]

        for name, prop in props.items():
            missing = prop["missing"]
            # Squeeze out any singleton dimensions
            values = prop["values"].squeeze()
            ndim = len(values.shape)
            if ndim == 2:
                # After squeezing out singleton dimensions, second dim must be > 1
                for i in range(values.shape[1]):
                    series = pd.Series(values[:, i])
                    if missing is not None and any(missing):
                        series.mask(missing, inplace=True)
                    df_dict[f"{name}_{i}"] = series

            elif ndim > 2:
                warnings.warn(
                    f"{data_type} {name} ({ndim}D) will not be exported to csv "
                    "with more than 2 dimensions",
                    stacklevel=2,
                )
                continue
            else:
                # Data is 1d
                series = pd.Series(values)
                if missing is not None and any(missing):
                    series.mask(missing, inplace=True)
                df_dict[name] = series

        dataframes.append(pd.DataFrame(df_dict))

    return tuple(dataframes)


def geff_to_csv(store: StoreLike, outpath: Path | str, overwrite: bool = False) -> None:
    """Convert a geff store to two csvs of nodes and edges

    Properties with more than 2 dimensions cannot be exported and will be skipped.
    Properties with two dimensions where the second dimension is > 1 will be unpacked
    into separate columns with the name "{prop_name}_{dim_index}"

    Args:
        store (StoreLike): Path to store or StoreLike object
        outpath (Path | str): Path to save output csvs. Any file extension will be
            stripped and replaced with "-nodes.csv" and "-edges.csv"
        overwrite (bool): If true, existing csvs will be overwritten
    """
    # Convert to path and remove any existing suffix
    outpath = Path(outpath).with_suffix("")
    # Add node/edge.csv to path
    node_path = f"{outpath}-nodes.csv"
    edge_path = f"{outpath}-edges.csv"

    # Convert and write to disk
    node_df, edge_df = geff_to_dataframes(store)
    mode = "w" if overwrite else "x"
    node_df.to_csv(node_path, mode=mode)
    edge_df.to_csv(edge_path, mode=mode)


def dataframes_to_memory_geff(
    node_df: pd.DataFrame,
    edge_df: pd.DataFrame,
    directed: bool = True,
    node_id_col: str = "id",
    edge_source_col: str = "source",
    edge_target_col: str = "target",
) -> InMemoryGeff:
    """Convert pandas DataFrames to an InMemoryGeff representation.

    Takes a node DataFrame and an edge DataFrame and converts them into the InMemoryGeff
    dict format. Missing values (NaN/None) are handled via boolean missing masks with
    correct dtypes preserved.

    Args:
        node_df (pd.DataFrame): DataFrame with node data. Must contain a node ID column
            and any number of property columns.
        edge_df (pd.DataFrame): DataFrame with edge data. Must contain source and target
            ID columns and any number of property columns.
        directed (bool): Whether the graph is directed. Defaults to True.
        node_id_col (str): Name of the node ID column in node_df. Defaults to "id".
        edge_source_col (str): Name of the source node column in edge_df. Defaults to "source".
        edge_target_col (str): Name of the target node column in edge_df. Defaults to "target".

    Raises:
        ValueError: If node_df is missing the node_id_col column, or edge_df is
            missing the edge_source_col or edge_target_col columns.

    Returns:
        InMemoryGeff: A dict with metadata, node_ids, edge_ids, node_props, and edge_props.
    """
    # Validate required columns
    if node_id_col not in node_df.columns:
        raise ValueError(
            f"node_df must contain a {node_id_col!r} column. Found columns: {list(node_df.columns)}"
        )
    missing_edge_cols = [
        col for col in (edge_source_col, edge_target_col) if col not in edge_df.columns
    ]
    if missing_edge_cols:
        raise ValueError(
            f"edge_df must contain {missing_edge_cols} column(s). "
            f"Found columns: {list(edge_df.columns)}"
        )

    # Extract node IDs
    if len(node_df) > 0:
        node_ids = np.asarray(node_df[node_id_col]).astype(np.uint64)
    else:
        node_ids = np.empty((0,), dtype=np.uint64)

    # Extract edge IDs
    if len(edge_df) > 0:
        edge_ids = np.column_stack(
            [
                np.asarray(edge_df[edge_source_col]),
                np.asarray(edge_df[edge_target_col]),
            ]
        ).astype(np.uint64)
    else:
        edge_ids = np.empty((0, 2), dtype=np.uint64)

    # Convert property columns to PropDictNpArray
    node_prop_cols = [c for c in node_df.columns if c != node_id_col]
    node_props = _df_columns_to_props(node_df, node_prop_cols)

    edge_prop_cols = [c for c in edge_df.columns if c not in (edge_source_col, edge_target_col)]
    edge_props = _df_columns_to_props(edge_df, edge_prop_cols)

    # Build metadata
    metadata = create_or_update_metadata(metadata=None, is_directed=directed)
    node_prop_meta = [
        create_props_metadata(identifier=name, prop_data=prop_data)
        for name, prop_data in node_props.items()
    ]
    edge_prop_meta = [
        create_props_metadata(identifier=name, prop_data=prop_data)
        for name, prop_data in edge_props.items()
    ]
    metadata = add_or_update_props_metadata(metadata, node_prop_meta, "node")
    metadata = add_or_update_props_metadata(metadata, edge_prop_meta, "edge")

    return {
        "metadata": metadata,
        "node_ids": node_ids,
        "edge_ids": edge_ids,
        "node_props": node_props,
        "edge_props": edge_props,
    }


def _df_columns_to_props(df: pd.DataFrame, columns: list[str]) -> dict[str, PropDictNpArray]:
    """Convert DataFrame columns to a dict of PropDictNpArray.

    Replaces NaN/None with None before passing to construct_props, which handles
    default value filling and missing mask creation.

    Args:
        df (pd.DataFrame): DataFrame containing the columns to convert.
        columns (list[str]): List of column names to convert.

    Returns:
        dict[str, PropDictNpArray]: A mapping of column names to PropDictNpArray dicts.
    """
    props: dict[str, PropDictNpArray] = {}
    for col in columns:
        values = [None if pd.isna(v) else v for v in df[col]]
        props[col] = construct_props(values)
    return props


def dataframes_to_geff(
    node_df: pd.DataFrame,
    edge_df: pd.DataFrame,
    store: StoreLike,
    directed: bool = True,
    node_id_col: str = "id",
    edge_source_col: str = "source",
    edge_target_col: str = "target",
    zarr_format: Literal[2, 3] = 2,
) -> None:
    """Convert node and edge pandas DataFrames to a geff store.

    The node DataFrame must contain a column with node IDs (default "id"). All other
    columns are stored as node properties. The edge DataFrame must contain columns for
    source and target node IDs (default "source" and "target"). All other columns
    are stored as edge properties. Missing values (NaN) are recorded
    in the GEFF missing mask. Columns starting with "Unnamed:" are ignored (e.g.
    pandas index columns written by ``df.to_csv()``).

    Args:
        node_df (pd.DataFrame): DataFrame with node data. Must contain a node ID column
            and any number of property columns.
        edge_df (pd.DataFrame): DataFrame with edge data. Must contain source and target
            ID columns and any number of property columns.
        store (StoreLike): The zarr store to write to.
        directed (bool): Whether the graph is directed. Defaults to True.
        node_id_col (str): Name of the node ID column in node_df. Defaults to "id".
        edge_source_col (str): Name of the source node column in edge_df. Defaults to "source".
        edge_target_col (str): Name of the target node column in edge_df. Defaults to "target".
        zarr_format (Literal[2, 3]): The zarr specification to use when writing. Defaults to 2.
    """
    in_memory_geff = dataframes_to_memory_geff(
        node_df,
        edge_df,
        directed=directed,
        node_id_col=node_id_col,
        edge_source_col=edge_source_col,
        edge_target_col=edge_target_col,
    )
    write_arrays(store, zarr_format=zarr_format, **in_memory_geff)


def csv_to_geff(
    node_csv: Path | str,
    edge_csv: Path | str,
    store: StoreLike,
    directed: bool = True,
    node_id_col: str = "id",
    edge_source_col: str = "source",
    edge_target_col: str = "target",
    zarr_format: Literal[2, 3] = 2,
) -> None:
    """Convert node and edge CSV files to a geff store.

    The CSVs are expected to have a header row.
    The node CSV must contain a column with node IDs (default "id"). All other
    columns are stored as node properties. The edge CSV must contain columns for
    source and target node IDs (default "source" and "target"). All other columns
    are stored as edge properties. Missing values (empty cells / NaN) are recorded
    in the GEFF missing mask. Columns starting with "Unnamed:" are ignored (e.g.
    pandas index columns written by ``df.to_csv()``).

    Args:
        node_csv (Path | str): Path to the node CSV file.
        edge_csv (Path | str): Path to the edge CSV file.
        store (StoreLike): The zarr store to write to.
        directed (bool): Whether the graph is directed. Defaults to True.
        node_id_col (str): Name of the node ID column in the node CSV. Defaults to "id".
        edge_source_col (str): Name of the source node column in the edge CSV.
            Defaults to "source".
        edge_target_col (str): Name of the target node column in the edge CSV.
            Defaults to "target".
        zarr_format (Literal[2, 3]): The zarr specification to use when writing. Defaults to 2.

    Raises:
        ValueError: If required columns are missing from the CSVs.
    """
    node_df = pd.read_csv(node_csv)
    edge_df = pd.read_csv(edge_csv)

    # Drop unnamed columns (e.g. pandas index columns written by df.to_csv())
    node_df = node_df.loc[:, ~node_df.columns.str.startswith("Unnamed:")]
    edge_df = edge_df.loc[:, ~edge_df.columns.str.startswith("Unnamed:")]

    dataframes_to_geff(
        node_df,
        edge_df,
        store,
        directed=directed,
        node_id_col=node_id_col,
        edge_source_col=edge_source_col,
        edge_target_col=edge_target_col,
        zarr_format=zarr_format,
    )
