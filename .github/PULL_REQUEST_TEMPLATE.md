# Proposed Change
Briefly describe the contribution. If it resolves an issue or feature request, be sure to link to that issue.

# Types of Changes
What types of changes does your code introduce? Delete those that do not apply.
- Bugfix (non-breaking change which fixes an issue)
- New feature or enhancement
- Documentation update
- Tests
- Maintenance (e.g. dependencies, CI, releases, etc.)

Which topics does your change affect? Delete those that do not apply.
- Specification
- Implementations (`geff._graph_libs`)
- Convert
- Core io
- Metadata
- Testing
- Validate

# Checklist
Put an x in the boxes that apply. You can also fill these out after creating the PR. If you're unsure about any of them, don't hesitate to ask. We're here to help! This is simply a reminder of what we are going to look for before merging your code.

- [ ] I have read the [developer/contributing](https://github.com/live-image-tracking-tools/geff/blob/main/CONTRIBUTING) docs.
- [ ] I have added tests that prove that my feature works in various situations or tests the bugfix (if appropriate).
- [ ] I have checked that I maintained or improved code coverage.
- [ ] I have written docstrings and checked that they render correctly by looking at the docs preview (link left as a comment on the PR).

## If you changed the specification
- [ ] I have checked that any validation functions and tests reflect the changes.
- [ ] I have updated the GeffMetadata and the json schema using `pytest --update-schema` if necessary.
- [ ] I have updated docs/specification.md to reflect the change.
- [ ] I have updated implementations to reflect the change. (This can happen in separate PRs on a feature branch, but must be complete before merging into main.)

## If you have added or changed an implementation
- [ ] I wrote tests for the new implementation using standard fixtures supplied in conftest.py.
- [ ] I updated pyproject.toml with new dependencies if needed.
- [ ] I added a function to tests/bench.py to benchmark the new implementation.

# Further Comments
If this is a relatively large or complex change, kick off the discussion by explaining why you chose the solution you did and what alternatives you considered, etc...