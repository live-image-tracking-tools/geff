import shutil
from pathlib import Path

import numpy as np
import tifffile
import typer
import zarr
from skimage.measure import regionprops
from zarr.storage import StoreLike

import geff
from geff.metadata_schema import Axis, GeffMetadata
from geff.write_arrays import write_arrays


def from_ctc_to_geff(
    ctc_path: Path,
    geff_path: Path,
    segmentation_store: StoreLike | None = None,
    tczyx: bool = False,
    overwrite: bool = False,
) -> None:
    """
    Convert a CTC file to a GEFF file.

    Args:
        ctc_path: The path to the CTC file.
        geff_path: The path to the GEFF file.
        segmentation_store: The path or store to save the segmentation to.
                            If not provided, it won't be exported.
        tczyx: Expand data to make it (T, C, Z, Y, X) otherwise it's (T,) + Frame shape.
        overwrite: Whether to overwrite the GEFF file if it already exists.
    """
    ctc_path = Path(ctc_path)
    geff_path = Path(geff_path)

    if not ctc_path.exists():
        raise FileNotFoundError(f"CTC file {ctc_path} does not exist")

    tracks_file_found = False

    for tracks_file in ["man_track.txt", "res_track.txt"]:
        tracks_file_path = ctc_path / tracks_file
        if tracks_file_path.exists():
            tracks_file_found = True
            break

    if not tracks_file_found:
        raise FileNotFoundError(
            f"Tracks file {ctc_path}/man_track.txt or {ctc_path}/res_track.txt does not exist"
        )

    if geff_path.exists() and not overwrite:
        raise FileExistsError(f"GEFF file {geff_path} already exists")

    if geff_path.exists() and overwrite:
        shutil.rmtree(geff_path)

    tracks: dict[int, list[int]] = {}

    edges = []
    node_props: dict[str, list[int | float]] = {
        "id": [],
        "tracklet_id": [],
        "t": [],
        "x": [],
        "y": [],
    }

    segm_array = None
    node_id = 0

    sorted_files = sorted(ctc_path.glob("*.tif"))
    n_1_padding: tuple[int, ...] = ()
    expand_dims: tuple[None, ...] | slice = slice(None)

    for t, filepath in enumerate(sorted_files):
        frame = tifffile.imread(filepath)

        if segmentation_store is not None and segm_array is None:
            if frame.ndim == 3:
                node_props["z"] = []

            # created in first iteration
            if tczyx:
                n_1_padding = (1,) * (5 - frame.ndim - 1)  # forcing data to be (T, C, Z, Y, X)
                expand_dims = (np.newaxis,) * len(n_1_padding)

            segm_array = zarr.create_array(
                segmentation_store,
                shape=(len(sorted_files), *n_1_padding, *frame.shape),
                chunks=(1, *n_1_padding, *frame.shape),
                dtype=frame.dtype,
                overwrite=overwrite,
            )

        if segm_array is not None:
            segm_array[t] = frame[expand_dims]

        for obj in regionprops(frame):
            tracklet_id = obj.label
            node_props["id"].append(node_id)
            node_props["tracklet_id"].append(tracklet_id)
            node_props["t"].append(t)
            # using y,x for 2d and z,y,x for 3d
            for c, v in zip(("x", "y", "z"), obj.centroid[::-1], strict=False):
                node_props[c].append(v)

            if tracklet_id not in tracks:
                tracks[tracklet_id] = []

            tracks[tracklet_id].append(node_id)
            node_id += 1

    if len(node_props["id"]) == 0:
        raise ValueError(f"No nodes found in the CTC directory {ctc_path}")

    for node_ids in tracks.values():
        # connect simple-paths of each track
        for i in range(len(node_ids) - 1):
            # forward in time (parent -> child)
            edges.append((node_ids[i], node_ids[i + 1]))

    tracks_table = np.loadtxt(tracks_file_path, dtype=int)

    # removing orphan tracklets
    tracks_table = tracks_table[tracks_table[:, -1] > 0]

    for row in tracks_table:
        child_track_id = row[0]
        parent_track_id = row[-1]
        child_node_id = tracks[child_track_id][0]
        parent_node_id = tracks[parent_track_id][-1]
        # forward in time (parent -> child)
        edges.append((parent_node_id, child_node_id))

    axis_names = [
        Axis(name="t", type="time"),
        Axis(name="y", type="space"),
        Axis(name="x", type="space"),
    ]
    if "z" in node_props:
        axis_names.insert(1, Axis(name="z", type="space"))

    node_ids = np.asarray(node_props.pop("id"), dtype=int)

    write_arrays(
        geff_path=geff_path,
        node_ids=node_ids,
        node_props={name: (np.asarray(values), None) for name, values in node_props.items()},
        edge_ids=np.asarray(edges, dtype=node_ids.dtype),
        edge_props={},
        metadata=GeffMetadata(
            geff_version=geff.__version__,
            axes=axis_names,
            directed=True,
        ),
    )


def from_ctc_to_geff_cli(
    ctc_path: Path,
    geff_path: Path,
    segm_path: Path | None = None,
    tczyx: bool = False,
    overwrite: bool = False,
) -> None:
    """
    Convert a CTC file to a GEFF file.

    Args:
        ctc_path: The path to the CTC file.
        geff_path: The path to the GEFF file.
        segm_path: The path to export the segmentation file, if not provided, it won't be exported.
        tczyx: Expand data to make it (T, C, Z, Y, X) otherwise it's (T,) + Frame shape.
        overwrite: Whether to overwrite the GEFF file if it already exists.
    """
    from_ctc_to_geff(
        ctc_path=ctc_path,
        geff_path=geff_path,
        segmentation_store=segm_path,
        tczyx=tczyx,
        overwrite=overwrite,
    )


app = typer.Typer()
app.command()(from_ctc_to_geff_cli)

if __name__ == "__main__":
    app()
