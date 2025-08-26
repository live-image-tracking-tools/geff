try:
    import pandas as pd
except ImportError as e:
    raise ImportError("'pandas' is required to use the dataframe interoperability") from e

from pathlib import Path

from zarr.storage import StoreLike

from geff._typing import PropDictNpArray
from geff.core_io._base_read import read_to_memory


def _expand_props(
    prop_dict: PropDictNpArray,
    name: str,
) -> pd.DataFrame:
    """
    Expand a property dictionary to a pandas DataFrame.
    The expanded DataFrame columns are named as:
    name_0_0, name_0_1, name_1_0, name_1_1
    for a (N, 2, 2) array.

    Args:
        prop_dict (PropDictNpArray): The property dictionary to expand.
        name (str): The name of the property.

    Returns:
        pd.DataFrame: The expanded property dictionary.
    """

    df = pd.DataFrame(prop_dict["values"])

    if prop_dict["missing"] is not None:
        df.mask(prop_dict["missing"], inplace=True)

    # add dimensions as the format of the columns
    # name_0_0, name_0_1, name_1_0, name_1_1, ...
    columns = [name]
    remaining_dims = df.shape[1:]
    while remaining_dims:
        new_columns = []
        for c in columns:
            for i in range(remaining_dims[0]):
                new_columns.append(f"{c}_{i}")
        columns = new_columns

    df.columns = columns

    return df


def geff_to_dataframes(
    store: StoreLike,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Convert a GEFF store to a pandas DataFrame.

    Args:
        store (StoreLike): The store to convert.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: The nodes and edges dataframes.
    """
    memory_geff = read_to_memory(store)

    nodes_df = pd.concat(
        [_expand_props(node_props, name) for name, node_props in memory_geff["node_props"].items()],
        axis="columns",
    ).set_index(memory_geff["node_ids"])

    edges_df = pd.concat(
        [_expand_props(edge_props, name) for name, edge_props in memory_geff["edge_props"].items()],
        axis="columns",
    ).set_index(memory_geff["edge_ids"])

    return nodes_df, edges_df


def geff_to_csv(store: StoreLike, outpath: Path | str) -> None:
    """Convert a geff store to two csvs of nodes and edges

    Args:
        store (StoreLike): Path to store or StoreLike object
        outpath (Path | str): Path to save output csvs. Any file extension will be
            stripped and replaced with "-nodes.csv" and "-edges.csv"
    """
    # Convert to path and remove any existing suffix
    outpath = Path(outpath).with_suffix("")
    # Add node/edge.csv to path
    node_path = f"{outpath}-nodes.csv"
    edge_path = f"{outpath}-edges.csv"

    # Convert and write to disk
    node_df, edge_df = geff_to_dataframes(store)
    node_df.to_csv(node_path)
    edge_df.to_csv(edge_path)
