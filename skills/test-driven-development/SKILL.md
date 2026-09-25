---
name: test-driven-development
description: Use when implementing any feature or bugfix, before writing implementation code
---

# Test-Driven Development (TDD)

## Overview

Write the test first. Watch it fail. Write minimal code to pass. Refactoring is a separate concern that belongs in code review, not the implementation loop.

**Core principle:** If you didn't watch the test fail, you do not know if it tests the right thing.

**Violating the letter of the rules is violating the spirit of the rules.**

## When to Use

**Always:**
- New features
- Bug fixes
- Behavior changes

**Exceptions (ask your human partner):**
- Throwaway prototypes (use `godmode:prototype` instead)
- Generated code
- Configuration files

Thinking "skip TDD just this once"? Stop. That is rationalization.

## The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Write code before the test? Delete it. Start over.

**No exceptions:**
- Do not keep it as "reference"
- Do not "adapt" it while writing tests
- Do not look at it
- Delete means delete

Implement fresh from tests. Period.

## Step 0: Test Only at Pre-Agreed Seams

A **seam** is the public boundary you test at: the interface where you observe behavior without reaching inside. Tests live at seams, never against internals.

No test is written at an unagreed seam. You cannot test everything, so agreeing the seams up front is how testing effort lands on the critical paths and complex logic instead of every edge case. Your human partner agrees seams while they are present, not in the middle of an automated run. Find the agreed seam in this order:

1. **The plan task's "Seam under test"** (agreed when the spec and plan were approved). Use it. Do not re-ask.
2. **The approved Bounded design or spec's Testing Decisions.** Use it. Do not re-ask.
3. **No agreed seam, interactive session** (a bug fix or a change with no plan): write the seam down and ask before the first test: "The seam under test is [interface]. Tests will exercise it through its public interface only. Is this the right seam?"
4. **No agreed seam, inside plan execution** (subagent-driven-development or executing-plans, where you do not stop to ask): pick the highest existing seam that reaches the behavior, record it as a ledgered ruling, and continue. An implementer subagent reports NEEDS_CONTEXT instead.

**REQUIRED SUB-SKILL:** If the seam placement is unclear — where the module's interface lives, how deep it should be, whether a new seam is needed — invoke `godmode:codebase-design` for the vocabulary and principles before proceeding.

Read CONTEXT.md (if it exists) so test names and interface vocabulary use the project's domain language, and respect ADRs in the area you are touching.

**Prefer existing seams.** Before proposing a new seam, check whether an existing public interface already reaches the behavior. Use the highest seam possible.

## Red-Green Loop

Work in **vertical slices** (tracer bullets): one seam, one test, one minimal implementation per cycle. Do not write all tests before all implementations (horizontal slicing). Bulk tests verify imagined behavior; tracer bullets respond to what the last cycle taught you.

```
[Confirm seam] -> [RED: Write failing test] -> [Verify it fails] -> [GREEN: Minimal code] -> [Verify it passes] -> [Repeat]
```

### RED: Write Failing Test

Write one minimal test showing what should happen at the confirmed seam.

```typescript
test('retries failed operations 3 times', async () => {
  let attempts = 0;
  const operation = () => {
    attempts++;
    if (attempts < 3) throw new Error('fail');
    return 'success';
  };

  const result = await retryOperation(operation);

  expect(result).toBe('success');
  expect(attempts).toBe(3);
});
```

**Requirements:**
- One behavior
- Clear name that describes the behavior
- Tests the real code through the public interface (no mocks unless unavoidable)
- Expected values come from an independent source of truth: a known-good literal, a worked example, the spec. Never recompute the expected value the same way the code does.

**Anti-patterns:**
- **Implementation-coupled:** mocks internal collaborators, tests private methods, or verifies through a side channel. The tell: the test breaks when you refactor but behavior has not changed.
- **Tautological:** the assertion recomputes the expected value the way the code does — it passes by construction and can never disagree with the code.
- **Horizontal slicing:** writing all tests first, then all implementations. Work in vertical slices instead.

For what a good test looks like at a seam, see [tests.md](tests.md). Before reaching for a mock, read [mocking.md](mocking.md): mock only at system boundaries, never your own modules.

### Verify RED: Watch It Fail

**MANDATORY. Never skip.**

Run the test. Confirm:
- Test fails (not errors)
- Failure message is expected
- Fails because feature is missing (not typos or setup problems)

**Test passes immediately?** You are testing existing behavior, or the test is tautological. Fix the test.

**Test errors?** Fix the error, re-run until it fails correctly.

### GREEN: Minimal Code

Write the simplest code to pass the test. Nothing more.

Do not add features, refactor other code, or "improve" beyond the test.

### Verify GREEN: Watch It Pass

**MANDATORY.**

Run the test. Confirm:
- Test passes
- Other tests still pass
- Output is pristine (no errors, warnings)

**"Other tests" means the project's full test suite, not just your file.** Before calling the change done, run the project's test command (`pytest`, `npm test`, `cargo test`). Any failure that run shows — including one you did not cause — goes in your report by name.

**Test fails?** Fix code, not test.

**Other tests fail?** Fix now.

### REFACTOR: Not Part of This Loop

**Refactoring belongs in the code review stage, not here.** The RED-GREEN loop is about behavior verification, not code quality. Once a test passes, move directly to the next slice.

If you notice code quality issues during the GREEN phase, note them for the code review stage. Do not stop and refactor now — you will lose the tight feedback loop and start guessing at what the tests cover.

**REQUIRED SUB-SKILL:** When the task is complete and enters review, invoke `godmode:requesting-code-review`. The Standards axis of that review is where refactoring opportunities are surfaced and addressed.

### Repeat

Next vertical slice: next failing test for the next behavior at the confirmed seam.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Too simple to test" | Simple code breaks. Test takes 30 seconds. |
| "I'll test after" | Tests written after pass immediately — which proves nothing. You never watched the test fail. |
| "Already manually tested" | Manual testing leaves no record, cannot be re-run, is easy to forget under pressure. |
| "Test hard = design unclear" | Listen to the test. Hard to test = hard to use. Review the seam with `godmode:codebase-design`. |
| "I need to refactor before I can write the test" | Write the test at the current seam first. The refactor is the next step, in code review. |
| "Keep as reference, write tests first" | You will adapt it. That is testing after. Delete means delete. |
| "TDD will slow me down" | TDD IS the pragmatic path: catches bugs before commit, prevents regressions, lets you refactor without fear. |

## Red Flags — STOP and Start Over

- Code before test
- Test after implementation
- Test passes immediately without a change to production code
- Cannot explain why test failed
- Tests added "later"
- Rationalizing "just this once"
- "I already manually tested it"
- Refactoring during the GREEN phase instead of noting it for review
- "Keep as reference" or "adapt existing code"
- "TDD is dogmatic, I am being pragmatic"

**All of these mean: Delete code. Start over with TDD.**

## Verification Checklist

Before marking work complete:

- [ ] Every test goes through a pre-agreed seam (or a ledgered ruling / partner-confirmed seam per Step 0)
- [ ] Every new function/method has a test
- [ ] Watched each test fail before implementing
- [ ] Each test failed for the expected reason (feature missing, not typo)
- [ ] Wrote minimal code to pass each test
- [ ] All tests pass including the full project suite
- [ ] Output pristine (no errors, warnings)
- [ ] Tests use real code (mocks only if unavoidable)
- [ ] Refactoring noted for code review, not done during implementation
- [ ] **REQUIRED SUB-SKILL:** Use `godmode:verification-before-completion` before claiming work is done

## When Stuck

| Problem | Solution |
|---------|----------|
| Do not know how to test | Write the wished-for API. Write the assertion first. Ask your human partner. |
| Test too complicated | Design too complicated. Review the seam with `godmode:codebase-design`. Simplify the interface. |
| Must mock everything | Code too coupled. Use dependency injection. |
| Test setup is huge | Extract helpers. Still complex? Simplify the design. |
