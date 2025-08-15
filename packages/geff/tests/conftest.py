import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--update-schema",
        action="store_true",
        default=False,
        help="Allow tests to update the geff_metadata_schema.json file in-place.",
    )
