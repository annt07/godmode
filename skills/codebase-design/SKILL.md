---
name: codebase-design
description: Use when designing or reviewing any module interface, seam placement, or testability structure. Use when another skill needs the deep-module vocabulary (module, interface, depth, seam, adapter, leverage, locality). Use when the user wants to improve a module's design, make code more testable, or decide where a boundary goes.
---

# Codebase Design

Design **deep modules**: a lot of behaviour behind a small interface, placed at a clean seam, testable through that interface. Use this language and these principles wherever code is being designed or restructured. The aim is leverage for callers, locality for maintainers, and testability for everyone.

## Glossary

Use these terms exactly. Do not substitute "component," "service," "API," or "boundary." Consistent language is the whole point.

**Module**: anything with an interface and an implementation. Deliberately scale-agnostic: a function, class, package, or tier-spanning slice.

**Interface**: everything a caller must know to use the module correctly: the type signature, but also invariants, ordering constraints, error modes, required configuration, and performance characteristics.

**Implementation**: what is inside a module. Distinct from **Adapter**: a thing can be a small adapter with a large implementation (a Postgres repo) or a large adapter with a small implementation (an in-memory fake). Reach for "adapter" when the seam is the topic; "implementation" otherwise.

**Depth**: leverage at the interface. The amount of behaviour a caller (or test) can exercise per unit of interface they have to learn. A module is **deep** when a large amount of behaviour sits behind a small interface, **shallow** when the interface is nearly as complex as the implementation.

**Seam** (Michael Feathers): a place where you can alter behaviour without editing in that place; the *location* at which a module's interface lives. Where to put the seam is its own design decision, distinct from what goes behind it.

**Adapter**: a concrete thing that satisfies an interface at a seam. Describes *role* (what slot it fills), not substance (what is inside).

**Leverage**: what callers get from depth. More capability per unit of interface they learn.

**Locality**: what maintainers get from depth. Change, bugs, knowledge, and verification concentrate in one place rather than spreading across callers.

## Deep vs Shallow

**Deep module** = small interface + lots of implementation:

```
+-----------------------+
|   Small Interface     |  <- Few methods, simple params
+-----------------------+
|                       |
|  Deep Implementation  |  <- Complex logic hidden
|                       |
+-----------------------+
```

**Shallow module** = large interface + little implementation (avoid):

```
+----------------------------------+
|       Large Interface            |  <- Many methods, complex params
+----------------------------------+
|  Thin Implementation             |  <- Just passes through
+----------------------------------+
```

When designing an interface, ask:

- Can I reduce the number of methods?
- Can I simplify the parameters?
- Can I hide more complexity inside?

## Principles

- **Depth is a property of the interface, not the implementation.** A deep module can be internally composed of small, swappable parts; they just are not part of the interface.
- **The deletion test.** Imagine deleting the module. If complexity vanishes, it was a pass-through. If complexity reappears across N callers, it was earning its keep.
- **The interface is the test surface.** Callers and tests cross the same seam. If you want to test *past* the interface, the module is probably the wrong shape.
- **One adapter means a hypothetical seam. Two adapters means a real one.** Do not introduce a seam unless something actually varies across it.

## Designing for Testability

Good interfaces make testing natural:

1. **Accept dependencies, do not create them.**

   ```typescript
   // Testable
   function processOrder(order, paymentGateway) {}

   // Hard to test
   function processOrder(order) {
     const gateway = new StripeGateway();
   }
   ```

2. **Return results, do not produce side effects.**

   ```typescript
   // Testable
   function calculateDiscount(cart): Discount {}

   // Hard to test
   function applyDiscount(cart): void {
     cart.total -= discount;
   }
   ```

3. **Small surface area.** Fewer methods = fewer tests needed. Fewer params = simpler test setup.

## Relationships

- A **Module** has exactly one **Interface** (the surface it presents to callers and tests).
- **Depth** is a property of a **Module**, measured against its **Interface**.
- A **Seam** is where a **Module**'s **Interface** lives.
- An **Adapter** sits at a **Seam** and satisfies the **Interface**.
- **Depth** produces **Leverage** for callers and **Locality** for maintainers.

## Design-It-Twice

When exploring alternative interfaces for a module, spin up parallel sub-agents to design the interface several radically different ways, then compare on depth, locality, and seam placement. Reserve this for architectural decisions where the interface shape is genuinely uncertain. The full procedure, including the sub-agent briefs and the comparison format, is in [DESIGN-IT-TWICE.md](DESIGN-IT-TWICE.md).

## Deepening a Shallow Module

When a module fails the deletion test, or dependencies make it hard to test through its interface, follow [DEEPENING.md](DEEPENING.md): classify the dependencies, pick the seam discipline that fits, and decide what sits behind the seam.
