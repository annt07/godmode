---
name: prototype
description: Use when a spike needs a throwaway implementation to answer a design or feasibility question. Use when the user wants to sanity-check whether a state model or logic feels right, or explore what a UI should look like. Use when brainstorming classifies the task as a Spike.
---

# Prototype

A prototype is **throwaway code that answers a question**. The question decides the shape.

## Pick a Branch

Identify which question is being answered, using the user's prompt, the surrounding code, or by asking if the user is around:

- **"Does this logic or state model feel right?"** Build a single shareable HTML file (free-play buttons plus tabbed guided walkthroughs) that pushes the state machine through cases that are hard to reason about on paper, and that a non-developer can drive.
- **"What should this look like?"** Generate several radically different UI variations on a single route, switchable via a URL search param and a floating bottom bar.

Build the logic branch by following [LOGIC.md](LOGIC.md) and the UI branch by following [UI.md](UI.md).

The two branches produce very different artifacts, so getting this wrong wastes the whole prototype. If the question is genuinely ambiguous and the user is not reachable, default to whichever branch better matches the surrounding code (a backend module: logic; a page or component: UI) and state the assumption at the top of the prototype.

## Rules That Apply to Both

1. **Throwaway from day one, and clearly marked as such.** Locate the prototype code close to where it will actually be used so context is obvious, but name it so a casual reader can see it is a prototype, not production.
2. **Trivial to run.** A UI prototype starts from one command in the project's task runner. A logic demo is a single HTML file the user double-clicks. Either way, no thinking required to start it.
3. **No persistence by default.** State lives in memory. Persistence is the thing the prototype is *checking*, not something it should depend on.
4. **Skip the polish.** No tests, no error handling beyond what makes the prototype *runnable*, no abstractions. The point is to learn something fast.
5. **Surface the state.** After every action (logic) or on every variant switch (UI), print or render the full relevant state so the user can see what changed.
6. **Capture it when done.** Fold any validated decision into the real code, then capture the prototype itself as a **primary source**: commit it to a throwaway branch, out of main, and leave a context pointer to that branch on the implementation issue. Capture the answer too (the verdict and the question it settled) in the issue or a commit. The main branch keeps only the validated decision.

   **How to capture** (in a git repo):
   1. Write `PROTOTYPE.md` beside the prototype files: the question, what you tried, and the verdict.
   2. `git switch -c prototype/<name>`, then `git add` the prototype files and `PROTOTYPE.md` only (never other uncommitted work), and commit.
   3. `git switch -` back to the branch you started on. The prototype files are now gone from the working tree.
   4. Report the verdict and the branch name.

   For a pure feasibility question (nothing to build yet), there is no decision to fold into real code: the answer lives in your report and in `PROTOTYPE.md`, and the working tree you return to is exactly as you found it. Outside a git repo, keep the prototype in its own clearly named folder and report its path.

## Red Flags

| Thought | Reality |
|---------|---------|
| "The prototype works, so I'll keep the code" | A spike's output is an answer. Keeping the code is a new request; classify it via `godmode:brainstorming`. |
| "I'll refine the prototype into the real implementation" | A prototype is throwaway. The decision it validated goes into the real codebase via the normal workflow. |
| "No need to capture it" | An uncaptured prototype is a lost decision. Commit it to a throwaway branch and record the answer. |
| "It was only a quick script, I'll delete it (or leave it untracked, or put it in /tmp)" | Deleted, untracked or temp-dir prototypes are all lost. Capture it on `prototype/<name>` and leave the working tree clean. |
