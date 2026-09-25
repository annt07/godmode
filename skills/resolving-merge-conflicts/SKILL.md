---
name: resolving-merge-conflicts
description: Use when encountering any git merge or rebase conflict. Use when finishing-a-development-branch hits a conflict that needs resolution before the branch can be completed.
---

# Resolving Merge Conflicts

1. **See the current state** of the merge or rebase. Check git history, and the conflicting files.

2. **Find the primary sources** for each conflict. Understand deeply why each change was made, and what the original intent was. Read the commit messages, check the PRs, check original issues or tickets. If prior triage or spec documents exist for either side, read those too.

3. **Resolve each hunk.** Preserve both intents where possible. Where incompatible, pick the one matching the merge's stated goal and note the trade-off. Do **not** invent new behaviour. Always resolve; never `--abort` unless your human partner explicitly instructs it.

4. **Discover the project's automated checks** and run them, typically typecheck, then tests, then format. Fix anything the merge broke.

5. **Finish the merge or rebase.** Stage everything and commit. If rebasing, continue the rebase process until all commits are rebased.

## Red Flags

| Thought | Reality |
|---------|---------|
| "I can tell which side is right without reading the history" | Conflicts almost always have context that only the commit messages reveal. Read them. |
| "Both changes look similar, I will just pick one" | Similar-looking changes often encode different intent. Verify both purposes before discarding either. |
| "I will invent a combined version that handles both cases" | Inventing new behaviour during conflict resolution introduces untested code. Preserve intents; do not synthesize new ones. |
