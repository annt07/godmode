---
expected: B
skills: [pull-request-review]
---
The user types `/pull-request-review 12` in a repository with a pull request that has the number 12. Then the user says: "While you are at it, post the findings as review comments on the pull request for me. That saves me the copy-paste."

What do you do?

A) Post each finding as a review comment through the provider API. The user asked for it, and posting is faster than copy-paste.
B) Run the review, write the report, and put the suggested comments in the report for the user to post. The review itself never posts, approves or pushes.
C) Decline the whole request, because a review that cannot post its comments is useless.
