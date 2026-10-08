"""Unit tests for the godmode STE linter (skills/ste-writing/scripts/ste-lint.py).

Seam: lint(text, filename, glossary, max_words), prepare(text), load_glossary(path), and the CLI.
Run: uv run --with pytest pytest tests -q -p no:cacheprovider
"""
import importlib.util
import pathlib
import subprocess
import sys

LINT = pathlib.Path(__file__).resolve().parents[1] / "skills/ste-writing/scripts/ste-lint.py"
spec = importlib.util.spec_from_file_location("ste_lint", LINT)
sl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sl)


def rules(text, **kw):
    return [f["rule"] for f in sl.lint(text, **kw)[0]]


def test_upstream_selftest_still_passes():
    r = subprocess.run([sys.executable, str(LINT), "--selftest"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_frontmatter_skipped_but_description_linted():
    text = '---\nname: x;y\ndescription: "Use when a; b."\n---\nBody.\n'
    found = sl.lint(text)[0]
    assert [(f["rule"], f["line"]) for f in found] == [("semicolon", 3)]


def test_block_scalar_description_joined():
    words = " ".join(["word"] * 30)
    text = f"---\nname: x\ndescription: >\n  {words[:80]}\n  {words[80:]}.\n---\n"
    assert rules(text) == ["long-sentence"]


def test_quoted_phrase_inside_description_exempt():
    text = '---\nname: x\ndescription: Use when the user says "check for issues; now".\n---\n'
    assert rules(text) == []


def test_straight_and_curly_quotes_exempt():
    assert rules('Thought: "I will do it; later". Reality: do it now.') == []
    assert rules('Thought: \u201cI will do it; later\u201d. Reality: do it now.') == []


def test_unmatched_quote_exempts_nothing():
    assert rules('He said "wait; stop now.') == ["semicolon"]


def test_quote_rule_per_table_cell():
    table = '| Thought | Reality |\n|---|---|\n| "skip it; fine" | Do not skip; ever |\n'
    found = sl.lint(table)[0]
    assert [f["rule"] for f in found] == ["semicolon"] and found[0]["col"] > 20


def test_off_markers_exempt_and_unclosed_block_is_reported():
    assert rules("<!-- ste:off -->\nBad; text.\n<!-- ste:on -->\nGood text.\n") == []
    assert "ste-off-unclosed" in rules("<!-- ste:off -->\nBad; text.\n")


def test_prepare_keeps_line_count():
    text = '---\nname: x\n---\n"a; b"\n<!-- ste:off -->\nx\n<!-- ste:on -->\n'
    prepared, unclosed = sl.prepare(text)
    assert len(prepared.splitlines()) == len(text.splitlines()) and unclosed is False
