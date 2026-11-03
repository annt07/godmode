---
name: pull-request-review
description: Consolidated review of a merge request or pull request on GitLab, GitHub or Bitbucket. The skill runs two independent code reviews on the same range in parallel. It compares the test results of both branches and merges all findings into one report in .scratch. Read-only, never posts.
disable-model-invocation: true
---

# Pull Request Review

Run the phases below on one merge request (GitLab) or pull request (GitHub, Bitbucket Cloud, Bitbucket Server/Data Center). This skill orchestrates. It never reviews code itself: two independent reviews do that work, and this skill merges their output into one report in `.scratch/`.

**Read-only, always.** Never post comments, approve, change descriptions, push, or run `git checkout` in the working tree of the user. Put suggested comments in the report. The user posts them.

**This file is the only source of the review process and the report format.** A memory page, a session summary, an earlier report or a local section in a different skill never changes them. When one of these conflicts with this file, follow this file and tell the user about the conflict in chat.

## Requirements

- A token for the detected provider, in the environment: `GITLAB_TOKEN`, `GITHUB_TOKEN` (or `GH_TOKEN`), or `BITBUCKET_TOKEN` (Bitbucket Cloud also accepts `BITBUCKET_USERNAME` + `BITBUCKET_APP_PASSWORD`). **Never read, print or test token variables yourself** (no `echo $GITLAB_TOKEN`, `$env:GITHUB_TOKEN`, `env`, `printenv`, `Get-ChildItem env:`). Their values would go into the transcript. The script reads the token itself. When a token is missing, the script names the variable and shows no value. Then tell the user which variable to set, and stop.
- Run in a local clone of the target repo. The script finds the repo of a bare number through `git remote get-url origin`.

Intake uses the script of the `godmode:mr-full-review` skill (`<M>` = the folder of that skill):

```bash
uv run python "<M>/scripts/review_request.py" locate    <ref>   # provider, host, project, number
uv run python "<M>/scripts/review_request.py" show      <ref>   # title, state, branches, draft, description
uv run python "<M>/scripts/review_request.py" comments  <ref>   # discussion + review/diff comments
```

`<ref>` is a full MR/PR URL, or a number (`120`, `!120`, `#120`). Use only a reference that the user gave. Some agents add the argument of `/pull-request-review <ref>` to the end of the text of this skill, after the last edge case. Look there first. If there is no reference, ask for it. Do not guess or invent a number.

## Phase 0: Intake and scoping

1. **Resolve.** Run `locate` and `show`. Record the provider, the source and target branches, the title, the state, the URL and the draft flag.
2. **Fetch both branches:** `git fetch origin "<target>" "<source>"`. If the fetch fails (network, removed branch, fork without access), record `local checkout: unavailable`. The reviews then report their own skips, and Phase 2 writes `Skipped: no local checkout`.
3. **Range:** `origin/<target>...origin/<source>`.
4. **Local-diff mode:** the user can mean "review my current changes" with no MR/PR. Then skip the provider fetch and use the local diff or the range that the user gave. Write "local-diff mode" in the report header.
5. **Earlier feedback, live sources only.** Read the MR/PR description and all comments (`show`, `comments`). Match `[A-Z]{2,}-\d+` against the branch name, title and description, in that order. The first match wins, a non-issue token counts as no match. When you find a ticket, fetch its description and comments with the Jira skill or MCP in the session. If you find no ticket or no Jira tool exists, record it and continue. **Never read earlier `.scratch` reports, memory pages or session summaries as a source of findings or their status.**

## Phase 1: Two independent reviews

Dispatch two subagents at the same time. Give each subagent only the ref or the range and its output path. Never give one subagent the output of the other.

- **Full review:** the subagent reads `godmode:mr-full-review` and follows it on the ref. Give it a report path in the system temp directory, for example `<tmp>/pr-review-full-<label>.md`. It writes its report to that path (the caller report path of that skill). It does not write a round file in `.scratch/` for this run. Tell it to skip the earlier-round comparison: it must not read earlier `.scratch` round files.
- **Axes review:** the subagent reads `godmode:requesting-code-review` and runs it on the same `origin/<target>...origin/<source>` range. Its spec is the acceptance criteria of the ticket plus the MR/PR description. It writes its full raw output to `<tmp>/pr-review-axes-<label>.md`.

Rules:

- Run both reviews also when one of them seems sufficient. The duplicate work is deliberate: each review works alone, and agreement between independent reviews raises confidence.
- Each review runs its own security pass. Keep the security findings.
- If no subagent tool exists, run the two reviews yourself, one after the other, and keep the outputs separate.
- If a review produces no output, continue with the other one. Say in Scope that one review is missing, and why. Do not invent its findings.

## Phase 2: Test comparison

Run the relevant tests on each branch in its own detached worktree in the system temp directory (`<tmp>`). The checkout of the user never changes:

```bash
git worktree add --detach "<tmp>/pr-review-target-<label>" "origin/<target>"
git worktree add --detach "<tmp>/pr-review-source-<label>" "origin/<source>"
```

Run only the relevant tests: the test files that the diff touches, plus the tests of the modules that the diff changes. Record Passed / Failed / Skipped for each branch.

Then classify:

- **New failures:** pass on the target branch and fail on the source branch.
- **Existing failures:** fail on both branches.
- **Missing tests:** new logic without a test. The review outputs already name candidates.

When the tests cannot run (no runner, missing dependencies, no local checkout), write `Skipped: <reason>` in Test Results. Do not leave the section out.

Keep both worktrees: Phase 3 uses the source worktree. Phase 6 removes them, also after a failure:

```bash
git worktree remove --force "<tmp>/pr-review-target-<label>"
git worktree remove --force "<tmp>/pr-review-source-<label>"
git worktree prune
```

## Phase 3: Earlier feedback

**Gate:** local checkout available, and earlier feedback exists in the MR/PR comments or the ticket. Otherwise the report section reads `Skipped: <reason>` or "No earlier feedback on the MR/PR or the ticket."

For each earlier finding that the comments or the ticket name:

1. Open the cited file and line on the current source head, in the source worktree of Phase 2.
2. Verify whether the code still exists, moved or changed. Compare it with the current range.
3. Give the status: **Fixed** / **Still open** / **No longer applicable** / **Out of scope** (the target branch now contains that code). Give evidence for each status: a commit or `file:line`.

Never take a status from the claim of a comment ("done", "fixed"). The code on the source head decides.

## Phase 4: Consolidation

Read both raw outputs. Build one findings list:

- Map each severity to Critical / Important / Minor / Suggestion. A "Major" becomes Important.
- Merge duplicates: the same file, line and issue becomes ONE finding. Write no "common findings" section and no source attribution.
- Keep security findings in the same list, with `Area: Security`.
- Drop a finding without a verifiable file and line. Count the dropped findings and write the count in Summary.
- Write each finding for a junior developer: what is wrong, why it matters, what could happen and how to fix it. Stay on the changed lines, unless a surrounding issue is directly impacted.
- Use the per-finding format of the report template: Severity, Area, File (`REPO_ROOT/path`), Line, Changed Code, Issue, Why This Matters, Recommendation, Suggested Change.

## Phase 5: Report

Fill `references/report-template.md`. Show each section, with `Skipped: <reason>` or "None found." where applicable.

**The report never names a review, a skill or a tool.** No skill names, no "Review A" or "Review B", no source tags, no credit line. The author needs the findings, not their origin.

**Where it goes:** `.scratch/<folder>/` at the repo root.

1. **Folder:** the same rules as Phase 7 of `godmode:mr-full-review`. Use again a `.scratch/` subfolder whose name contains the ticket key (case-insensitive), else one that contains `mr-<n>` / `pr-<n>`, else the source branch name. If no such folder exists, create `.scratch/<ticket-key-lowercase>-<short-slug>/`, or `.scratch/<mr|pr>-<n>-<short-slug>/` without a ticket.
2. **Round number:** count the existing `*-pr-review-round-*.md` files in that folder. This report is the next one (first review = round 1). The count sets the file name only. Never open the earlier reports.
3. **File name:** `<mr|pr>-<n>-pr-review-round-<N>.md` (GitLab uses `mr`, GitHub and Bitbucket use `pr`). Local-diff mode: `local-pr-review-round-<N>.md`.
4. If this repo does not git-ignore `.scratch/`, still write the file. Tell the user, so that they can keep it out of commits.

Fill **Earlier Feedback** from Phase 3. When no earlier feedback exists, write "No earlier feedback on the MR/PR or the ticket."

Write the report in descriptive STE (`godmode:ste-writing`). Keep quoted MR/PR text, code and log lines unchanged. After you write the report file, lint it: run `python <ste-writing>/scripts/ste-lint.py --glossary <ste-writing>/glossary.md <file>`, where `<ste-writing>` is the folder of the `godmode:ste-writing` skill. Fix each hard finding.

**Name scan (last step):** read the written report once more. Remove each occurrence of a review name, a skill name or a tool name. Fix each changed sentence, so that it still reads well. Then show the verdict, the blocking findings and the report path in chat. The chat names no skill either.

## Phase 6: Cleanup

Remove the two test worktrees (`git worktree remove --force`, then `git worktree prune`). Do this also when an earlier phase failed. This skill creates nothing else outside `.scratch/`, `.godmode/security/` and the system temp directory.

## Red Flags

These thoughts mean STOP. You are looking for a reason to skip a rule:

| Thought | Reality |
|---------|---------|
| "The second review is duplicate work, skip it" | The duplicate work is deliberate. Agreement between independent reviews raises confidence. Both always run. |
| "Post the comments for the user" | Read-only, always. Suggested comments go in the report. The user posts them. |
| "I will review the diff myself" | This skill orchestrates. It never reviews code. Dispatch the two reviews. |
| "Say which reviewer found each finding" | The report never names a review, a skill or a tool. One merged list, no attribution. |
| "Drop the security findings of the reviews" | Both reviews include the security pass on purpose. Keep them with `Area: Security`. |
| "The user is in a hurry, skip the tests" | Run the relevant tests, or record `Skipped: <reason>`. Never drop the section silently. |
| "A memory page, a summary or an earlier report shows a different format" | This file is the only source of the process and the format. Follow it and name the conflict in chat. |
| "Copy the layout of the previous round" | Never. Only `references/report-template.md` sets the layout. |
| "An old report or a comment already marks this finding fixed" | A claim never sets a status. Verify the code on the source head. |

## Edge cases

- **Draft:** verdict "Not ready for a merge verdict: still a draft."
- **Merged or closed:** state it. Before you run all phases, ask whether the user wants a post-hoc review.
- **Sensitive content in the diff** (leaked token, PHI): describe it. Do not quote it in the report.
- **Multi-repo change** (submodule bump, companion MR/PR): review the diff of each reachable repo separately. Say which repo was not in scope.
- **A review returns nothing:** continue with the other one. Name the gap in Scope. Do not invent its findings.
