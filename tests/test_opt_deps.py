import re
import sys
from unittest.mock import patch

import pytest


def test_without_spatial_graph():
    with patch.dict(sys.modules, {"spatial_graph": None}):
        with pytest.raises(
            ImportError, match=re.escape("install with geff[spatial_graph] to use read_sg")
        ):
            pass

        with pytest.raises(
            ImportError, match=re.escape("install with geff[spatial_graph] to use write_sg")
        ):
            pass


def test_without_rustworkx():
    with patch.dict(sys.modules, {"rustworkx": None}):
        with pytest.raises(ImportError, match=re.escape("install with geff[rx] to use read_rx")):
            pass
        with pytest.raises(ImportError, match=re.escape("install with geff[rx] to use write_rx")):
            pass
