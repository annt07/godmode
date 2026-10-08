---
name: codebase-design
description: Use when you design or review a module interface, a seam placement or a testability structure. Use when a different skill needs the deep-module vocabulary (module, interface, depth, seam, adapter, leverage, locality). Use when the user wants to improve the design of a module, make code more testable, or decide where a boundary goes.
---

# Codebase Design

Design **deep modules**. A deep module has a lot of behavior behind a small interface. It sits at a clean seam, and you can test it through that interface. Use this language and these principles wherever you design or change the structure of code. The aim is leverage for callers, locality for maintainers, and testability for everyone.

## Glossary

Use these terms exactly. Do not use "component," "service," "API," or "boundary" in their place. The full purpose of this glossary is one consistent language.

**Module**: anything with an interface and an implementation. Its scale does not matter. It can be a function, a class, a package, or a slice that goes through more than one tier.

**Interface**: everything that a caller must know to use the module correctly. This is the type signature. It is also the invariants, the order constraints, the error modes, the required configuration and the performance characteristics.

**Implementation**: what is inside a module. It is different from an **Adapter**. A thing can be a small adapter with a large implementation (a Postgres repo). It can also be a large adapter with a small implementation (an in-memory fake). Use "adapter" when the topic is the seam. Use "implementation" in other cases.

**Depth**: leverage at the interface. It is the amount of behavior that a caller (or a test) can use for each unit of interface that it must learn. A module is **deep** when a large amount of behavior sits behind a small interface. A module is **shallow** when the interface is almost as complex as the implementation.

**Seam** (Michael Feathers): a place where you can change behavior without an edit in that place. It is the *location* of the interface of a module. The position of the seam is a separate design decision. It is different from the decision about what goes behind the seam.

**Adapter**: a concrete thing that satisfies an interface at a seam. The term tells the *role* (which slot it fills). It does not tell the substance (what is inside).

**Leverage**: what callers get from depth. It is more capability for each unit of interface that they learn.

**Locality**: what maintainers get from depth. Change, bugs, knowledge and verification stay in one place. They do not spread across callers.

## Deep vs Shallow

**Deep module** = small interface + a large implementation:

```
+-----------------------+
|   Small Interface     |  <- Few methods, simple params
+-----------------------+
|                       |
|  Deep Implementation  |  <- Complex logic hidden
|                       |
+-----------------------+
```

**Shallow module** = large interface + a small implementation (avoid it):

```
+----------------------------------+
|       Large Interface            |  <- Many methods, complex params
+----------------------------------+
|  Thin Implementation             |  <- Just passes through
+----------------------------------+
```

When you design an interface, ask these questions:

- Can I decrease the number of methods?
- Can I make the parameters simpler?
- Can I hide more complexity inside?

## Principles

- **Depth is a property of the interface, not of the implementation.** A deep module can contain small parts that you can replace. These parts are not part of the interface.
- **The deletion test.** Imagine that you remove the module. If the complexity goes away, the module was a pass-through. If the complexity comes back across N callers, the module was useful.
- **The interface is the test surface.** Callers and tests cross the same seam. If you want to test *past* the interface, the module probably has the wrong shape.
- **One adapter means a hypothetical seam. Two adapters means a real one.** Do not add a seam unless something actually changes across it.

## Designing for Testability

A good interface makes a test easy:

1. **Accept dependencies. Do not create them.**

   ```typescript
   // Testable
   function processOrder(order, paymentGateway) {}

   // Hard to test
   function processOrder(order) {
     const gateway = new StripeGateway();
   }
   ```

2. **Return results. Do not make side effects.**

   ```typescript
   // Testable
   function calculateDiscount(cart): Discount {}

   // Hard to test
   function applyDiscount(cart): void {
     cart.total -= discount;
   }
   ```

3. **Small surface area.** Fewer methods = fewer tests. Fewer params = a simpler test setup.

## Relationships

- A **Module** has exactly one **Interface** (the surface that it gives to callers and tests).
- **Depth** is a property of a **Module**. You measure it against its **Interface**.
- A **Seam** is the location of the **Interface** of a **Module**.
- An **Adapter** sits at a **Seam** and satisfies the **Interface**.
- **Depth** gives **Leverage** to callers and **Locality** to maintainers.

## Design-It-Twice

When you examine alternative interfaces for a module, start parallel subagents. Each subagent designs the interface in a radically different way. Then compare the designs on depth, locality and seam placement. Use this method only for architectural decisions where the shape of the interface is really uncertain. [DESIGN-IT-TWICE.md](DESIGN-IT-TWICE.md) gives the full procedure, with the subagent briefs and the comparison format.

## Deepening a Shallow Module

A module can fail the deletion test. Its dependencies can also make a test through its interface difficult. In these cases, follow [DEEPENING.md](DEEPENING.md). Classify the dependencies, select the seam discipline that fits, and decide what sits behind the seam.
