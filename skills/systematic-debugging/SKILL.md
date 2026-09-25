---
name: systematic-debugging
description: Use when encountering any bug, test failure, unexpected behavior, or performance problem, before proposing fixes
---

# Systematic Debugging

## Overview

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure. And you cannot find the root cause without a tight feedback loop.

**Violating the letter of this process is violating the spirit of debugging.**

## The Iron Law

```
NO FIXES WITHOUT A TIGHT FEEDBACK LOOP AND ROOT CAUSE INVESTIGATION FIRST
```

If you have not completed Phase 1 (feedback loop) and Phase 2 (root cause), you cannot propose fixes.

## When to Use

Use for ANY technical issue:
- Test failures
- Bugs in production
- Unexpected behavior
- Performance problems
- Build failures
- Integration issues

**Use this ESPECIALLY when:**
- Under time pressure (emergencies make guessing tempting)
- "Just one quick fix" seems obvious
- You have already tried multiple fixes
- Previous fix did not work
- You do not fully understand the issue

## The Six Phases

You MUST complete each phase before proceeding to the next.

### Phase 1: Build a Feedback Loop

**This is the skill.** Everything else is mechanical. If you have a **tight** pass/fail signal for the bug (one that goes red on *this* bug), you will find the cause. If you do not have one, no amount of staring at code will save you.

Spend disproportionate effort here. **Be aggressive. Be creative. Refuse to give up.**

#### Ways to Construct a Feedback Loop (in roughly this order)

1. **Failing test** at whatever seam reaches the bug: unit, integration, e2e.
2. **Curl / HTTP script** against a running dev server.
3. **CLI invocation** with a fixture input, diffing stdout against a known-good snapshot.
4. **Headless browser script** (Playwright/Puppeteer) that drives the UI and asserts on DOM/console/network.
5. **Replay a captured trace.** Save a real network request/payload/event log to disk; replay it through the code path in isolation.
6. **Throwaway harness.** Spin up a minimal subset of the system (one service, mocked deps) that exercises the bug code path with a single function call.
7. **Property/fuzz loop.** If the bug is "sometimes wrong output", run 1000 random inputs and look for the failure mode.
8. **Bisection harness.** If the bug appeared between two known states (commit, dataset, version), automate "boot at state X, check, repeat" so you can `git bisect run` it.
9. **Differential loop.** Run the same input through old-version vs new-version (or two configs) and diff outputs.
10. **HITL script (last resort).** If a human must click, drive *them* with a structured script so the loop is still structured. Captured output feeds back to you.

#### Tighten the Loop

Treat the loop as a product. Once you have *a* loop, **tighten** it:

- Can I make it faster? (Cache setup, skip unrelated init, narrow the test scope.)
- Can I make the signal sharper? (Assert on the specific symptom, not "did not crash".)
- Can I make it more deterministic? (Pin time, seed RNG, isolate filesystem, freeze network.)

A 30-second flaky loop is barely better than no loop; a 2-second deterministic one is a debugging superpower.

#### Non-Deterministic Bugs

The goal is not a clean repro but a **higher reproduction rate**. Loop the trigger 100x, parallelise, add stress, narrow timing windows, inject sleeps. A 50%-flake bug is debuggable; 1% is not.

#### Completion Criterion: A Tight Loop That Goes Red

Phase 1 is done when you can name **one command** (a script path, a test invocation, a curl) that you have **already run at least once**, and that is:

- [ ] **Red-capable**: it drives the actual bug code path and asserts the **user's exact symptom**. Not "runs without erroring"; it must be able to *catch this specific bug*.
- [ ] **Deterministic**: same verdict every run.
- [ ] **Fast**: seconds, not minutes.
- [ ] **Agent-runnable**: you can run it unattended.

If you catch yourself reading code to build a theory before this command exists, **stop: jumping straight to a hypothesis is the exact failure this skill prevents.**

#### Redact

This skill has you show commands, outputs, and captured artifacts. **Redact every secret first**: write `<REDACTED>` in its place. Build loops against env vars.

#### When You Genuinely Cannot Build a Loop

Stop and say so explicitly. List what you tried. Ask the user for: (a) access to whatever environment reproduces it, (b) a redacted captured artifact (HAR file, log dump, core dump, screen recording with timestamps), or (c) permission to add temporary production instrumentation. Do **not** proceed to hypothesise without a loop.

---

### Phase 2: Root Cause Investigation

Once the loop is tight and red, investigate root cause. **Do NOT propose fixes yet.**

1. **Read Error Messages Carefully**
   - Do not skip past errors or warnings
   - Read stack traces completely
   - Note line numbers, file paths, error codes

2. **Reproduce Consistently**
   - Run the loop. Watch it go red as the bug appears.
   - Confirm the loop produces the failure mode the **user** described, not a different failure nearby. Wrong bug = wrong fix.
   - Confirm reproducible across multiple runs.

3. **Minimise**
   - Shrink the repro to the **smallest scenario that still goes red**. Cut inputs, callers, config, data, and steps one at a time, re-running the loop after each cut.
   - Done when every remaining element is load-bearing: removing any one of them makes the loop go green.

4. **Check Recent Changes**
   - What changed that could cause this?
   - Git diff, recent commits, new dependencies, config changes.

5. **Gather Evidence in Multi-Component Systems**

   For systems with multiple components (CI/build/signing, API/service/database):

   Before proposing fixes, add diagnostic instrumentation:
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
   - Where does bad value originate?
   - What called this with bad value?
   - Keep tracing up until you find the source
   - Fix at source, not at symptom

**HARD STOP before Phase 3.** Do not form hypotheses here. Your only outputs from Phase 2 are: a list of observed facts, a minimised repro, and a traced data-flow observation. Hypotheses belong in Phase 3. If you find yourself writing "I think the bug is..." during Phase 2, stop and move to Phase 3 deliberately.

---

### Phase 3: Hypothesise

Generate **3-5 ranked hypotheses** before testing any of them. Single-hypothesis generation anchors on the first plausible idea.

Each hypothesis must be **falsifiable**: state the prediction it makes.

> Format: "If X is the cause, then changing Y will make the bug disappear / changing Z will make it worse."

If you cannot state the prediction, the hypothesis is a vibe: discard or sharpen it.

**Show the ranked list to your human partner before testing.** They often have domain knowledge that re-ranks instantly, or know hypotheses they have already ruled out. Cheap checkpoint, big time saver. Do not block on it; proceed with your ranking if the user is AFK.

---

### Phase 4: Instrument and Pattern Analysis

Each probe must map to a specific prediction from Phase 3. **Change one variable at a time.**

1. **Find Working Examples**
   - Locate similar working code in the same codebase
   - What works that is similar to what is broken?

2. **Compare Against References**
   - If implementing a pattern, read the reference implementation COMPLETELY
   - Understand the pattern fully before applying

3. **Identify Differences**
   - What is different between working and broken?
   - List every difference, however small

4. **Tool Preference for Probing**
   - Debugger / REPL inspection if the env supports it. One breakpoint beats ten logs.
   - Targeted logs at the boundaries that distinguish hypotheses.
   - Never "log everything and grep".
   - Tag every debug log with a unique prefix, e.g. `[DEBUG-a4f2]`. Cleanup at the end becomes a single grep.

5. **Perf Branch**
   For performance regressions: establish a baseline measurement (timing harness, profiler, query plan), then bisect. Measure first, fix second.

---

### Phase 5: Fix and Regression Test

**Form a single hypothesis.** State clearly: "I think X is the root cause because Y."

**REQUIRED SUB-SKILL:** Use `godmode:test-driven-development` to write the failing test and implement the fix. Follow the RED-GREEN loop exactly.

Write the regression test **before the fix**, but only if there is a **correct seam** for it.

A correct seam is one where the test exercises the **real bug pattern** as it occurs at the call site. If the only available seam is too shallow (unit test that cannot replicate the chain that triggered the bug), a regression test there gives false confidence.

**If no correct seam exists, that itself is the finding.** Note it. The codebase architecture is preventing the bug from being locked down. Flag this for the code review stage.

If a correct seam exists:

1. Turn the minimised repro into a failing test at that seam (RED — watch it fail).
2. Apply the fix (GREEN — watch it pass).
3. Re-run the Phase 1 feedback loop against the original (un-minimised) scenario.

**If the fix does not work:**
- STOP.
- Count: how many fixes have you tried?
- If fewer than 3: return to Phase 3, re-hypothesise with new information.
- **If 3 or more fixes failed: STOP and question the architecture** (see below).

**If 3+ Fixes Failed: Question Architecture**

Pattern indicating an architectural problem:
- Each fix reveals new shared state, coupling, or a problem in a different place.
- Fixes require "massive refactoring" to implement.
- Each fix creates new symptoms elsewhere.

STOP and discuss with your human partner before attempting more fixes. This is not a failed hypothesis — this is a wrong architecture.

---

### Phase 6: Cleanup

Required before declaring done:

- [ ] Original repro no longer reproduces (re-run the Phase 1 loop)
- [ ] Regression test passes (or absence of correct seam is documented)
- [ ] All `[DEBUG-...]` instrumentation removed (`grep` the prefix)
- [ ] Throwaway prototypes deleted (or moved to a clearly-marked debug location)
- [ ] The hypothesis that turned out correct is stated in the commit / PR message, so the next debugger learns
- [ ] **REQUIRED SUB-SKILL:** Use `godmode:verification-before-completion` before claiming the bug is fixed

---

## Red Flags — STOP and Follow Process

If you catch yourself thinking:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- Proposing solutions before building a feedback loop
- Proposing solutions before tracing data flow
- **"One more fix attempt" (when already tried 2+)**
- **Each fix reveals a new problem in a different place**

**ALL of these mean: STOP. Return to Phase 1.**

**If 3+ fixes failed:** Question the architecture (see Phase 5).

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Issue is simple, don't need a feedback loop" | Simple issues have root causes too. The loop is fast for simple bugs. |
| "Emergency, no time for process" | Systematic debugging is FASTER than guess-and-check thrashing. |
| "Just try this first, then investigate" | First fix sets the pattern. Do it right from the start. |
| "I'll write test after confirming fix works" | Untested fixes do not stick. Test first proves it. |
| "Multiple fixes at once saves time" | Cannot isolate what worked. Causes new bugs. |
| "One more fix attempt" (after 2+ failures) | 3+ failures = architectural problem. Question the pattern, do not fix again. |
| "I cannot build a feedback loop for this" | You have not exhausted the 10 methods. Try all of them before stopping. |
