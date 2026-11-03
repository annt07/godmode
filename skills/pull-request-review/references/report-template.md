# Report template

Phase 4 of `SKILL.md` reads this file. Fill each section on each run. A section with nothing to report still shows, with its content or an explicit `Skipped: <reason>` / "None found.". Never remove a section because it seemed not applicable. Say why instead.

The report never names a review, a skill or a tool. It contains no source attribution.

```markdown
# Pull Request Review Report

## Summary
Ref: <url or number>  |  <title>  |  <source> -> <target>  |  reviewed at <head sha, short>  |  <date>
Verdict: **Ready | With fixes | Not ready**  <one sentence tied to the findings>
Draft: "Not ready for a merge verdict: still a draft."
Findings: <N> (<critical> Critical, <important> Important, <minor> Minor, <suggestion> Suggestion). Dropped for a missing verifiable file and line: <N>.

## Scope
<What the review checked: two independent reviews of the same range, a test run on each branch, hygiene. What was skipped and why, in plain words (for example "CI log review skipped: no CI configuration in this repo").>

## Test Results
| Branch | Passed | Failed | Skipped |
|---|---|---|---|
| <target> | ... | ... | ... |
| <source> | ... | ... | ... |

New failures (fail on <source>, pass on <target>): <list or "None">
Existing failures (fail on both branches): <list or "None">
<When the tests could not run: "Skipped: <reason>".>

## Findings
<One list, ordered Critical -> Important -> Minor -> Suggestion. Duplicates merged into one item. Each item:
**[Severity: Critical | Important | Minor | Suggestion] [Area: <Correctness | Design | Tests | Security | Docs | CI | Other>]** <file>:<line>
Changed Code: <short snippet from the diff>
Issue: <what is wrong>
Why This Matters: <why it matters and what could happen>
Recommendation: <the concrete fix>
Suggested Change: <suggestion block when applicable>
"None found." if empty.>

## Missing Tests
<Each gap names file::function and the behaviour that the missing test should pin. "None found." if empty.>

## Since Round <N-1>
<Round 2 onward only. Round 1 writes "First review round.". Each earlier finding: Fixed / Still open / No longer applicable, with evidence (file:line or commit).>

## Recommendation
**Ready | With fixes | Not ready**
<One or two sentences tied to the findings and the test results above.>

## Summary For Author
<A plain-language paragraph for the author of the change: what is good, what must change, what to do next.>
```
