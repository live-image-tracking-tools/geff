try:
    import rustworkx
except ImportError as e:
    raise ImportError(
        "This module requires rustworkx to be installed. "
        "Please install it with `pip install 'geff[rx]'`."
    ) from e
