---
name: brainstorming
description: "You MUST use this before any creative work: new features, new components, added functionality or changed behavior. It explores the intent of the user, the requirements and the design before implementation."
---

# Brainstorming Ideas Into Designs

Change ideas into complete designs and specs through a natural dialogue with your human partner.

First, find how much process the request needs. Then work through your path. Understand the context. Make the idea clear with grilling. Show a design that uses the deep-module vocabulary. Get the approval of your human partner.

## Establish Shared Understanding

The result of brainstorming is an understanding that your human partner can recognize and correct. It comes from what they want to do.

1. **Find the intent.** Use the request and the available context to find the intended result, who it is for, and what success is. If that information is missing, ask one focused question about the purpose or the intended use. Ask it before you propose features or an approach.
2. **Write back your understanding.** Write a short note that your partner can assess. Give the intended result, the relevant constraints and the success criteria. Keep what they said apart from your assumptions. Ask them to correct the note. Add their answer before you use the note as the design brief.
3. **Keep the intent in the design.** Put the agreed understanding into the design artifact of the selected path.

When the request already gives the purpose and the constraints, show that understanding. Do not ask the same questions again.

<HARD-GATE>
Before any implementation action, complete the prerequisites of the selected path. Implementation actions include an invocation of an implementation skill, product code, scaffolding, the installation of product dependencies, and a new external project.

- Spike: the human partner approves the question and the probe.
- Bounded: the human partner approves the short design in chat.
- Architectural: the human partner reviews and approves the written spec. Then they review the written implementation plan and select its execution method. An approval of the design in conversation permits only the spec. An approval of the written spec permits only the invocation of writing-plans.

A reply approves only the stage that you showed. Only a reply after the presentation can approve it. The request that started the work never approves the design that you made from it, however complete the request is. An approval of an idea or a feature scope does not approve artifacts that do not exist yet. Continue at the first stage that is not complete. Do not use one approval to skip the remaining stages of the selected path. While these prerequisites are not complete, you can explore the project without changes.
</HARD-GATE>

## Three Paths

Before your first question, classify the request. Say the class aloud, so that your human partner can change it. For example: "this looks bounded, so I'll present a short design here rather than write a spec".

- **Spike**: a feasibility question ("can we...", "is it possible...", "quick and dirty is fine"). Its result is an answer, not code that you keep. Show the question and what you will try in 2-3 sentences. Get a nod. Then investigate as cheaply as correctness permits. Use `godmode:prototype` to make any throwaway code. Report the findings as a recommendation. Label anything that you made as throwaway.
- **Bounded**: a small, clear change to code that already exists in this repository: a new flag, a small endpoint, a fix in one file. Knowledge of the kind of app is not sufficient. Bounded means that the flow that you change is already here and you can read it. If no flow exists to change, the task is not bounded. Run the grilling skill (see below). Show a short design IN CHAT. Then STOP. Implementation starts only after your human partner says yes.
- **Architectural**: new projects, new subsystems, and changes to how components fit together or to interfaces that others use. Follow the full process: grilling, approaches, a design in sections, a written spec through `godmode:to-spec`, then the writing-plans skill.

If you are not sure which of two paths applies, take the heavier path. A path can only go up. If you find hidden complexity during the task, the path goes up. Stop. Say so. Go to the heavier path. A path never goes down during a task.

## Clarifying Questions: Use Grilling

**REQUIRED SUB-SKILL:** For all clarifying questions on all paths, invoke `godmode:grilling`. It walks the design tree with questions. Use the frontier-round format of grilling, not one question at a time.

The frontier model of grilling asks all open questions that are not blocked in one round, with your recommended answer for each. It waits for the answers. Then it goes to the next round of questions that are no longer blocked. This is more efficient than one question in each message. It also makes sure that you visit each branch of the design tree.

Grilling costs only what the request leaves open. Sometimes the request, the codebase or an incoming Grilling Summary already settles each decision. Then the frontier is empty: say so in one line and go directly to the design. A Bounded change usually needs one round or none. Never make up questions to fill a round.

To find facts during grilling (filesystem, existing code, tool capabilities), dispatch `godmode:research` as a background agent. Do not ask your partner for facts that you can find yourself.

## Module Design: Use Codebase Design Vocabulary

**REQUIRED SUB-SKILL:** When you design any module boundary, seam or interface, on any path, invoke the vocabulary of `godmode:codebase-design`. Use the terms module, interface, depth, seam, adapter, leverage and locality exactly. Apply the deletion test to each boundary that you propose. Ask: if you remove this module, does the complexity collect in one place, or does it only move?

## Domain Language: Use Domain Modeling

**REQUIRED SUB-SKILL:** When domain terms are fuzzy, in conflict or new, invoke `godmode:domain-modeling` inline. Update CONTEXT.md when the decisions become clear. Offer an ADR only when all three conditions are true. The decision is hard to reverse, it is surprising without context, and it is a real trade-off.

## Anti-Pattern: "Too Simple To Need Approval"

Each path ends when your human partner approves the required design, before implementation. A bounded change can need only two sentences in chat. A new project is architectural. It needs the written spec and the planning handoffs. Make the artifact the right size for the selected path. Complete the reviews of that path before implementation.

## Writing

Write each design note, design section and spec in descriptive STE (`godmode:ste-writing`).

## Red Flags

| Thought | Reality |
|---------|---------|
| "This is too simple to need a design" | Follow the selected path. A bounded change gets a short design in chat. An architectural change gets the written spec and the planning handoffs. |
| "I'll call it bounded and skip the spec" | If you use a label to skip work, that IS the doubt. Take the heavier path. |
| "I understand this kind of app, so it's bounded" | Bounded measures the repository, not what you know. A new project has no existing flow. It is architectural. |
| "The spike works, so I'll keep the code" | The result of a spike is an answer. To keep the code is a new request. Classify it. |
| "I'll just ask one question first, then grill" | Grilling IS the step for clarifying questions. Invoke it directly. |
| "The design is obvious, no need for codebase-design vocabulary" | An obvious design has seams that are not obvious. Apply the vocabulary. |
| "The domain terms are clear enough" | If CONTEXT.md does not define the terms, they are not clear enough. Use domain-modeling. |
| "It grew, but I'm almost done — no need to re-classify" | Hidden complexity makes the path heavier during the task. Stop and say so. |

## Checklist

Classify first and announce the path. Then make one task for each item on your path, and complete the tasks in order.

**Spike:**
1. Explore the project context: only enough to frame the probe
2. Show the question and the probe plan: 2-3 sentences
3. Get approval: a nod is sufficient
4. Investigate with `godmode:prototype`: as cheaply as correctness permits
5. Report the findings: give a recommendation, and label anything that you made as throwaway

**Bounded:**
1. Explore the project context: read the files, the docs and the recent commits, and read CONTEXT.md
2. **REQUIRED SUB-SKILL:** Invoke `godmode:grilling` for clarifying questions (frontier rounds, recommended answers)
3. Show a short design in chat: the approach, the files that change, the seams that the tests use, and the tests. When your partner approves this design, they also agree to those seams. The implementation uses the seams without a new question
4. Get approval: STOP and wait for an explicit yes. End your turn directly after the design. Approval is a reply that your partner sends after they see this design. Nothing in the original request counts ("that is the whole spec", "just add it", an exact signature), because your partner did not see your design when they wrote it
5. Implement: no plan document. **REQUIRED SUB-SKILL:** Invoke `godmode:test-driven-development` before the first test, and use the seams that the approved design named. Before you report the change as complete, invoke `godmode:verification-before-completion`

**Architectural:**
1. Explore the project context: read the files, the docs and the recent commits, and read CONTEXT.md
2. If the project is too large for one spec, divide it into sub-projects. Brainstorm the first sub-project through the normal design flow
3. **REQUIRED SUB-SKILL:** Invoke `godmode:grilling`. Understand the purpose, the constraints and the success criteria through frontier rounds
4. Propose 2-3 approaches, with their trade-offs and your recommendation
5. Show the design in sections. Make each section as large as its complexity needs. **REQUIRED SUB-SKILL:** Use the vocabulary of `godmode:codebase-design` for each module boundary or seam. Invoke `godmode:domain-modeling` for each fuzzy or new domain term. Get the approval of the user after each section
6. **REQUIRED SUB-SKILL:** Invoke `godmode:to-spec`. Write the structured spec to `docs/godmode/specs/YYYY-MM-DD-<topic>-design.md` and commit it
7. Spec self-review: look for placeholders, contradictions, ambiguity and scope creep, and fix them in the spec
8. The user reviews the written spec: ask the user to review it before you continue
9. Go to implementation: invoke `godmode:writing-plans`

## After the Design (Architectural Path)

**Spec Self-Review:**
After you write the spec document, look at it again as a new reader:

1. **Placeholder scan:** Look for "TBD", "TODO", sections that are not complete, and vague requirements. Fix them.
2. **Internal consistency:** Look for sections that contradict each other. Make sure that the architecture agrees with the feature descriptions.
3. **Scope check:** Is the spec small enough for one implementation plan, or must you divide it?
4. **Ambiguity check:** Look for a requirement that a reader can understand in two ways. If you find one, select one meaning and write it clearly.

Fix each problem in the spec. You do not have to review again. Fix the problems and continue.

**User Review Gate:**
After the spec review loop is complete, ask the user to review the written spec before you continue:

> "Spec written and committed to `<path>`. Please review it and let me know if you want to make any changes before we start writing out the implementation plan."

Wait for the response of the user. Continue only after the user approves.

**Implementation:**

- Invoke `godmode:writing-plans` to make a detailed implementation plan.
- Do NOT invoke any other skill. writing-plans is the next step.
