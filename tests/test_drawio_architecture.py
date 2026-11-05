"""Tests for the drawio-architecture skill: wiring, frontmatter, examples.

Run: uv run --with pytest pytest tests/test_drawio_architecture.py -q
"""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "drawio-architecture"
SKILL_MD = SKILL / "SKILL.md"
EXAMPLES = sorted((SKILL / "examples").glob("*.drawio"))

# The examples ship publicly. They must show a fictitious system, never a real one.
BANNED = re.compile(r"okf|\bnpi\b|rate[_ ]?sheet|cxid|provider|contract|elevance|anthem|claim|ehap|"
                    r"hospital|\bhmo\b|fee schedule|surgery|revenue code", re.I)


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, "SKILL.md has no YAML frontmatter"
    return m.group(1)


def test_skill_files_exist():
    for rel in ["SKILL.md", "agents/openai.yaml", "references/house-style.md", "references/page-types.md",
                "scripts/drawio_kit.py", "scripts/check.py", "scripts/validate.py", "scripts/LICENSE-validate"]:
        assert (SKILL / rel).exists(), rel
    assert len(EXAMPLES) == 4, EXAMPLES


def test_frontmatter_name_matches_folder_and_is_user_only():
    fm = frontmatter(SKILL_MD.read_text(encoding="utf-8"))
    assert re.search(r"^name:\s*drawio-architecture\s*$", fm, re.M)
    assert re.search(r"^disable-model-invocation:\s*true\s*$", fm, re.M)
    assert "allow_implicit_invocation: false" in (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")


def test_listed_in_router_installer_and_eval_common():
    router = (ROOT / "skills" / "using-godmode" / "SKILL.md").read_text(encoding="utf-8")
    assert "`/drawio-architecture`" in router
    install = (ROOT / "skills" / "setup-godmode" / "scripts" / "install.mjs").read_text(encoding="utf-8")
    assert '"drawio-architecture"' in re.search(r"USER_ONLY = \[(.*?)\]", install).group(1)
    common = (ROOT / "tests" / "agent-eval" / "common.py").read_text(encoding="utf-8")
    assert '"drawio-architecture"' in common


def test_referenced_examples_exist():
    text = SKILL_MD.read_text(encoding="utf-8") + (SKILL / "references" / "page-types.md").read_text(encoding="utf-8")
    for name in re.findall(r"examples/([\w-]+\.drawio)", text):
        assert (SKILL / "examples" / name).exists(), name


def test_no_real_system_data():
    hits = []
    for f in [p for p in SKILL.rglob("*") if p.is_file() and p.suffix in {".md", ".drawio", ".py", ".yaml"}]:
        if f.name == "validate.py":
            continue
        text = f.read_text(encoding="utf-8")
        hits += [f"{f.name}: {m.group(0)}" for m in BANNED.finditer(text)]
        hits += [f"{f.name}: {n}" for n in re.findall(r"(?<![\d#.])\d{9,10}(?!\d)", text) if n != "1111111111"]
    assert not hits, hits


def test_examples_pass_check():
    run = subprocess.run([sys.executable, str(SKILL / "scripts" / "check.py"), *map(str, EXAMPLES)],
                         capture_output=True, text=True, encoding="utf-8")
    assert run.returncode == 0, run.stdout + run.stderr
    assert run.stdout.count("   OK") == len(EXAMPLES), run.stdout
