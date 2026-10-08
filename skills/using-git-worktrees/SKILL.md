---
name: using-git-worktrees
description: Use when you start feature work that needs isolation from the current workspace, or before you execute implementation plans. It makes sure that an isolated workspace exists, with native tools or with a git worktree as the fallback.
---

# Using Git Worktrees

## Overview

Make sure that the work occurs in an isolated workspace. Use the native worktree tools of your platform first. Use manual git worktrees only when no native tool is available.

**Core principle:** First, find existing isolation. Then use native tools. Then use git as the fallback. Never fight the harness.

**Announce at start:** "I'm using the using-git-worktrees skill to set up an isolated workspace."

## Step 0: Detect Existing Isolation

**Before you make anything, verify if you are already in an isolated workspace.**

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
BRANCH=$(git branch --show-current)
```

**Submodule guard:** `GIT_DIR != GIT_COMMON` is also true in git submodules. Before you decide "already in a worktree," verify that you are not in a submodule:

```bash
# If this returns a path, you're in a submodule, not a worktree — treat as normal repo
git rev-parse --show-superproject-working-tree 2>/dev/null
```

**If `GIT_DIR != GIT_COMMON` (and not a submodule):** You are already in a linked worktree. Go to Step 2 (Project Setup). Do NOT make a second worktree.

Report with the branch state:
- On a branch: "Already in isolated workspace at `<path>` on branch `<name>`."
- Detached HEAD: "Already in isolated workspace at `<path>` (detached HEAD, externally managed). Branch creation needed at finish time."

**If `GIT_DIR == GIT_COMMON` (or in a submodule):** You are in a normal repository checkout.

Do your instructions already give the worktree preference of the user? If not, ask for consent before you make a worktree:

> "Would you like me to set up an isolated worktree? It protects your current branch from changes."

If the user already declared a preference, obey it and do not ask. If the user refuses consent, work in place and go to Step 2.

## Step 1: Create Isolated Workspace

**You have two methods. Try them in this order.**

### 1a. Native Worktree Tools (preferred)

The user asked for an isolated workspace (Step 0 consent). Do you already have a method to make a worktree? It can be a tool with a name like `EnterWorktree`, `WorktreeCreate`, a `/worktree` command or a `--worktree` flag. If you do, use it and go to Step 2.

Native tools set the directory location, make the branch and do the cleanup automatically. If you have a native tool and use `git worktree add`, you make phantom state that your harness cannot see or manage.

Go to Step 1b only if no native worktree tool is available.

### 1b. Git Worktree Fallback

**Use this only if Step 1a does not apply**, because no native worktree tool is available. Make a worktree manually with git.

#### Directory Selection

Use this priority order. An explicit preference of the user always wins over the observed filesystem state.

1. **Look in your instructions for a declared preference for the worktree directory.** If the user already specified one, use it and do not ask.

2. **Look for an existing worktree directory in the project:**
   ```bash
   ls -d .worktrees 2>/dev/null     # Preferred (hidden)
   ls -d worktrees 2>/dev/null      # Alternative
   ```
   If you find one, use it. If both exist, `.worktrees` wins.

3. **If no other guidance is available**, use `.worktrees/` at the project root as the default.

#### Safety Verification (project-local directories only)

**You MUST verify that git ignores the directory before you make the worktree:**

```bash
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```

**If git does NOT ignore it:** Add it to .gitignore and commit the change. Then continue.

**Why critical:** This prevents an accidental commit of the worktree contents to the repository.

#### Create the Worktree

```bash
# Determine path based on chosen location
path="$LOCATION/$BRANCH_NAME"

git worktree add "$path" -b "$BRANCH_NAME"
cd "$path"
```

**Sandbox fallback:** If `git worktree add` fails with a permission error (sandbox denial), tell the user that the sandbox blocked the worktree creation. Also tell them that you work in the current directory instead. Then run the setup and the baseline tests in place.

## Step 2: Project Setup

Find the applicable setup automatically, and run it:

```bash
# Node.js
if [ -f package.json ]; then npm install; fi

# Rust
if [ -f Cargo.toml ]; then cargo build; fi

# Python
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
if [ -f pyproject.toml ]; then poetry install; fi

# Go
if [ -f go.mod ]; then go mod download; fi
```

## Step 3: Verify Clean Baseline

Run the tests to make sure that the workspace starts clean:

```bash
# Use project-appropriate command
npm test / cargo test / pytest / go test ./...
```

**If tests fail:** Report the failures. Ask if you continue or investigate.

**If tests pass:** Report that the workspace is ready.

### Report

```
Worktree ready at <full-path>
Tests passing (<N> tests, 0 failures)
Ready to implement <feature-name>
```

## Quick Reference

| Situation | Action |
|-----------|--------|
| Already in linked worktree | Do not make a worktree (Step 0) |
| In a submodule | Treat it as a normal repository (Step 0 guard) |
| Native worktree tool available | Use it (Step 1a) |
| No native tool | Git worktree fallback (Step 1b) |
| `.worktrees/` exists | Use it (verify that git ignores it) |
| `worktrees/` exists | Use it (verify that git ignores it) |
| Both exist | Use `.worktrees/` |
| Neither exists | Look in the instruction file, then use the default `.worktrees/` |
| Directory not ignored | Add it to .gitignore and commit |
| Permission error on create | Sandbox fallback: work in place |
| Tests fail during baseline | Report the failures and ask |
| No package.json/Cargo.toml | Skip the dependency installation |

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "I'm obviously not in a worktree — no need to check" | Run Step 0. Isolation that the harness made and submodules can both deceive a visual check. The detection commands give the answer. |
| "`git worktree add` is quicker than hunting for a native tool" | A native tool (for example `EnterWorktree`) owns the location, the branches and the cleanup. To bypass it is the #1 mistake. It makes phantom state that your harness cannot see or manage. |
| "The worktree directory is surely ignored already" | Run `git check-ignore`. If git does not ignore the worktree directory, the whole tree goes into the repository at commit. |
| "Any directory name works" | Explicit instructions win over an existing worktree directory in the project. That directory wins over the `.worktrees/` default. |
| "The workspace is fresh — baseline tests can wait" | A dirty baseline makes each later failure ambiguous. Run the tests now. Your human partner decides if you continue after failures. |
