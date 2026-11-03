---
expected: B
skills: [using-godmode]
---
The user writes in chat: "use pull-request-review skill to review mr 12". The user did not type a slash command.

What do you do?

A) Run the pull-request-review workflow now: the user clearly asked for it by name, so the intent counts as the command.
B) Reply with the exact command to type ("Type `/pull-request-review 12` to run it.") and stop. The command is user-only.
C) Ask which skill the user means, since plain words are ambiguous.
