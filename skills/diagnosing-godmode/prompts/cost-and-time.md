Read `prompts/analyst-common.md` first. It gives your role, inputs,
context-safety rules, and the return format. This file adds the dimension.

Dimension: Cost and time

Find where the tokens and the wall-clock time went.

1. Tokens. Use only the usage records and counter meanings that the case
   file established. Before you calculate totals, state whether each
   counter is incremental or cumulative. Get the difference of cumulative
   observations. Do not change a missing observation into zero. Report the
   five turns with the largest supported totals. Report the supported
   totals for each associated session.
2. Wall-clock. Use the evidenced timestamp fields, event boundaries, and
   units that the case file records. Report the five longest supported
   turns. Report each gap longer than ten minutes between consecutive events
   (idle, a wait for an associated session, or a wait for your human
   partner). Say which one only when the records show it.
3. Largest tool results: use the evidenced tool-result records of the case
   file. Report the ten largest results with their tool and turn. Measure
   the records before you extract bounded content.
4. Compactions: count and find the records that discovery established as
   compaction events. Report the available before/after counters. Report
   what the session did when each compaction occurred. Mark unsupported
   fields as absent.
5. Associated sessions: count them. For each one, report the supported
   usage, the duration, and the turn that dispatched it.
6. Report the turns, subagents, tools, or repeats that dominate the
   totals, with numbers. Do not speculate about why a turn was expensive
   beyond what the transcript shows.
