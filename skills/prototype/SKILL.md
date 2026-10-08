---
name: prototype
description: Use when a spike needs a throwaway implementation to answer a design or feasibility question. Use when the user wants a quick test of whether a state model or logic feels right. Also use when the user wants to examine what a UI should look like. Use when brainstorming classifies the task as a Spike.
---

# Prototype

A prototype is **throwaway code that answers a question**. The question sets the shape.

## Pick a Branch

Find which question the prototype answers. Use the prompt of the user or the surrounding code. If the user is available, you can also ask:

- **"Does this logic or state model feel right?"** Build a single HTML file that you can share, with free-play buttons and tabbed guided walkthroughs. It moves the state machine through cases that are hard to think through on paper. A non-developer can operate it.
- **"What should this look like?"** Make several radically different UI variations on a single route. The user selects a variation with a URL search param and a floating bottom bar.

Follow [LOGIC.md](LOGIC.md) to build the logic branch. Follow [UI.md](UI.md) to build the UI branch.

The two branches make very different artifacts. Thus the wrong branch wastes the full prototype. The question can be really ambiguous while the user is not available. In that case, use the branch that better matches the surrounding code (logic for a backend module, UI for a page or component). State the assumption at the top of the prototype.

## Rules That Apply to Both

1. **Throwaway from day one, and clearly marked as such.** Put the prototype code near the place where it will actually be used, so that the context is obvious. But give it a name that shows a casual reader that it is a prototype, not production.
2. **Trivial to run.** A UI prototype starts from one command in the task runner of the project. A logic demo is a single HTML file that the user double-clicks. In both cases, the user does not have to think to start it.
3. **No persistence by default.** State is in memory. Persistence is the thing that the prototype *tests*, not something that it should depend on.
4. **Skip the polish.** No tests, no abstractions, and no error handling other than what makes the prototype *runnable*. The purpose is to learn something fast.
5. **Surface the state.** After each action (logic) or at each variant change (UI), print or render the full relevant state. Then the user can see what changed.
6. **Capture it when done.** Put each verified decision into the real code. Then keep the prototype itself as a **primary source**. Commit it to a throwaway branch, not to main. Put a context pointer to that branch on the implementation issue. Also record the answer (the verdict and the question that it settled) in the issue or in a commit. The main branch keeps only the verified decision.

   **How to capture** (in a git repo):
   1. Write `PROTOTYPE.md` next to the prototype files. Include the question, what you tried, and the verdict.
   2. Run `git switch -c prototype/<name>`. Then `git add` only the prototype files and `PROTOTYPE.md` (never other uncommitted work), and commit.
   3. Run `git switch -` to go back to the branch where you started. The prototype files are then not in the working tree.
   4. Report the verdict and the branch name.

   A pure feasibility question has nothing to build yet. Thus there is no decision to put into real code. The answer is in your report and in `PROTOTYPE.md`. The working tree that you go back to is exactly as you found it. Outside a git repo, keep the prototype in its own folder with a clear name, and report its path.

## Red Flags

| Thought | Reality |
|---------|---------|
| "The prototype works, so I'll keep the code" | The output of a spike is an answer. To keep the code is a new request. Classify it with `godmode:brainstorming`. |
| "I'll refine the prototype into the real implementation" | A prototype is throwaway. The decision that it verified goes into the real codebase through the normal workflow. |
| "No need to capture it" | A prototype that nobody keeps is a lost decision. Commit it to a throwaway branch and record the answer. |
| "It was only a quick script, I'll delete it (or leave it untracked, or put it in /tmp)" | A removed prototype is lost. An untracked prototype or a prototype in a temp dir is also lost. Keep it on `prototype/<name>` and leave the working tree clean. |
