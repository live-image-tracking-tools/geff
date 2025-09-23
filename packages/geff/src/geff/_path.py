from __future__ import annotations

from typing import Final

NODES: Final = "nodes"
"""Path at which we expect to find the nodes group in a GEFF group."""

EDGES: Final = "edges"
"""Path at which we expect to find the edges group in a GEFF group."""

IDS: Final = "ids"
"""Path at which we expect to find the IDs array in a nodes or edges group."""

PROPS: Final = "props"
"""Path at which we expect to find the props group in a nodes or edges group."""

VALUES: Final = "values"
"""Path at which we expect to find the values array in a props group."""

MISSING: Final = "missing"
"""Path at which we expect to find the missing array in a props group."""

DATA: Final = "data"
"""Path at which we expect to find the data array in a var length props group."""

NODE_IDS: Final = f"{NODES}/{IDS}"
"""Shortcut for the path to the node IDs in a GEFF."""
EDGE_IDS: Final = f"{EDGES}/{IDS}"
"""Shortcut for the path to the edge IDs in a GEFF."""
NODE_PROPS: Final = f"{NODES}/{PROPS}"
"""Shortcut for the path to the node properties group in a GEFF."""
EDGE_PROPS: Final = f"{EDGES}/{PROPS}"
"""Shortcut for the path to the edge properties group in a GEFF."""
