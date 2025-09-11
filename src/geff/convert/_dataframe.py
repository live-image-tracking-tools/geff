try:
    import pandas as pd
except ImportError as e:
    raise ImportError("Please install with geff[pandas] to use this module.") from e

import warnings
from pathlib import Path

from zarr.storage import StoreLike

from geff.core_io._base_read import read_to_memory


def geff_to_dataframes(
    store: StoreLike,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Convert a GEFF store to a pandas DataFrame.

    Properties with more than 2 dimensions cannot be converted and will be skipped
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


def geff_to_csv(store: StoreLike, outpath: Path | str) -> None:
    """Convert a geff store to two csvs of nodes and edges

    Properties with more than 2 dimensions cannot be exported and will be skipped
    Properties with two dimensions where the second dimension is > 1 will be unpacked
    into separate columns with the name "{prop_name}_{dim_index}"

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
