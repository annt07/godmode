"""Tests for the pull-request-review skill: wiring, frontmatter and report template.

Run: uv run --with pytest pytest tests/test_pull_request_review.py -q
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "pull-request-review"
SKILL_MD = SKILL / "SKILL.md"
TEMPLATE = SKILL / "references" / "report-template.md"

# The consolidated report must never name a skill, review or tool. Word-boundary
# matching, so ordinary words ("a review", "review asks") do not count.
BANNED = ["mr-full-review", "requesting-code-review", "vuln-scan", "godmode",
          "review a", "review b"]


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, "SKILL.md has no YAML frontmatter"
    return m.group(1)


def test_skill_files_exist():
    assert SKILL_MD.exists(), "skills/pull-request-review/SKILL.md missing"
    assert TEMPLATE.exists(), "references/report-template.md missing"
    assert (SKILL / "agents" / "openai.yaml").exists(), "agents/openai.yaml missing"


def test_frontmatter_name_matches_folder_and_is_user_only():
    fm = frontmatter(SKILL_MD.read_text(encoding="utf-8"))
    assert re.search(r"^name:\s*pull-request-review\s*$", fm, re.M)
    assert re.search(r"^disable-model-invocation:\s*true\s*$", fm, re.M)
    assert re.search(r"^description:\s*\S", fm, re.M)


def test_openai_yaml_blocks_implicit_invocation():
    text = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
    assert "allow_implicit_invocation: false" in text


def test_listed_in_router_installer_and_eval_common():
    router = (ROOT / "skills" / "using-godmode" / "SKILL.md").read_text(encoding="utf-8")
    assert "`/pull-request-review`" in router

    install = (ROOT / "skills" / "setup-godmode" / "scripts" / "install.mjs").read_text(encoding="utf-8")
    user_only = re.search(r"USER_ONLY = \[(.*?)\]", install).group(1)
    assert '"pull-request-review"' in user_only
    # The bootstrap block's user-only line is rendered from USER_ONLY.
    assert "USER_ONLY.map" in install

    common = (ROOT / "tests" / "agent-eval" / "common.py").read_text(encoding="utf-8")
    assert '"pull-request-review"' in common


def test_template_has_no_banned_names():
    text = TEMPLATE.read_text(encoding="utf-8").lower()
    hits = [n for n in BANNED if re.search(rf"\b{re.escape(n)}\b", text)]
    assert not hits, hits


def test_template_sections_in_order():
    text = TEMPLATE.read_text(encoding="utf-8")
    sections = ["# Pull Request Review Report", "## Summary", "## Scope",
                "## Test Results", "## Findings", "## Missing Tests",
                "## Earlier Feedback", "## Recommendation", "## Summary For Author"]
    pos = [text.find(s) for s in sections]
    missing = [s for s, p in zip(sections, pos) if p == -1]
    assert not missing, missing
    assert pos == sorted(pos)


def test_full_review_writes_report_to_a_caller_path():
    """The orchestrator collects the review report at a given path, not .scratch."""
    text = (ROOT / "skills" / "mr-full-review" / "SKILL.md").read_text(encoding="utf-8").lower()
    assert "caller" in text and "report path" in text


def test_full_review_can_skip_earlier_round_check():
    """The orchestrator tells the full-review subagent to skip .scratch round files."""
    text = (ROOT / "skills" / "mr-full-review" / "SKILL.md").read_text(encoding="utf-8").lower()
    assert re.search(r"caller\b[^.]{0,80}skip", text, re.S)


def test_skill_file_is_the_only_source_of_the_format():
    """No memory page, summary, earlier report or foreign skill section overrides it."""
    text = SKILL_MD.read_text(encoding="utf-8").lower()
    assert "only source" in text
    assert "memory" in text


def test_no_earlier_report_as_finding_source():
    text = SKILL_MD.read_text(encoding="utf-8").lower()
    assert "read the previous round" not in text
    assert "never read earlier" in text


def test_earlier_feedback_uses_live_sources():
    text = SKILL_MD.read_text(encoding="utf-8")
    assert "comments" in text
    assert "jira" in text.lower() or "ticket" in text.lower()


def test_template_has_earlier_feedback_not_since_round():
    text = TEMPLATE.read_text(encoding="utf-8")
    assert "## Earlier Feedback" in text
    assert "since round" not in text.lower()


def test_router_rejects_plain_words_invocation():
    text = (ROOT / "skills" / "using-godmode" / "SKILL.md").read_text(encoding="utf-8").lower()
    assert "plain words" in text
    assert "to run it" in text
