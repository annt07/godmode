---
name: finishing-a-development-branch
description: Use when implementation is complete, all tests pass, and you must decide how to integrate the work.
---

# Finishing a Development Branch

## Overview

**Core principle:** Verify the tests. Resolve all conflicts. Find the environment. Show the options. Execute the choice. Clean the workspace.

**Announce at start:** "I'm using the finishing-a-development-branch skill to complete this work."

## Step 1: Verify Tests

Run the full test suite of the project (`npm test` / `cargo test` / `pytest` / `go test ./...`).

**If tests fail**, report the failures and stop. The menu comes after a green suite:

```
Tests failing (<N> failures). Must fix before completing:

[Show failures]
```

**If tests pass:** Continue to Step 2.

<!-- ste:off -->
## Step 2: Check for Merge Conflicts
<!-- ste:on -->

Before you try to integrate, verify if a merge or rebase with the base branch would cause conflicts:

```bash
git fetch origin
git merge-tree $(git merge-base HEAD origin/<base-branch>) HEAD origin/<base-branch>
```

**If conflicts exist:**

**REQUIRED SUB-SKILL:** Invoke `godmode:resolving-merge-conflicts` to resolve each conflict before you continue. The skill guides you to find primary sources for each side and to keep both intents where possible. It also tells you to run each automated check after the resolution.

Continue to Step 3 only after you resolve all conflicts and the tests still pass.

## Step 3: Detect Environment

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
WORKTREE_PATH=$(git rev-parse --show-toplevel)
```

This result decides which menu to show and how the cleanup works:

| State | Menu | Cleanup |
|-------|------|---------|
| `GIT_DIR == GIT_COMMON` (normal repo) | Standard 3 options | No worktree to clean |
| `GIT_DIR != GIT_COMMON`, named branch | Standard 3 options | Based on provenance (see Step 7) |
| `GIT_DIR != GIT_COMMON`, detached HEAD | Reduced 2 options (no merge) | An external system manages it. Leave it in place. |

## Step 4: Determine Base Branch

The base branch is the branch where this work started. Usually the plan, the conversation or the upstream of the branch names it. If you do not know it yet, ask: "This branch split from <your best guess> — is that correct?" Get approval before you merge. A merge into the wrong base is expensive to undo.

## Step 5: Present Options

**Normal repo and named-branch worktree: show exactly these 3 options:**

```
Implementation complete. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)

Which option?
```

**Detached HEAD: show exactly these 2 options:**

```
Implementation complete. You're on a detached HEAD (externally managed workspace).

1. Push as new branch and create a Pull Request
2. Keep as-is (I'll handle it later)

Which option?
```

Show the menu word for word. Wait for their answer. The integration decision is theirs.

## Step 6: Execute Choice

### Option 1: Merge Locally

```bash
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT"

git checkout <base-branch>
git pull
git merge <feature-branch>
```

If the merge causes more conflicts, invoke `godmode:resolving-merge-conflicts` again before you continue.

Verify the tests on the merged result. If the tests fail, stop. Leave the worktree and the branch in place, and investigate. You did not push anything, so the merge is local and recoverable.

When the merged result is green, clean the worktree (Step 7). Then remove the branch:

```bash
git branch -d <feature-branch>
```

### Option 2: Push and Create PR

```bash
git push -u origin <feature-branch>
```

Then make the pull/merge request against <base-branch> with the tooling of the forge. If the repository has a PR template, obey it. If it has conventions, obey them too. Report the URL to your human partner.

Keep the worktree. Your human partner works on the PR feedback there.

### Option 3: Keep As-Is

Report: "Keeping branch <name>. Worktree preserved at <path>."

### If Your Human Partner Asks to Discard the Work

First, get their approval:

```
This will permanently delete:
- Branch <name>
- All commits: <commit-list>
- Worktree at <path>

Type 'discard' to confirm.
```

Wait for that exact approval. When it comes, clean the worktree (Step 7). Then force the removal of the branch:

```bash
git branch -D <feature-branch>
```

## Step 7: Cleanup Workspace

**This step runs for Option 1 and for approved discards.** Options 2 and 3 always keep the worktree.

**If `GIT_DIR == GIT_COMMON`:** This is a normal repository, with no worktree to clean. The step is complete.

**If `WORKTREE_PATH` is under `.worktrees/` or `worktrees/`:** We own the cleanup:

```bash
git worktree remove "$WORKTREE_PATH"
git worktree prune
```

**If git refuses the removal** (`contains modified or untracked files`): Never use `--force` on your own decision. Show your human partner what they can lose, and ask:

```bash
git -C "$WORKTREE_PATH" status --porcelain -uall
```

```
Worktree removal refused — these files were never committed:

<file list>

1. Commit them to <branch> before cleanup
2. Move them into <main repo root>
3. Delete them (unrecoverable)

Which?
```

Do what they chose. Then remove the worktree.

**Otherwise:** The host environment owns this workspace. Leave it in place.

## Quick Reference

| Option | Merge | Push | Keep Worktree | Cleanup Branch |
|--------|-------|------|---------------|----------------|
| 1. Merge locally | yes | - | - | yes |
| 2. Create PR | - | yes | yes | - |
| 3. Keep as-is | - | - | yes | - |
| Discard (explicit request only) | - | - | - | yes (force) |

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Tests passed earlier this session" | Run the suite on the tree that you will integrate. A green run proves only the tree that it ran on. |
| "The conflict looks minor, I can just pick one side" | Invoke `godmode:resolving-merge-conflicts`. Conflicts that look minor contain intent that only the history shows. |
| "They obviously want it merged" | Integration is the decision of your human partner. Show the menu and wait. |
| "The merged-result failure is probably flaky" | A merged result that fails stops all work. The branch and the worktree stay in place while you investigate. |
| "The base branch is obviously main" | Verify the fork point, or ask. A merge into the wrong base is expensive to undo. |
