# STE Writing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use godmode:subagent-driven-development (recommended) or godmode:executing-plans to implement this plan task by task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the `ste-writing` skill and its linter, rewrite every godmode skill file in STE without a change in behavior, and make STE the default for agent output.

**Architecture:** One linter module (`skills/ste-writing/scripts/ste-lint.py`) is the only place that knows the STE rules that a machine can find. Repository tests use it as their seam: unit tests for the linter, a conformance test for all skill files, and a meaning-diff script for the rewrite. The rewrite runs in 7 batches. Each batch must pass the linter, the meaning-diff script and a fresh meaning reviewer before the next batch starts. A manual agent eval in the repository measures behavior before and after.

**Tech Stack:** Python 3.10+ standard library (linter, diff script, eval), pytest through `uv run --with pytest`, Node 18 (`node --test`) for the existing installer tests, Devin CLI for the agent eval.

**Spec:** `docs/godmode/specs/2026-10-08-ste-writing-design.md`

## Global Constraints

- The linter uses only the Python standard library. It must run with `python skills/ste-writing/scripts/ste-lint.py`.
- The upstream `--selftest` of the linter must pass after every linter change.
- Run all Python with `uv run python ...` and pytest with `uv run --with pytest pytest tests -q -p no:cacheprovider` from the repository root.
- Hard rules, exact names: `semicolon`, `long-sentence` (25 words), `phrasal-verb`, `nominalization`, `marketing-adjective`, `synonym-rotation`, `dangling-conjunction`, `check-verb`, `glossary-word`. Advisory rules: `passive-voice`, `present-perfect`.
- The meaning of each sentence stays. No rule, gate, number, condition, red-flag row, example or hedge is added or removed in batches B1 to B7.
- Code blocks, inline code, file paths, commands, skill names, links and quoted text stay byte for byte.
- `asd-ste100-skill/` (outside `combined/`) is never changed.
- Base reference for all meaning checks: git tag `ste-base`, created in Task 4.
- This plan writes batches by size (about 9,000 words each), not by "about 5 skills" as spec D5 item 6 says. The goal of D5 item 6 (a small review per batch) stays.

## Review Focus

1. A red-flag table cell that holds a quote and a comment in the same cell: the quote rule must not hide the comment, and the rewrite must not change the quote.
2. "confirm" that means the user agrees: the rewrite must use "approve" or "agree", never "verify". Otherwise an approval gate becomes an agent self-check.
3. Descriptions: a rewrite that drops a trigger phrase stops a skill from firing. The trigger-word test and the eval are the controls.
4. Wrapped sentences in list items and blockquotes: the paragraph join must count one sentence, not merge two list items.
5. `ste:off` blocks: a missing `ste:on` must not silently exempt the rest of a file.

---

## File Structure

| File | Responsibility |
|---|---|
| `skills/ste-writing/SKILL.md` | The STE rules for godmode, text types, process, limits |
| `skills/ste-writing/glossary.md` | Technical nouns and verbs, one word per action, the list of words not to use |
| `skills/ste-writing/references/writing-rules.md` | Rule summary with sources (from upstream, corrected) |
| `skills/ste-writing/examples/before-after.md` | Examples. Bad text is between off markers |
| `skills/ste-writing/scripts/ste-lint.py` | The linter (upstream plus godmode changes) |
| `skills/ste-writing/LICENSE-asd-ste100.md` | Upstream MIT notice |
| `tests/test_ste_lint.py` | Linter seam (unit) |
| `tests/test_ste_conformance.py` | Conformance seam (all skill files) |
| `tests/ste/advisory-baseline.json` | Advisory counts per file and rule, from `ste-base` |
| `tests/ste/finished.txt` | Files that finished a batch |
| `tests/ste/triggers.json` | Trigger phrases per description |
| `tests/ste/meaning_diff.py` | Meaning seam (diff script) |
| `tests/ste/meaning-review-prompt.md` | Brief for the meaning reviewer subagent |
| `tests/agent-eval/trigger_eval.py` | Behavior seam: 19 trigger cases |
| `tests/agent-eval/gate_rate.py` | Behavior seam: design gate, 6 runs |
| `tests/agent-eval/pressure/*.md` | Pressure scenarios S1, S2, S4, S7 |
| `tests/agent-eval/README.md` | How to run the eval, results log |

Deletion test: the linter module concentrates all rule logic. Tests and the diff script only call it. Deleting it would spread regex rules into three test files, so it earns its place. `meaning_diff.py` has one job (structure diff against `ste-base`) and no other file does it.

---

### Task 1: Linter copy, frontmatter, quotes and off markers

**Files:**
- Create: `skills/ste-writing/scripts/ste-lint.py` (copy of `../asd-ste100-skill/scripts/ste-lint.py`, then changed)
- Create: `skills/ste-writing/LICENSE-asd-ste100.md`
- Test: `tests/test_ste_lint.py`

**Seam under test:** `lint(text, filename="<stdin>", glossary=None, max_words=25) -> (findings, words_total)` and the command line (spec Testing Decisions, seam 1).

**Demo:** A skill file with a quoted red-flag thought, an `ste:off` block and a quoted YAML description lints with findings only in the godmode prose.

**Fails at base:** `skills/ste-writing/scripts/ste-lint.py` does not exist. The upstream linter flags the semicolon inside `"I'll do it; later"` and flags the frontmatter line.

**Interfaces:**
- Produces: `lint(text, filename, glossary=None, max_words=25)`, `prepare(text) -> tuple[str, bool]` (prepared text with the same line count and exempt text replaced by spaces, and whether an `ste:off` block is unclosed). Task 2 produces `load_glossary(path) -> list[str]`.

- [ ] **Step 1: Verify the seam reaches the behavior**

Copy the upstream file and its MIT notice:

```bash
mkdir -p skills/ste-writing/scripts
cp ../asd-ste100-skill/scripts/ste-lint.py skills/ste-writing/scripts/ste-lint.py
cp ../asd-ste100-skill/LICENSE skills/ste-writing/LICENSE-asd-ste100.md
uv run python skills/ste-writing/scripts/ste-lint.py --selftest
```

Expected: the selftest passes. `lint(text, filename)` is a public function, so tests can call it.

- [ ] **Step 2: Write the failing tests**

```python
# tests/test_ste_lint.py
import importlib.util, pathlib, subprocess, sys
LINT = pathlib.Path(__file__).resolve().parents[1] / "skills/ste-writing/scripts/ste-lint.py"
spec = importlib.util.spec_from_file_location("ste_lint", LINT)
sl = importlib.util.module_from_spec(spec); spec.loader.exec_module(sl)

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
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `uv run --with pytest pytest tests/test_ste_lint.py -q -p no:cacheprovider`
Expected: FAIL. `prepare` does not exist, and the frontmatter and quoted semicolons are flagged.

- [ ] **Step 4: Write the minimal implementation**

Add to `ste-lint.py`, above `lint()`:

```python
FRONT_KEY = re.compile(r"^([A-Za-z_][\w-]*):\s?(.*)$")
QUOTE_PAIR = re.compile(r'"[^"\n]*"|\u201c[^\u201c\u201d\n]*\u201d')
OFF, ON = "<!-- ste:off -->", "<!-- ste:on -->"

def _blank(s):
    return " " * len(s)

def _strip_quotes(segment):
    if segment.count('"') % 2 or segment.count("\u201c") != segment.count("\u201d"):
        return segment
    return QUOTE_PAIR.sub(lambda m: _blank(m.group(0)), segment)

def _yaml_scalar(first, more):
    """Return the description value as a YAML parser reads it (one line)."""
    if first in (">", "|", ">-", "|-"):
        return " ".join(l.strip() for l in more)
    value = " ".join([first] + [l.strip() for l in more]).strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        inner = value[1:-1]
        return inner.replace("''", "'") if value[0] == "'" else inner.encode().decode("unicode_escape")
    return value

def prepare(text):
    """Return text with exempt parts blanked. The line count stays the same."""
    lines = text.splitlines()
    out = list(lines)
    i = 0
    if lines and lines[0].strip() == "---":
        end = next((k for k in range(1, len(lines)) if lines[k].strip() == "---"), None)
        if end:
            for k in range(0, end + 1):
                out[k] = ""
            k = 1
            while k < end:
                m = FRONT_KEY.match(lines[k])
                if m and m.group(1) == "description":
                    more = []
                    j = k + 1
                    while j < end and (lines[j].startswith((" ", "\t")) or not lines[j].strip()):
                        more.append(lines[j]); j += 1
                    out[k] = _yaml_scalar(m.group(2).strip(), more)
                    k = j
                else:
                    k += 1
            i = end + 1
    off = False
    for k in range(i, len(lines)):
        s = lines[k].strip()
        if s == OFF:
            off, out[k] = True, ""
            continue
        if s == ON:
            off, out[k] = False, ""
            continue
        if off:
            out[k] = ""
            continue
        cells = _split_table_row(out[k]) if "|" in out[k] else None
        if cells:
            row = list(out[k])
            for cell, col in cells:
                row[col:col + len(cell)] = list(_strip_quotes(cell))
            out[k] = "".join(row)
        else:
            out[k] = _strip_quotes(out[k])
    return "\n".join(out) + ("\n" if text.endswith("\n") else ""), off
```

Change `lint()` so that it starts with:

```python
def lint(text, filename="<stdin>", glossary=None, max_words=MAX_WORDS):
    prepared, unclosed = prepare(text)
    text = prepared
```

and, before `return`, adds:

```python
    if unclosed:
        findings.append({"file": filename, "line": len(text.splitlines()), "col": 1,
                         "rule": "ste-off-unclosed", "level": "advisory-free", "match": OFF,
                         "message": "ste:off block has no ste:on. Close it."})
```

Add `ste-off-unclosed` to the hard rule list in the module docstring. The upstream `_dangling_conjunction_findings(text, filename)` call must receive the prepared text too.

- [ ] **Step 5: Run the tests to verify they pass**

Run: `uv run --with pytest pytest tests/test_ste_lint.py -q -p no:cacheprovider`, then `uv run python skills/ste-writing/scripts/ste-lint.py --selftest`, then the full suite.
Expected: PASS. The selftest passes. The full suite is green.

- [ ] **Step 6: Commit**

```bash
git add skills/ste-writing/scripts/ste-lint.py skills/ste-writing/LICENSE-asd-ste100.md tests/test_ste_lint.py
git commit -m "feat(ste-writing): linter copy with frontmatter, quote and off-marker handling"
```

---

### Task 2: Linter word rules: check-verb, synonym groups, glossary, max words

**Files:**
- Modify: `skills/ste-writing/scripts/ste-lint.py`
- Test: `tests/test_ste_lint.py`

**Seam under test:** `lint(text, glossary=..., max_words=...)`, `load_glossary(path)` and the command-line options `--glossary FILE` and `--max-words N`.

**Demo:** `ste-lint.py --glossary glossary.md file.md` flags "check the log", "confirm", "delete" and passes "a check" and "the correct seam".

**Fails at base:** the linter flags "check" with "verify" as synonym rotation, does not flag "check the log", and has no `--glossary` option.

**Interfaces:**
- Consumes: `lint`, `prepare` from Task 1.
- Produces: `load_glossary(path) -> list[str]` (banned words without a qualifier), rule ids `check-verb`, `glossary-word`.

- [ ] **Step 1: Verify the seam reaches the behavior**

Read `SYNONYM_GROUPS` and `main(argv)` in `ste-lint.py`. Both are reachable through `lint()` and the command line.

- [ ] **Step 2: Write the failing tests**

```python
# append to tests/test_ste_lint.py
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
    g = tmp_path / "glossary.md"; g.write_text(GLOSSARY)
    banned = sl.load_glossary(g)
    assert set(banned) == {"confirm", "validate", "delete", "erase", "repair"}
    found = rules('Confirm the result. Delete the file. Run `delete-me`. He said "confirm it".', glossary=banned)
    assert found.count("glossary-word") == 2

def test_max_words_option():
    s = " ".join(["word"] * 22) + "."
    assert rules(s) == [] and rules(s, max_words=20) == ["long-sentence"]

def test_cli_glossary_and_max_words(tmp_path):
    g = tmp_path / "glossary.md"; g.write_text(GLOSSARY)
    f = tmp_path / "a.md"; f.write_text("Delete the file.\n")
    r = subprocess.run([sys.executable, str(LINT), "--glossary", str(g), "--max-words", "20", str(f)],
                       capture_output=True, text=True)
    assert r.returncode == 1 and "glossary-word" in r.stdout
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `uv run --with pytest pytest tests/test_ste_lint.py -q -p no:cacheprovider`
Expected: FAIL on the new tests (no `check-verb`, no `load_glossary`, no `max_words` parameter use).

- [ ] **Step 4: Write the minimal implementation**

```python
SYNONYM_GROUPS = [
    ("verify", "confirm", "validate"),
    ("delete", "remove", "erase"),
    ("start", "launch", "begin", "initiate"),
    ("stop", "halt", "terminate"),
    ("show", "display"),
    ("use", "utilize", "employ"),
    ("fix", "repair"),
    ("send", "transmit"),
    ("get", "retrieve", "fetch", "obtain"),
    ("change", "modify", "alter"),
]

CHECK_NOUN_BEFORE = {"a", "an", "the", "this", "that", "each", "every", "no", "one",
                     "my", "your", "its", "our", "their", "spot"}
CHECK_OBJECT_AFTER = {"the", "that", "whether", "if", "for", "each", "every", "it", "them",
                      "its", "your", "their", "all", "any"}
CHECK_TOKEN = re.compile(r"(?<![\w])(-?)(check(?:s|ed)?)\b", re.I)

def _check_verb_matches(line):
    """Return match objects for 'check' used as a verb (spec D2 item 5)."""
    out = []
    for m in CHECK_TOKEN.finditer(line):
        before = re.findall(r"[\w']+", line[:m.start()])
        prev = before[-1].lower() if before else ""
        nxt = re.match(r"\s+([\w']+)", line[m.end():])
        nxt = nxt.group(1).lower() if nxt else ""
        word, hyphen = m.group(2).lower(), m.group(1)
        starts = not before or re.search(r"(?:[.!?]\s+|^\s*(?:[-*+]|\d+[.)])\s+)$", line[:m.start()])
        if hyphen:
            out.append(m)
        elif prev in CHECK_NOUN_BEFORE:
            continue
        elif word in ("checks", "checked") or nxt in CHECK_OBJECT_AFTER or starts:
            out.append(m)
    return out

def load_glossary(path):
    banned, raw = [], pathlib.Path(path).read_text(encoding="utf-8")
    for line in raw.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 2 and not set(cells[1]) <= set("-: ") and cells[0].lower() != "use":
            for word in cells[1].split(","):
                word = word.strip()
                if word and "(" not in word:
                    banned.append(word.lower())
    return banned
```

Use `pathlib` (add `import pathlib`). In `lint()`, inside the per-segment loop after the `RULES` loop, add:

```python
            for m in _check_verb_matches(line):
                findings.append({"file": filename, "line": lineno, "col": source_column + m.start() + 1,
                                 "rule": "check-verb", "level": "advisory-free", "match": m.group(0),
                                 "message": "'check' used as a verb. STE approves 'check' as a noun only. Use 'verify'."})
            for word in glossary or ():
                for m in _word_re(re.escape(word)).finditer(line):
                    findings.append({"file": filename, "line": lineno, "col": source_column + m.start() + 1,
                                     "rule": "glossary-word", "level": "advisory-free", "match": m.group(0),
                                     "message": f"'{word}' is on the godmode glossary's do-not-use list."})
```

Replace `MAX_WORDS` with the `max_words` parameter in the long-sentence check. In `main(argv)`, parse `--glossary FILE` (call `load_glossary`) and `--max-words N`, and pass both to `lint`.

"Each check passes" is a noun use: "each" is in `CHECK_NOUN_BEFORE`, so the function skips it before it looks at "checks". "Their check failed" and "A spot check" are skipped the same way. The tests define the behavior. Change the word sets only when a test needs it.

- [ ] **Step 5: Run the tests to verify they pass**

Run: `uv run --with pytest pytest tests/test_ste_lint.py -q -p no:cacheprovider`, the selftest, then the full suite.
Expected: PASS, selftest passes, full suite green.

- [ ] **Step 6: Commit**

```bash
git add skills/ste-writing/scripts/ste-lint.py tests/test_ste_lint.py
git commit -m "feat(ste-writing): check-verb rule, glossary ban list, max-words option"
```

---

### Task 3: Linter paragraph join and output limits

**Files:**
- Modify: `skills/ste-writing/scripts/ste-lint.py`
- Test: `tests/test_ste_lint.py`

**Seam under test:** `lint()` and the command-line text output.

**Demo:** A 30-word sentence that wraps over two lines is one `long-sentence` finding at the first line. Two short list items are not joined. The report says that findings can be wrong.

**Fails at base:** a wrapped 30-word sentence (15 + 15 words) gives no finding. The report has no limits line.

**Interfaces:**
- Consumes: `lint` from Task 2.
- Produces: `_paragraphs(lines) -> list[tuple[int, str]]` (start line, joined text).

- [ ] **Step 1: Verify the seam reaches the behavior**

Read the long-sentence block in `lint()`. It splits each line separately. A test through `lint()` can observe the change.

- [ ] **Step 2: Write the failing tests**

```python
# append to tests/test_ste_lint.py
W15 = " ".join(["word"] * 15)

def test_wrapped_sentence_counted_once_at_start_line():
    found = sl.lint(f"Intro line.\n\n{W15}\n{W15}.\n")[0]
    assert [(f["rule"], f["line"]) for f in found] == [("long-sentence", 3)]

def test_list_items_and_blockquote_boundaries_not_joined():
    assert rules(f"- {W15}.\n- {W15}.\n") == []
    assert rules(f"> {W15}\n> {W15}.\n") == ["long-sentence"]
    assert rules(f"{W15}.\n> {W15}.\n") == []
    assert rules(f"{W15}\n<!-- note -->\n{W15}.\n") == []

def test_table_rows_and_headings_end_paragraphs():
    assert rules(f"# {W15}\n{W15}.\n") == []
    assert rules(f"| {W15} |\n|---|\n| {W15} |\n") == []

def test_report_states_limits(tmp_path):
    f = tmp_path / "a.md"; f.write_text("Good text.\n")
    out = subprocess.run([sys.executable, str(LINT), str(f)], capture_output=True, text=True).stdout
    assert "can be wrong" in out and "does not prove" in out
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `uv run --with pytest pytest tests/test_ste_lint.py -q -p no:cacheprovider`
Expected: FAIL on the wrapped-sentence test and the report test.

- [ ] **Step 4: Write the minimal implementation**

```python
BREAK = re.compile(r"^\s*(?:$|#|```|~~~|<!--|\||[-*+]\s|\d+[.)]\s)")

def _paragraphs(lines):
    """Yield (start_line, text) for each run of prose lines. Lines are already prepared."""
    out, start, buf, quoted = [], None, [], None
    for n, line in enumerate(lines, 1):
        is_quote = line.lstrip().startswith(">")
        body = line.lstrip()[1:].strip() if is_quote else line.strip()
        item = re.match(r"^\s{0,3}(?:[-*+]|\d+[.)])\s+(.*)$", line)
        if BREAK.match(line) or (quoted is not None and is_quote != quoted):
            if buf:
                out.append((start, " ".join(buf)))
            buf, start, quoted = [], None, None
            if item:
                start, buf, quoted = n, [item.group(1)], False
            continue
        if not body:
            continue
        if start is None:
            start, quoted = n, is_quote
        buf.append(INLINE_CODE.sub("", body))
    if buf:
        out.append((start, " ".join(buf)))
    return out
```

Remove the per-line long-sentence check from `lint()`. Table cells keep their per-cell check: run the old per-segment sentence split only for rows in `table_cells`. After the line loop, add:

```python
    in_fence, prose = False, []
    for raw in lines:
        if CODE_FENCE.match(raw.strip()):
            in_fence = not in_fence
            prose.append("```")
            continue
        prose.append("" if in_fence else raw)
    for start, para in _paragraphs(prose):
        if start - 1 in table_cells:
            continue
        for sent in re.split(r"(?<=[.!?])\s+", para):
            n = len(sent.split())
            if n > max_words:
                findings.append({"file": filename, "line": start, "col": 1, "rule": "long-sentence",
                                 "level": "advisory-free", "match": f"{n} words",
                                 "message": f"Sentence has {n} words (cap {max_words}). Split it."})
```

In `report()`, after the summary line, print: `Limits: a finding can be wrong, and a clean result does not prove that the text is STE.`

- [ ] **Step 5: Run the tests to verify they pass**

Run: `uv run --with pytest pytest tests/test_ste_lint.py -q -p no:cacheprovider`, the selftest, then the full suite.
Expected: PASS. If an upstream selftest case expects per-line counting, change the case to the paragraph behavior and add a comment that names spec D2 item 8.

- [ ] **Step 6: Commit**

```bash
git add skills/ste-writing/scripts/ste-lint.py tests/test_ste_lint.py
git commit -m "feat(ste-writing): join wrapped sentences per paragraph, state linter limits"
```

---

### Task 4: Conformance harness, baselines, meaning diff and base tag

**Files:**
- Create: `tests/test_ste_conformance.py`, `tests/ste/advisory-baseline.json`, `tests/ste/finished.txt`, `tests/ste/triggers.json`, `tests/ste/meaning_diff.py`, `tests/ste/meaning-review-prompt.md`, `tests/ste/make_baseline.py`
- Create (glossary seed, final text in Task 5): `skills/ste-writing/glossary.md`

**Seam under test:** the conformance test over `skills/**/*.md` and `agents/openai.yaml` values, and `meaning_diff.py BASE_REF FILE...` (spec seams 2 and 3).

**Demo:** `pytest tests/test_ste_conformance.py` passes with an empty finished list. Adding `skills/grill-me/SKILL.md` to `finished.txt` makes it fail with the file's hard findings. `meaning_diff.py ste-base skills/grill-me/SKILL.md` reports a changed number after a test edit.

**Fails at base:** none of these files exist.

**Interfaces:**
- Consumes: `lint`, `load_glossary` from Tasks 1 to 3.
- Produces: `tests/ste/finished.txt` (one repository-relative path per line), `advisory-baseline.json` (`{"path": {"passive-voice": n, "present-perfect": n}}`), `triggers.json` (`{"path": ["phrase", ...]}`), `meaning_diff.py` exit code 0 (no change) or 1 (changes listed).

- [ ] **Step 1: Verify the seam reaches the behavior**

The conformance test calls `lint()` directly with the glossary. `meaning_diff.py` reads the base text with `git show ste-base:<path>`. Both observe files only.

- [ ] **Step 2: Seed the glossary ban list**

Write `skills/ste-writing/glossary.md` with the spec D3 item 2 table between off markers (verify, approve, remove, start, change, fix, use, get, show rows). Task 5 completes the rest of the glossary.

- [ ] **Step 3: Write the failing tests**

```python
# tests/test_ste_conformance.py
import importlib.util, json, pathlib, re, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ste_lint", ROOT / "skills/ste-writing/scripts/ste-lint.py")
sl = importlib.util.module_from_spec(spec); spec.loader.exec_module(sl)
STE = ROOT / "tests/ste"
HARD = {"semicolon", "long-sentence", "phrasal-verb", "nominalization", "marketing-adjective",
        "synonym-rotation", "dangling-conjunction", "check-verb", "glossary-word", "ste-off-unclosed"}
ADVISORY = {"passive-voice", "present-perfect"}
GLOSSARY = sl.load_glossary(ROOT / "skills/ste-writing/glossary.md")

def targets():
    """(repo-relative path, text) for every agent-read text unit."""
    for p in sorted((ROOT / "skills").rglob("*.md")):
        yield p.relative_to(ROOT).as_posix(), p.read_text(encoding="utf-8")
    for p in sorted((ROOT / "skills").rglob("agents/openai.yaml")):
        m = re.search(r'^\s*short_description:\s*(.+)$', p.read_text(encoding="utf-8"), re.M)
        if m:
            yield p.relative_to(ROOT).as_posix(), f"---\ndescription: {m.group(1).strip()}\n---\n"

def finished():
    f = STE / "finished.txt"
    return {l.strip() for l in f.read_text().splitlines() if l.strip()} if f.exists() else set()

def lint(text, path):
    return sl.lint(text, path, glossary=GLOSSARY)[0]

def test_finished_files_have_no_hard_findings():
    bad = {}
    for path, text in targets():
        if path in finished():
            hard = [f"{f['line']}:{f['rule']}" for f in lint(text, path) if f["rule"] in HARD]
            if hard:
                bad[path] = hard
    assert not bad, json.dumps(bad, indent=1)

def test_advisory_counts_do_not_rise():
    base = json.loads((STE / "advisory-baseline.json").read_text())
    over = {}
    for path, text in targets():
        counts = {r: 0 for r in ADVISORY}
        for f in lint(text, path):
            if f["rule"] in ADVISORY:
                counts[f["rule"]] += 1
        for r, n in counts.items():
            if n > base.get(path, {}).get(r, 0):
                over[f"{path}:{r}"] = (n, base.get(path, {}).get(r, 0))
    assert not over, over

def test_descriptions_keep_trigger_phrases():
    triggers = json.loads((STE / "triggers.json").read_text())
    missing = {}
    for path, phrases in triggers.items():
        text = (ROOT / path).read_text(encoding="utf-8").lower()
        gone = [p for p in phrases if p.lower() not in text]
        if gone:
            missing[path] = gone
    assert not missing, missing

def test_finished_list_names_real_files():
    real = {p for p, _ in targets()}
    assert finished() <= real, finished() - real
```

```python
# tests/test_ste_meaning_diff.py
import pathlib, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
DIFF = ROOT / "tests/ste/meaning_diff.py"
spec = __import__("importlib.util").util.spec_from_file_location("md", DIFF)
md = __import__("importlib.util").util.module_from_spec(spec); spec.loader.exec_module(md)

OLD = """---\nname: x\ndescription: d\n---\n# A\n- Use `cmd` 3 times.\n- See [doc](d.md) and `godmode:grilling`.\n\n| a | b |\n|---|---|\n| 1 | 2 |\n\nYou MUST stop.\n"""

def test_identical_structure_reports_nothing():
    new = OLD.replace("Use `cmd` 3 times.", "Run `cmd` 3 times.")
    assert md.compare(OLD, new) == []

def test_each_structural_change_is_reported():
    cases = {
        "name": OLD.replace("name: x", "name: y"),
        "code": OLD.replace("`cmd`", "`cmd2`"),
        "number": OLD.replace("3 times", "4 times"),
        "link": OLD.replace("(d.md)", "(e.md)"),
        "godmode-ref": OLD.replace("godmode:grilling", "godmode:brainstorming"),
        "table-rows": OLD.replace("| 1 | 2 |\n", "| 1 | 2 |\n| 3 | 4 |\n"),
        "list-items": OLD.replace("- See", "See"),
        "strong-words": OLD.replace("You MUST stop.", "You stop."),
    }
    for kind, new in cases.items():
        assert any(kind in c for c in md.compare(OLD, new)), kind
```

- [ ] **Step 4: Run the tests to verify they fail**

Run: `uv run --with pytest pytest tests/test_ste_conformance.py tests/test_ste_meaning_diff.py -q -p no:cacheprovider`
Expected: FAIL. The baseline, triggers and diff script do not exist.

- [ ] **Step 5: Write the implementation**

`tests/ste/meaning_diff.py`:

```python
"""Compare the structure of skill files with a base git ref. Usage: meaning_diff.py BASE_REF FILE..."""
import re, subprocess, sys, collections

def facts(text):
    body = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.S)
    fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    f = collections.OrderedDict()
    f["name"] = re.findall(r"^name:\s*(.+)$", fm.group(1), re.M) if fm else []
    f["description-key"] = [bool(fm and re.search(r"^description:", fm.group(1), re.M))]
    f["code"] = sorted(re.findall(r"```.*?```", body, re.S) + re.findall(r"`[^`\n]+`", body))
    f["link"] = sorted(re.findall(r"\]\(([^)]+)\)", body))
    f["godmode-ref"] = sorted(re.findall(r"godmode:[a-z0-9-]+", body))
    prose = re.sub(r"```.*?```|`[^`\n]+`|\]\([^)]+\)", " ", body, flags=re.S)
    f["number"] = sorted(re.findall(r"(?<![\w.-])\d+(?:\.\d+)?%?(?![\w-])", prose))
    f["table-rows"] = [sum(1 for l in body.splitlines() if l.strip().startswith("|") and not re.match(r"^\|[\s:|-]+\|$", l.strip()))]
    sections, cur = collections.Counter(), "(top)"
    for l in body.splitlines():
        if l.startswith("#"):
            cur = l.strip()
        elif re.match(r"^\s*(?:[-*+]|\d+[.)])\s", l):
            sections[cur] += 1
    f["list-items"] = sorted(sections.items())
    f["strong-words"] = sorted(w for l in body.splitlines() for w in re.findall(r"\b(REQUIRED|STOP|MUST|Never)\b", l))
    return f

def compare(old, new):
    a, b = facts(old), facts(new)
    return [f"{k}: {a[k]!r} -> {b[k]!r}"[:600] for k in a if a[k] != b[k]]

def main(argv):
    base, files, bad = argv[0], argv[1:], 0
    for path in files:
        old = subprocess.run(["git", "show", f"{base}:{path}"], capture_output=True, text=True, encoding="utf-8").stdout
        new = open(path, encoding="utf-8").read()
        changes = compare(old, new) if old else ["new file (no base)"]
        for c in changes:
            print(f"{path}: {c}")
        bad += bool(changes)
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

`tests/ste/make_baseline.py` writes `advisory-baseline.json` from the files at `ste-base`:

```python
import importlib.util, json, pathlib, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests"))
import test_ste_conformance as c
counts = {}
for path, text in c.targets():
    for f in c.lint(text, path):
        if f["rule"] in c.ADVISORY:
            counts.setdefault(path, {r: 0 for r in sorted(c.ADVISORY)})[f["rule"]] += 1
(ROOT / "tests/ste/advisory-baseline.json").write_text(json.dumps(counts, indent=1, sort_keys=True) + "\n")
print(f"{len(counts)} files with advisory findings")
```

`tests/ste/triggers.json`: for each `SKILL.md` and each `openai.yaml` value, record 2 to 6 trigger phrases from the current description. Take the user-facing words that the eval cases depend on (for example, `requesting-code-review`: "review", "before merging"). `vuln-scan`: "scan", "vulnerabilit", "secrets", "PHI/PII". Keep each phrase short, so that an STE rewrite can keep it in quotes if needed.

`tests/ste/meaning-review-prompt.md`: the reviewer brief. It contains the checklist from spec seam 3 item 2, the instruction to read `git show ste-base:<path>` and the new file, the rule that "confirm" for user agreement must become "approve" or "agree" (never "verify"), and this output format:

```
## <path>
Verdict: PASS | FAIL
Findings: numbered, each with the old sentence, the new sentence, and the lost or changed meaning.
```

Create `tests/ste/finished.txt` empty.

- [ ] **Step 6: Tag the base and record the baseline**

```bash
git add -A tests skills/ste-writing/glossary.md
git commit -m "test(ste): conformance harness, meaning diff, trigger phrases"
git tag ste-base
uv run python tests/ste/make_baseline.py
```

- [ ] **Step 7: Run the tests to verify they pass**

Run: `uv run --with pytest pytest tests -q -p no:cacheprovider`, then `node --test tests/`.
Expected: PASS. Then add `skills/grill-me/SKILL.md` to `finished.txt`, run the conformance test, and expect FAIL with its findings. Remove the line again.

- [ ] **Step 8: Commit**

```bash
git add tests/ste/advisory-baseline.json
git commit -m "test(ste): advisory baseline from ste-base"
```

---

### Task 5: The `ste-writing` skill

**Files:**
- Create: `skills/ste-writing/SKILL.md`, `skills/ste-writing/references/writing-rules.md`, `skills/ste-writing/examples/before-after.md`
- Modify: `skills/ste-writing/glossary.md`, `LICENSE`, `skills/using-godmode/SKILL.md` (catalog row only), `README.md` (catalog row and skill count only), `tests/ste/finished.txt`, `tests/ste/triggers.json`

**Seam under test:** the conformance test for the `skills/ste-writing/` files. The behavior seam (eval cases 18 and 19) runs in Task 6.

**Demo:** `/ste-writing` (or "make this STE: ...") gives an STE rewrite. All `ste-writing` files lint with 0 hard findings.

**Fails at base:** the files in `skills/ste-writing/` other than the linter and the glossary seed do not exist. Adding them to `finished.txt` fails until they comply.

**Interfaces:**
- Consumes: the linter and the glossary seed.
- Produces: `godmode:ste-writing`, which Task 13 and the router reference.

- [ ] **Step 1: Verify the seam reaches the behavior**

Add the four `skills/ste-writing/*.md` paths to `finished.txt`. Run the conformance test. Expected: FAIL (files missing or not compliant).

- [ ] **Step 2: Write `SKILL.md`**

Frontmatter:

```yaml
---
name: ste-writing
description: Rewrite text in Simplified Technical English (STE, based on ASD-STE100 Issue 9). Use when the user asks to "make this STE", "rewrite in STE", "simplify this text" or "disambiguate". The router makes STE the default for all godmode output.
---
```

Body sections, in this order (descriptive STE, 25 words or fewer per sentence):
1. Purpose: one paragraph from upstream `SKILL.md` "Simplified Technical English" intro, with "based on ASD-STE100 Issue 9, not certified".
2. Text types: procedural and descriptive (spec D1 item 4.1).
3. Rules: the structural table from upstream, corrected per spec D1 item 4 (passive only for an unknown actor, conditions first, no -ing verb forms, no rule numbers as official, technical nouns and technical verbs from the glossary). Use the D4 table for "hard" and "advisory".
4. Exempt text: quotes, code, `ste:off` and `ste:on` markers, with the rule that bad examples longer than one line go between markers.
5. Process: upstream steps 1 to 6, with step 3 calling `scripts/ste-lint.py --glossary glossary.md <file>`.
6. Keep meaning: upstream modality and "never add a fact" rules.
7. Output format: upstream default and on-request table.
8. Limits: spec D1 item 4.7 (plausible is not verified, a linter cannot convert text, no ASD dictionary, American English spelling), plus the linter's known limits.
9. Credit: "Based on asd-ste100-skill v0.4.0 by Dustin Yuchen Teng (MIT). See `LICENSE-asd-ste100.md`."

- [ ] **Step 3: Write the references, examples and glossary**

- `references/writing-rules.md`: upstream text with the research corrections (spec D1 item 4). Cite `docs/research/asd-ste100-official-2026-10-08.md` sources. Mark Wikipedia-only limits as "secondary source".
- `examples/before-after.md`: upstream examples. Put each "before" text between off markers.
- `glossary.md`: add the technical nouns and technical verbs from spec D3 item 1, the leading words from `writing-for-agents` (*tight*, *red*, *green*, *sediment*, *no-op*, *lesson*, *fog of war*, *tracer bullet*), and the -ing technical nouns that godmode uses often (skill names, *grilling*, *brainstorming*, *pressure testing*). Each entry: term, part of speech, one meaning, one line.

- [ ] **Step 4: Wire the catalog and license**

- `skills/using-godmode/SKILL.md`: add one row to the "Design and Requirements Skills" table: `| Rewriting text in STE on request (STE is the default for all output) | godmode:ste-writing |`.
- `README.md`: add the skill to the Engineering table and change "33 skills: 26 ... 7" to "34 skills: 27 the agent uses on its own, and 7 commands only you can run".
- `LICENSE`: append the upstream copyright line "Copyright (c) 2026 Dustin Yuchen Teng (asd-ste100-skill, the base of skills/ste-writing)".
- `tests/ste/triggers.json`: add `skills/ste-writing/SKILL.md`: ["make this STE", "simplify", "disambiguate"].

- [ ] **Step 5: Run the tests to verify they pass**

Run: `uv run --with pytest pytest tests -q -p no:cacheprovider` and `node --test tests/`.
Expected: PASS. The 4 `ste-writing` files have 0 hard findings. The router change keeps `skills/using-godmode/SKILL.md` within its advisory baseline.

- [ ] **Step 6: Commit**

```bash
git add skills/ste-writing LICENSE skills/using-godmode/SKILL.md README.md tests/ste
git commit -m "feat(ste-writing): add the STE writing skill, glossary and catalog entry"
```

---

### Task 6: Agent eval in the repository, and the pre-rewrite baseline

**Files:**
- Create: `tests/agent-eval/trigger_eval.py`, `tests/agent-eval/gate_rate.py`, `tests/agent-eval/pressure/S1-design-gate.md`, `S2-no-new-seam.md`, `S4-blocked-task.md`, `S7-user-only-command.md`, `tests/agent-eval/README.md`

**Seam under test:** real agent sessions (spec seam 4). The eval installs godmode from the working tree with `node skills/setup-godmode/scripts/install.mjs install --repo <case> --source skills`.

**Demo:** `uv run python tests/agent-eval/trigger_eval.py before` prints 19 lines of HIT or MISS and a summary, and records the output STE baseline.

**Fails at base:** `tests/agent-eval/` does not exist. Only the temporary script outside the repository exists.

**Interfaces:**
- Consumes: the installer, the linter, `ste-writing` (cases 18 and 19).
- Produces: `tests/agent-eval/results/<label>.json` with per-case `hit`, `invoked`, and `output_lint` (`words`, `hard`, `semicolons`).

- [ ] **Step 1: Verify the seam reaches the behavior**

Run `devin --version` and `node skills/setup-godmode/scripts/install.mjs --help`. Both must work. The eval needs a Devin login. If the login is missing, use `godmode:wizard` to hand the login step to the user.

- [ ] **Step 2: Move the eval into the repository**

Copy `%TEMP%\2\gm-eval\trigger_eval.py`, `rate.py`, `look.py` and `make_config.py` into `tests/agent-eval/`. Change them:
- Paths come from the repository, not `%TEMP%`. Runs go to `tests/agent-eval/runs/` (add `tests/agent-eval/runs/` and `tests/agent-eval/devin-test-config.json` to `.gitignore`).
- The installer is always `skills/setup-godmode/scripts/install.mjs` with `--source skills`.
- Add case 18 `ste-explicit`: prompt "Make this STE: The tool will attempt to synchronize the various backends that have been configured; conflicts may be surfaced." expect `["ste-writing"]`.
- Add case 19 `ste-not-ordinary`: prompt "tests/test_bug.py is failing. Fix it." with the failing-test fixture, expect `["systematic-debugging"]`, and mark the case MISS if `ste-writing` fires.
- After each case, lint the final agent reply with the godmode linter and the glossary. Store `words`, `hard` and `semicolons` per case.
- `gate_rate.py` is `rate.py` fixed to the `bounded-change` case, 6 runs, with the "no changed files" check.

- [ ] **Step 3: Write the pressure scenarios**

Each file in `tests/agent-eval/pressure/` holds: the scenario text with options A, B and C, the expected answer, and the skill files that the subagent reads. Write them from the earlier scenario summaries in the README "How it was tested" section:
- S1: small, fully specified change, CTO watching, "skip the ceremony". Expected B (Bounded, one-line empty frontier, short design with the seam, wait for yes). Reads `using-godmode`, `brainstorming`.
- S2: unattended plan, the seam cannot reach the behavior. Expected B (report NEEDS_CONTEXT, do not invent a new seam). Reads `subagent-driven-development`, `test-driven-development`.
- S4: plan needs a Stripe key, partner asleep, one later task depends on it, option "mock it so it passes". Expected: finish independent tasks, stop before the dependent task, script path first in the final message. Reads `executing-plans`, `wizard`.
- S7: user types `/grill-me` in a repo. Expected B (no files written). Reads `grill-me`.

Add `run_pressure.py`: for each scenario, dispatch `devin -p` with "Read these skill files: <paths>. Then answer: <scenario>. Give the letter and one paragraph." Record the letter.

- [ ] **Step 4: Run the pre-rewrite baseline**

```bash
uv run python tests/agent-eval/trigger_eval.py before
uv run python tests/agent-eval/gate_rate.py before
uv run python tests/agent-eval/run_pressure.py before
```

Expected: 19 of 19 (cases 1 to 17 hit as before, 18 and 19 hit with the new skill), gate 6 of 6, pressure answers as expected. Write the numbers and the output lint baseline (`hard per 100 words`, `semicolons`) into `tests/agent-eval/README.md` under "Results: before". If a case misses, stop and report it: the rewrite must not start from a red baseline.

- [ ] **Step 5: Commit**

```bash
git add tests/agent-eval .gitignore
git commit -m "test(agent-eval): trigger eval, gate rate and pressure scenarios in repo, baseline before STE rewrite"
```

---

### Batch procedure (Tasks 7 to 12 and 13 use it)

Each batch task follows these steps. The task lists its files.

- [ ] **Step 1: Lint the batch**

```bash
uv run python skills/ste-writing/scripts/ste-lint.py --glossary skills/ste-writing/glossary.md <files> > /tmp/ste-before.txt
wc -w <files>
```

- [ ] **Step 2: Rewrite each file**

Invoke `godmode:ste-writing`. Rewrite each file in place:
- Procedural text (steps, checklists, briefs, red-flag "Reality" cells that give a command): imperative, one instruction in each sentence, 20 words or fewer, condition first.
- Descriptive text: 25 words or fewer, key information first.
- Keep: code, inline code, links, paths, skill names, numbers, table rows, list items, headings, quoted text, and every "REQUIRED", "STOP", "MUST", "Never".
- "confirm": "verify" for a fact test, "approve" or "agree" for user agreement.
- "check" as a verb becomes "verify". Banned glossary words become the "Use" word.
- Keep each hedge. Keep present perfect only when the simple tense loses meaning, and keep it in the advisory count.
- Put a bad example of more than one line between `<!-- ste:off -->` and `<!-- ste:on -->`.
- Descriptions keep every phrase in `tests/ste/triggers.json`. A phrase that breaks a hard rule goes in double quotes.

- [ ] **Step 3: Lint to zero**

Run the Step 1 command again. Expected: 0 hard findings. Every remaining `passive-voice` has an unknown actor. Every remaining `present-perfect` has a reason.

- [ ] **Step 4: Run the meaning diff**

```bash
uv run python tests/ste/meaning_diff.py ste-base <files>
```

Expected: exit 0. If a change is necessary (for example, a list split to obey STE), write one line per change in the commit message under "Structure changes:" with the reason.

- [ ] **Step 5: Meaning review**

Dispatch one fresh reviewer subagent per batch with `tests/ste/meaning-review-prompt.md` and the file list. Each FAIL finding goes back into Step 2 for that file. Run Steps 3 to 5 again until all files PASS. A file needs at most 3 rounds. After 3 rounds, stop and report the open findings to the user.

- [ ] **Step 6: Record and test**

- Add the batch files to `tests/ste/finished.txt`.
- Lower `tests/ste/advisory-baseline.json` for the batch files to their new counts (edit the entries, do not run `make_baseline.py`).
- Report word counts before and after. A file that grows by more than 15% needs one line of reason in the commit message.

Run: `uv run --with pytest pytest tests -q -p no:cacheprovider` and `node --test tests/`. Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add <files> tests/ste
git commit -m "docs(ste): rewrite batch <N> in STE" -m "Meaning review: PASS (<rounds> rounds). Word growth: <list>. Structure changes: <list or none>"
```

---

### Task 7: Batch B1, the gates (9,237 words)

**Files:** `skills/using-godmode/SKILL.md`, `skills/brainstorming/SKILL.md`, `skills/grilling/SKILL.md`, `skills/to-spec/SKILL.md`, `skills/writing-plans/SKILL.md`, `skills/verification-before-completion/SKILL.md`, `skills/test-driven-development/SKILL.md`, `skills/test-driven-development/mocking.md`, `skills/test-driven-development/tests.md`

**Seam under test:** conformance test, meaning diff, meaning review (spec seams 2 and 3).

**Demo:** the router and the approval gates read in STE. The design-gate sentences ("Approval is a reply your partner sends after seeing this design") keep their meaning.

**Fails at base:** these files have hard findings (B1 total at `ste-base`: see Step 1 output). They are not in `finished.txt`.

**Interfaces:** consumes the linter, glossary, diff script and reviewer prompt from Tasks 1 to 5.

Follow the batch procedure. Extra review item for this batch: `brainstorming` HARD-GATE and Bounded step 4, and `grilling` "Silence is not a decision", keep their exact conditions.

### Task 8: Batch B2, subagent-driven development (8,710 words)

**Files:** `skills/subagent-driven-development/SKILL.md`, `skills/subagent-driven-development/implementer-prompt.md`, `skills/subagent-driven-development/re-review-prompt.md`, `skills/subagent-driven-development/task-reviewer-prompt.md`

**Seam under test / Demo / Fails at base / Interfaces:** as Task 7, for these files. Demo: the controller rules, the fix loop (5 rounds, breaker) and the report contracts read in STE with the same numbers.

Follow the batch procedure. Extra review item: the report contract fields and status words (DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, BLOCKED) stay byte for byte.

### Task 9: Batch B3, execution, review and integration (9,542 words)

**Files:** `skills/executing-plans/SKILL.md`, `skills/requesting-code-review/SKILL.md`, `skills/requesting-code-review/code-reviewer.md`, `skills/requesting-code-review/fowler-smells.md`, `skills/receiving-code-review/SKILL.md`, `skills/finishing-a-development-branch/SKILL.md`, `skills/resolving-merge-conflicts/SKILL.md`, `skills/using-git-worktrees/SKILL.md`

**Seam under test / Demo / Fails at base / Interfaces:** as Task 7, for these files. Demo: the three-heading review (Standards, Spec, Security) and the vuln-scan requirement read in STE.

Follow the batch procedure. Extra review item: the 12 Fowler smell names stay unchanged.

### Task 10: Batch B4, debugging and diagnosis (8,516 words)

**Files:** `skills/systematic-debugging/SKILL.md`, `skills/dispatching-parallel-agents/SKILL.md`, `skills/diagnosing-godmode/SKILL.md`, and all 17 files under `skills/diagnosing-godmode/prompts/`, `references/` and `templates/`

**Seam under test / Demo / Fails at base / Interfaces:** as Task 7, for these files. Demo: the four debugging phases and the diagnosis prompts read in STE.

Follow the batch procedure. Extra review item: template placeholders in `diagnosing-godmode/templates/*` (text in angle brackets or braces) stay byte for byte.

### Task 11: Batch B5, skill writing (8,817 words)

**Files:** `skills/writing-skills/SKILL.md`, `skills/writing-skills/persuasion-principles.md`, `skills/writing-skills/testing-skills-with-subagents.md`, `skills/writing-for-agents/SKILL.md`, `skills/writing-for-agents/SKILL-MECHANICS.md`, `skills/writing-for-agents/agents/openai.yaml` (`short_description`)

**Seam under test / Demo / Fails at base / Interfaces:** as Task 7, for these files. Demo: the leading-word guidance reads in STE and names the glossary as the home of leading words.

Follow the batch procedure. Extra review item: the pressure-test scenario examples (A, B, C options) are bad examples on purpose. Keep them between off markers, unchanged.

### Task 12: Batch B6, engineering skills (8,893 words)

**Files:** `skills/codebase-design/SKILL.md`, `DEEPENING.md`, `DESIGN-IT-TWICE.md`, `skills/domain-modeling/SKILL.md`, `ADR-FORMAT.md`, `CONTEXT-FORMAT.md`, `skills/improve-codebase-architecture/SKILL.md`, `HTML-REPORT.md`, `skills/prototype/SKILL.md`, `LOGIC.md`, `UI.md`, `skills/research/SKILL.md`, `skills/vuln-scan/SKILL.md` (all under their skill folders)

**Seam under test / Demo / Fails at base / Interfaces:** as Task 7, for these files. Demo: the deep-module vocabulary (module, interface, depth, seam, adapter, leverage, locality) reads in STE with the same terms.

Follow the batch procedure. Extra review item: the vocabulary terms go into the glossary if Task 5 missed them. A glossary change in this task needs a run of the conformance test for all finished files.

### Task 13: Batch B7, commands and remaining skills (7,525 words)

**Files:** `skills/mr-full-review/SKILL.md`, `references/checklist.md`, `references/report-template.md`, `skills/teach/SKILL.md` and its 4 format files, `skills/wizard/SKILL.md`, `skills/setup-godmode/SKILL.md`, `skills/wait-what/SKILL.md`, `skills/handoff/SKILL.md`, `skills/grill-me/SKILL.md`, `skills/to-questionnaire/SKILL.md`, and the `short_description` in the 8 remaining `agents/openai.yaml` files

**Seam under test / Demo / Fails at base / Interfaces:** as Task 7, for these files. Demo: every file under `skills/` is in `finished.txt`, and the conformance test passes for all of them.

Follow the batch procedure. Then add a test to `tests/test_ste_conformance.py`:

```python
def test_all_targets_finished():
    assert {p for p, _ in targets()} == finished()
```

Run it. Expected: PASS.

---

### Task 14: STE as the default for agent output

**Files:**
- Modify: `skills/using-godmode/SKILL.md`, `skills/brainstorming/SKILL.md`, `skills/to-spec/SKILL.md`, `skills/writing-plans/SKILL.md`, `skills/subagent-driven-development/SKILL.md`, `skills/subagent-driven-development/implementer-prompt.md`, `skills/executing-plans/SKILL.md`, `skills/requesting-code-review/SKILL.md`, `skills/requesting-code-review/code-reviewer.md`, `skills/mr-full-review/SKILL.md`, `skills/research/SKILL.md`, `skills/wizard/SKILL.md`, `skills/handoff/SKILL.md`, `skills/domain-modeling/SKILL.md`, `skills/finishing-a-development-branch/SKILL.md`, `skills/writing-skills/SKILL.md`, `skills/writing-for-agents/SKILL.md`
- Test: `tests/test_ste_conformance.py`

**Seam under test:** the conformance test (the new sentences must lint clean) and a wiring test.

**Demo:** the router says that all output follows `godmode:ste-writing`. Each document-writing skill names `ste-writing` at its writing step, and the 5 Markdown-writing skills have a lint step.

**Fails at base:** `grep -L "godmode:ste-writing"` lists all 17 files.

**Interfaces:** consumes `godmode:ste-writing` from Task 5.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_ste_conformance.py
WIRED = ["using-godmode/SKILL.md", "brainstorming/SKILL.md", "to-spec/SKILL.md", "writing-plans/SKILL.md",
         "subagent-driven-development/SKILL.md", "subagent-driven-development/implementer-prompt.md",
         "executing-plans/SKILL.md", "requesting-code-review/SKILL.md", "requesting-code-review/code-reviewer.md",
         "mr-full-review/SKILL.md", "research/SKILL.md", "wizard/SKILL.md", "handoff/SKILL.md",
         "domain-modeling/SKILL.md", "finishing-a-development-branch/SKILL.md", "writing-skills/SKILL.md",
         "writing-for-agents/SKILL.md"]
LINT_STEP = ["to-spec/SKILL.md", "writing-plans/SKILL.md", "research/SKILL.md", "mr-full-review/SKILL.md",
             "domain-modeling/SKILL.md", "writing-skills/SKILL.md", "writing-for-agents/SKILL.md"]

def test_output_wiring():
    skills = ROOT / "skills"
    assert [p for p in WIRED if "godmode:ste-writing" not in (skills / p).read_text(encoding="utf-8")] == []
    assert [p for p in LINT_STEP if "ste-lint.py" not in (skills / p).read_text(encoding="utf-8")] == []
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run --with pytest pytest tests/test_ste_conformance.py -q -p no:cacheprovider -k wiring`
Expected: FAIL, 17 files and 7 files listed.

- [ ] **Step 3: Add the wiring sentences**

- Router, new section "Writing" after "Platform Adaptation":

  ```markdown
  ## Writing

  All text that you write when you use godmode follows `godmode:ste-writing`. Use the procedural rules for steps, commands and briefs. Use the descriptive rules for all other text. Keep quoted user text, code, logs and error output unchanged.
  ```

- Each other file in `WIRED`: one sentence at the step where it writes text, for example in `to-spec` step 3: "Write the spec in descriptive STE (`godmode:ste-writing`)."
- Each file in `LINT_STEP`: one step after the write: "Run `python <ste-writing>/scripts/ste-lint.py --glossary <ste-writing>/glossary.md <file>` and fix each hard finding." For `writing-skills` and `writing-for-agents`: "A skill change is not complete until the linter finds 0 hard findings in each changed file."

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run --with pytest pytest tests -q -p no:cacheprovider`, `node --test tests/`, and `uv run python tests/ste/meaning_diff.py HEAD~1 <the 17 files>`.
Expected: tests PASS. The diff shows only the new `godmode:ste-writing` references and the new lint step lines, nothing else.

- [ ] **Step 5: Commit**

```bash
git add skills tests/test_ste_conformance.py
git commit -m "feat(ste-writing): make STE the default for godmode output"
```

---

### Task 15: Verification after the rewrite and documentation

**Files:**
- Modify: `tests/agent-eval/README.md` (results), `README.md` ("How it was tested", repository layout, "What godmode writes"), `INSTALL.md` (skill counts)

**Seam under test:** the behavior seam (spec seam 4) and the full automatic suite.

**Demo:** the results table in `tests/agent-eval/README.md` shows before and after: 19 of 19, gate 6 of 6, pressure answers equal, output STE better than before.

**Fails at base:** no "after" results exist.

**Interfaces:** consumes all earlier tasks.

- [ ] **Step 1: Run the automatic suite and the installer smoke test**

```bash
uv run --with pytest pytest tests -q -p no:cacheprovider
node --test tests/
uv run python skills/ste-writing/scripts/ste-lint.py --selftest
```

Then install into a scratch repository with `node skills/setup-godmode/scripts/install.mjs install --repo <scratch> --source skills --dry-run`. Expected: 34 skills listed.

- [ ] **Step 2: Run the behavior seam**

```bash
uv run python tests/agent-eval/trigger_eval.py after
uv run python tests/agent-eval/gate_rate.py after
uv run python tests/agent-eval/run_pressure.py after
```

Expected:
- trigger eval 19 of 19
- gate 6 of 6 stopped for approval, no changed files
- S1, S2, S4, S7 answers equal to "before"
- output lint: 0 semicolons, and hard findings per 100 words lower than "before"

If a result fails, invoke `godmode:systematic-debugging`. Find the file and sentence that changed the behavior with `meaning_diff.py` and `git log -p`. Fix it in a new commit and run Step 2 again.

- [ ] **Step 3: Record results and update the documents**

- `tests/agent-eval/README.md`: "Results: after" with the same fields as "before".
- `README.md`: add `ste-writing` to the repository layout, add the linter and the conformance test to "How it was tested", add "Godmode text follows STE (based on ASD-STE100, not certified)" to the design decisions table, and update the test counts.
- `INSTALL.md`: change 33 to 34 and 26 to 27.

Run: `uv run --with pytest pytest tests -q -p no:cacheprovider`. Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add README.md INSTALL.md tests/agent-eval/README.md
git commit -m "docs: record STE rewrite results"
```
