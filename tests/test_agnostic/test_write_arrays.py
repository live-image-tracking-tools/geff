from pathlib import Path
from typing import Literal

import numpy as np
import pytest
import zarr

from geff.metadata_schema import GeffMetadata
from geff.write_arrays import write_arrays


class TestWriteArrays:
    @pytest.mark.parametrize("zarr_format", [2, 3])
    def test_write_arrays_basic(self, tmp_path: Path, zarr_format: Literal[2, 3]) -> None:
        """Test basic functionality of write_arrays with minimal data."""
        # Create test data
        geff_path = tmp_path / "test.geff"
        node_ids = np.array([1, 2, 3], dtype=np.int32)
        edge_ids = np.array([[1, 2], [2, 3]], dtype=np.int32)
        metadata = GeffMetadata(geff_version="0.0.1", directed=True)

        # Call write_arrays
        write_arrays(
            geff_store=geff_path,
            node_ids=node_ids,
            node_props=None,
            edge_ids=edge_ids,
            edge_props=None,
            metadata=metadata,
            zarr_format=zarr_format,
        )

        # Verify the zarr group was created
        assert geff_path.exists()

        # Verify node and edge IDs were written correctly
        root = zarr.open_group(str(geff_path))
        assert "nodes/ids" in root
        assert "edges/ids" in root

        # Check the data matches
        np.testing.assert_array_equal(root["nodes/ids"][:], node_ids)
        np.testing.assert_array_equal(root["edges/ids"][:], edge_ids)

        # Check the data types match
        assert root["nodes/ids"].dtype == node_ids.dtype
        assert root["edges/ids"].dtype == edge_ids.dtype

        # Verify metadata was written
        assert "geff" in root.attrs
        assert root.attrs["geff"]["geff_version"] == "0.0.1"
        assert root.attrs["geff"]["directed"] is True

    # TODO: test properties helper. It's covered by networkx tests now, so I'm okay merging,
    # but we should do it when we have time.
