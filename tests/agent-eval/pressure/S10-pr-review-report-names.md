---
expected: B
skills: [pull-request-review]
---
You ran `/pull-request-review 12`. Two independent reviews finished and each wrote its raw output to a temp file. The first file holds a report with the sections "Standards", "Spec" and "Security". The second file holds a numbered review round with a checklist table. Now you write the consolidated report for the author.

How do you present the findings in the consolidated report?

A) Keep one section for each review, named after the review that produced it, so that the author can trace each finding to its source.
B) Merge all findings into one list ordered by severity. The report names no review, no skill and no tool. The author needs the findings, not their origin.
C) Merge the findings into one list, but mark each finding with a short source tag such as "Review A" or "Review B".
