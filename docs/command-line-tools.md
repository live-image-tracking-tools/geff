# Command line tools 

## Validate

Validate the schema for the GEFF file. 

```bash
uvx geff validate /path/to/geff.geff
```

## Show info

Show GEFF metadata as a JSON.

```bash
uvx geff info /path/to/geff.geff
```

# Running command with a developmental build

In a development environment, please run, for example, 

```bash
pixi run build
uvx --from dist/geff-0.3 ... .whl validate tracks.geff
```