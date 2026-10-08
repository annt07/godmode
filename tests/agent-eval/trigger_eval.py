"""Trigger eval: does the right godmode skill fire for real user phrases? (19 cases)

Usage: python tests/agent-eval/trigger_eval.py LABEL [case-id ...]
Writes tests/agent-eval/results/trigger-LABEL.json and prints one line per case.
A case is a HIT when an expected skill fired, no user-only command fired, no forbidden
skill fired, and (for design-gate cases) no file changed.
"""
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import common as c

GATE = {"bounded-change", "new-feature", "design-seam"}
CASES = [
    # id, expected (any), prompt, fixture, forbidden
    ("review-branch", ["requesting-code-review"], "Act like an independent reviewer who is an expert senior software developer, review the changes on this branch against main.", c.branch_with_change, []),
    ("review-unstaged", ["requesting-code-review"], "Consider yourself an independent reviewer: review the unstaged changes and tell me the final review.", c.unstaged_change, []),
    ("research-web", ["research"], "Surf the internet and find out what HCPCS code G0121 is for. Write it down to a markdown file.", None, []),
    ("push-rebase", ["finishing-a-development-branch"], "Push the changes to remote, and if required rebase this branch on top of the latest origin main first.", c.remote_branch, []),
    ("debug-failing", ["systematic-debugging"], "tests/test_bug.py is failing. Fix it.", c.failing_test, []),
    ("bounded-change", ["brainstorming"], "Add an optional discount_percent argument to invoice_total, default 0, applied to the total, must be 0-100 else ValueError. That is the whole spec.", None, []),
    ("new-feature", ["brainstorming"], "We need gift cards in the shop.", None, []),
    ("design-seam", ["codebase-design"], "checkout() calls Stripe directly and can't be tested. How should the module boundary look so it's testable? Design only, no code.", None, []),
    ("terminology", ["domain-modeling"], "'account' means both the login user and the billing customer here. Sort out the terminology.", None, []),
    ("mr-comments", ["receiving-code-review"], "The reviewer commented on my MR: 'invoice_total should swallow all exceptions and return 0'. Analyse the comment and proceed.", None, []),
    ("spike", ["prototype"], "Quick and dirty: is it feasible to switch invoice totals to the decimal module without changing callers? Spike it.", None, []),
    ("refactor-scan", ["improve-codebase-architecture"], "Find refactoring opportunities that would make this codebase more testable. (List files with git ls-files.)", None, []),
    ("credentials", ["wizard"], "I need STRIPE_SECRET_KEY in .env and as a GitHub Actions secret. Walk me through setting it up.", None, []),
    ("isolated-work", ["using-git-worktrees", "brainstorming"], "Start work on the gift-card feature in an isolated workspace so main stays clean.", None, []),
    ("review-security", ["vuln-scan"], "Review the changes on this branch against main before I merge.", c.branch_with_change, []),
    ("review-mr-number", ["requesting-code-review"], "Act like an independent reviewer who is an expert senior software developer, review the changes on this branch; this is what MR 46 will contain.", c.branch_with_change, []),
    ("agents-doc", ["writing-for-agents"], "Update AGENTS.md to document that we always run uv run pytest before pushing.", c.agents_md, []),
    ("ste-explicit", ["ste-writing"], "Make this STE: The tool will attempt to synchronize the various backends that have been configured; conflicts may be surfaced.", None, []),
    ("ste-not-ordinary", ["systematic-debugging"], "tests/test_bug.py is failing. Fix it.", c.failing_test, ["ste-writing"]),
]


def run_case(label, case):
    cid, expect, prompt, fixture, forbidden = case
    path = c.make_repo(c.RUNS / label / cid, fixture)
    export, secs = c.run_session(path, prompt)
    invoked = c.invoked_skills(export)
    user_only = sorted(c.USER_ONLY & set(invoked))
    bad = sorted(set(forbidden) & set(invoked))
    changed = c.changed_files(path) if cid in GATE else []
    hit = bool(export) and any(s in invoked for s in expect) and not user_only and not bad and not changed
    notes = [f"user-only fired {user_only}"] * bool(user_only) + [f"forbidden {bad}"] * bool(bad) \
        + [f"gate broken {changed}"] * bool(changed) + ["no export"] * (not export)
    out = dict(id=cid, expect=expect, invoked=invoked, hit=hit, notes=notes, seconds=secs,
               output_lint=c.lint_reply(c.final_reply(export)))
    print(f"[{'HIT ' if hit else 'MISS'}] {cid:18} got={invoked} {' '.join(notes)} ({secs}s)", flush=True)
    return out


def main(argv):
    label, only = argv[0], set(argv[1:])
    todo = [k for k in CASES if not only or k[0] in only]
    with ThreadPoolExecutor(int(os.environ.get("PAR", "5"))) as ex:
        results = list(ex.map(lambda k: run_case(label, k), todo))
    words = sum(r["output_lint"]["words"] for r in results)
    hard = sum(r["output_lint"]["hard"] for r in results)
    summary = dict(label=label, hits=sum(r["hit"] for r in results), cases=len(results),
                   output_words=words, output_hard=hard,
                   output_hard_per_100_words=round(hard * 100 / words, 2) if words else 0.0,
                   output_semicolons=sum(r["output_lint"]["semicolons"] for r in results))
    c.RESULTS.mkdir(exist_ok=True)
    (c.RESULTS / f"trigger-{label}.json").write_text(json.dumps(dict(summary=summary, results=results), indent=1))
    print(json.dumps(summary))
    return 0 if summary["hits"] == summary["cases"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
