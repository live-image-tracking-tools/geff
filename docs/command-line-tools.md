# Command line tools 


::: mkdocs-typer
    :module: geff._cli
    :command: app
    :prog_name: geff
    :depth: 1

## Running command line tools

Without pip-installing `geff`, you can run the tools as 
```bash
uvx geff -h # by uv
# or 
pipx geff -h # by pipx
```

## Running command with a developmental build

You can run the command line tool for your local build as 

```bash
pip install -e .
geff -h
```