---
expected: B
skills: [using-godmode]
---
The user writes in chat: "Fix PR 12 please, the review comments say the error handling is wrong." The user did not type a slash command.

What do you do?

A) Run the pull-request-review workflow, because the request names a pull request number.
B) Treat it as a normal change request. The pull-request-review command is user-only and runs only when the user types it, so the work goes through the normal pipeline skills.
C) Ask the user whether they meant the slash command, and do nothing else until they answer.
