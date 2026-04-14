# Conversion to GEFF

If you already have tracking data stored in another format, we have some functions for converting data to GEFF.

## Cell Tracking Challenge (CTC)

To use the `geff` cli to convert CTC data to GEFF, see the docs for [`geff convert-ctc`][convert-ctc].

To use the `geff` python API, see the docs for [`ctc_tiffs_to_zarr`][geff.convert.ctc_tiffs_to_zarr] and [`from_ctc_to_geff`][geff.convert.from_ctc_to_geff].

## Trackmate XML

!!! note
    Conversion from TrackMate XML to GEFF is currently NOT lossless, but we are working on it.      
    The output GEFF is missing:

    * for each spot, the coordinates of its ROI (segmentation)
    * for each track, the value of its features (e.g., `TRACK_DISPLACEMENT`, `TRACK_MEAN_SPEED`)

To convert a Trackmat XML file to GEFF using the `geff` cli, see the docs for [`geff convert-trackmate-xml`][convert-trackmate-xml].

To use the `geff` python API, see the docs for [`from_trackmate_xml_to_geff`][geff.convert.from_trackmate_xml_to_geff].

## DataFrames / CSV

To convert pandas DataFrames to a GEFF store, use [`dataframes_to_geff`][geff.convert.dataframes_to_geff]. The node DataFrame must have an ID column (default `"id"`) and the edge DataFrame must have source and target columns (default `"source"` and `"target"`). All other columns become node or edge properties.

To convert CSV files directly, use [`csv_to_geff`][geff.convert.csv_to_geff]. The CSVs are expected to have a header row and a pandas-style index column.

To convert in the other direction, use [`geff_to_dataframes`][geff.convert.geff_to_dataframes] or [`geff_to_csv`][geff.convert.geff_to_csv].

## AceTree

An example of how to convert AceTree data to a GEFF is available [here](https://github.com/zhirongbaolab/AceTreePythonReader/blob/main/testAceTreeReaderGeffWrite.py).