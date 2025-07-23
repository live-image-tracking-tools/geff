# Command line tools 

## Validate

Validate the schema for the GEFF file. 

```bash                         
pip install geff
geff validate /path/to/geff.geff
```

## Show info

Show GEFF metadata as a JSON.

```bash
pip install geff
geff info /path/to/geff.geff
```

# Running command line tools asss     

Without pip-installing `geff`, you can run the tools as 
```bash
uvx geff -h # by uv
# or 
pipx geff -h # by pipx
```

# Running command with a developmental build

You can run the command line tool for your local build as 

```bash
pip install -e .
geff -h
```