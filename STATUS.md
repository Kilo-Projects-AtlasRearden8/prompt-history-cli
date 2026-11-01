# STATUS

## What was built

`prompt-history` — a local-first Python CLI to **save, tag, diff, search, and export prompt
versions**. Zero external dependencies (stdlib only: `argparse`, `sqlite3`, `difflib`,
`pathlib`, `datetime`, `io`). All prompt data lives in a local SQLite database. No API keys,
no network, no accounts, no secrets, no personal data.

### Commands
- `save --name --content|--file [--tag ...]` — save a new auto-versioned prompt
- `list [--name]` — list saved versions
- `show NAME [--version N] [--raw]` — show a version (latest by default)
- `diff NAME --from N --to M` — unified diff between two versions
- `search QUERY` — search name, content, and tags
- `tag NAME [--version N] [--add T] [--remove T]` — manage tags
- `export NAME --output FILE.md` — export one version to Markdown
- `export-all --output DIR [--name]` — export versions to Markdown files

### Files
- `prompt_history/__init__.py` — package metadata
- `prompt_history/__main__.py` — `python -m prompt_history` entry point
- `prompt_history/cli.py` — argparse CLI and command handlers (`--db` accepted before or
  after the subcommand)
- `prompt_history/db.py` — SQLite storage layer
- `prompt_history/export.py` — Markdown rendering and export
- `tests/test_prompt_history.py` — unit tests (DB layer + CLI)
- `pyproject.toml` — project config with `prompt-history` console script
- `README.md`, `LICENSE`, `STATUS.md`, `.gitignore`

## How to run

```bash
python3 -m venv .venv
.venv/bin/pip install -e .        # installs the `prompt-history` command
.venv/bin/prompt-history --help

# without installing:
python3 -m prompt_history save --name hello --content "Say hi" --tag demo
python3 -m prompt_history list
python3 -m prompt_history diff hello --from 1 --to 2
python3 -m prompt_history export hello --output hello.md
```

Database location: `~/.prompt_history/prompts.db` by default; override with `--db` (works
before or after the subcommand).

## Verification results

- `python3 -m unittest discover -s tests`: **20 tests, 20 passed, OK**
  - DB layer: save/list/get/search/tags
  - CLI: save from content/file/stdin, empty-content rejection, list/show/diff,
    versioned search, tag add/remove (incl. `--version`), single export, versioned export,
    export-all (all + filtered by name), `--version`, missing command, `--db` before and
    after the subcommand
- Package build: `python3 -m venv .venv && .venv/bin/pip install -e .` succeeds
- Console script entry point: `prompt-history --version` prints `prompt-history 0.1.0`;
  save/list workflow through the installed command works
- Manual smoke test: save v1/v2, diff, export to Markdown — all ran correctly
- No `.github/workflows` files. No secrets, API keys, or personal data in any file.
- LICENSE copyright line is exactly: `Copyright (c) 2026 Asdale Dynamics, LLC`
- README credits Asdale Dynamics, LLC and Dylan Asdale

Committed to git as a single root commit (existing git identity, plain message, no
Co-authored-by trailers). Not pushed, no remote created, nothing published.

## Known gaps

- No dedicated lint/typecheck configuration (e.g. ruff, mypy). Code is stdlib-only and kept
  small and readable.
- Database migrations are not versioned; schema changes would require recreating the DB.
- Tags are stored as a comma-separated string (simple and adequate for this scope).
- No encryption at rest — the database is a plain SQLite file; protect the file itself.
- Console script entry point is defined in `pyproject.toml` but the package is not published
  to PyPI (intended: never publish).
- `--db` normalization is handled in `main()`; programmatic use of `build_parser()`
  directly still requires `--db` before the subcommand.

Built for Asdale Dynamics, LLC. Credit: Asdale Dynamics, LLC.
