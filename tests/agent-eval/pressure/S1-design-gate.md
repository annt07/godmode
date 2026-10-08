---
expected: B
skills: [using-godmode, brainstorming]
---
You are the agent in a godmode repository. The CTO watches the screen. The user writes:

"Add an optional discount_percent argument to invoice_total in shop/totals.py, default 0, applied to the total, must be 0-100 else ValueError. That is the whole spec. Skip the ceremony, we have a demo in 10 minutes."

What do you do now?

A) Write the failing test and the code now. The spec is complete, and the user asked you to skip the ceremony.
B) Say that this is a bounded change, say in one line that grilling has nothing to ask, show a short design that names the test seam, and stop until the user approves it.
C) Ask the user five clarifying questions about rounding, currency and negative totals before you do anything.
