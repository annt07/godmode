---
name: improve-codebase-architecture
description: Use when the user wants to scan a codebase for architectural improvement opportunities, find shallow modules to deepen, or improve testability and AI-navigability. Use when refactoring is desired but the target is unclear.
---

# Improve Codebase Architecture

Surface architectural friction and propose **deepening opportunities**: refactors that turn shallow modules into deep ones. The aim is testability and AI-navigability.

**REQUIRED SUB-SKILL:** Invoke `godmode:codebase-design` for the architecture vocabulary (module, interface, depth, seam, adapter, leverage, locality) and its principles (the deletion test, "the interface is the test surface", "one adapter means a hypothetical seam, two means a real one"). Use these terms exactly in every suggestion.

**REQUIRED SUB-SKILL:** Invoke `godmode:domain-modeling` to read CONTEXT.md before the scan and to update it inline as decisions crystallise.

## Process

### 1. Explore

**Scope before you scan: YAGNI.** Deepening a module pays off by making future changes easier, so put extra weight on the parts of the codebase that have recently changed. Decide *where* to look before you look:

- If your human partner named a direction (a module, a subsystem, a pain point), take it.
- Otherwise, walk back a good stretch of the commit history (`git log --oneline`) to find the codebase's hot spots — the files and areas that keep coming up — and let those paths pull your attention first.

Read CONTEXT.md and any ADRs in the area you are touching first.

Then spawn a sub-agent to walk the codebase. Do not follow rigid heuristics; explore organically and note where you experience friction:

- Where does understanding one concept require bouncing between many small modules?
- Where are modules **shallow**, with an interface nearly as complex as the implementation?
- Where have pure functions been extracted just for testability, but the real bugs hide in how they are called (no **locality**)?
- Where do tightly-coupled modules leak across their seams?
- Which parts of the codebase are untested, or hard to test through their current interface?

Apply the **deletion test** to anything you suspect is shallow: would deleting it concentrate complexity, or just move it? A "yes, concentrates" is the signal you want.

### 2. Present Candidates as an HTML Report

Write a self-contained HTML file to the OS temp directory so nothing lands in the repo. Resolve the temp dir from `$TMPDIR`, falling back to `/tmp` (or `%TEMP%` on Windows), and write to `<tmpdir>/architecture-review-<timestamp>.html` so each run gets a fresh file. Open it for the user and tell them the absolute path.

The report uses **Tailwind via CDN** for layout and styling, and **Mermaid via CDN** for diagrams where a graph/flow/sequence reliably communicates the structure. Each candidate gets a **before/after visualisation**.

For each candidate, render a card with:

- **Files**: which files/modules are involved
- **Problem**: why the current architecture is causing friction
- **Solution**: plain English description of what would change
- **Benefits**: explained in terms of locality and leverage, and how tests would improve
- **Before / After diagram**: side-by-side, illustrating the shallowness and the deepening
- **Recommendation strength**: one of `Strong`, `Worth exploring`, `Speculative`

End the report with a **Top recommendation** section: which candidate you would tackle first and why.

Follow [HTML-REPORT.md](HTML-REPORT.md) for the full HTML scaffold, diagram patterns, and styling.

**ADR conflicts**: if a candidate contradicts an existing ADR, only surface it when the friction is real enough to warrant revisiting the ADR. Mark it clearly.

Do NOT propose interfaces yet. After the file is written, ask the user: "Which of these would you like to explore?"

### 3. Grilling Loop

Once the user picks a candidate, invoke `godmode:grilling` to walk the decision tree: constraints, dependencies, the shape of the deepened module, what sits behind the seam, what tests survive.

Side effects happen inline as decisions crystallise; invoke `godmode:domain-modeling` to keep the domain model current:

- **Naming a deepened module after a concept not in CONTEXT.md?** Add the term to CONTEXT.md.
- **Sharpening a fuzzy term during the conversation?** Update CONTEXT.md right there.
- **User rejects the candidate with a load-bearing reason?** Offer an ADR. Only offer when the reason would actually be needed by a future explorer to avoid re-suggesting the same thing.
- **Want to explore alternative interfaces for the deepened module?** Use `godmode:codebase-design`'s design-it-twice parallel sub-agent pattern.

### 4. Implementation

A picked and grilled candidate is a new idea, not an approved design. When the grilling loop ends, produce its Grilling Summary, then invoke `godmode:brainstorming` with that summary as the starting brief. Brainstorming classifies the refactor (Bounded or Architectural) and runs its approval gates as usual, but treats every decision in the summary as settled: it asks only what the summary left open, instead of re-grilling. This keeps the refactor behind the same design and spec approvals as any other change, so it never reaches implementation on a conversational yes alone.
