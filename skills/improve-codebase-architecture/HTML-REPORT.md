# HTML Report Format

The architectural review is a single self-contained HTML file in the OS temp directory. Tailwind and Mermaid both come from CDNs. Mermaid makes graph-shaped diagrams reliably. Hand-built divs and inline SVG make the more editorial visuals (mass diagrams, cross-sections). Mix the two. Do not use Mermaid for everything, because then the report starts to look generic.

## Scaffold

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Architecture review for {{repo name}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
      mermaid.initialize({ startOnLoad: true, theme: "neutral", securityLevel: "loose" });
    </script>
    <style>
      /* small custom layer for things Tailwind doesn't cover cleanly:
         dashed seam lines, hand-drawn-feeling arrow heads, etc. */
      .seam { stroke-dasharray: 4 4; }
      .leak { stroke: #dc2626; }
      .deep { background: linear-gradient(135deg, #0f172a, #1e293b); }
    </style>
  </head>
  <body class="bg-stone-50 text-slate-900 font-sans">
    <main class="max-w-5xl mx-auto px-6 py-12 space-y-12">
      <header>...</header>
      <section id="candidates" class="space-y-10">...</section>
      <section id="top-recommendation">...</section>
    </main>
  </body>
</html>
```

## Header

Repo name, date, and a compact legend: solid box = module, dashed line = seam, red arrow = leakage, thick dark box = deep module. Do not write an introduction paragraph. Go directly to the candidates.

## Candidate card

The diagrams carry the weight. The prose is short and plain. It uses the glossary terms (from the `godmode:codebase-design` skill) without ceremony.

Each candidate is one `<article>`:

- **Title**: short, and gives the name of the deepening (e.g. "Collapse the Order intake pipeline").
- **Badge row**: the recommendation strength (`Strong` = emerald, `Worth exploring` = amber, `Speculative` = slate), and a tag for the dependency category (`in-process`, `local-substitutable`, `ports & adapters`, `mock`).
- **Files**: a monospaced list, `font-mono text-sm`.
- **Before / After diagram**: the centerpiece. Two columns, side by side. See the patterns below.
- **Problem**: one sentence. What hurts.
- **Solution**: one sentence. What changes.
- **Wins**: bullets, ≤6 words each. e.g. "Tests hit one interface", "Pricing logic stops leaking", "Delete 4 shallow wrappers".
- **ADR callout** (if applicable): one line in an amber-tinted box.

Do not write paragraphs of explanation. If a reader needs a paragraph to understand the diagram, draw the diagram again.

## Diagram patterns

Select the pattern that fits the candidate. Mix them. Do not make all diagrams look the same. Variety is part of the purpose.

### Mermaid graph (the workhorse for dependencies / call flow)

Use a Mermaid `flowchart` or `graph` when the point is "X calls Y calls Z, and look at the mess." Put it in a Tailwind-styled card, so that it fits with the rest of the page. Use classDef to make leakage edges red and the deep module dark. Sequence diagrams work well for "before: 6 round-trips; after: 1."

```html
<div class="rounded-lg border border-slate-200 bg-white p-4">
  <pre class="mermaid">
    flowchart LR
      A[OrderHandler] --> B[OrderValidator]
      B --> C[OrderRepo]
      C -.leak.-> D[PricingClient]
      classDef leak stroke:#dc2626,stroke-width:2px;
      class C,D leak
  </pre>
</div>
```

### Hand-built boxes-and-arrows (when Mermaid's layout fights you)

Show modules as `<div>`s with borders and labels. Show arrows as inline SVG `<line>` or `<path>` elements. Put them in absolute positions over a relative container. Use this pattern when the "after" diagram must look like one deep module with a thick border and gray internals. Mermaid does not render that with the right weight.

### Cross-section (good for layered shallowness)

Put horizontal bands (`h-12 border-l-4`) on top of each other to show the layers that a call goes through. Before: 6 thin layers, and each layer does nothing. After: 1 thick band with a label for the combined responsibility.

### Mass diagram (good for "interface as wide as implementation")

Draw two rectangles for each module: one for the interface surface area and one for the implementation. Before: the interface rectangle is almost as tall as the implementation rectangle (shallow). After: the interface rectangle is short and the implementation rectangle is tall (deep).

### Call-graph collapse

Before: a tree of function calls, shown as nested boxes. After: the same tree as one box, with the calls that are now internal shown faded inside it.

## Style guidance

- Make it editorial, not like a corporate dashboard. Use a lot of whitespace. A serif font for headings is optional (`font-serif` works well with stone/slate).
- Use color sparingly: one accent (emerald or indigo), red for leakage and amber for warnings.
- Keep diagrams ~320px tall, so that the before and after diagrams fit side by side without a scroll.
- Use `text-xs uppercase tracking-wider` for module labels inside diagrams, so that they look schematic, not like UI.
- The only scripts are the Tailwind CDN and the Mermaid ESM import. In all other ways the report is static: no app code, and no interactivity other than the rendering that Mermaid does.

## Top recommendation section

One larger card. It contains the candidate name, one sentence about the reason, and an anchor link to its card. Nothing more.

## Tone

Use plain, concise English. But take the architectural nouns and verbs directly from the `godmode:codebase-design` skill. A short text is not a reason to use other terms.

**Use exactly:** module, interface, implementation, depth, deep, shallow, seam, adapter, leverage, locality.

**Never substitute:** component, service, unit (for module) · API, signature (for interface) · boundary (for seam) · layer, wrapper (for module, when you mean module).

**Phrasings that fit the style:**

- "Order intake module is shallow: interface nearly matches the implementation."
- "Pricing leaks across the seam."
- "Deepen: one interface, one place to test."
- "Two adapters justify the seam: HTTP in prod, in-memory in tests."

**Wins bullets** give the gain in glossary terms: *"locality: bugs concentrate in one module"*, *"leverage: one interface, N call sites"*, *"interface shrinks; implementation absorbs the wrappers"*. Do not write *"easier to maintain"* or *"cleaner code"*. These terms are not in the glossary, and they do not have a reason to be in the report.

Do not hedge, do not write empty introductions, and do not write "it's worth noting that…". If a sentence can be a bullet, make it a bullet. If you can remove a bullet, remove it. If a term is not in the `godmode:codebase-design` glossary, find a term that is in it before you make a new one.
