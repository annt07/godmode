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


GLOSSARY = """# Glossary
<!-- ste:off -->
| Use | Do not use |
|---|---|
| verify (the agent tests a fact) | confirm, validate, check (verb) |
| remove | delete, erase |
| fix | repair, correct (verb) |
<!-- ste:on -->
"""


def test_check_verb_patterns():
    for s in ["Check the log.", "Then check that it passes.", "It checks the file.",
              "We checked it.", "- check each task", "Do a sanity-check first."]:
        assert "check-verb" in rules(s), s


def test_check_noun_not_flagged():
    for s in ["Run a check for errors.", "The check the linter runs is fast.", "Use the checklist.",
              "Each check passes.", "Their check failed.", "A spot check is enough."]:
        assert "check-verb" not in rules(s), s


def test_check_and_correct_left_synonym_groups():
    assert "synonym-rotation" not in rules("Verify the file. Then do a check.")
    assert "synonym-rotation" not in rules("Fix the bug. Use the correct seam.")


def test_glossary_words_flagged_outside_exempt_text(tmp_path):
    g = tmp_path / "glossary.md"
    g.write_text(GLOSSARY)
    banned = sl.load_glossary(g)
    assert set(banned) == {"confirm", "validate", "delete", "erase", "repair"}
    found = rules('Confirm the result. Delete the file. Run `delete-me`. He said "confirm it".', glossary=banned)
    assert found.count("glossary-word") == 2


def test_max_words_option():
    s = " ".join(["word"] * 22) + "."
    assert rules(s) == [] and rules(s, max_words=20) == ["long-sentence"]


def test_cli_glossary_and_max_words(tmp_path):
    g = tmp_path / "glossary.md"
    g.write_text(GLOSSARY)
    f = tmp_path / "a.md"
    f.write_text("Delete the file.\n")
    r = subprocess.run([sys.executable, str(LINT), "--glossary", str(g), "--max-words", "20", str(f)],
                       capture_output=True, text=True)
    assert r.returncode == 1 and "glossary-word" in r.stdout


W15 = " ".join(["word"] * 15)


def test_wrapped_sentence_counted_once_at_start_line():
    found = sl.lint(f"Intro line.\n\n{W15}\n{W15}.\n")[0]
    assert [(f["rule"], f["line"]) for f in found] == [("long-sentence", 3)]


def test_list_items_and_blockquote_boundaries_not_joined():
    assert rules(f"- {W15}.\n- {W15}.\n") == []
    assert rules(f"> {W15}\n> {W15}.\n") == ["long-sentence"]
    assert rules(f"{W15}.\n> {W15}.\n") == []
    assert rules(f"{W15}\n<!-- note -->\n{W15}.\n") == []


def test_list_item_continuation_is_joined():
    assert rules(f"- {W15}\n  {W15}.\n") == ["long-sentence"]


def test_table_rows_and_headings_end_paragraphs():
    assert rules(f"# {W15}\n{W15}.\n") == []
    assert rules(f"| {W15} |\n|---|\n| {W15} |\n") == []


def test_report_states_limits(tmp_path):
    f = tmp_path / "a.md"
    f.write_text("Good text.\n")
    out = subprocess.run([sys.executable, str(LINT), str(f)], capture_output=True, text=True).stdout
    assert "can be wrong" in out and "does not prove" in out


def test_word_in_two_glossary_rows_reported_once(tmp_path):
    g = tmp_path / "glossary.md"
    g.write_text("| Use | Do not use |\n|---|---|\n| verify | confirm |\n| approve | confirm |\n")
    banned = sl.load_glossary(g)
    assert banned == ["confirm"]
    assert rules("Confirm it.", glossary=banned) == ["glossary-word"]


def test_glossary_reads_only_the_do_not_use_table(tmp_path):
    g = tmp_path / "glossary.md"
    g.write_text("| Use | Do not use |\n|---|---|\n| remove | delete |\n\n"
                 "| Term | Meaning |\n|---|---|\n| seam | A public interface, the test seam |\n")
    assert sl.load_glossary(g) == ["delete"]


def test_sentence_end_inside_bold_or_quotes_splits():
    assert rules(f"**{W15}.** {W15}.") == []
    assert rules(f"He said: {W15}.) {W15}.") == []


def test_check_verb_before_common_objects_and_adverbs():
    for s in ["Then check results.", "Always check output.", "Check logs first.", "You check carefully."]:
        assert "check-verb" in rules(s), s


def test_yaml_description_with_trailing_comment_is_linted():
    text = '---\nname: x\ndescription: "Use when a; b." # note\n---\n'
    assert rules(text) == ["semicolon"]
