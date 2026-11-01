"""SQLite storage layer for prompt versions."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    version INTEGER NOT NULL,
    content TEXT NOT NULL,
    tags TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_prompts_name ON prompts(name);
CREATE INDEX IF NOT EXISTS idx_prompts_version ON prompts(name, version);
CREATE INDEX IF NOT EXISTS idx_prompts_created ON prompts(created_at);
"""


class PromptDB:
    """Local SQLite database of prompt versions.

    All data stays on the user's machine. No network calls, no keys.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    # ------------------------------------------------------------------ write

    def save_prompt(self, name: str, content: str, tags: list[str] | None = None) -> tuple[int, int]:
        """Insert a new version of a prompt. Returns (row_id, version)."""
        row = self.conn.execute(
            "SELECT MAX(version) FROM prompts WHERE name = ?", (name,)
        ).fetchone()
        version = (row[0] or 0) + 1
        tags_str = ",".join(tags or [])
        created_at = datetime.now(timezone.utc).isoformat()
        cur = self.conn.execute(
            "INSERT INTO prompts (name, version, content, tags, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (name, version, content, tags_str, created_at),
        )
        self.conn.commit()
        return cur.lastrowid, version

    def set_tags(self, prompt_id: int, tags: list[str]) -> None:
        """Replace the tags on a stored prompt version."""
        self.conn.execute(
            "UPDATE prompts SET tags = ? WHERE id = ?", (",".join(tags), prompt_id)
        )
        self.conn.commit()

    # ------------------------------------------------------------------ read

    def list_prompts(self, name: str | None = None) -> list[sqlite3.Row]:
        """List prompt versions, newest first within each name."""
        if name:
            return self.conn.execute(
                "SELECT id, name, version, tags, created_at FROM prompts "
                "WHERE name = ? ORDER BY version DESC", (name,)
            ).fetchall()
        return self.conn.execute(
            "SELECT id, name, version, tags, created_at FROM prompts "
            "ORDER BY name COLLATE NOCASE, version DESC"
        ).fetchall()

    def get_prompt(
        self, name: str, version: int | None = None
    ) -> sqlite3.Row | None:
        """Fetch one prompt version (latest if version is omitted)."""
        if version is None:
            return self.conn.execute(
                "SELECT id, name, version, content, tags, created_at FROM prompts "
                "WHERE name = ? ORDER BY version DESC LIMIT 1", (name,)
            ).fetchone()
        return self.conn.execute(
            "SELECT id, name, version, content, tags, created_at FROM prompts "
            "WHERE name = ? AND version = ?", (name, version)
        ).fetchone()

    def search(self, query: str) -> list[sqlite3.Row]:
        """Search name, content, and tags for a substring (case-insensitive)."""
        like = f"%{query}%"
        return self.conn.execute(
            "SELECT id, name, version, tags, created_at FROM prompts "
            "WHERE name LIKE ? OR content LIKE ? OR tags LIKE ? "
            "ORDER BY name COLLATE NOCASE, version DESC",
            (like, like, like),
        ).fetchall()

    def close(self) -> None:
        self.conn.close()
