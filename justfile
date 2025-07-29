# run tests with pytest
test:
    uv run pytest

# run tests with pytest and show coverage
test-cov:
    uv run pytest --cov --cov-report=term-missing

# run benchmarks
benchmark:
    uv run --group bench pytest tests/bench.py

# build wheel and sdist
build:
    uv build

# build docs and start a local server to preview them
docs-serve:
    uv run --group docs --isolated mkdocs serve

# build docs in strict mode
docs-build:
    uv run --group docs --isolated mkdocs build --strict

# tag and release <version>
release version:
    git tag -a {{version}} -m {{version}}
    git push upstream --follow-tags
