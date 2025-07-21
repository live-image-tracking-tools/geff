"""This file is triggered by mkdocs.yml in the "hooks" section.

It generates the HTML documentation on the `on_page_markdown` hook.
"""

from __future__ import annotations

import re
import subprocess
import tempfile
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.files import Files
    from mkdocs.structure.pages import Page

DOCS = Path(__file__).parent
ROOT = DOCS.parent


@cache  # only run this once per session
def _gen_schema_docs() -> str:
    """Generate the html schema documentation from the geff-schema.json file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # temporary path for the schema html docs
        dest = Path(tmpdir, "schema.html")

        # uncomment if you want to ensure that the schema is up to date
        # write_metadata_schema(ROOT / "geff-schema.json")

        # generate the schema documentation
        subprocess.run(
            [
                "generate-schema-doc",
                "--no-copy-css",
                "--no-copy-js",
                "geff-schema.json",
                str(dest),
            ]
        )

        # Read in docs, and make some modifications
        text = dest.read_text()
        # not needed since we're embedding the schema in the docs
        text = re.sub(r"<!DOCTYPE html>\s*<html[^>]*>", "", text, count=1)
        text = re.sub(r"</html>\s*$", "", text, count=1).strip()
        # remove the footer
        text = re.sub(r"<footer>.*?</footer>", "", text, flags=re.DOTALL)
        text = text.replace("<h1>GeffSchema</h1>", "")
        # remove the script and link tags that are not needed
        # these files are included in the mkdocs.yml config as extra_css and extra_javascript
        text = text.replace('<script src="schema_doc.min.js"></script>', "")
        text = text.replace('<link rel="stylesheet" type="text/css" href="schema_doc.css">', "")
        return f'<div id="geff-schema">{text}</div>'


def on_page_markdown(
    markdown: str, /, *, page: Page, config: MkDocsConfig, files: Files
) -> str | None:
    """Hook to modify the markdown content before it is processed."""
    # replace the <!-- GEFF-SCHEMA --> comment with the generated schema docs
    markdown = markdown.replace("<!-- GEFF-SCHEMA -->", _gen_schema_docs())
    return markdown
