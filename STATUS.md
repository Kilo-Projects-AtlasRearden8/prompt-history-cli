# STATUS

## What was built

`prompt-history` — a local-first Python CLI to save, tag, diff, search, and export
prompt versions. Zero external dependencies (stdlib only: `argparse`, `sqlite3`,
`difflib`, `pathlib`, `datetime`). All prompt data lives in a local SQLite database.
No API keys, no network, no accounts, no secrets.

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
- `prompt_history/cli.py` — argparse CLI and command handlers
- `prompt_history/db.py` — SQLite storage layer
- `prompt_history/export.py` — Markdown rendering and export
- `tests/test_prompt_history.py` — unit tests (DB layer + CLI)
- `pyproject.toml` — project config with `prompt-history` console script
- `README.md`, `LICENSE`, `STATUS.md`, `.gitignore`

## How to run

```bash
python3 -m pip install -e .        # installs the `prompt-history` command
prompt-history --help

# without installing:
python3 -m prompt_history save --name hello --content "Say hi" --tag demo
python3 -m prompt_history list
python3 -m prompt_history diff hello --from 1 --to 2
python3 -m prompt_history export hello --output hello.md
```

Database location: `~/.prompt_history/prompts.db` by default; override with `--db`.

## Verification results

- `python3 -m unittest discover -s tests`: **15 tests, 15 passed, OK**
  - DB layer: save/list/get/search/tags
  - CLI: save from content/file, empty-content rejection, list/show/diff,
    search, tag add/remove, single export, export-all, `--version`, missing command
- Manual smoke test: save v1/v2, diff, export to Markdown — all ran correctly
- No lint/typecheck tooling configured in this minimal project; code is stdlib-only
  and reviewed for basic correctness

## Known gaps

- No dedicated lint/typecheck configuration (e.g. ruff, mypy)
- Database migrations are not versioned; schema changes would require recreating the DB
- Tags are stored as a comma-separated string (fine for this scope; simple LIKE search)
- No encryption at rest — database is a plain SQLite file; protect the file itself
- Console script entry point defined in `pyproject.toml` but not installed to a real
  PyPI index (intended: never publish)

Built for Asdale Dynamics, LLC. Credit: Asdale Dynamics, LLC.
