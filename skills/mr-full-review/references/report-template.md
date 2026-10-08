# Report template

Phase 7 of `SKILL.md` reads this file. Fill each section on each run. A section with nothing to report still shows, with its content or an explicit `Skipped: <reason>` / "None found.". Never remove a section because it seemed not applicable. Say why instead.

```markdown
# Review round <N>: <title> (<!iid | #number>)
<url>  |  provider: <gitlab | github | bitbucket-cloud | bitbucket-server>  |  <source> -> <target>  |  reviewed at <head sha, short>  |  <date>

## Verdict
**<Approve as-is | Approve with non-blocking comments | Request changes | Needs discussion>**
<1-2 sentences tied to the blocking findings below, or their absence. Draft: "Not ready for a merge verdict: still a draft.">

## Since round <N-1>
<Round 2 onward only; round 1 writes "First review round.". Each earlier finding: Fixed / Still open / No longer applicable, with evidence (file:line or commit).>

## Scope classification
| Field | Value |
|---|---|
| Type | ... |
| Size | ... |
| Surfaces touched | ... |
| Touches tests? | ... |
| Security-sensitive? | ... |
| Ticket | ... |
| Local checkout | ... |
| CI configured | ... |
| Draft | ... |
| Multi-repo | ... |

## Blocking findings
<Numbered. Each item:
**[Severity: Critical/Important] [Axis: Standards | Spec | Security]** <Title>: `<file>:<line>`
<Concrete failure scenario: specific input or state, then the wrong output or crash.>
Suggested fix: <specific, actionable>
"None found." if empty.>

## Non-blocking findings
<Same format for Minor items. "None found." if empty.>

## Security (vuln-scan)
<Summary table from vuln-scan's review mode (ID | Category | Severity | File), its verdict, and the report path under .godmode/security/. Describe leaked secrets or PHI, never quote them.>

## Checklist coverage
| Section | Status | Notes |
|---|---|---|
| A. Requirements traceability | Pass / Fail / Flagged / Skipped: <reason> | |
| B. Correctness and design quality | ... | |
| C. Security | ... | |
| D. Test coverage | ... | |
| E. Live verification | ... | |
| F. Description and title | ... | |
| G. Commits and branch | ... | |
| H. Scope and churn | ... | |
| I. Breaking changes and compatibility | ... | |
| J. Operational readiness | ... | |
| K. Dependencies and documentation | ... | |
| L. UI and accessibility | ... | |
| M. Dead code and debug leftovers | ... | |

## Requirements traceability
<If a ticket was found:
### Acceptance criteria
| AC | Met? | Evidence |
|---|---|---|
| ... | Met / Not met / Met in intent, not literal text | file:line or quote |

### Definition of Done
| Item | Status | Note |
|---|---|---|

Otherwise: "Skipped: no ticket linked.">

## Recommended next steps
<Each tied to a finding or gap, for example:
- Add a test for `path/module.py::new_function` pinning <behaviour>: nothing covers the branch at line N.
- Replace the stale description line "<current>" with "<suggested>".
- Check CODEOWNERS approval in the <provider> UI.
- Sampled coverage: files X, Y, Z reviewed in depth, the rest spot-checked.
"None: no further action recommended." if empty.>

## Suggested comments (for you to post)
<Comment text the user can paste into the MR/PR or the ticket, one block per destination, formatted as it would be posted. This skill never posts. "No comment needed: findings are minor." if none is warranted.>
```
