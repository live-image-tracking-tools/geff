try:
    import spatial_graph
except ImportError as e:
    raise ImportError(
        "This module requires spatial-graph to be installed. "
        "Please install it with `pip install 'geff[spatial-graph]'`."
    ) from e
