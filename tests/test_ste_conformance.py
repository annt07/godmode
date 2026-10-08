"""Conformance seam: every agent-read text unit under skills/ follows the godmode STE rules.

Files listed in tests/ste/finished.txt must have 0 hard findings. Advisory counts must not
rise above tests/ste/advisory-baseline.json (recorded from the ste-base tag). Descriptions
must keep the trigger phrases in tests/ste/triggers.json.
Run: uv run --with pytest pytest tests -q -p no:cacheprovider
"""
import importlib.util
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ste_lint", ROOT / "skills/ste-writing/scripts/ste-lint.py")
sl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sl)
STE = ROOT / "tests/ste"
HARD = {"semicolon", "long-sentence", "phrasal-verb", "nominalization", "marketing-adjective",
        "synonym-rotation", "dangling-conjunction", "check-verb", "glossary-word", "ste-off-unclosed"}
ADVISORY = {"passive-voice", "present-perfect"}
GLOSSARY = sl.load_glossary(ROOT / "skills/ste-writing/glossary.md")


def targets():
    """(repo-relative path, text) for every agent-read text unit."""
    for p in sorted((ROOT / "skills").rglob("*.md")):
        if p.name.startswith("LICENSE"):
            continue  # legal text stays verbatim
        yield p.relative_to(ROOT).as_posix(), p.read_text(encoding="utf-8")
    for p in sorted((ROOT / "skills").rglob("agents/openai.yaml")):
        m = re.search(r"^\s*short_description:\s*(.+)$", p.read_text(encoding="utf-8"), re.M)
        if m:
            yield p.relative_to(ROOT).as_posix(), f"---\ndescription: {m.group(1).strip()}\n---\n"


def finished():
    f = STE / "finished.txt"
    return {l.strip() for l in f.read_text().splitlines() if l.strip()} if f.exists() else set()


def lint(text, path):
    return sl.lint(text, path, glossary=GLOSSARY)[0]


def test_finished_files_have_no_hard_findings():
    done, bad = finished(), {}
    for path, text in targets():
        if path in done:
            hard = [f"{f['line']}:{f['rule']}:{f['match']}" for f in lint(text, path) if f["rule"] in HARD]
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
            limit = base.get(path, {}).get(r, 0)
            if n > limit:
                over[f"{path}:{r}"] = (n, limit)
    assert not over, over


def test_descriptions_keep_trigger_phrases():
    triggers = json.loads((STE / "triggers.json").read_text(encoding="utf-8"))
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


def test_all_targets_finished():
    assert {p for p, _ in targets()} == finished()
