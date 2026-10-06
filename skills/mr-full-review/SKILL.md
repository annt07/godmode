---
name: mr-full-review
description: Full, standardized review of a merge request or pull request on GitLab, GitHub or Bitbucket (provider auto-detected) - ticket/AC cross-check, two-axis code review, vulnerability scan, tests, CI, hygiene - written to .scratch as a numbered review round. Read-only, never posts.
disable-model-invocation: true
---

# MR / PR Full Review

Run the phases below against one merge request (GitLab) or pull request (GitHub, Bitbucket Cloud, Bitbucket Server/Data Center), and write the report to `.scratch/` as the next numbered round. Every phase states its own gate: when a gate isn't met, write `Skipped: <reason>` in the report instead of leaving the row out. Read `references/checklist.md` before Phase 6 and `references/report-template.md` before Phase 7.

**Read-only, always.** Never post comments, approve, change descriptions, push, or check out branches in the user's working tree. Suggested comments go in the report for the user to post themselves.

## Requirements

- A token for the detected provider, in the environment: `GITLAB_TOKEN`, `GITHUB_TOKEN` (or `GH_TOKEN`), or `BITBUCKET_TOKEN` (Bitbucket Cloud also accepts `BITBUCKET_USERNAME` + `BITBUCKET_APP_PASSWORD`). **Never read, print or test token variables yourself** (no `echo $GITLAB_TOKEN`, `$env:GITHUB_TOKEN`, `env`, `printenv`, `Get-ChildItem env:`): their values would land in the transcript. Run `locate`, then `show`: the script reads the token itself, and when one is missing it names the variable without revealing anything. Then tell the user which variable to set, and stop.
- Run inside a local clone of the target repo. Bare numbers resolve through `git remote get-url origin`.
- Hosts whose name doesn't reveal the provider (e.g. `git.corp.example`): pass `--provider gitlab|github|bitbucket-cloud|bitbucket-server`, or have the user set `GODMODE_GIT_PROVIDERS="git.corp.example=gitlab"`.

The bundled script, used throughout (`<S>` = this skill's folder):

```bash
uv run python "<S>/scripts/review_request.py" locate    <ref>   # provider, host, project, number
uv run python "<S>/scripts/review_request.py" show      <ref>   # title, state, branches, draft, description
uv run python "<S>/scripts/review_request.py" comments  <ref>   # discussion + review/diff comments
uv run python "<S>/scripts/review_request.py" pipelines <ref>   # latest CI status (+ failed job log tails)
```

`<ref>` is a full MR/PR URL, or a number (`120`, `!120`, `#120`). Use only a reference the user actually gave. When invoked as `/mr-full-review <ref>`, some agents append the argument to the very end of this skill's text, after the last edge case: look there first. If there's none anywhere, ask for it; never guess or invent a number.

## Phase 0: Intake and scoping

1. **Resolve and fetch.** Run `locate`, `show` and `comments`. Note the provider, source and target branches, title, description, state, URL, draft flag and author.
2. **Ticket.** Match `[A-Z]{2,}-\d+` against the branch name, title and description, in that order; the first match wins. A "ticket" that doesn't resolve to a real issue (e.g. `UTF-8`) counts as no match. If found, fetch its acceptance criteria, Definition of Done and comments with the Jira skill or MCP available in the session (e.g. `jira-acli`, `jira-issue`). If none is found or no Jira tool exists, record it and move on; never block.
3. **Review checkout, isolated.** Fetch both branches, then give the review its own detached worktree outside the repo, so the user's checkout is never switched or modified:
   ```bash
   git fetch origin "<target>" "<source>"
   git worktree add --detach "<tmp>/godmode-review-<label>" "origin/<source>"
   ```
   (`<tmp>` = the system temp directory.) If the fetch fails (network, deleted branch, fork without access), record `local checkout: unavailable` and skip the worktree; Phases 2-4 then report `Skipped`. GitHub forks: fetch `pull/<n>/head`; Bitbucket and GitLab expose similar refs (`refs/pull-requests/<n>/from`, `refs/merge-requests/<n>/head`).
4. **Size the diff:** `git diff --stat origin/<target>...origin/<source>`.
5. **Scope table** (gates every phase below): type (feature/bugfix/docs/refactor/config/chore/mixed), size (small < 100 lines, large > 500 lines or > 20 files), surfaces touched (backend/API, UI, infra/CI, DB/migration, docs, tests), touches tests, security-sensitive (auth, secrets/config, crypto, permissions, network boundaries, dependency manifests, PHI/PII handling), ticket, local checkout, CI configured (`.gitlab-ci.yml`, `.github/workflows/`, `bitbucket-pipelines.yml`, `Jenkinsfile`), draft, multi-repo.

   Large changes: review high-risk files in depth (auth, config, migrations, security-sensitive) and say in the report that coverage was sampled.

   **Local-diff mode:** if the user means "review my current changes" with no MR/PR, skip the provider fetch, review `git diff` (or the given range) directly, and say "local-diff mode" in the report header.

## Phase 1: Requirements traceability

**Gate:** a ticket was found. Otherwise `Skipped: no ticket referenced in title, description or branch name.`

Walk every acceptance criterion and Definition-of-Done item individually against the actual diff, not against the description's claims: **Met / Not met / Met in intent, not literal text** (name the gap). Check that design decisions settled in ticket or MR/PR comments are reflected in the code, not just acknowledged.

## Phase 2: Code review (two axes)

**Gate:** local checkout available.

Invoke `godmode:requesting-code-review` over `origin/<target>...origin/<source>`, run inside the review worktree. The **spec** for its Spec axis is the ticket's acceptance criteria plus the MR/PR description (and resolved review threads); the Standards axis uses the repo's own conventions. Fold its Standards and Spec findings in as-is: don't re-derive their severities.

## Phase 3: Security (vuln-scan)

**Gate:** local checkout available. Runs regardless of the security-sensitive flag.

`requesting-code-review` already runs `godmode:vuln-scan` in review mode over the same range; use its `## Security` section. If Phase 2 was skipped but a diff is available, run `godmode:vuln-scan` in review mode directly. When the scope table flagged the change security-sensitive, confirm in the report that the scan covered those files. This phase also covers secrets and dependency/licence changes (checklist C).

## Phase 4: Test coverage

**Gate:** local checkout available, and the change isn't docs-only or config-only.

For each new or changed function or logic branch, check that a test covers it. Give an approximate coverage delta (new logic lines vs. new or changed test lines), labelled approximate. For gaps, name the exact `file::function` and the behaviour the missing test should pin, not "add more tests".

## Phase 5: Live verification (optional)

**Gate:** the repo has runnable verification tooling (for example a `run-*-job-local` / `check-*-status-local` skill or a documented local run) **and** the change or its AC makes a runtime claim that tooling can check. Otherwise `Skipped: no live-verifiable claim, or no local verification tooling.`

When it runs, execute against the review worktree and compare real output with the claim.

## Phase 6: Hygiene and the remaining checklist

Always runs: work through `references/checklist.md` sections F-M, each with its own gate. Highlights:
- **Description and title:** do they still match the diff? Quote stale lines and give the corrected sentence.
- **Scope and churn:** unrelated files, formatting-only churn, unexplained generated files.
- **CI:** run `pipelines <ref>`. On failure, read the log tails and say whether this change caused it or it's an infra flake (runner, network, registry). GitHub Actions and GitLab give log tails; Bitbucket gives status links only, so say "open the failed build for logs" with its URL. `Unavailable` only if the command itself errors; `Skipped: no CI configuration in this repo` is a different, real gap.
- **CODEOWNERS / required approvals:** not read here. Write `Unavailable: check the <provider> UI`.

## Phase 7: Report

Fill `references/report-template.md`. Every section renders, with `Skipped: <reason>` or "None found." where appropriate.

**Where it goes:** `.scratch/<folder>/` at the repo root.

1. **Folder:** reuse an existing `.scratch/` subfolder whose name contains the ticket key (case-insensitive), else one containing `mr-<n>` / `pr-<n>`, else the source branch name. If none exists, create `.scratch/<ticket-key-lowercase>-<short-slug>/`, or `.scratch/<mr|pr>-<n>-<short-slug>/` when there's no ticket.
2. **Round number:** count existing `<mr|pr>-<n>-review-round-*.md` files in that folder; this report is the next one (first review = round 1).
3. **File name:** `<mr|pr>-<n>-review-round-<N>.md` (GitLab uses `mr`, GitHub and Bitbucket use `pr`). Local-diff mode: `local-review-round-<N>.md` in the ticket or branch folder.
4. If `.scratch/` isn't git-ignored in this repo, still write the file, and tell the user so they can keep it out of commits.

In round 2 onward, read the previous round first and add a **Since round N-1** section to the report: each earlier finding marked Fixed / Still open / No longer applicable, with evidence.

Print the verdict, the blocking findings and the report path in chat.

## Phase 8: Cleanup

Remove the review worktree (`git worktree remove --force "<tmp>/godmode-review-<label>"`, then `git worktree prune`). Do this even when an earlier phase failed. Nothing else was created outside `.scratch/` and `.godmode/security/`.

## Edge cases

- **Multi-repo change** (submodule bump, companion MR/PR): review each reachable repo's diff separately; say which wasn't in scope.
- **Sensitive content in the diff** (leaked token, PHI): describe it, never quote it in the report.
- **Draft:** verdict "Not ready for a merge verdict: still a draft" instead of Approve/Request changes.
- **Merged or closed:** state it, and ask whether a post-hoc review is wanted before running everything.
- **Provider MCP tools** (e.g. a GitLab MCP server) may supplement the script when already authenticated; never block waiting on them.
