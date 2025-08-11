from __future__ import annotations

from typing import Final

NODES: Final = "nodes"
"""Path at which we expect to find the Nodes group in a GEFF group."""

EDGES: Final = "edges"
"""Path at which we expect to find the Edges group in a GEFF group."""

IDS: Final = "ids"
"""Path at which we expect to find the IDs array in a Nodes or Edges group."""

PROPS: Final = "props"
"""Path at which we expect to find the Props group in a Nodes or Edges group."""

VALUES: Final = "values"
"""Path at which we expect to find the Values array in a Nodes or Edges group."""

MISSING: Final = "missing"
"""Path at which we expect to find the Missing array in a Nodes or Edges group."""

NODE_IDS: Final = f"{NODES}/{IDS}"
"""Shortcut for the path to the node IDs in a GEFF."""
EDGE_IDS: Final = f"{EDGES}/{IDS}"
"""Shortcut for the path to the edge IDs in a GEFF."""
NODE_PROPS: Final = f"{NODES}/{PROPS}"
"""Shortcut for the path to the node properties group in a GEFF."""
EDGE_PROPS: Final = f"{EDGES}/{PROPS}"
"""Shortcut for the path to the edge properties group in a GEFF."""
