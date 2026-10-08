Read `prompts/analyst-common.md` first. It gives your role, inputs,
context-safety rules, and the return format. This file adds the dimension.

Dimension: Plan adherence

Find the plan that the session agreed to. Then map each plan step to what
happened. Here, "Plan" means any agreed course of action, not git commits.

1. Find the agreed plan. It can be one of these:
   - a design or plan agreed in chat (look for the assistant text before a
     human "yes/ok/go ahead"),
   - a spec or plan file that the session wrote (tool calls that write
     under `docs/`, `plans/`, `specs/`, or any file that the human named),
   - a todo-list record with a meaning that the case file established,
   - any numbered checklist in assistant text.

   Quote each plan step with its `path:line`.
2. Mark the structural events between the plan and its execution:
   compaction events that discovery identified, resumes, aborted turns,
   and dispatches of associated sessions. Write down their line numbers.
   Plan drift immediately after one of these events is a separate finding.
3. For each plan step, find the tool calls and assistant text that
   executed it, or show that none did. Report:
   - steps skipped (you found no execution). Quote the plan step.
   - steps executed out of order (the line numbers show the order).
   - steps changed silently (the execution is different from the plan
     step, and the assistant never announced it). Quote both.
   - steps invented (work that no plan step covers).
   - drift immediately after a structural event. Cite the event line and
     the first divergent action.
4. If you cannot find a plan, say so as the only finding. Give the lines
   that you examined.
