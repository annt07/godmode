# MR/PR review checklist

Read by Phase 6 of `SKILL.md` for sections F-M (A-E have their own phases and are listed here for completeness; don't re-run them in Phase 6). Every item states when it applies. When it doesn't, the checklist row in the report reads `Skipped: <reason>`; it is never omitted.

## A. Requirements traceability *(Phase 1)*

- Each acceptance criterion checked against the diff. **Applies when:** a ticket is linked. **Skip reason:** "no ticket referenced in title, description or branch name."
- Each Definition-of-Done item checked, with "met in intent, not literal text" kept separate from "met".
- Decisions settled in ticket or MR/PR comments are reflected in the code. **Applies when:** the ticket or MR/PR has discussion beyond its description.

## B. Correctness and design quality *(Phase 2, `requesting-code-review`)*

- Standards axis (design, smells, tests, conventions) and Spec axis (does it do what the ticket and description promise). **Applies when:** the source branch fetched. **Skip reason:** "no local checkout available."

## C. Security *(Phase 3, `vuln-scan` in review mode)*

- Injection, unsafe deserialization, authn/authz, secrets, PHI/PII exposure, SSRF, crypto/TLS, LLM/agent risks, dependency and licence changes. **Applies when:** the source branch fetched. **Escalate when:** Phase 0 flagged the change security-sensitive: confirm the scan covered those files instead of trusting a clean result.

## D. Test coverage *(Phase 4)*

- New or changed logic has a new or updated test. **Applies when:** not docs-only or config-only. **Skip reason:** "docs-only or config-only change, no new logic."
- Approximate coverage delta (new logic lines vs. new/changed test lines), labelled approximate.
- Each gap names `file::function` and the behaviour the missing test should pin.

## E. Live verification *(Phase 5)*

- Run it, or check real data, instead of reading code and assuming. **Applies when:** the repo has runnable verification tooling AND the change makes a runtime claim it can check. **Skip reason:** "no live-verifiable claim, or no local verification tooling."

## F. Description and title

- The description still matches the current diff: quote stale lines and give the corrected sentence.
- The title identifies the change without opening the diff.
- The ticket reference is present (compare with Phase 0's detection).
- Screenshots or other evidence for UI-visible changes. **Applies when:** UI touched. **Skip reason:** "no UI surface touched."

## G. Commits and branch

- Commits are atomic and descriptive, not one "fix stuff" commit for several concerns.
- The branch name follows the repo's convention (check a few recently merged MRs/PRs if unsure).
- No unresolved conflicts; the branch isn't so far behind the target that merging gets risky.

## H. Scope and churn

- Diff size and shape match the stated purpose; flag scope creep.
- Unrelated churn: formatting-only changes to untouched files, unexplained lockfile or build-artifact noise.

## I. Breaking changes and compatibility

- API, schema and contract changes are backward compatible with existing callers, or the break is called out.
- Data migrations are reversible, with backfills accounted for.
- Version bump applied where the repo's convention requires it.
- Feature flag or rollback path for risky changes. **Applies when:** a behaviour-changing surface is touched (not docs/tests/config only).

## J. Operational readiness

- CI status from `review_request.py pipelines <ref>`. On failure, read the log tails (GitLab, GitHub Actions) or open the failed build URL (Bitbucket), and say whether the failure comes from this diff or is an infra flake. No CI configuration in the repo at all is a different row: `Skipped: no CI configuration in this repo`. Use `Unavailable` only when the command itself errors.
- CODEOWNERS and required approvals: `Unavailable: check the <provider> UI`.
- Deployment or infra configuration reviewed for the target environment. **Applies when:** infra/CI touched.

## K. Dependencies and documentation

- New or updated dependencies are necessary and licence-compatible (Phase 3 usually covers this; add only what it missed).
- README or docs updated for user-facing behaviour changes.
- CHANGELOG entry where the repo's convention requires one.

## L. UI and accessibility

- Alt text, label associations, contrast, keyboard navigation, responsive layout for new or changed UI. **Applies when:** UI touched. **Skip reason:** "no UI surface touched."

## M. Dead code and debug leftovers

- Leftover `print` / `console.log` / debugger statements not behind a debug flag.
- Commented-out code without explanation.
- TODOs without a ticket reference.
