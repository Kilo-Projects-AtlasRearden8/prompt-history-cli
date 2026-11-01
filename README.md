# prompt-history

A friendly, local-first command-line tool to **save, tag, diff, search, and export prompt versions**.

Built for **Dylan Asdale** and **Asdale Dynamics, LLC** — beginner-friendly AI education, books,
and practical tools, explained "like a friend would": plain English, step by step, never
condescending. Dylan is a registered nurse turned AI author and founder of Asdale Dynamics, LLC
(Indiana, formed October 2026). You can find his writing at
[dylanasdale.github.io](https://dylanasdale.github.io) and in *The Massive AI Manual*.

Everything stays on your computer. There are no API keys, no accounts, no network calls, and no
cloud. Your prompts live in a simple SQLite file that you control.

## Who this is for

Anyone who writes AI prompts and wants a simple version history on their own machine:

- **Writers and authors** tracking prompt drafts for books, KDP publishing, or marketing
- **Small-business owners** using AI for eBay/Amazon reselling, bookkeeping, or admin
- **Healthcare workers** exploring AI for education (this tool is educational only — never
  medical advice)
- **Educators and students** learning prompt engineering and local AI
- **Hobbyists** tinkering with local LLMs, FFXIV, chess, or any other prompt library

If you've ever rewritten a prompt and wished you could see what changed, or go back to an
earlier version, this tool is for you.

## Install

You need Python 3.8 or newer. No external packages are required.

### Option 1: Install the `prompt-history` command

```bash
git clone https://github.com/asdaledynamics/prompt-history-cli
cd prompt-history-cli
python3 -m pip install -e .
```

This puts a `prompt-history` command on your `PATH`.

### Option 2: Run without installing

```bash
python3 -m prompt_history --help
```

## Quick start

Save your first prompt:

```bash
prompt-history save --name "welcome-email" --content "Write a friendly welcome email" --tag onboarding --tag email
```

Save a revised version later (versions are grouped by name automatically):

```bash
prompt-history save --name "welcome-email" --content "Write a warm, concise welcome email for new users" --tag onboarding --tag email --tag v2
```

See what you've saved:

```bash
prompt-history list
prompt-history list --name "welcome-email"
```

Show the latest version of a prompt:

```bash
prompt-history show welcome-email
```

Show a specific version:

```bash
prompt-history show welcome-email --version 1
```

See exactly what changed between two versions:

```bash
prompt-history diff welcome-email --from 1 --to 2
```

Add or remove tags on a version:

```bash
prompt-history tag welcome-email --version 2 --add priority-high --remove draft
```

Search your whole prompt library by name, content, or tags:

```bash
prompt-history search onboarding
```

Export a version to Markdown:

```bash
prompt-history export welcome-email --output welcome-email.md
```

Export all your prompts (or just the ones matching a name) to Markdown files in a folder:

```bash
prompt-history export-all --output ./prompt-exports
prompt-history export-all --name "welcome-email" --output ./welcome-exports
```

## Where your data lives

By default, prompts are stored in `~/.prompt_history/prompts.db` — an ordinary SQLite file on
your machine. You can put it somewhere else with the `--db` option:

```bash
prompt-history --db ./my-project/prompts.db save --name "project-prompt" --content "..."
```

The `--db` option can go before or after the subcommand — whichever reads more naturally to
you.

Because everything is local, you can back up, move, or sync that `.db` file however you like.
Nothing is sent anywhere.

## Commands at a glance

| Command | What it does |
|---------|--------------|
| `save` | Save a new prompt version (`--name`, `--content` or `--file`, `--tag`) |
| `list` | List saved prompt versions (`--name` to filter) |
| `show` | Show a prompt version (`--version N` for a specific one, `--raw` for content only) |
| `diff` | Show a line-by-line diff between two versions (`--from`, `--to`) |
| `search` | Search name, content, and tags |
| `tag` | Add (`--add`) or remove (`--remove`) tags on a version |
| `export` | Export one version to a Markdown file (`--output`) |
| `export-all` | Export versions to Markdown files in a folder (`--output`) |

## Test it

```bash
python3 -m unittest discover -s tests
```

## Credits & license

Created for **Asdale Dynamics, LLC** — beginner-friendly AI education, books, guides, and
practical open-source tools the LLC can publish or sell.

Licensed under the MIT License. See [LICENSE](LICENSE).

Copyright (c) 2026 Asdale Dynamics, LLC
