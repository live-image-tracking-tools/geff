from typing import TYPE_CHECKING, Any

from geff.convert._trackmate_xml import from_trackmate_xml_to_geff

if TYPE_CHECKING:
    from ._ctc import ctc_tiffs_to_zarr, from_ctc_to_geff
    from ._dataframe import (
        csv_to_geff,
        dataframes_to_geff,
        dataframes_to_memory_geff,
        geff_to_csv,
        geff_to_dataframes,
    )

__all__ = [
    "csv_to_geff",
    "ctc_tiffs_to_zarr",
    "dataframes_to_geff",
    "dataframes_to_memory_geff",
    "from_ctc_to_geff",
    "from_trackmate_xml_to_geff",
    "geff_to_csv",
    "geff_to_dataframes",
]


def __getattr__(name: str) -> Any:
    if name == "ctc_tiffs_to_zarr":
        from geff.convert._ctc import ctc_tiffs_to_zarr

        return ctc_tiffs_to_zarr
    if name == "from_ctc_to_geff":
        from geff.convert._ctc import from_ctc_to_geff

        return from_ctc_to_geff
    if name == "csv_to_geff":
        from geff.convert._dataframe import csv_to_geff

        return csv_to_geff
    if name == "geff_to_csv":
        from geff.convert._dataframe import geff_to_csv

        return geff_to_csv
    if name == "dataframes_to_geff":
        from geff.convert._dataframe import dataframes_to_geff

        return dataframes_to_geff
    if name == "dataframes_to_memory_geff":
        from geff.convert._dataframe import dataframes_to_memory_geff

        return dataframes_to_memory_geff
    if name == "geff_to_dataframes":
        from geff.convert._dataframe import geff_to_dataframes

        return geff_to_dataframes
