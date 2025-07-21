import itertools
from pathlib import Path

import numpy as np
import pytest
import zarr
from typer.testing import CliRunner

from geff.interops.ctc import app, from_ctc_to_geff
from geff.networkx.io import read_nx

tifffile = pytest.importorskip("tifffile")


def create_mock_data(
    tmp_path: Path,
    is_gt: bool,
) -> Path:
    """
    mock graph is:

    t=0      1       7
             |       |
    t=1      1       |
            / \\     |
    t=2    2   5     9
    """
    labels = np.zeros((3, 10, 10), dtype=np.uint16)

    labels[0, 3, 3] = 1
    labels[0, 8, 8] = 7

    labels[1, 3, 4] = 1

    labels[2, 2, 3] = 5
    labels[2, 4, 5] = 2
    labels[2, 8, 9] = 9

    fmt = "man_track{:03d}.tif" if is_gt else "mask{:03d}.tif"

    for t in range(labels.shape[0]):
        tifffile.imwrite(
            tmp_path / fmt.format(t),
            labels[t],
            compression="LZW",
        )

    tracks_file = tmp_path / ("man_track.txt" if is_gt else "res_track.txt")
    # track_id, start, end, parent_id
    tracks_table = [[1, 0, 1, 0], [2, 2, 2, 1], [5, 2, 2, 1], [7, 0, 0, 0], [9, 2, 2, 7]]

    np.savetxt(
        tracks_file,
        tracks_table,
        fmt="%d",
    )

    return tmp_path


@pytest.mark.parametrize(
    "cli,is_gt,tczyx",
    list(itertools.product([False, True], [True, False], [True, False])),
)
def test_ctc_to_geff(
    tmp_path: Path,
    cli: bool,
    is_gt: bool,
    tczyx: bool,
) -> None:
    ctc_path = create_mock_data(tmp_path, is_gt)
    geff_path = ctc_path / "little.geff"
    segm_path = ctc_path / "segm.zarr"

    if cli:
        cmd_args = [str(ctc_path), str(geff_path), "--segm-path", str(segm_path)]
        if tczyx:
            cmd_args.append("--tczyx")
        result = CliRunner().invoke(app, cmd_args)
        assert result.exit_code == 0, (
            f"{cmd_args} failed with exit code {result.exit_code} and "
            f"message:\n{result.stdout}\n{result.stderr}"
        )
    else:
        from_ctc_to_geff(
            ctc_path=ctc_path,
            geff_path=geff_path,
            segmentation_store=segm_path,
            tczyx=True,
        )

    assert geff_path.exists()

    graph, _ = read_nx(geff_path)

    expected_nodes = {0, 1, 2, 3, 4, 5}
    expected_edges = {(0, 2), (2, 3), (2, 4), (1, 5)}

    assert set(graph.nodes()) == expected_nodes
    assert set(graph.edges()) == expected_edges

    for _, data in graph.nodes(data=True):
        for key in ["tracklet_id", "t", "y", "x"]:
            assert key in data

    expected_segm = np.stack([tifffile.imread(p) for p in sorted(ctc_path.glob("*.tif"))])

    segm = zarr.open(segm_path, mode="r")[...]

    assert segm.shape[0] == expected_segm.shape[0]

    if tczyx:
        assert segm.ndim == 5

    for t in range(expected_segm.shape[0]):
        np.testing.assert_array_equal(
            np.squeeze(segm[t]),
            expected_segm[t],
            err_msg=f"t={t}",
        )
