---
name: domain-modeling
description: Use when resolving domain terminology, creating or editing a CONTEXT.md, recording or editing an ADR, or when another skill needs the project's domain language to be precise. Use when a term is fuzzy, overloaded, or in conflict with existing glossary entries.
---

# Domain Modeling

Actively build and sharpen the project's domain model as you design. This is the *active* discipline: challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise. Merely *reading* CONTEXT.md for vocabulary is not this skill: that is a one-line habit any skill can do. This skill is for when you are changing the model, not just consuming it.

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

If a CONTEXT-MAP.md exists at the root, the repo has multiple contexts. The map points to where each one lives.

Create files lazily: only when you have something to write. If no CONTEXT.md exists, create one when the first term is resolved. If no docs/adr/ exists, create it when the first ADR is needed.

## During the Session

### Challenge Against the Glossary

When your human partner uses a term that conflicts with the existing language in CONTEXT.md, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y. Which is it?"

### Sharpen Fuzzy Language

When the user uses vague or overloaded terms, propose a precise canonical term. "You are saying 'account': do you mean the Customer or the User? Those are different things."

### Discuss Concrete Scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-Reference with Code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible. Which is right?"

### Update CONTEXT.md Inline

When a term is resolved, update CONTEXT.md right there. Do not batch these up: capture them as they happen.

Use the structure in [CONTEXT-FORMAT.md](CONTEXT-FORMAT.md). CONTEXT.md should be totally devoid of implementation details. Do not treat CONTEXT.md as a spec, a scratch pad, or a repository for implementation decisions. It is a glossary and nothing else.

### Offer ADRs Sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse**: the cost of changing your mind later is meaningful
2. **Surprising without context**: a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off**: there were genuine alternatives and you picked one for specific reasons

If any of the three is missing, skip the ADR. When you do write one, use [ADR-FORMAT.md](ADR-FORMAT.md).
