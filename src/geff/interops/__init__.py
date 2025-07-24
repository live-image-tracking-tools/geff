from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .ctc import ctc_tiffs_to_zarr, from_ctc_to_geff
    from .trackmate_xml import from_trackmate_xml_to_geff

__all__ = ["ctc_tiffs_to_zarr", "from_ctc_to_geff", "from_trackmate_xml_to_geff"]


def __getattr__(name: str) -> Any:
    if name == "ctc_tiffs_to_zarr":
        try:
            from geff.interops.ctc import ctc_tiffs_to_zarr

            return ctc_tiffs_to_zarr
        except ImportError as e:
            raise ImportError("install with geff[ctc] to use ctc_tiffs_to_zarr") from e
    if name == "from_ctc_to_geff":
        try:
            from geff.interops.ctc import from_ctc_to_geff

            return from_ctc_to_geff
        except ImportError as e:
            raise ImportError("install with geff[ctc] to use from_ctc_to_geff") from e
    if name == "from_trackmate_xml_to_geff":
        try:
            from geff.interops.trackmate_xml import from_trackmate_xml_to_geff

            return from_trackmate_xml_to_geff
        except ImportError as e:
            raise ImportError(
                "install with geff[trackmate_xml] to use from_trackmate_xml_to_geff"
            ) from e
