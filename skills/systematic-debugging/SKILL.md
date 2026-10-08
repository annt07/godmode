---
name: systematic-debugging
description: Use when you find any bug, test failure, unexpected behavior, or performance problem, before you propose fixes.
---

# Systematic Debugging

## Overview

**Core principle:** ALWAYS find the root cause before you try a fix. A fix of a symptom is a failure. And you cannot find the root cause without a tight feedback loop.

**If you break the letter of this process, you break the spirit of debugging.**

## The Iron Law

```
NO FIXES WITHOUT A TIGHT FEEDBACK LOOP AND ROOT CAUSE INVESTIGATION FIRST
```

If you did not complete Phase 1 (feedback loop) and Phase 2 (root cause), you cannot propose fixes.

## When to Use

Use this skill for ANY technical issue:
- Test failures
- Bugs in production
- Unexpected behavior
- Performance problems
- Build failures
- Integration issues

**Use this skill ESPECIALLY in these conditions:**
- You are under time pressure (an emergency makes a guess attractive).
- "Just one quick fix" seems obvious.
- You already tried more than one fix.
- The previous fix did not work.
- You do not fully understand the issue.

## The Six Phases

You MUST complete each phase before you go to the next phase.

### Phase 1: Build a Feedback Loop

**This is the skill.** All the other work is mechanical. If you have a **tight** pass/fail signal for the bug (a signal that goes red on *this* bug), you will find the cause. If you do not have one, no quantity of time on the code will save you.

Put much more effort here than in the other phases. **Be aggressive. Be creative. Do not give up.**

#### Ways to Construct a Feedback Loop (in roughly this order)

1. **Failing test** at the seam that reaches the bug: unit, integration or e2e.
2. **Curl / HTTP script** against a dev server that runs.
3. **CLI invocation** with a fixture input. Diff stdout against a known-good snapshot.
4. **Headless browser script** (Playwright/Puppeteer) that controls the UI and asserts on DOM/console/network.
5. **Replay a captured trace.** Save a real network request/payload/event log to disk. Replay it through the code path in isolation.
6. **Throwaway harness.** Start a minimal subset of the system (one service, mocked deps). The subset runs the code path of the bug with a single function call.
7. **Property/fuzz loop.** If the bug is "sometimes wrong output", run 1000 random inputs and look for the failure mode.
8. **Bisection harness.** If the bug appeared between two known states (commit, dataset, version), automate "boot at state X, check, repeat" so that you can `git bisect run` it.
9. **Differential loop.** Run the same input through the old version and the new version (or two configs). Diff the outputs.
10. **HITL script (last resort).** If a human must click, guide *them* with a structured script. Thus the loop stays structured. The captured output comes back to you. Start from [scripts/hitl-loop.template.sh](scripts/hitl-loop.template.sh).

#### Tighten the Loop

Think of the loop as a product. When you have *a* loop, **tighten** it:

- Can I make it faster? (Cache the setup, skip unrelated init, make the test scope smaller.)
- Can I make the signal sharper? (Assert on the specific symptom, not "did not crash".)
- Can I make it more deterministic? (Pin the time, seed the RNG, isolate the filesystem, freeze the network.)

A 30-second flaky loop is only a little better than no loop. A 2-second deterministic loop is a very strong debugging tool.

#### Non-Deterministic Bugs

The goal is not a clean repro. The goal is a **higher reproduction rate**. Do these actions:

- Run the trigger in a loop 100x.
- Run it in parallel.
- Add stress.
- Make the timing windows smaller.
- Inject sleeps.

You can debug a 50%-flake bug. You cannot debug a 1% bug.

#### Completion Criterion: A Tight Loop That Goes Red

Phase 1 is complete when you can name **one command** (a script path, a test invocation, a curl). You must **already run it at least one time**, and the command must be:

- [ ] **Red-capable**: it runs the actual code path of the bug and asserts the **user's exact symptom**. "Runs without an error" is not sufficient. It must be able to *catch this specific bug*.
- [ ] **Deterministic**: it gives the same verdict on each run.
- [ ] **Fast**: it takes seconds, not minutes.
- [ ] **Agent-runnable**: you can run it without a human.

You can find that you read code to make a theory before this command exists. Then **stop: a jump directly to a hypothesis is the exact failure that this skill prevents.**

#### Redact

This skill tells you to show commands, outputs and captured artifacts. **Redact each secret first**: write `<REDACTED>` in its place. Build loops that use env vars.

#### When You Genuinely Cannot Build a Loop

Stop and say so explicitly. List the methods that you tried. Ask the user for one of these:

- (a) access to an environment that reproduces it,
- (b) a redacted captured artifact (HAR file, log dump, core dump, screen recording with timestamps),
- (c) permission to add temporary production instrumentation.

Do **not** go on to a hypothesis without a loop.

---

### Phase 2: Root Cause Investigation

When the loop is tight and red, investigate the root cause. **Do NOT propose fixes yet.**

1. **Read Error Messages Carefully**
   - Do not skip errors or warnings.
   - Read the full stack traces.
   - Write down line numbers, file paths and error codes.

2. **Reproduce Consistently**
   - Run the loop. Watch it go red when the bug occurs.
   - Verify that the loop makes the failure mode that the **user** described, not a different failure near it. Wrong bug = wrong fix.
   - Verify that the failure occurs again on more than one run.

3. **Minimise**
   - Make the repro into the **smallest scenario that still goes red**. Remove inputs, callers, config, data and steps one at a time. Run the loop again after each removal.
   - This step is complete when each remaining element is necessary: if you remove any one of them, the loop goes green.

4. **Check Recent Changes**
   - Which change can be the cause of this?
   - Look at the git diff, recent commits, new dependencies and config changes.

5. **Gather Evidence in Multi-Component Systems**

   For systems with more than one component (CI/build/signing, API/service/database):

   Before you propose fixes, add diagnostic instrumentation:
   ```
   For EACH component boundary:
     - Log what data enters component
     - Log what data exits component
     - Verify environment/config propagation
     - Check state at each layer

   Run once to gather evidence showing WHERE it breaks
   THEN analyze evidence to identify failing component
   THEN investigate that specific component
   ```

6. **Trace Data Flow**
   - Where does the bad value come from?
   - Which caller sent the bad value?
   - Continue to trace up until you find the source.
   - Fix the problem at the source, not at the symptom.

**HARD STOP before Phase 3.** Do not make hypotheses here. Phase 2 gives only these outputs: a list of observed facts, a minimised repro and an observation of the traced data flow. Hypotheses belong in Phase 3. You can find that you write "I think the bug is..." during Phase 2. Then stop and go to Phase 3 deliberately.

---

### Phase 3: Hypothesise

Make **3-5 ranked hypotheses** before you test any of them. If you make only one hypothesis, you stay fixed on the first plausible idea.

Each hypothesis must be **falsifiable**: state the prediction that it makes.

> Format: "If X is the cause, then changing Y will make the bug disappear / changing Z will make it worse."

If you cannot state the prediction, the hypothesis is only a feeling. Discard it or make it sharper.

**Show the ranked list to your human partner before you test.** They often have domain knowledge that changes the ranking immediately. They can also know hypotheses that they already ruled out. This checkpoint costs little and saves much time. Do not wait for it. If the user is AFK, continue with your ranking.

---

### Phase 4: Instrument and Pattern Analysis

Each probe must map to a specific prediction from Phase 3. **Change one variable at a time.**

1. **Find Working Examples**
   - Find similar code that works in the same codebase.
   - Which code works and is similar to the broken code?

2. **Compare Against References**
   - If you implement a pattern, read the full reference implementation.
   - Understand the full pattern before you apply it.

3. **Identify Differences**
   - What is different between the code that works and the broken code?
   - List each difference, also a small difference.

4. **Tool Preference for Probing**
   - Use a debugger / REPL inspection if the env supports it. One breakpoint is better than ten logs.
   - Use targeted logs at the boundaries that separate the hypotheses.
   - Never "log everything and grep".
   - Tag each debug log with a unique prefix, for example `[DEBUG-a4f2]`. Then the cleanup at the end is a single grep.

5. **Perf Branch**
   For performance regressions, do these steps:
   1. Make a baseline measurement (timing harness, profiler, query plan).
   2. Bisect.

   Measure first, fix second.

---

### Phase 5: Fix and Regression Test

**Make a single hypothesis.** State it clearly: "I think X is the root cause because Y."

**REQUIRED SUB-SKILL:** Use `godmode:test-driven-development` to write the failing test and implement the fix. Follow the RED-GREEN loop exactly.

Write the regression test **before the fix**, but only if there is a **correct seam** for it.

At a correct seam, the test runs the **real bug pattern** as it occurs at the call site. The only available seam can be too shallow (a unit test that cannot replicate the chain that caused the bug). Then a regression test at that seam gives false confidence.

**If no correct seam exists, that fact is the finding.** Write it down. The codebase architecture prevents a test that locks the bug out. Do these actions:

- Describe the missing seam with the vocabulary of `godmode:codebase-design` (which module, which interface, why the current one is too shallow).
- Flag it for the code review stage.
- In your final report, recommend `godmode:improve-codebase-architecture` for that area.

Recommend it. Do not start the refactor inside a bug fix.

If a correct seam exists:

1. Change the minimised repro into a failing test at that seam (RED — watch it fail).
2. Apply the fix (GREEN — watch it pass).
3. Run the Phase 1 feedback loop again against the original (un-minimised) scenario.

**If the fix does not work:**
- STOP.
- Count: how many fixes did you try?
- If fewer than 3: go back to Phase 3. Make new hypotheses with the new information.
- **If 3 or more fixes failed: STOP and question the architecture** (see below).

**If 3+ Fixes Failed: Question Architecture**

This pattern shows an architectural problem:
- Each fix shows new shared state, coupling, or a problem in a different place.
- Fixes need "massive refactoring" to implement.
- Each fix causes new symptoms in other places.

STOP and discuss with your human partner before you try more fixes. This is not a failed hypothesis — this is a wrong architecture.

---

### Phase 6: Cleanup

Complete these items before you say that the work is done:

- [ ] The original repro does not reproduce now (run the Phase 1 loop again).
- [ ] The regression test passes (or a document records that no correct seam exists).
- [ ] You removed all `[DEBUG-...]` instrumentation (`grep` the prefix).
- [ ] You removed the throwaway prototypes (or moved them to a debug location with a clear mark).
- [ ] The commit / PR message states the hypothesis that was correct, so that the next debugger learns.
- [ ] **REQUIRED SUB-SKILL:** Use `godmode:verification-before-completion` before you say that the bug is fixed.

---

## Red Flags — STOP and Follow Process

If you find that you think one of these:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- You propose solutions before you build a feedback loop.
- You propose solutions before you trace the data flow.
- **"One more fix attempt" (when you already tried 2+)**
- **Each fix shows a new problem in a different place.**

**ALL of these mean: STOP. Return to Phase 1.**

**If 3+ fixes failed:** Question the architecture (see Phase 5).

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Issue is simple, don't need a feedback loop" | Simple issues also have root causes. For simple bugs, the loop is fast. |
| "Emergency, no time for process" | Systematic debugging is FASTER than a series of random guesses. |
| "Just try this first, then investigate" | The first fix sets the pattern. Do it correctly from the start. |
| "I'll write test after confirming fix works" | Fixes without tests do not stay fixed. A test first proves the fix. |
| "Multiple fixes at once saves time" | You cannot isolate the fix that worked. It causes new bugs. |
| "One more fix attempt" (after 2+ failures) | 3+ failures = architectural problem. Question the pattern. Do not fix again. |
| "I cannot build a feedback loop for this" | You did not try all 10 methods. Try all of them before you stop. |
