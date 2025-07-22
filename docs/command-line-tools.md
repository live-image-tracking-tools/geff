# Command line tools 

## Validate

Validate the schema for the GEFF file. 

```python
uvx geff validate /path/to/geff.geff
# Or maybe you need the following for Zarr 3
# uvx --with zarr==3.1.0 geff validate /path/to/geff.geff
```

## Show info

Show GEFF metadata as a JSON.

```python
uvx geff info /path/to/geff.geff
# Or maybe you need the following for Zarr 3
# uvx --with zarr==3.1.0 geff validate /path/to/geff.geff
```