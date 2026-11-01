"""Markdown export for prompt versions."""

from __future__ import annotations

from typing import Sequence

from .db import PromptDB, sqlite3


def render_markdown(row: sqlite3.Row) -> str:
    """Render a single prompt version as Markdown."""
    tags = row["tags"] or ""
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    tag_line = ", ".join(tag_list) if tag_list else "(none)"
    lines: list[str] = []
    lines.append(f"# Prompt: {row['name']}")
    lines.append("")
    lines.append(f"- **Version:** {row['version']}")
    lines.append(f"- **Created:** {row['created_at']}")
    lines.append(f"- **Tags:** {tag_line}")
    lines.append("")
    lines.append("## Content")
    lines.append("")
    lines.append("```text")
    lines.append(row["content"])
    if not row["content"].endswith("\n"):
        lines.append("")
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def export_to_file(db: PromptDB, name: str, output: str, version: int | None = None) -> str:
    """Export a prompt version to a Markdown file. Returns the output path."""
    row = db.get_prompt(name, version)
    if row is None:
        specifier = f"{row and row['name'] or name}@{version or 'latest'}"
        raise FileNotFoundError(f"No prompt version found: {specifier}")
    content = render_markdown(row)
    with open(output, "w", encoding="utf-8") as fh:
        fh.write(content)
    return output


def export_all_to_directory(
    db: PromptDB, output_dir: str, name: str | None = None
) -> Sequence[str]:
    """Export all (or filtered) prompt versions to Markdown files in a directory."""
    from pathlib import Path

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for row in db.list_prompts(name):
        full = db.get_prompt(row["name"], row["version"])
        if full is None:
            continue
        safe_name = f"{row['name']}_v{row['version']}".replace("/", "_")
        path = out / f"{safe_name}.md"
        path.write_text(render_markdown(full), encoding="utf-8")
        written.append(str(path))
    return written
