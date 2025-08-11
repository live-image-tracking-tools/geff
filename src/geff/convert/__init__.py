from typing import TYPE_CHECKING, Any

from geff.convert.trackmate_xml import from_trackmate_xml_to_geff

if TYPE_CHECKING:
    from .ctc import ctc_tiffs_to_zarr, from_ctc_to_geff

__all__ = ["ctc_tiffs_to_zarr", "from_ctc_to_geff", "from_trackmate_xml_to_geff"]


def __getattr__(name: str) -> Any:
    if name == "ctc_tiffs_to_zarr":
        from geff.convert.ctc import ctc_tiffs_to_zarr

        return ctc_tiffs_to_zarr
    if name == "from_ctc_to_geff":
        from geff.convert.ctc import from_ctc_to_geff

        return from_ctc_to_geff
