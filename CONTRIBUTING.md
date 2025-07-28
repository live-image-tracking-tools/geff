# CONTRIBUTING

## Setup

For local development, clone the repo:

```sh
git clone https://github.com/funkelab/geff.git
cd geff
```

### Install with generic environment manager

```sh
# <create and activate virtual environment>
pip install -e . --group dev
```

### Install with pixi

If you are using [pixi](https://pixi.sh/):

```sh
pixi install
```

### Install with uv

If you are using [uv](https://docs.astral.sh/uv/):

```sh
uv sync
```

> [!IMPORTANT]
> **All commands below assume an activate virtual environment, but you
> may also use `pixi run <COMMAND>` or `uv run <COMMAND>` to run them.**

## Testing

To run tests

```sh
pytest
```

> [!TIP]
> `uv` is a very powerful dev tool for running tests against different
> python versions and dependency pins.  Useful flags to `uv run`:
>
> - `uv run --resolution lowest-direct`: Uses the *minimum* declared declared
>   versions in `pyproject.toml`, to ensure that you've accurately pinned deps.
> - `uv run -p 3.X`: Test against Python version `3.X`
>
> For example, to run tests on python 3.10, using minimum stated deps:
>
> ```sh
> uv run -p 3.10 --resolution lowest-direct pytest
> ```
>
> and... if you wanted to *further* ensure that no `dev` dependencies are "accidentally"
> causing your tests to pass by being included, the bare minimum env would be:
>
> ```sh
> uv run -p 3.10 --resolution lowest-direct --no-dev --group test pytest
> # where '--group test' could also be '--group test-third-party'
> ```

## Style

We utilize `pre-commit` with ruff for linting and formatting. If you would like to run `pre-commit` locally:

```sh
pre-commit run -a
```

To always run `pre-commit` before committing, you can install the pre-commit hooks by running:

```sh
pre-commit install
```

On github pull requests, [pre-commit.ci](https://pre-commit.ci/), will always run and commit changes on any open PRs.

## Releases

In order to deploy a new version, tag the commit with a version number and push
it to github. This will trigger a github action that will build and deploy to
PyPI. (see the "build-and-inspect-package" and "upload-to-pypi" steps in
[workflows/ci.yaml](./.github/workflows/ci.yaml)). The version number is
determined automatically based on the tag (using `setuptools-scm`)

```sh
git tag -a v0.1.0 -m v0.1.0
git push --follow-tags
```

## Docs

Docs are written with [MkDocs](https://www.mkdocs.org).

`mkdocs` commands below must either be run in a virtual environment with the
`docs` group installed (`pip install -e . --group docs`)

or via uv:  

```sh
uv run --group docs mkdocs <command>
```

or via pixi:  

```sh
pixi run -e docs mkdocs <command>
```

- `mkdocs serve` - Start the live-reloading docs server.
- `mkdocs build` - Build the documentation site.
- `mkdocs -h` - Print help message and exit.
