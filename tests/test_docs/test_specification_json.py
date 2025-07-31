import json
import os
import re


# Adapted from mdextractor.extract_md_blocks
# https://github.com/chigwell/mdextractor
def extract_md_jsonc_blocks(text: str) -> list:
    """
    Extracts fenced code blocks from markdown text.

    Args:
        text (str): The markdown text from which to extract code blocks.

    Returns:
        list: A list of extracted code blocks, stripped of leading/trailing whitespace.
    """
    pattern = r"```jsonc\s+(.*?)```"
    compiled_pattern = re.compile(pattern, re.DOTALL)
    matches = compiled_pattern.findall(text)
    return [block.strip() for block in matches]


def remove_single_line_js_comments(jsonc_code: str) -> str:
    """
    Remove single line comments

    Args:
        text (str): The jsonc (JSON with Comments) code

    Returns:
        cleaned_code (str): JSON code (with single line comments)
    """
    comment_pattern = r"//.*"
    cleaned_code = re.sub(comment_pattern, "", jsonc_code)
    return cleaned_code


def test_specification_md():
    """
    Test JSON code blocks in docs/specification.md
    """
    script_dir = os.path.dirname(__file__)
    specification_md_path = os.path.join(script_dir, "..", "..", "docs", "specification.md")
    with open(specification_md_path) as f:
        markdown_text = f.read()

    jsonc_blocks = extract_md_jsonc_blocks(markdown_text)

    for jsonc_block in jsonc_blocks:
        json_block = remove_single_line_js_comments(jsonc_block)
        json_dict = json.loads(json_block)
        # Ensure the dict is not empty
        assert json_dict
        # Ensure the geff key is not empty
        assert json_dict["geff"]
        try:
            # Add a Python style comment, this should fail
            json.loads("# bad comment\n" + json_block)
            raise AssertionError(
                "JSON checker does not raise a JSONDecodeError with Python-style comments"
            )
        except json.JSONDecodeError:
            assert True
