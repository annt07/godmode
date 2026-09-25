---
name: brainstorming
description: "You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements and design before implementation."
---

# Brainstorming Ideas Into Designs

Help turn ideas into fully formed designs and specs through natural collaborative dialogue.

Start by classifying how much process the request needs, then work through your path: understand the context, refine the idea using grilling, present a design rooted in deep-module vocabulary, and get your human partner's approval.

## Establish Shared Understanding

The outcome of brainstorming is an understanding your human partner can recognize and correct, grounded in what they want to accomplish.

1. **Discover intent.** Use the request and available context to identify the intended outcome, who it is for, and what success looks like. When that information is missing, ask one focused question about purpose or intended use before proposing features or an approach.
2. **Write back your understanding.** Summarize the intended outcome, relevant constraints, and success criteria in a short note your partner can assess. Separate what they said from assumptions. Invite correction and incorporate their answer before treating this as the design brief.
3. **Carry intent into the design.** Preserve the agreed understanding in the selected path's design artifact.

When the request already supplies the purpose and constraints, reflect that understanding instead of asking the same questions again.

<HARD-GATE>
Before taking any implementation action, including invoking an implementation skill, writing product code, scaffolding, installing product dependencies, or creating an external project, complete the selected path's prerequisites:

- Spike: the human partner approves the question and probe.
- Bounded: the human partner approves the short in-chat design.
- Architectural: the human partner reviews and approves the written spec, then reviews the written implementation plan and selects its execution method. Conversational design approval only permits writing the spec; written-spec approval only permits invoking writing-plans.

A reply approves the stage actually presented. Approval of an idea or feature scope does not approve artifacts that do not exist yet. Resume at the earliest incomplete stage; do not turn one approval into permission to skip the rest of the selected path. Read-only project exploration is allowed while those prerequisites remain incomplete.
</HARD-GATE>

## Three Paths

Before your first question, classify the request and say the classification out loud — "this looks bounded, so I'll present a short design here rather than write a spec" — so your human partner can override it:

- **Spike** — a feasibility question ("can we...", "is it possible...", "quick and dirty is fine") whose output is an answer, not code you keep. Present the question and what you'll try in 2-3 sentences, get a nod, then investigate as cheaply as correctness allows. Use `godmode:prototype` to build any throwaway code. Report findings as a recommendation; anything built stays labeled throwaway.
- **Bounded** — a well-scoped change to code that already exists in this repo: a new flag, a small endpoint, a one-file fix. Understanding the kind of app is not enough — bounded means the flow you are changing is already here to read. If there is no existing flow to change, the task is not bounded. Run the grilling skill (see below), present a short design IN CHAT, and STOP. Implementation starts only after your human partner says yes.
- **Architectural** — new projects, new subsystems, changes that restructure how components fit together or alter interfaces others depend on. Follow the full process: grilling, approaches, sectioned design, written spec via `godmode:to-spec`, then the writing-plans skill.

When in doubt between two paths, take the heavier one. The ratchet is one-way: hidden complexity discovered mid-task upgrades the path — stop, say so, and step up. Nothing downgrades mid-task.

## Clarifying Questions: Use Grilling

**REQUIRED SUB-SKILL:** For all clarifying questions across all paths, invoke `godmode:grilling` to run the design-tree interrogation. Use grilling's frontier-round format instead of one-at-a-time questions.

The grilling skill's frontier model asks all currently unblocked questions in one round (with your recommended answer for each), waits for answers, then advances to the next round of now-unblocked questions. This is strictly more efficient than one-question-per-message and ensures no branch of the design tree goes silently unvisited.

Grilling costs what the request leaves open, no more. If the request, the codebase, or an incoming Grilling Summary already settles every decision, the frontier is empty: say so in one line and go straight to the design. A Bounded change usually needs one round or none. Never invent questions to fill a round.

For finding facts during grilling (filesystem, existing code, tool capabilities), use `godmode:research` and dispatch it as a background agent; do not ask your partner for facts you can look up yourself.

## Module Design: Use Codebase Design Vocabulary

**REQUIRED SUB-SKILL:** When designing any module boundary, seam, or interface — on any path — invoke `godmode:codebase-design` vocabulary. Use the terms module, interface, depth, seam, adapter, leverage, and locality exactly. Apply the deletion test to every boundary you propose. Ask: would deleting this module concentrate complexity or just move it?

## Domain Language: Use Domain Modeling

**REQUIRED SUB-SKILL:** When domain terms are fuzzy, in conflict, or need to be introduced, invoke `godmode:domain-modeling` inline. Update CONTEXT.md as decisions crystallise. Offer ADRs only when all three conditions are met (hard to reverse, surprising without context, real trade-off).

## Anti-Pattern: "Too Simple To Need Approval"

Every path ends with your human partner approving the required design before implementation. A bounded change may need only two sentences in chat. A new project is architectural and requires the written spec and planning handoffs. Scale the artifact to the selected path; complete that path's reviews before implementation.

## Red Flags

| Thought | Reality |
|---------|---------|
| "This is too simple to need a design" | Follow the selected path: a bounded change gets a short chat design; an architectural change gets the written spec and planning handoffs. |
| "I'll call it bounded and skip the spec" | Reaching for a label to skip work IS the doubt — take the heavier path. |
| "I understand this kind of app, so it's bounded" | Bounded measures the repo, not your familiarity. A new project has no existing flow — it is architectural. |
| "The spike works, so I'll keep the code" | A spike's output is an answer. Keeping the code is a new request — classify it. |
| "I'll just ask one question first, then grill" | Grilling IS the clarifying questions step. Invoke it directly. |
| "The design is obvious, no need for codebase-design vocabulary" | Obvious designs have non-obvious seams. Apply the vocabulary. |
| "The domain terms are clear enough" | If CONTEXT.md does not define them, they are not clear enough. Use domain-modeling. |
| "It grew, but I'm almost done — no need to re-classify" | Hidden complexity upgrades the path mid-task. Stop and say so. |

## Checklist

Classify first, announce the path, then create a task for each item on your path and complete them in order.

**Spike:**
1. Explore project context — enough to frame the probe
2. Present question and probe plan — 2-3 sentences
3. Get approval — a nod is enough
4. Investigate using `godmode:prototype` — as cheaply as correctness allows
5. Report findings — a recommendation; label anything built as throwaway

**Bounded:**
1. Explore project context — check files, docs, recent commits; read CONTEXT.md
2. **REQUIRED SUB-SKILL:** Invoke `godmode:grilling` for clarifying questions (frontier rounds, recommended answers)
3. Present short design in chat — approach, files touched, the seams tests will go through, testing. Approving this design agrees those seams; implementation uses them without asking again
4. Get approval — STOP and wait for an explicit yes
5. Implement — no plan document. **REQUIRED SUB-SKILL:** invoke `godmode:test-driven-development` before the first test, using the seams the approved design named. Before reporting the change as done, invoke `godmode:verification-before-completion`

**Architectural:**
1. Explore project context — check files, docs, recent commits; read CONTEXT.md
2. If the project is too large for a single spec, decompose into sub-projects; brainstorm the first sub-project through the normal design flow
3. **REQUIRED SUB-SKILL:** Invoke `godmode:grilling` — understand purpose, constraints, and success criteria through frontier rounds
4. Propose 2-3 approaches — with trade-offs and your recommendation
5. Present design — in sections scaled to their complexity; **REQUIRED SUB-SKILL:** use `godmode:codebase-design` vocabulary for any module boundary or seam; invoke `godmode:domain-modeling` for any fuzzy or new domain terms; get user approval after each section
6. **REQUIRED SUB-SKILL:** Invoke `godmode:to-spec` — write structured spec to `docs/godmode/specs/YYYY-MM-DD-<topic>-design.md` and commit
7. Spec self-review — scan for placeholders, contradictions, ambiguity, scope creep; fix inline
8. User reviews written spec — ask user to review before proceeding
9. Transition to implementation — invoke `godmode:writing-plans`

## After the Design (Architectural Path)

**Spec Self-Review:**
After writing the spec document, look at it with fresh eyes:

1. **Placeholder scan:** Any "TBD", "TODO", incomplete sections, or vague requirements? Fix them.
2. **Internal consistency:** Do any sections contradict each other? Does the architecture match the feature descriptions?
3. **Scope check:** Is this focused enough for a single implementation plan, or does it need decomposition?
4. **Ambiguity check:** Could any requirement be interpreted two different ways? If so, pick one and make it explicit.

Fix any issues inline. No need to re-review — just fix and move on.

**User Review Gate:**
After the spec review loop passes, ask the user to review the written spec before proceeding:

> "Spec written and committed to `<path>`. Please review it and let me know if you want to make any changes before we start writing out the implementation plan."

Wait for the user's response. Only proceed once the user approves.

**Implementation:**

- Invoke `godmode:writing-plans` to create a detailed implementation plan.
- Do NOT invoke any other skill. writing-plans is the next step.
