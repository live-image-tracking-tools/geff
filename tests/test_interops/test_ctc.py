from pathlib import Path

import numpy as np
import pytest

from geff.interops.ctc import from_ctc_to_geff
from geff.networkx.io import read_nx

tifffile = pytest.importorskip("tifffile")


@pytest.fixture
def mock_ctc_data(
    tmp_path: Path,
    request: pytest.FixtureRequest,
) -> Path:
    """
    mock graph is:

    t=0      1       7
             |       |
    t=1      1       |
            / \\     |
    t=2    2   5     9
    """
    is_gt = request.param

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


@pytest.mark.parametrize("mock_ctc_data", [True, False], indirect=True)
def test_ctc_to_geff(mock_ctc_data: Path) -> None:
    geff_path = mock_ctc_data / "little.geff"
    from_ctc_to_geff(
        ctc_path=mock_ctc_data,
        geff_path=geff_path,
    )

    assert geff_path.exists()

    graph = read_nx(geff_path)

    # expected_nodes = {
    #     "1_0",
    #     "1_1",
    #     "2_2",
    #     "5_2",
    #     "7_0",
    #     "9_2",
    # }

    # expected_edges = {
    #     ("1_0", "1_1"),
    #     ("1_1", "2_2"),
    #     ("2_2", "5_2"),
    #     ("7_0", "9_2"),
    # }

    expected_nodes = {0, 1, 2, 3, 4, 5}
    expected_edges = {(0, 2), (2, 3), (2, 4), (1, 5)}

    assert set(graph.nodes()) == expected_nodes
    assert set(graph.edges()) == expected_edges

    for _, data in graph.nodes(data=True):
        for key in ["track_id", "t", "y", "x"]:
            assert key in data
