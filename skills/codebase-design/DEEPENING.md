# Deepening

This file tells how to deepen a cluster of shallow modules safely, for the dependencies that they have. It uses the vocabulary in [SKILL.md](SKILL.md): **module**, **interface**, **seam**, **adapter**.

## Dependency categories

When you examine a candidate for deepening, classify its dependencies. The category sets how you test the deepened module across its seam.

### 1. In-process

Pure computation, in-memory state, no I/O. You can always deepen these modules. Merge the modules and test directly through the new interface. You do not need an adapter.

### 2. Local-substitutable

These are dependencies that have local test stand-ins (PGLite for Postgres, an in-memory filesystem). You can deepen the module if the stand-in exists. Test the deepened module with the stand-in in the test suite. The seam is internal. There is no port at the external interface of the module.

### 3. Remote but owned (Ports & Adapters)

These are your own services across a network boundary (microservices, internal APIs). Define a **port** (interface) at the seam. The deep module owns the logic. You inject the transport as an **adapter**. Tests use an in-memory adapter. Production uses an HTTP/gRPC/queue adapter.

Recommendation shape: *"Define a port at the seam, implement an HTTP adapter for production and an in-memory adapter for testing, so the logic sits in one deep module even though it's deployed across a network."*

### 4. True external (Mock)

These are third-party services (Stripe, Twilio, etc.) that you do not control. The deepened module gets the external dependency as an injected port. Tests give a mock adapter.

## Seam discipline

- **One adapter means a hypothetical seam. Two adapters means a real one.** Do not add a port unless you have a reason for at least two adapters (usually production + test). A seam with a single adapter is only indirection.
- **Internal seams vs external seams.** A deep module can have internal seams in addition to the external seam at its interface. Internal seams are private to its implementation, and its own tests use them. Do not expose internal seams through the interface only because tests use them.

## Testing strategy: replace, don't layer

- When tests at the interface of the deepened module exist, old unit tests on shallow modules become waste. Remove them.
- Write new tests at the interface of the deepened module. The **interface is the test surface**.
- Tests assert on observable results through the interface, not on internal state.
- Tests should survive internal refactors, because they describe behavior, not implementation. If a test must change when the implementation changes, the test goes past the interface.
