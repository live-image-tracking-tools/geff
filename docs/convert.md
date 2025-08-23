# Conversion to GEFF

If you already have tracking data stored in another format, we have some functions for converting data to GEFF.

## Cell Tracking Challenge (CTC)

To use the `geff` cli to convert CTC data to GEFF, see the docs for [`geff convert-ctc`][convert-ctc].

To use the `geff` python API, see the docs for [`ctc_tiffs_to_zarr`][geff.convert.ctc_tiffs_to_zarr] and [`from_ctc_to_geff`][geff.convert.from_ctc_to_geff].

## Trackmate XML

!!! note

    TODO add description of what is currently missing for lossless conversion from trackmate to geff

To convert a Trackmat XML file to GEFF using the `geff` cli, see the docs for [`geff convert-trackmate-xml`][convert-trackmate-xml].

To use the `geff` python API, see the docs for [`from_trackmate_xml_to_geff`][geff.convert.from_trackmate_xml_to_geff].

## AceTree

An example of how to convert AceTree data to a GEFF is available [here](https://github.com/zhirongbaolab/AceTreePythonReader/blob/main/testAceTreeReaderGeffWrite.py). 