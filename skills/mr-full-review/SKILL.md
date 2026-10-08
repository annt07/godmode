---
name: mr-full-review
description: Full, standard review of a merge request or pull request on GitLab, GitHub or Bitbucket. The skill finds the provider automatically. It does a check of the change against the ticket and its AC, a two-axis code review and a vulnerability scan. It also reviews tests, CI and hygiene. It writes the result to .scratch as a numbered review round. Read-only, never posts.
disable-model-invocation: true
---

# MR / PR Full Review

Run the phases below on one merge request (GitLab) or pull request (GitHub, Bitbucket Cloud, Bitbucket Server/Data Center). Write the report to `.scratch/` as the next numbered round. Each phase states its own gate. When a gate is not met, write `Skipped: <reason>` in the report. Do not leave the row out. Read `references/checklist.md` before Phase 6 and `references/report-template.md` before Phase 7.

**Read-only, always.** Never post comments, approve, change descriptions, push, or run `git checkout` in the working tree of the user. Put suggested comments in the report. The user posts them.

## Requirements

- A token for the detected provider, in the environment: `GITLAB_TOKEN`, `GITHUB_TOKEN` (or `GH_TOKEN`), or `BITBUCKET_TOKEN` (Bitbucket Cloud also accepts `BITBUCKET_USERNAME` + `BITBUCKET_APP_PASSWORD`). **Never read, print or test token variables yourself** (no `echo $GITLAB_TOKEN`, `$env:GITHUB_TOKEN`, `env`, `printenv`, `Get-ChildItem env:`). Their values would go into the transcript. Run `locate`, then `show`. The script reads the token itself. When a token is missing, the script names the variable and shows no value. Then tell the user which variable to set, and stop.
- Run in a local clone of the target repo. The script finds the repo of a bare number through `git remote get-url origin`.
- A host can have a name that does not show the provider (for example `git.corp.example`). For such a host, pass `--provider gitlab|github|bitbucket-cloud|bitbucket-server`, or tell the user to set `GODMODE_GIT_PROVIDERS="git.corp.example=gitlab"`.

All phases use the bundled script (`<S>` = the folder of this skill):

```bash
uv run python "<S>/scripts/review_request.py" locate    <ref>   # provider, host, project, number
uv run python "<S>/scripts/review_request.py" show      <ref>   # title, state, branches, draft, description
uv run python "<S>/scripts/review_request.py" comments  <ref>   # discussion + review/diff comments
uv run python "<S>/scripts/review_request.py" pipelines <ref>   # latest CI status (+ failed job log tails)
```

`<ref>` is a full MR/PR URL, or a number (`120`, `!120`, `#120`). Use only a reference that the user gave. Some agents add the argument of `/mr-full-review <ref>` to the end of the text of this skill, after the last edge case. Look there first. If there is no reference, ask for it. Do not guess or invent a number.

## Phase 0: Intake and scoping

1. **Resolve and fetch.** Run `locate`, `show` and `comments`. Record the provider, source and target branches, title, description, state, URL, draft flag and author.
2. **Ticket.** Match `[A-Z]{2,}-\d+` against the branch name, title and description, in that order. The first match wins. A "ticket" that is not a real issue (for example `UTF-8`) counts as no match. If you find a ticket, fetch its acceptance criteria, Definition of Done and comments. Use the Jira skill or MCP in the session (for example `jira-acli`, `jira-issue`). If you find no ticket or no Jira tool exists, record it and continue. Do not block.
3. **Review checkout, isolated.** Fetch both branches. Then give the review its own detached worktree outside the repo. Thus the checkout of the user never switches or changes:
   ```bash
   git fetch origin "<target>" "<source>"
   git worktree add --detach "<tmp>/godmode-review-<label>" "origin/<source>"
   ```
   (`<tmp>` = the system temp directory.) The fetch can fail (network, removed branch, fork without access). If it fails, record `local checkout: unavailable` and skip the worktree. Phases 2-4 then report `Skipped`. GitHub forks: fetch `pull/<n>/head`. Bitbucket and GitLab give similar refs (`refs/pull-requests/<n>/from`, `refs/merge-requests/<n>/head`).
4. **Size the diff:** `git diff --stat origin/<target>...origin/<source>`.
5. **Scope table** (it is the gate for each phase below). Record these items:
   - type (feature/bugfix/docs/refactor/config/chore/mixed)
   - size (small < 100 lines, large > 500 lines or > 20 files)
   - surfaces touched (backend/API, UI, infra/CI, DB/migration, docs, tests)
   - touches tests
   - security-sensitive (auth, secrets/config, crypto, permissions, network boundaries, dependency manifests, PHI/PII handling)
   - ticket, local checkout
   - CI configured (`.gitlab-ci.yml`, `.github/workflows/`, `bitbucket-pipelines.yml`, `Jenkinsfile`)
   - draft, multi-repo

   Large changes: review high-risk files in depth (auth, config, migrations, security-sensitive). Say in the report that the review covered only a sample.

   **Local-diff mode:** the user can mean "review my current changes" with no MR/PR. In that case, skip the provider fetch. Review `git diff` (or the given range) directly. Write "local-diff mode" in the report header.

## Phase 1: Requirements traceability

**Gate:** you found a ticket. Otherwise `Skipped: no ticket referenced in title, description or branch name.`

Compare each acceptance criterion and Definition-of-Done item, one at a time, with the actual diff. Do not compare it with the claims of the description. Use **Met / Not met / Met in intent, not literal text** (name the gap). Verify that the code contains the design decisions from ticket or MR/PR comments. An acknowledgement in a comment is not sufficient.

## Phase 2: Code review (two axes)

**Gate:** local checkout available.

Invoke `godmode:requesting-code-review` over `origin/<target>...origin/<source>`, and run it in the review worktree. The **spec** for its Spec axis is the acceptance criteria of the ticket plus the MR/PR description (and resolved review threads). The Standards axis uses the conventions of the repo. Add its Standards and Spec findings without change. Do not derive their severities again.

## Phase 3: Security (vuln-scan)

**Gate:** local checkout available. This phase runs for all changes, security-sensitive or not.

`requesting-code-review` already runs `godmode:vuln-scan` in review mode over the same range. Use its `## Security` section. If you skipped Phase 2 but a diff is available, run `godmode:vuln-scan` in review mode directly. If the scope table marks the change security-sensitive, verify that the scan covered those files, and state it in the report. This phase also covers secrets and dependency/licence changes (checklist C).

## Phase 4: Test coverage

**Gate:** local checkout available, and the change is not docs-only or config-only.

For each new or changed function or logic branch, verify that a test covers it. Give an approximate coverage delta (new logic lines vs. new or changed test lines), labelled approximate. For each gap, name the exact `file::function`. Also name the behaviour that the missing test should pin, not "add more tests".

## Phase 5: Live verification (optional)

**Gate:** both of these conditions are true:

- The repo has verification tooling that runs (for example a `run-*-job-local` / `check-*-status-local` skill or a documented local run).
- The change or its AC makes a runtime claim that the tooling can verify.

Otherwise `Skipped: no live-verifiable claim, or no local verification tooling.`

When this phase runs, run the tooling in the review worktree. Compare the real output with the claim.

## Phase 6: Hygiene and the remaining checklist

This phase always runs. Do sections F-M of `references/checklist.md`, each with its own gate. Highlights:
- **Description and title:** do they still agree with the diff? Quote old lines and give the corrected sentence.
- **Scope and churn:** unrelated files, churn that changes only formatting, generated files without an explanation.
- **CI:** run `pipelines <ref>`. On failure, read the log tails. Say whether this change caused it or it is an infra flake (runner, network, registry). GitHub Actions and GitLab give log tails. Bitbucket gives only status links, so write "open the failed build for logs" with its URL. Write `Unavailable` only if the command itself fails. `Skipped: no CI configuration in this repo` is a different, real gap.
- **CODEOWNERS / required approvals:** this skill does not read them. Write `Unavailable: check the <provider> UI`.

## Phase 7: Report

Fill `references/report-template.md`. Show each section, with `Skipped: <reason>` or "None found." where applicable.

**Where it goes:** `.scratch/<folder>/` at the repo root.

1. **Folder:** use again an existing `.scratch/` subfolder whose name contains the ticket key (case-insensitive). Else use one that contains `mr-<n>` / `pr-<n>`. Else use the source branch name. If no such folder exists, create `.scratch/<ticket-key-lowercase>-<short-slug>/`. If there is no ticket, create `.scratch/<mr|pr>-<n>-<short-slug>/`.
2. **Round number:** count the existing `<mr|pr>-<n>-review-round-*.md` files in that folder. This report is the next one (first review = round 1).
3. **File name:** `<mr|pr>-<n>-review-round-<N>.md` (GitLab uses `mr`, GitHub and Bitbucket use `pr`). Local-diff mode: `local-review-round-<N>.md` in the ticket or branch folder.
4. If this repo does not git-ignore `.scratch/`, still write the file. Tell the user, so that they can keep it out of commits.

In round 2 and later rounds, first read the previous round. Add a **Since round N-1** section to the report. In it, mark each earlier finding Fixed / Still open / No longer applicable, with evidence.

Show the verdict, the blocking findings and the report path in chat.

Write the report in descriptive STE (`godmode:ste-writing`). Keep quoted MR/PR text, code and log lines unchanged. After you write the report file, lint it: Run `python <ste-writing>/scripts/ste-lint.py --glossary <ste-writing>/glossary.md <file>`, where `<ste-writing>` is the folder of the `godmode:ste-writing` skill. Fix each hard finding.

## Phase 8: Cleanup

Remove the review worktree (`git worktree remove --force "<tmp>/godmode-review-<label>"`, then `git worktree prune`). Do this also when an earlier phase failed. This skill creates nothing else outside `.scratch/` and `.godmode/security/`.

## Edge cases

- **Multi-repo change** (submodule bump, companion MR/PR): review the diff of each reachable repo separately. Say which repo was not in scope.
- **Sensitive content in the diff** (leaked token, PHI): describe it. Do not quote it in the report.
- **Draft:** verdict "Not ready for a merge verdict: still a draft" instead of Approve/Request changes.
- **Merged or closed:** state it. Before you run all phases, ask whether the user wants a post-hoc review.
- **Provider MCP tools** (for example a GitLab MCP server) can add to the script when they are already authenticated. Do not block while you wait for them.
