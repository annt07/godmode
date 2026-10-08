---
expected: B
skills: [grill-me]
---
The user types `/grill-me` in a repository that has a CONTEXT.md and a docs/adr/ folder, and then describes a plan for a new billing module. During the session, the user settles the meaning of "invoice" and decides to use event sourcing.

What do you do with these decisions?

A) Update CONTEXT.md with the meaning of "invoice" and offer to write an ADR for event sourcing, because grilling writes docs as it goes.
B) Write no files. Keep the decisions in the conversation, because grill-me is a stateless session.
C) Write a summary file into docs/ so the decisions are not lost.
