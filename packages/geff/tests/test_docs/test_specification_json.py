import json
import re
from pathlib import Path

import pydantic
import pytest

from geff_spec import GeffSchema

DOCS = Path(__file__).parent.parent.parent.parent.parent / "docs"
SPECIFICATION_MD_PATH = DOCS / "specification.md"

# Matches fenced JSONC code blocks in markdown files
JSONC_MD_RE = re.compile(r"```jsonc\s+(.*?)```", re.DOTALL)
# Matches JavaScript-style single line comments
JSONC_SINGLE_LINE_COMMENT_RE = re.compile(r"//.*")


def check_jsonc_markdown_blocks(markdown_text, geff=True):
    """Test if JSON with comment code blocks in markdown validate as geff."""
    jsonc_blocks = JSONC_MD_RE.findall(markdown_text)
    assert jsonc_blocks, "markdown_text does not contain any jsonc blocks"

    for jsonc_block in jsonc_blocks:
        json_block = JSONC_SINGLE_LINE_COMMENT_RE.sub("", jsonc_block)

        # Distinguish between JSON parsing and geff validation
        json_dict = json.loads(json_block)
        assert json_dict, "json is empty"

        if geff:
            GeffSchema.model_validate_json(json_block)


def test_specification_md():
    """Test JSONC blocks in docs/specification.md validate as geff."""
    check_jsonc_markdown_blocks(SPECIFICATION_MD_PATH.read_text())


def test_check_jsonc_markdown_blocks():
    """Test JSONC extraction, parsing, and geff validation."""
    # Check minimal valid geff with comments
    check_jsonc_markdown_blocks("""
    # Minimal geff specification

    This is an example of a minimal geff specification.

    ```jsonc
    // minimal geff
    {
        "geff": { // geff is a required field
            "geff_version": "0.0.0", // version must be of the form major.minor.patch
            // directed must be a boolean value
            "directed": true,
            "node_props_metadata": { },
            "edge_props_metadata": { }
        }
    }
    ```
    """)

    with pytest.raises(AssertionError, match="markdown_text does not contain any jsonc blocks"):
        check_jsonc_markdown_blocks("""
        # This is a markdown header

        Markdown text
        """)

    with pytest.raises(AssertionError, match="json is empty"):
        check_jsonc_markdown_blocks("""
        ```jsonc
        {}
        ```
        """)

    # Check JSON only
    check_jsonc_markdown_blocks(
        """
        # OME-NGFF
        ```jsonc
        {
            "ome": {}
        }
        ```
        """,
        False,
    )

    # Check for invalid geff
    with pytest.raises(pydantic.ValidationError):
        check_jsonc_markdown_blocks("""
        ```jsonc
        {
            "geff": {}
        }
        ```
        """)

    # Check for invalid comments
    with pytest.raises(json.JSONDecodeError):
        check_jsonc_markdown_blocks("""
        ```jsonc
        # Bad Python-style comment
        {
            "geff": {}
        }
        ```
        """)
