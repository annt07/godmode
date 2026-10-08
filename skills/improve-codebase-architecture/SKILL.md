---
name: improve-codebase-architecture
description: Use when the user wants to scan a codebase for architectural improvement opportunities, find shallow modules to deepen, or improve testability and AI-navigability. Use when the user wants refactoring but the target is not clear.
---

# Improve Codebase Architecture

Find architectural friction and propose **deepening opportunities**. These are refactors that change shallow modules into deep ones. The aim is testability and AI-navigability.

**REQUIRED SUB-SKILL:** Invoke `godmode:codebase-design` for the architecture vocabulary (module, interface, depth, seam, adapter, leverage, locality) and its principles (the deletion test, "the interface is the test surface", "one adapter means a hypothetical seam, two means a real one"). Use these terms exactly in each suggestion.

**REQUIRED SUB-SKILL:** Invoke `godmode:domain-modeling` to read CONTEXT.md before the scan. Also use it to update CONTEXT.md inline when decisions become clear.

## Process

### 1. Explore

**Scope before you scan: YAGNI.** A deeper module is useful because it makes future changes easier. Thus give more weight to the parts of the codebase that changed recently. Decide *where* to look before you look:

- If your human partner gave a direction (a module, a subsystem, a pain point), use it.
- If not, read back through a good part of the commit history (`git log --oneline`). Find the hot spots of the codebase — the files and areas that occur again and again. Look at those paths first.

First, read CONTEXT.md and all ADRs in the area that you change.

Then start a subagent to go through the codebase. Do not follow rigid heuristics. Explore freely and record each place where you find friction:

- Where must you go between many small modules to understand one concept?
- Where are modules **shallow**, with an interface almost as complex as the implementation?
- Where did someone extract pure functions only for testability, while the real bugs hide in the calls to them (no **locality**)?
- Where do tightly-coupled modules leak across their seams?
- Which parts of the codebase have no tests, or are hard to test through their current interface?

Apply the **deletion test** to each thing that you think is shallow. Would its removal concentrate complexity, or only move it? A "yes, concentrates" is the signal that you want.

### 2. Present Candidates as an HTML Report

Write a self-contained HTML file to the OS temp directory, so that nothing goes into the repo. Get the temp dir from `$TMPDIR`. If it is not set, use `/tmp` (or `%TEMP%` on Windows). Write to `<tmpdir>/architecture-review-<timestamp>.html`, so that each run gets a new file. Open the file for the user and tell them the absolute path.

The report uses **Tailwind via CDN** for layout and styling. It uses **Mermaid via CDN** for diagrams where a graph, flow or sequence shows the structure reliably. Each candidate gets a **before/after visualisation**.

For each candidate, make a card with these items:

- **Files**: the files or modules that are part of the candidate
- **Problem**: why the current architecture causes friction
- **Solution**: a plain English description of what would change
- **Benefits**: the gain in locality and leverage, and how the tests would improve
- **Before / After diagram**: side by side, with the shallowness and the deepening
- **Recommendation strength**: one of `Strong`, `Worth exploring`, `Speculative`

End the report with a **Top recommendation** section. Tell which candidate you would do first, and why.

Follow [HTML-REPORT.md](HTML-REPORT.md) for the full HTML scaffold, the diagram patterns and the styling.

**ADR conflicts**: a candidate can contradict an existing ADR. Show it only when the friction is real enough to examine the ADR again. Mark it clearly.

Do NOT propose interfaces yet. After you write the file, ask the user: "Which of these would you like to explore?"

### 3. Grilling Loop

When the user selects a candidate, invoke `godmode:grilling` to go through the decision tree. The tree includes the constraints, the dependencies, the shape of the deepened module, what sits behind the seam, and which tests survive.

Side effects occur inline when decisions become clear. Invoke `godmode:domain-modeling` to keep the domain model current:

- **Do you name a deepened module after a concept that is not in CONTEXT.md?** Add the term to CONTEXT.md.
- **Do you make a fuzzy term precise in the conversation?** Update CONTEXT.md at that time.
- **Does the user reject the candidate for an important reason?** Offer an ADR. Offer it only when a future explorer would actually need the reason, so that they do not suggest the same thing again.
- **Do you want to examine alternative interfaces for the deepened module?** Use the design-it-twice pattern of parallel subagents from `godmode:codebase-design`.

### 4. Implementation

A candidate that the user selected and that went through grilling is a new idea. It is not an approved design. When the grilling loop ends, write its Grilling Summary. Then invoke `godmode:brainstorming` with that summary as the starting brief. Brainstorming classifies the refactor (Bounded or Architectural) and runs its approval gates as usual. But it treats each decision in the summary as settled. It asks only about the items that the summary left open, and it does not do the grilling again. Thus the refactor needs the same design and spec approvals as any other change. It never reaches implementation on a conversational yes alone.
