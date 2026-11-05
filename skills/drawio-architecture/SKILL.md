---
name: drawio-architecture
description: Make or edit hand-designed, colourful draw.io architecture diagrams. It has four page types. They are high level (system context), data flow (call order), low level (module map) and a worked example of one record. The skill makes centred, aligned .drawio files. They show coloured zones and labelled arrows, and the text fits. Use only when the user types /drawio-architecture.
disable-model-invocation: true
---

# drawio-architecture

This skill makes hand-designed `.drawio` pages in one approved house style. You put each box and each bend in position yourself. A script never sets the layout of the page.

## Files

- `references/house-style.md`: palette, shapes, fonts, edges and text-fit rules.
- `references/page-types.md`: recipes and coordinates for the 4 page types.
- `scripts/drawio_kit.py`: the `Page` helper, with `zone`, `box`, `text`, `cell_grid`, `edge`, `legend` and `save`. It uses only the Python standard library.
- `scripts/check.py`: the validator and the text-fit check. It removes the zone noise from the validator output.
- `scripts/validate.py`: the draw.io validator that `check.py` runs (MIT, see `scripts/LICENSE-validate`).
- `examples/`: the four approved pages, for a fictitious system. Start from the example of the same page type.

## Workflow

1. **Facts first.** Read the code: imports, call paths, tables and real output. Write down the facts. Never invent a box, an edge or a value.
2. **Select the page type** (high level, data flow, low level or worked example). Read its recipe in `references/page-types.md`.
3. **Plan the grid.** Before you write XML, write the zones and the boxes with x, y, w and h. Use approximately 14 boxes at most. For each edge, decide the exit side, the entry side and the waypoints. No edge must cross a different edge.
4. **Build** the page with a short script in a temp folder:

   ```python
   import sys; sys.path.insert(0, r"<skill>/scripts")
   from drawio_kit import Page
   p = Page("Title", "Takeaway sentence.", name="2 · Data flow")
   p.zone("z1", "1 · START", "blue", 40, 110, 250, 330)
   p.box("s1", "<b>① acme build</b><br>cli.py", "blue", 65, 160, 200, 70)
   p.edge("f1", "s1", "s2", "", "blue", exit=(0.5, 1), entry=(0.5, 0))
   p.legend("<b>Legend</b>&nbsp;&nbsp; ━ flow &nbsp;&nbsp; ┅ write / external")
   p.save("docs/diagrams/acme-data-flow.drawio")
   ```

   For small changes, you can edit the XML of an example directly.
5. **Verify** each file. Run the command below, and fix the diagram until the command prints `OK` for each file:

   ```bash
   uv run python <skill>/scripts/check.py docs/diagrams/<file>.drawio
   ```

   The result must show 0 errors, 0 crossings, no edge through a real box and no text-fit hit. Fix the diagram: use shorter text, a larger box or a new waypoint. Never make the check less strict.
6. **Review one page at a time.** The user opens the file in draw.io or app.diagrams.net. Get the review of the user before you start the next page.

## Rules

- Use hand layout only. Do not use auto-layout, a generator or Graphviz.
- Use colour: each page shows coloured, numbered zones (see the palette).
- Centre the title, the takeaway, the legend and all labels.
- Make the text fit: use `whiteSpace=wrap` on all cells, and `check.py` must pass.
- A solid edge is a flow. A dashed edge is a write, an external call, an optional step or a legacy step.
- Use 3 key boxes (bold border and shadow) on a page at most.
- Each page has a title, a takeaway of one sentence and a legend.
- Use only fictitious data in examples: no real customer names, personal IDs or tax ids.
- Put the output in `docs/diagrams/`. Add each new page to the list in `docs/diagrams/README.md`.
