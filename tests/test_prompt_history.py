"""Tests for prompt_history."""

from __future__ import annotations

import argparse
import tempfile
import unittest
from pathlib import Path

from prompt_history.cli import build_parser, main
from prompt_history.db import PromptDB


class PromptDBTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.db = PromptDB(self.tmp.name)

    def tearDown(self) -> None:
        self.db.close()
        Path(self.tmp.name).unlink(missing_ok=True)

    def test_save_and_list(self) -> None:
        self.db.save_prompt("greeting", "Hello world", ["hello"])
        self.db.save_prompt("greeting", "Hello there, world!", ["hello", "greeting"])
        rows = self.db.list_prompts()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["name"], "greeting")
        self.assertEqual(rows[0]["version"], 2)
        self.assertEqual(rows[1]["version"], 1)

    def test_get_latest_and_version(self) -> None:
        self.db.save_prompt("poem", "Roses are red", [])
        self.db.save_prompt("poem", "Violets are blue", [])
        latest = self.db.get_prompt("poem")
        self.assertEqual(latest["version"], 2)
        self.assertEqual(latest["content"], "Violets are blue")
        v1 = self.db.get_prompt("poem", 1)
        self.assertIsNotNone(v1)
        self.assertEqual(v1["content"], "Roses are red")

    def test_get_missing_returns_none(self) -> None:
        self.assertIsNone(self.db.get_prompt("nope"))
        self.assertIsNone(self.db.get_prompt("nope", 3))

    def test_search(self) -> None:
        self.db.save_prompt("alpha", "The quick brown fox", ["animal"])
        self.db.save_prompt("beta", "Jumps over the lazy dog", ["animal"])
        self.db.save_prompt("gamma", "Unrelated content", [])
        results = self.db.search("fox")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "alpha")
        results = self.db.search("animal")
        self.assertEqual(len(results), 2)
        results = self.db.search("ZONK")
        self.assertEqual(len(results), 0)

    def test_tags(self) -> None:
        row_id, _ = self.db.save_prompt("tagged", "content", ["a"])
        self.db.set_tags(row_id, ["a", "b", "c"])
        row = self.db.get_prompt("tagged")
        tags = [t.strip() for t in (row["tags"] or "").split(",") if t.strip()]
        self.assertEqual(tags, ["a", "b", "c"])


class CLITestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.db_path = self.tmp.name
        self.parser = build_parser()

    def tearDown(self) -> None:
        Path(self.tmp.name).unlink(missing_ok=True)

    def _run(self, *args: str) -> int:
        return main(["--db", self.db_path, *args])

    def test_save_from_content_and_file(self) -> None:
        code = self._run("save", "--name", "hi", "--content", "Hello world", "--tag", "t1")
        self.assertEqual(code, 0)
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
            fh.write("File content here")
            fpath = fh.name
        try:
            code = self._run("save", "--name", "fromfile", "--file", fpath)
            self.assertEqual(code, 0)
        finally:
            Path(fpath).unlink(missing_ok=True)

    def test_save_empty_fails(self) -> None:
        code = self._run("save", "--name", "empty", "--content", "   ")
        self.assertEqual(code, 1)

    def test_list_show_diff(self) -> None:
        self._run("save", "--name", "d", "--content", "line one\nline two\n")
        self._run("save", "--name", "d", "--content", "line one\nline three\n")
        code = self._run("list", "--name", "d")
        self.assertEqual(code, 0)
        code = self._run("show", "d")
        self.assertEqual(code, 0)
        code = self._run("show", "d", "--version", "1", "--raw")
        self.assertEqual(code, 0)
        code = self._run("diff", "d", "--from", "1", "--to", "2")
        self.assertEqual(code, 0)

    def test_show_missing_fails(self) -> None:
        code = self._run("show", "missing")
        self.assertEqual(code, 1)

    def test_search_cli(self) -> None:
        self._run("save", "--name", "s", "--content", "needle in a haystack", "--tag", "rare")
        code = self._run("search", "needle")
        self.assertEqual(code, 0)
        code = self._run("search", "absent")
        self.assertEqual(code, 0)

    def test_tag(self) -> None:
        self._run("save", "--name", "t", "--content", "x", "--tag", "old")
        code = self._run("tag", "t", "--add", "new", "--remove", "old")
        self.assertEqual(code, 0)

    def test_export(self) -> None:
        self._run("save", "--name", "e", "--content", "export me", "--tag", "x")
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "out.md"
            code = self._run("export", "e", "--output", str(out))
            self.assertEqual(code, 0)
            text = out.read_text(encoding="utf-8")
            self.assertIn("# Prompt: e", text)
            self.assertIn("export me", text)
            self.assertIn("x", text)

    def test_export_all(self) -> None:
        self._run("save", "--name", "a", "--content", "aaa")
        self._run("save", "--name", "b", "--content", "bbb")
        with tempfile.TemporaryDirectory() as td:
            code = self._run("export-all", "--output", td)
            self.assertEqual(code, 0)
            files = list(Path(td).glob("*.md"))
            self.assertEqual(len(files), 2)

    def test_version_flag(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            main(["--version"])
        self.assertEqual(ctx.exception.code, 0)

    def test_missing_command_fails(self) -> None:
        with self.assertRaises(SystemExit):
            main([])


if __name__ == "__main__":
    unittest.main()
