"""Command-line interface for prompt_history."""

from __future__ import annotations

import argparse
import difflib
import sys
from typing import Sequence

from . import __version__
from .db import PromptDB
from .export import export_all_to_directory, export_to_file, render_markdown


DEFAULT_DB = "~/.prompt_history/prompts.db"


def _resolve_db_path(db_arg: str | None) -> str:
    if db_arg:
        return db_arg
    import os

    return os.path.expanduser(DEFAULT_DB)


def _open_db(db_arg: str | None) -> PromptDB:
    return PromptDB(_resolve_db_path(db_arg))


def _print_table(rows) -> None:
    if not rows:
        print("(none)")
        return
    for row in rows:
        tags = row["tags"] or ""
        print(f"#{row['id']}  {row['name']} v{row['version']}  [{tags}]  {row['created_at']}")


def cmd_save(args: argparse.Namespace) -> int:
    db = _open_db(args.db)
    try:
        if args.content is not None:
            content = args.content
        elif args.file:
            with open(args.file, "r", encoding="utf-8") as fh:
                content = fh.read()
        else:
            content = sys.stdin.read()
        if not content.strip():
            print("Error: prompt content is empty.", file=sys.stderr)
            return 1
        tags = args.tag or []
        row_id, version = db.save_prompt(args.name, content, tags)
        print(f"Saved {args.name} v{version} (id {row_id})")
        return 0
    finally:
        db.close()


def cmd_list(args: argparse.Namespace) -> int:
    db = _open_db(args.db)
    try:
        rows = db.list_prompts(args.name)
        if not rows:
            print("(no prompts saved yet)")
            return 0
        for row in rows:
            tags = row["tags"] or ""
            print(f"#{row['id']}  {row['name']} v{row['version']}  [{tags}]  {row['created_at']}")
        return 0
    finally:
        db.close()


def cmd_show(args: argparse.Namespace) -> int:
    db = _open_db(args.db)
    try:
        row = db.get_prompt(args.name, args.version)
        if row is None:
            specifier = f"{args.name}@{args.version or 'latest'}"
            print(f"Error: no prompt version found: {specifier}", file=sys.stderr)
            return 1
        if args.raw:
            sys.stdout.write(row["content"])
            if not row["content"].endswith("\n"):
                sys.stdout.write("\n")
        else:
            print(f"# {row['name']} v{row['version']}")
            print(f"Created: {row['created_at']}")
            tags = row["tags"] or ""
            print(f"Tags: {tags or '(none)'}")
            print("")
            print(row["content"])
        return 0
    finally:
        db.close()


def cmd_diff(args: argparse.Namespace) -> int:
    db = _open_db(args.db)
    try:
        a = db.get_prompt(args.name, args.from_version)
        b = db.get_prompt(args.name, args.to_version)
        if a is None:
            print(f"Error: no prompt version found: {args.name}@{args.from_version or 'latest'}",
                  file=sys.stderr)
            return 1
        if b is None:
            print(f"Error: no prompt version found: {args.name}@{args.to_version or 'latest'}",
                  file=sys.stderr)
            return 1
        diff = difflib.unified_diff(
            a["content"].splitlines(keepends=True),
            b["content"].splitlines(keepends=True),
            fromfile=f"{args.name} v{a['version']}",
            tofile=f"{args.name} v{b['version']}",
        )
        sys.stdout.writelines(diff)
        return 0
    finally:
        db.close()


def cmd_search(args: argparse.Namespace) -> int:
    db = _open_db(args.db)
    try:
        rows = db.search(args.query)
        if not rows:
            print(f"No matches for: {args.query}")
            return 0
        for row in rows:
            print(f"#{row['id']}  {row['name']} v{row['version']}  [{row['tags']}]  {row['created_at']}")
        return 0
    finally:
        db.close()


def cmd_tag(args: argparse.Namespace) -> int:
    db = _open_db(args.db)
    try:
        row = db.get_prompt(args.name, args.version)
        if row is None:
            print(f"Error: no prompt version found: {args.name}@{args.version or 'latest'}",
                  file=sys.stderr)
            return 1
        current = [t.strip() for t in (row["tags"] or "").split(",") if t.strip()]
        if args.add:
            current.extend(t for t in args.add if t not in current)
        if args.remove:
            current = [t for t in current if t not in args.remove]
        db.set_tags(row["id"], current)
        print(f"Tagged {args.name} v{row['version']}: {', '.join(current) or '(none)'}")
        return 0
    finally:
        db.close()


def cmd_export(args: argparse.Namespace) -> int:
    db = _open_db(args.db)
    try:
        path = export_to_file(db, args.name, args.output, args.version)
        print(f"Exported {args.name} v{args.version or 'latest'} to {path}")
        return 0
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    finally:
        db.close()


def cmd_export_all(args: argparse.Namespace) -> int:
    db = _open_db(args.db)
    try:
        written = export_all_to_directory(db, args.output, args.name)
        if not written:
            print("(nothing to export)")
            return 0
        for path in written:
            print(f"Wrote {path}")
        return 0
    finally:
        db.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="prompt-history",
        description=(
            "Local-first CLI to save, tag, diff, search, and export prompt versions. "
            "All data stays in a local SQLite database. No keys, no network."
        ),
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--db", help="Path to the local SQLite database "
                        f"(default: {DEFAULT_DB})")

    sub = parser.add_subparsers(dest="command", required=True)

    p_save = sub.add_parser("save", help="Save a new prompt version")
    p_save.add_argument("--name", required=True, help="Prompt name (versions group by name)")
    p_save.add_argument("--content", help="Prompt text inline")
    p_save.add_argument("--file", help="Read prompt text from a file")
    p_save.add_argument("--tag", action="append", help="Tag to attach (repeatable)")
    p_save.set_defaults(func=cmd_save)

    p_list = sub.add_parser("list", help="List saved prompt versions")
    p_list.add_argument("--name", help="Filter by prompt name")
    p_list.set_defaults(func=cmd_list)

    p_show = sub.add_parser("show", help="Show a prompt version")
    p_show.add_argument("name", help="Prompt name")
    p_show.add_argument("--version", type=int, help="Version number (default: latest)")
    p_show.add_argument("--raw", action="store_true", help="Print content only")
    p_show.set_defaults(func=cmd_show)

    p_diff = sub.add_parser("diff", help="Diff two versions of a prompt")
    p_diff.add_argument("name", help="Prompt name")
    p_diff.add_argument("--from", dest="from_version", type=int,
                        help="From version (default: latest)")
    p_diff.add_argument("--to", dest="to_version", type=int,
                        help="To version (default: latest)")
    p_diff.set_defaults(func=cmd_diff)

    p_search = sub.add_parser("search", help="Search prompts by name, content, or tags")
    p_search.add_argument("query", help="Search text")
    p_search.set_defaults(func=cmd_search)

    p_tag = sub.add_parser("tag", help="Add or remove tags on a prompt version")
    p_tag.add_argument("name", help="Prompt name")
    p_tag.add_argument("--version", type=int, help="Version (default: latest)")
    p_tag.add_argument("--add", action="append", help="Tag to add (repeatable)")
    p_tag.add_argument("--remove", action="append", help="Tag to remove (repeatable)")
    p_tag.set_defaults(func=cmd_tag)

    p_export = sub.add_parser("export", help="Export a prompt version to Markdown")
    p_export.add_argument("name", help="Prompt name")
    p_export.add_argument("--version", type=int, help="Version (default: latest)")
    p_export.add_argument("--output", required=True, help="Output Markdown file path")
    p_export.set_defaults(func=cmd_export)

    p_export_all = sub.add_parser("export-all", help="Export prompt versions to Markdown files")
    p_export_all.add_argument("--name", help="Filter by prompt name")
    p_export_all.add_argument("--output", required=True, help="Output directory")
    p_export_all.set_defaults(func=cmd_export_all)

    return parser


def _extract_db(argv: list[str]) -> list[str]:
    """Move any --db <path> / --db=<path> to the front so it works before or after the subcommand.

    argparse only accepts top-level options before the subcommand. Beginners naturally type
    --db after the command, so we normalize argv here.
    """
    db: str | None = None
    out: list[str] = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--db" and i + 1 < len(argv):
            db = argv[i + 1]
            i += 2
        elif arg.startswith("--db="):
            db = arg.split("=", 1)[1]
            i += 1
        else:
            out.append(arg)
            i += 1
    if db is not None:
        out = ["--db", db] + out
    return out


def main(argv: Sequence[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(_extract_db(list(argv)))
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
