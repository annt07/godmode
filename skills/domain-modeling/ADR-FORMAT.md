# ADR Format

ADRs are in `docs/adr/` and have sequential numbers: `0001-slug.md`, `0002-slug.md`, etc.

Create the `docs/adr/` directory only when you need the first ADR.

## Template

```md
# {Short title of the decision}

{1-3 sentences: what's the context, what did we decide, and why.}
```

That is all. An ADR can be a single paragraph. Its value is the record *that* someone made a decision and *why*. Its value is not in the sections that it fills.

## Optional sections

Include these sections only when they add real value. Most ADRs will not need them.

- **Status** frontmatter (`proposed | accepted | deprecated | superseded by ADR-NNNN`): useful when the team examines decisions again
- **Considered Options**: only when the rejected alternatives are worth a record
- **Consequences**: only when downstream effects are not obvious and need attention

## Numbering

Find the highest number in `docs/adr/` and add one.

## When to offer an ADR

All three of these conditions must be true:

1. **Hard to reverse**: it is costly to change your mind later
2. **Surprising without context**: a future reader will look at the code and ask "why on earth did they do it this way?"
3. **The result of a real trade-off**: there were real alternatives and you selected one for specific reasons

If it is easy to reverse a decision, do not record it. You will only reverse it. If it is not surprising, nobody will ask why. If there was no real alternative, there is nothing to record except "we did the obvious thing."

### What qualifies

- **Architectural shape.** "We're using a monorepo." "The write model is event-sourced, the read model is projected into Postgres."
- **Integration patterns between contexts.** "Ordering and Billing communicate via domain events, not synchronous HTTP."
- **Technology choices that carry lock-in.** Database, message bus, auth provider, deployment target. Not every library. Only the libraries that would take a quarter to replace.
- **Boundary and scope decisions.** "Customer data is owned by the Customer context; other contexts reference it by ID only." The explicit no-s are as valuable as the yes-s.
- **Deliberate deviations from the obvious path.** "We're using manual SQL instead of an ORM because X." Anything where a reasonable reader would think the opposite. These records stop the next engineer from "fixing" something that was deliberate.
- **Constraints not visible in the code.** "We can't use AWS because of compliance requirements." "Response times must be under 200ms because of the partner API contract."
- **Rejected alternatives when the rejection is non-obvious.** If you considered GraphQL and selected REST for subtle reasons, record it. If you do not, someone will suggest GraphQL again in six months.
