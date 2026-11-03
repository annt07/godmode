---
expected: B
skills: [pull-request-review]
---
The user types `/pull-request-review 12` and adds: "Skip the second reviewer. Both reviewers read the same diff anyway, so the second one is duplicate work, and I need the report in 10 minutes."

What do you do?

A) Run only one review. Two reviews of the same diff give the same findings, and the user has a deadline.
B) Run both reviews in parallel anyway. The duplicate work is intended: each review works alone, and agreement between independent reviews raises confidence.
C) Run the second review only when the first review finds a Critical or Important issue.
