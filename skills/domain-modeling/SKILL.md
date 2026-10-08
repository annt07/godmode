---
name: domain-modeling
description: Use when you resolve domain terminology, create or edit a CONTEXT.md, or record or edit an ADR. Also use when a different skill needs a precise domain language for the project. Use when a term is fuzzy, has too many meanings, or conflicts with entries that are already in the glossary.
---

# Domain Modeling

Actively build the domain model of the project and make it more precise while you design. This is the *active* discipline. Challenge terms, invent edge-case scenarios, and write the glossary and the decisions immediately when they become clear. To only *read* CONTEXT.md for vocabulary is not this skill. That is a one-line habit that any skill can do. Use this skill when you change the model, not when you only use it.

## File Structure

Most repos have a single context:

```
/
+-- CONTEXT.md
+-- docs/
|   +-- adr/
|       +-- 0001-event-sourced-orders.md
|       +-- 0002-postgres-for-write-model.md
+-- src/
```

If a CONTEXT-MAP.md exists at the root, the repo has more than one context. The map shows the location of each context.

Create files only when you have something to write in them. If no CONTEXT.md exists, create one when you resolve the first term. If no docs/adr/ exists, create it when you need the first ADR.

Write `CONTEXT.md` entries and ADRs in descriptive STE (`godmode:ste-writing`). After you change one of these files, lint it: Run `python <ste-writing>/scripts/ste-lint.py --glossary <ste-writing>/glossary.md <file>`, where `<ste-writing>` is the folder of the `godmode:ste-writing` skill. Fix each hard finding.

## During the Session

### Challenge Against the Glossary

Your human partner can use a term that conflicts with the language that is already in CONTEXT.md. If this occurs, tell the partner immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y. Which is it?"

### Sharpen Fuzzy Language

When the user uses a vague term or a term with too many meanings, propose a precise canonical term. "You are saying 'account': do you mean the Customer or the User? Those are different things."

### Discuss Concrete Scenarios

When you discuss domain relationships, test them under stress with specific scenarios. Invent scenarios that examine edge cases. These scenarios make the user give precise boundaries between concepts.

### Cross-Reference with Code

When the user tells how something works, verify whether the code agrees. If you find a contradiction, tell the user: "Your code cancels entire Orders, but you just said partial cancellation is possible. Which is right?"

### Update CONTEXT.md Inline

When you resolve a term, update CONTEXT.md at that time. Do not collect the updates for later. Record each one when it occurs.

Use the structure in [CONTEXT-FORMAT.md](CONTEXT-FORMAT.md). CONTEXT.md should contain no implementation details. Do not use CONTEXT.md as a spec, a scratch pad, or a store for implementation decisions. It is a glossary and nothing else.

### Offer ADRs Sparingly

Offer to create an ADR only when all three conditions are true:

1. **Hard to reverse**: it is costly to change your mind later
2. **Surprising without context**: a future reader will ask "why did they do it this way?"
3. **The result of a real trade-off**: there were real alternatives and you selected one for specific reasons

If one of the three is missing, do not write the ADR. When you write one, use [ADR-FORMAT.md](ADR-FORMAT.md).
