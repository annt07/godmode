Read `prompts/analyst-common.md` first. It gives your role, inputs,
context-safety rules, and the return format. This file adds the dimension.

Dimension: Stumbles

Find each point where the session stopped its forward progress.

Sources. For each source, use the evidenced record meanings and the
extraction commands of the case file to find the line numbers:
- tool results marked as errors, non-zero exits, or explicit failure records.
- shell commands that failed (non-zero exit in the result, "command not
  found", "No such file").
- retries: the same tool call sent again in the same turn after an error.
- reverted edits: an edit, then an edit that puts back the earlier
  content. Also `git checkout`/`git restore`/`git revert`/`git reset` on a
  file that the session touched.
- backtracking in assistant text ("actually", "let me instead", "that was
  wrong", "I misread").
- human corrections: a human prompt that contradicts or corrects the
  action of the assistant immediately before it.
- permission denials, hook failures, API errors, rate limits, aborted
  turns, and context overflow or compaction in the middle of a task.

For each stumble, report the line, the turn, what failed, and what
happened next. What happened next is one of these: recovered in the same
turn / recovered later at line N / never recovered. Put identical repeated failures into one finding with a
count.
