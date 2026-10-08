---
name: handoff
description: Compact the current conversation into a handoff document that another agent can continue from.
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

Write a handoff document that summarizes the current conversation, so that a new agent can continue the work. Save it to the temporary directory of the OS of the user, not to the current workspace.

Include a "suggested skills" section in the document. In it, name the godmode skills that the next agent should call the Skill tool for (for example `brainstorming`, `prototype`, `executing-plans`). Also give the path of each plan ledger under `.godmode/sdd/`.

Do not copy content that other artifacts already record (specs, plans, ADRs, issues, commits, diffs). Refer to them by path or URL instead.

Remove all sensitive information, such as API keys, passwords, or personally identifiable information.

If the user gave arguments, use them as a description of the focus of the next session. Adapt the document to that focus.

Write the handoff document in descriptive STE (`godmode:ste-writing`).
