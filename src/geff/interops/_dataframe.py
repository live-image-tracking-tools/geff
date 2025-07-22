try:
    import pandas as pd
except ImportError as e:
    raise ImportError("'pandas' is required to use the dataframe interoperability") from e

from zarr.storage import StoreLike

from geff.dict_representation import PropDictNpArray
from geff.geff_reader import read_to_dict


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

    if "missing" in prop_dict:
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
    geff_data = read_to_dict(store)

    nodes_df = pd.concat(
        [_expand_props(node_props, name) for name, node_props in geff_data["node_props"].items()],
        axis="columns",
    ).set_index(geff_data["nodes"])

    edges_df = pd.concat(
        [_expand_props(edge_props, name) for name, edge_props in geff_data["edge_props"].items()],
        axis="columns",
    ).set_index(geff_data["edges"])

    return nodes_df, edges_df
