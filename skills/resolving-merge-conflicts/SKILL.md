---
name: resolving-merge-conflicts
description: Use when you find any git merge or rebase conflict. Use when finishing-a-development-branch finds a conflict that you must resolve before the branch can be complete.
---

# Resolving Merge Conflicts

1. **See the current state** of the merge or rebase. Verify the git history and the files in conflict.

2. **Find the primary sources** for each conflict. Learn fully why the author made each change, and what the original intent was. Read the commit messages. Read the PRs. Read the original issues or tickets. If triage or spec documents exist for one of the sides, read those too.

3. **Resolve each hunk.** Keep both intents where possible. If they are incompatible, select the one that agrees with the stated goal of the merge, and write down the trade-off. Do **not** invent new behaviour. Always resolve, and never use `--abort` unless your human partner explicitly tells you to.

4. **Find each automated check of the project** and run them, usually typecheck, then tests, then format. Fix all that the merge broke.

5. **Finish the merge or rebase.** Stage all changes and commit. If you rebase, continue the rebase until git rebases all commits.

## Red Flags

| Thought | Reality |
|---------|---------|
| "I can tell which side is right without reading the history" | Conflicts almost always have context that only the commit messages show. Read them. |
| "Both changes look similar, I will just pick one" | Changes that look similar often contain different intent. Verify both purposes before you discard one of them. |
| "I will invent a combined version that handles both cases" | New behaviour that you invent during conflict resolution adds untested code. Keep the intents. Do not make new ones. |
