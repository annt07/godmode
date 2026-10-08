---
name: test-driven-development
description: Use when implementing any feature or bugfix, before you write implementation code.
---

# Test-Driven Development (TDD)

## Overview

Write the test first. Watch it fail. Write minimal code to pass. Refactoring is a separate concern. It belongs in code review, not in the implementation loop.

**Core principle:** If you did not watch the test fail, you do not know if it tests the right thing.

**If you break the letter of the rules, you break the spirit of the rules.**

## When to Use

**Always:**
- New features
- Bug fixes
- Behavior changes

**Exceptions (ask your human partner):**
- Throwaway prototypes (use `godmode:prototype` instead)
- Generated code
- Configuration files

Do you think "skip TDD just this once"? Stop. That thought is an excuse.

## Entry Gate: Design Approved First

TDD is the implementation step, never the first step. Before you write the first test, one of these conditions must be true **in this session**:

- Your human partner approved a design from `godmode:brainstorming` (Bounded or Architectural).
- You execute an approved plan (`godmode:executing-plans` / `godmode:subagent-driven-development`).
- `godmode:systematic-debugging` found the root cause of a bug, and you write its regression test.

If no condition is true, stop. Invoke `godmode:brainstorming` now. Write no test or code until your partner approves its design. This rule also applies when the request looks like a complete spec ("that is the whole spec", exact signature, exact errors). A complete spec makes brainstorming quick (Bounded, nothing to ask, a short design that names the seam, wait for yes). It does not make brainstorming optional.

| Thought | Reality |
|---------|---------|
| "The user gave the whole spec, so there's nothing to design" | Brainstorming says that in one line and shows the seam. The yes of your partner is the gate, not your opinion that the spec is clear. |
| "TDD is a discipline skill, it doesn't need approval" | TDD decides how to build, not whether your partner wants this design. |
| "The spec in the request approves my design" | Approval is a reply that your partner sends after they see the design. If you showed the design in this same turn, nobody approved it yet. End the turn. |

## The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Did you write code before the test? Remove it. Start again.

**No exceptions:**
- Do not keep it as "reference"
- Do not "adapt" it while you write tests
- Do not look at it
- Remove means remove

Implement again from the tests, from zero. No exceptions.

## Step 0: Test Only at Pre-Agreed Seams

A **seam** is the public boundary where you test. At this interface, you observe behavior without access to the inside of the module. Tests go at seams, never against internals.

Write no test at a seam that you did not agree. You cannot test everything. When you agree the seams first, the test effort goes to the critical paths and the complex logic, not to each edge case. Your human partner agrees the seams while they are present, not during an automated run. Find the agreed seam in this order:

1. **The "Seam under test" of the plan task** (your partner agreed it when they approved the spec and the plan). Use it. Do not ask again.
2. **The approved Bounded design, or the Testing Decisions of the spec.** Use it. Do not ask again.
3. **No agreed seam, interactive session** (a bug fix or a change with no plan): write the seam. Before the first test, ask: "The seam under test is [interface]. Tests will exercise it through its public interface only. Is this the right seam?"
4. **No agreed seam, inside plan execution** (subagent-driven-development or executing-plans, where you do not stop to ask): select the highest existing seam that reaches the behavior. Record it as a ruling in the ledger, and continue. An implementer subagent reports NEEDS_CONTEXT instead.

**REQUIRED SUB-SKILL:** The location of the seam can be unclear. You may not know where the interface of the module is, how deep the module must be, or whether you need a new seam. Then invoke `godmode:codebase-design` for the vocabulary and the principles before you continue.

If CONTEXT.md exists, read it, so that test names and interface words use the domain language of the project. Obey each ADR in the area that you change.

**Prefer existing seams.** Before you propose a new seam, verify whether an existing public interface already reaches the behavior. Use the highest possible seam.

## Red-Green Loop

Work in **vertical slices** (tracer bullets): one seam, one test and one minimal implementation in each cycle. Do not write all tests before all implementations (horizontal slicing). A large set of tests verifies imagined behavior. A tracer bullet responds to what the last cycle showed you.

```
[Confirm seam] -> [RED: Write failing test] -> [Verify it fails] -> [GREEN: Minimal code] -> [Verify it passes] -> [Repeat]
```

### RED: Write Failing Test

Write one minimal test that shows what must occur at the agreed seam.

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
- Tests the real code through the public interface (no mocks, unless you cannot avoid them)
- Expected values come from an independent source of truth: a known-good literal, a worked example, the spec. Never calculate the expected value again in the same way as the code.

**Anti-patterns:**
- **Implementation-coupled:** the test mocks internal collaborators, tests private methods, or verifies through a side channel. The sign: the test breaks when you refactor, but the behavior did not change.
- **Tautological:** the assertion calculates the expected value again in the same way as the code. Thus it always passes, and it can never disagree with the code.
- **Horizontal slicing:** you write all tests first, then all implementations. Work in vertical slices instead.

For an example of a good test at a seam, see [tests.md](tests.md). Before you use a mock, read [mocking.md](mocking.md). Mock only at system boundaries, never your own modules.

### Verify RED: Watch It Fail

**MANDATORY. Never skip.**

Run the test. Verify these items:
- The test fails (it does not give an error)
- The failure message is the expected message
- The test fails because the feature is missing (not because of typos or setup problems)

**Does the test pass immediately?** Then you test existing behavior, or the test is tautological. Fix the test.

**Does the test give an error?** Fix the error. Run it again until it fails correctly.

### GREEN: Minimal Code

Write the simplest code to pass the test. Nothing more.

Do not add features. Do not refactor other code. Do not "improve" anything more than the test needs.

### Verify GREEN: Watch It Pass

**MANDATORY.**

Run the test. Verify these items:
- The test passes
- The other tests still pass
- The output is clean (no errors, no warnings)

**"Other tests" means the full test suite of the project, not only your file.** Before you say that the change is complete, run the test command of the project (`pytest`, `npm test`, `cargo test`). Each failure in that run goes into your report by name, also a failure that you did not cause.

**Does the test fail?** Fix the code, not the test.

**Do other tests fail?** Fix them now.

### REFACTOR: Not Part of This Loop

**Refactoring belongs in the code review stage, not here.** The RED-GREEN loop verifies behavior, not code quality. When a test passes, go directly to the next slice.

If you see code quality problems during the GREEN phase, write a note for the code review stage. Do not stop and refactor now. If you do, you lose the tight feedback loop, and you start to guess what the tests cover.

**REQUIRED SUB-SKILL:** When the task is complete and goes into review, invoke `godmode:requesting-code-review`. The Standards axis of that review finds and addresses the refactoring opportunities.

### Repeat

Next vertical slice: the next failing test for the next behavior at the agreed seam.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Too simple to test" | Simple code breaks. A test takes 30 seconds. |
| "I'll test after" | A test that you write after the code passes immediately. That proves nothing. You never watched the test fail. |
| "Already manually tested" | A manual test leaves no record. You cannot run it again. Under pressure, you forget it easily. |
| "Test hard = design unclear" | Listen to the test. Hard to test means hard to use. Review the seam with `godmode:codebase-design`. |
| "I need to refactor before I can write the test" | Write the test at the current seam first. The refactor is the next step, in code review. |
| "Keep as reference, write tests first" | You will adapt it. That is a test after the code. Remove means remove. |
| "TDD will slow me down" | TDD IS the pragmatic path. It finds bugs before the commit, it prevents regressions, and it lets you refactor without fear. |

## Red Flags — STOP and Start Over

- Code before the test
- A test after the implementation
- A test that passes immediately without a change to production code
- You cannot explain why the test failed
- Tests that you add "later"
- An excuse such as "just this once"
- "I already manually tested it"
- Refactoring during the GREEN phase instead of a note for review
- The thought "Keep as reference", or the thought "adapt existing code"
- "TDD is dogmatic, I am being pragmatic"

**All of these mean: Remove the code. Start again with TDD.**

## Verification Checklist

Before you mark the work complete:

- [ ] Each test goes through a pre-agreed seam. Step 0 also permits a seam from a ruling in the ledger, or a seam that your partner approved
- [ ] Each new function or method has a test
- [ ] You watched each test fail before the implementation
- [ ] Each test failed for the expected reason (feature missing, not typo)
- [ ] You wrote minimal code to pass each test
- [ ] All tests pass, including the full project suite
- [ ] The output is clean (no errors, no warnings)
- [ ] Tests use real code (mocks only if you cannot avoid them)
- [ ] You wrote notes about refactoring for code review, and did not refactor during implementation
- [ ] **REQUIRED SUB-SKILL:** Use `godmode:verification-before-completion` before you claim that the work is complete

## When Stuck

| Problem | Solution |
|---------|----------|
| You do not know how to test | Write the API that you want. Write the assertion first. Ask your human partner. |
| Test too complicated | The design is too complicated. Review the seam with `godmode:codebase-design`. Make the interface simpler. |
| Must mock everything | The code is too coupled. Use dependency injection. |
| Test setup is huge | Extract helpers. Is it still complex? Make the design simpler. |
