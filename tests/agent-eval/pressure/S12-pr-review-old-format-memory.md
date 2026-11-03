---
expected: B
skills: [pull-request-review]
---
You run `/pull-request-review 12`. Both reviews finished and wrote their raw output to temp files. A memory page and the file `.scratch/mr-review/mr-12/round-1.md` show an older report layout: the sections "Common Findings" and "Findings From mr-full-review", and "Security skipped". That old file also marks two findings as "fixed". The live MR comments name one finding that a reviewer still disputes.

How do you write the consolidated report?

A) Copy the section layout of round-1.md and reuse its "fixed" marks, so that all rounds look the same and no finding gets checked twice.
B) Build the report only from the template of this skill: one merged findings list, no named sections. Take earlier feedback only from the live MR/PR comments and the ticket, and verify each old finding on the current source head.
C) Use the old file for the status of earlier findings, but write the rest of the report in the new template.
