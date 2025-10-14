# Gibbiverse Link Fixer

Utilities to clean and enrich Markdown in the Gibbiverse blog content.

This tool scans a directory of Markdown files to:

- Remove or replace empty links like `[text]()`
- Replace known link aliases with real URLs from a small database
- Add tags to frontmatter based on a topics list found in the document body

It’s designed to be run locally or in CI before publishing.

## Features

- Detects empty Markdown links and removes them, optionally replacing with a URL from `links.yaml` if an alias matches the link text
- Leaves valid absolute URLs (`http(s)://...`) and anchors (`#...`) intact
- For relative paths, keeps the link only if it points to an existing file; otherwise treats it as external/missing and removes it
- Auto-tagging: scans the body text for topics from `topics.txt` and adds any matches to the YAML `tags` frontmatter, preserving existing tags

## Project layout

- `main.py` — Python CLI that performs link cleanup and tagging
- `pyproject.toml` — Python project metadata and dependencies
- `.mega-linter.yaml` — CI configuration to lint/format code and Markdown
- `.markdownlint.json` — Markdownlint rules
- `.github/workflows/mega-linter.yaml` — GitHub Actions workflow running MegaLinter

## Requirements

- Python 3.12+

## Installation

You can run with the system Python or create a virtual environment. With uv or pip:

Using pip:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r <(python -c 'import tomllib,sys;print("\n".join(tomllib.load(open("pyproject.toml","rb"))["project"]["dependencies"]))')
```

Using uv (optional):

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

Alternatively, install via editable mode:

```bash
pip install -e .
```

## Usage

From the `link-fixer` directory:

```bash
python main.py \
  --path ../             # Root directory to scan (defaults to ../)
  --links ../links.yaml  # YAML map: alias -> URL (defaults to ../links.yaml)
  --topics ../topics.txt # Text file with one topic per line (defaults to ../topics.txt)
```

Notes:

- `--path` should point to the folder containing your Markdown files (e.g., the blog root or `content/`)
- If a link text (alias) exists in `links.yaml`, the script will replace `[alias]()` or invalid `[alias](broken)` with `[alias](real_url)`
- `topics.txt` entries found in the body are merged into frontmatter `tags`

## Examples

Given this input:

```md
This is an [Obsidian]() note. See [GitHub](https://github.com/).

---
tags: [blog]
---

We mention embedded rust here.
```

And:

```yaml
# links.yaml
Obsidian: https://obsidian.md/
```

```txt
# topics.txt
embedded rust
```

The output becomes:

```md
This is an [Obsidian](https://obsidian.md/) note. See [GitHub](https://github.com/).

---
tags: [blog, embedded rust]
---

We mention embedded rust here.
```

## CI

MegaLinter runs on pushes and PRs (see `.github/workflows/mega-linter.yaml`) with the Python flavor. It lints/auto-formats:

- Markdown (markdownlint, link check, table formatter)
- YAML, JSON
- Python (ruff + ruff format)

## Troubleshooting

- Missing dependencies: ensure you’re using Python 3.12+ and installed dependencies from `pyproject.toml`
- Paths: `--path`, `--links`, and `--topics` are resolved relative to where you run `python main.py`. Use absolute paths if needed.
- Link replacement: only aliases present as keys in `links.yaml` are replaced.

## License

MIT (see repository root license if present).
