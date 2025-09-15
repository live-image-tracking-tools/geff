# run tests with pytest
test:
    uv run pytest

# run tests with pytest and show coverage
test-cov:
    uv run pytest --cov --cov-report=term-missing

# run benchmarks
benchmark:
    uv run --group bench pytest tests/test_bench.py

# build wheel and sdist
build:
    uv build

# build docs and start a local server to preview them
docs-serve:
    uv run --group docs --isolated --no-dev mkdocs serve

# build docs in strict mode
docs-build:
    uv run --group docs --isolated --no-dev mkdocs build --strict

# tag and release <version>
release version:
    git tag -a {{version}} -m {{version}}
    git push upstream --follow-tags

# update schema
update-schema:
    uv run pytest tests/test_metadata/test_metadata_schema.py::test_schema_file_updated --update-schema
