Read `prompts/analyst-common.md` first. It gives your role, inputs,
context-safety rules, and the return format. This file adds the dimension.

Dimension: Repeated work

Find the work that the session did more than one time.

1. Extract each tool call as `(line, turn, tool, key)`. The `key` is:
   - the file path for reads/edits/writes,
   - the command text for shell calls (remove trailing whitespace, keep the
     full command),
   - the `description` plus the first 80 characters of the prompt for
     subagent dispatches,
   - the query for searches.
2. Make groups by `(tool, key)`. Report the groups at or above the threshold:

   | Category | Threshold | Exempt |
   |---|---|---|
   | reads, searches | 3 | |
   | edits | 2 | |
   | shell commands | 2 | status commands and test runs (`git status`, `ls`, `pwd`, test runners) |
   | subagent dispatches | 2 with the same description | |
3. For each group, verify whether anything changed between the repetitions
   (a write to that file, a compaction, a human correction). Say which case
   it is:
   - A read again after an edit is not a finding.
   - A read again after a compaction is a finding. Attribute it to the
     compaction.
   - A read again with nothing between the reads is a finding by itself.
4. Look for decisions that the session made again. This is assistant text
   that gets to a conclusion that it stated earlier in the session. Examples
   are the same file, the same design choice, the same command to run.
   Quote both places.
5. Write one finding for each group, with the first and last line numbers
   and the count.
