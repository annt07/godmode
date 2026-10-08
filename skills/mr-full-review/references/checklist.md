# MR/PR review checklist

Phase 6 of `SKILL.md` reads this file for sections F-M. Sections A-E have their own phases. This file lists them only to be complete. Do not run them again in Phase 6. Each item states when it applies. When it does not apply, the checklist row in the report reads `Skipped: <reason>`. Do not omit the row.

## A. Requirements traceability *(Phase 1)*

- Verify each acceptance criterion against the diff. **Applies when:** a ticket is linked. **Skip reason:** "no ticket referenced in title, description or branch name."
- Verify each Definition-of-Done item. Keep "met in intent, not literal text" separate from "met".
- The code contains the decisions from ticket or MR/PR comments. **Applies when:** the ticket or MR/PR has discussion in addition to its description.

## B. Correctness and design quality *(Phase 2, `requesting-code-review`)*

- Standards axis (design, smells, tests, conventions) and Spec axis (does it do what the ticket and description promise). **Applies when:** the fetch of the source branch succeeded. **Skip reason:** "no local checkout available."

## C. Security *(Phase 3, `vuln-scan` in review mode)*

- Injection, unsafe deserialization, authn/authz, secrets, PHI/PII exposure, SSRF, crypto/TLS, LLM/agent risks, dependency and licence changes. **Applies when:** the fetch of the source branch succeeded. **Escalate when:** Phase 0 marked the change security-sensitive. Then verify that the scan covered those files. Do not trust a clean result.

## D. Test coverage *(Phase 4)*

- New or changed logic has a new or updated test. **Applies when:** not docs-only or config-only. **Skip reason:** "docs-only or config-only change, no new logic."
- Approximate coverage delta (new logic lines vs. new/changed test lines), labelled approximate.
- Each gap names `file::function` and the behaviour that the missing test should pin.

## E. Live verification *(Phase 5)*

- Run it, or verify real data. Do not only read code and assume. **Applies when:** the repo has verification tooling that runs AND the change makes a runtime claim that the tooling can verify. **Skip reason:** "no live-verifiable claim, or no local verification tooling."

## F. Description and title

- The description still agrees with the current diff. Quote old lines and give the corrected sentence.
- The title identifies the change without the need to open the diff.
- The ticket reference is present (compare with the detection of Phase 0).
- Screenshots or other evidence for changes that show in the UI. **Applies when:** UI touched. **Skip reason:** "no UI surface touched."

## G. Commits and branch

- Commits are atomic and descriptive, not one "fix stuff" commit for many concerns.
- The branch name follows the convention of the repo. If you are not sure, verify some recently merged MRs/PRs.
- No unresolved conflicts. The branch is not so far behind the target that a merge becomes risky.

## H. Scope and churn

- Diff size and shape agree with the stated purpose. Flag scope creep.
- Unrelated churn: changes that touch only formatting in files that the change does not otherwise touch, lockfile or build-artifact noise without an explanation.

## I. Breaking changes and compatibility

- API, schema and contract changes are backward compatible with existing callers, or the change states the break clearly.
- Data migrations are reversible, and they include the backfills.
- The version bump is present where the convention of the repo requires it.
- Feature flag or rollback path for risky changes. **Applies when:** the change touches a surface that changes behaviour (not docs/tests/config only).

## J. Operational readiness

- CI status from `review_request.py pipelines <ref>`. On failure, read the log tails (GitLab, GitHub Actions) or open the failed build URL (Bitbucket). Say whether the failure comes from this diff or is an infra flake. No CI configuration in the repo is a different row: `Skipped: no CI configuration in this repo`. Use `Unavailable` only when the command itself fails.
- CODEOWNERS and required approvals: `Unavailable: check the <provider> UI`.
- A review of the deployment or infra configuration for the target environment. **Applies when:** infra/CI touched.

## K. Dependencies and documentation

- New or updated dependencies are necessary and licence-compatible. Phase 3 usually covers this. Add only what it missed.
- README or docs updated for changes in user-facing behaviour.
- CHANGELOG entry where the convention of the repo requires one.

## L. UI and accessibility

- Alt text, label associations, contrast, keyboard navigation, responsive layout for new or changed UI. **Applies when:** UI touched. **Skip reason:** "no UI surface touched."

## M. Dead code and debug leftovers

- Leftover `print` / `console.log` / debugger statements that no debug flag controls.
- Commented-out code without an explanation.
- TODOs without a ticket reference.
