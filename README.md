# prompt-history

A local-first command-line tool to **save, tag, diff, search, and export prompt versions**.
Built for Dylan Asdale and Asdale Dynamics, LLC — beginner-friendly AI tools, plain English,
step by step, never condescending. All data stays on your machine in a local SQLite database.
No API keys, no network calls, no accounts.

## Who this is for

Anyone working with AI prompts who wants a simple, versioned prompt library on their own
computer: writers, educators, small-business owners, healthcare workers exploring AI
(education only — never medical advice), and hobbyists tinkering with local LLMs, FFXIV,
or chess prompts.

## Install

```bash
git clone https://github.com/asdaledynamics/prompt-history-cli
cd prompt-history-cli
python3 -m pip install -e .
```

This creates a `prompt-history` command on your `PATH`. You can also run it without
installing:

```bash
python3 -m prompt_history --help
```

Requires Python 3.8+. No external packages are needed.

## Quick start

Save your first prompt:

```bash
prompt-history save --name "email-draft" --content "Write a friendly onboarding email" --tag onboarding --tag email
```

Save a new version later:

```bash
prompt-history save --name "email-draft" --content "Write a warm, concise onboarding email for new users" --tag onboarding --tag email --tag v2
```

List your prompts:

```bash
prompt-history list
prompt-history list --name "email-draft"
```

Show the latest version:

```bash
prompt-history show email-draft
```

Show a specific version:

```bash
prompt-history show email-draft --version 1
```

Diff two versions:

```bash
prompt-history diff email-draft --from 1 --to 2
```

Add or remove tags:

```bash
prompt-history tag email-draft --version 2 --add priority-high --remove draft
```

Search your prompt library:

```bash
prompt-history search onboarding
```

Export a version to Markdown:

```bash
prompt-history export email-draft --output email-draft.md
```

Export everything (or a filtered set) to a folder of Markdown files:

```bash
prompt-history export-all --output ./prompt-exports
```

## Where data lives

By default prompts are stored in `~/.prompt_history/prompts.db` (a plain SQLite file).
Use `--db /path/to/db.sqlite` to keep the database wherever you like — in a project folder,
on a synced drive, or backed up however you prefer. Nothing leaves your machine.

## Commands

| Command | Purpose |
|---------|---------|
| `save` | Save a new prompt version (`--name`, `--content` or `--file`, `--tag`) |
| `list` | List saved prompt versions (`--name` to filter) |
| `show` | Show a prompt version (`--version` for a specific one, `--raw` for content only) |
| `diff` | Show a unified diff between two versions (`--from`, `--to`) |
| `search` | Search name, content, and tags |
| `tag` | Add (`--add`) or remove (`--remove`) tags on a version |
| `export` | Export one version to a Markdown file (`--output`) |
| `export-all` | Export versions to Markdown files in a directory (`--output`) |

## Testing

```bash
python3 -m unittest discover -s tests
```

## Credits & license

Created for **Asdale Dynamics, LLC** (Indiana, formed October 2026) — beginner-friendly AI
education, books, and practical open-source tools. Find Dylan Asdale's writing at
[dylanasdale.github.io](https://dylanasdale.github.io) and *The Massive AI Manual*.

Licensed under the MIT License. See [LICENSE](LICENSE).

Copyright (c) 2026 Asdale Dynamics, LLC
