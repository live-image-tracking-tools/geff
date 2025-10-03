# CONTRIBUTING

## Setup

For local development, clone the repo:

```sh
git clone https://github.com/live-image-tracking-tools/geff.git
cd geff
```

### Install with generic environment manager

```sh
# <create and activate virtual environment>
pip install -e packages/geff -e packages/geff-spec --group dev
```

### Install with uv

If you are using [uv](https://docs.astral.sh/uv/):

```sh
uv sync
```

> [!IMPORTANT]
> **All commands below assume an activate virtual environment, but you
> may also use `uv run <COMMAND>` to run them without activating an env.**

## Running Tasks

Many of the tasks listed below can be run quickly with the
[`just`](https://github.com/casey/just) task runner. [Install
just](https://just.systems/man/en/packages.html) (e.g. `brew install just` or
`winget install --id Casey.Just --exact`).  Since most of the tasks require uv,
you will also need to [install
uv](https://docs.astral.sh/uv/getting-started/installation/).

To list available tasks, run:

```sh
just --list
```

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

## Versioning

This repo contains two python libraries that are versioned independently.

### geff-spec
This library defines the specification. It has the pydantic models for the schema and the markdown of the written specification.

It is versioned: vA.B.C

change A = breaking spec change (e.g. field/type renaming/removal, change to on-disk requirements)
change B = non-breaking spec change (e.g. field addition)
change C = just a bump in the pydantic model or written specification (e.g. typos)

Geff spec is just A.B.
pydantic python geff-spec version is the full trio

### geff (reference implementation)
This library contains all the rest of the python code - validators, reference implementations, converters, cli tools. It depends on geff-spec.
The version is vX.Y.Z.A.B where A.B is the highest supported spec version.

Change X = major feature breaking change
Change Y = non-breaking feature release
Change Z = bug fix release

change A = (same as above)
change B = (same as above)

bumping A necessitates a bump to minimally Y…
would only bump X if is concomitant with a breaking geff-lib change
bumping B probably requires bump to Y to support the new schema

## Releases

The release process is slightly different for each package in the monorepo.

### geff

In order to deploy a new version, tag the commit with a version number and push
it to github. This will trigger a github action that will build and deploy to
PyPI. (see the "build-and-inspect-package" and "upload-geff-to-pypi" steps in
[workflows/ci.yaml](./.github/workflows/ci.yaml)). The version number is
determined automatically based on the tag (using `setuptools-scm`). This workflow
will only push `geff` not `geff-spec`. 

> [!TIP]
> If this `geff` release includes an update to `geff-spec` that will change the last two numbers of the version. Remember to change the upper pin on `geff-spec` in the `geff` dependencies.

```sh
git tag -a v1.0.0.1.0 -m v1.0.0.1.0
git push --follow-tags
```

### geff-spec

In order to deploy a new version, first update the version field in `packages/geff-spec/pyproject.toml`
and merge that change into main. Next tag the commit with that version number prefixed with "spec", e.g.
`spec-v0.1.0` and push it to github. This will trigger a github action that will build and deploy to
PyPI. (see the "build-and-inspect-package" and "upload-geff-spec-to-pypi" steps in
[workflows/ci.yaml](./.github/workflows/ci.yaml)).

```sh
git tag -a spec-v0.1.0 -m spec-v0.1.0
git push --follow-tags
```

## Building

To build all packages in the monorepo

```sh
uv build --all-packages
```

or to build a specific package, run:

```sh
uv build --package <package-name>
```

## Docs

Docs are written with [MkDocs](https://www.mkdocs.org).

`mkdocs` commands below must either be run in a virtual environment with the
`docs` group installed (`pip install -e . --group docs`)

or via uv:  

```sh
uv run --group docs mkdocs <command>
```

- `mkdocs serve` - Start the live-reloading docs server.
- `mkdocs build` - Build the documentation site.
- `mkdocs -h` - Print help message and exit.
