# Page types

Four recipes. Each recipe names its example in `examples/`. Copy the coordinates of the example and change them for your page. Do not start from a blank page.

## 1. High level — system context (`examples/acme-context.drawio`)

- Question that the page answers: what goes in, what comes out, who uses it, and what is external.
- Zones go from left to right at y=110, h=460, with gaps of 40 px:
  - 1 INPUTS blue (x40 w260)
  - 2 BUILD orange (x340 w300)
  - 3 OUTPUTS green (x680 w300)
  - 4 CONSUMPTION purple (x1020 w340)
- Band below, at y=600 h=210, full width: 5 EXTERNAL SERVICES & TOOLS red.
- 2–3 boxes in each zone, ~200–240 wide, 70–100 tall, one above the other at y=180/330/450.
- Key boxes: the main command, the main store, the public API.
- Edges: inputs → build (solid, blue), build → outputs (green), outputs → reader → app (purple). External and maintenance edges use a dashed red line. Long maintenance edges go around the page margin (x=1380, y=96).

## 2. Data flow — numbered call order (`examples/acme-data-flow.drawio`)

- Question: in which order do the steps run, and what does each step write?
- Top row of zones at y=110 h=330:
  - 1 START blue (x40 w250)
  - 2 EXTRACT ×N orange (x320 w400)
  - 3 LINK teal (x750 w250)
  - 4 PUBLISH ×N green (x1030 w330)
- Middle row at y=460 h=150: INPUT (x40 w250) and the external or source band (red, x320 w680). An example is a cache and an LLM, with "lookup" and "miss: prompt".
- Bottom band at y=640 h=160: 6 WRITES grey, with one box for each artefact. Put each box below the step that writes it.
- Steps ①–⑦ are boxes 165–280 wide and 70–80 tall, at y=160 and y=300. The main chain goes from left to right on y=195. Sub-steps go down.
- Write edges use a dashed grey line. They use the gaps between zones (x=312, x=1015) to go down to the writes band.

## 3. Low level — module or package map (`examples/acme-modules.drawio`)

- Question: which packages exist, and which package depends on which?
- Zones are layers in dependency order: 1 ENTRY · 2 ORCHESTRATION · 3 CORE · 4 FOUNDATION, plus a grey PUBLIC & TOOLS band.
- One box for each package: `<b>package</b><br>key modules`.
- Edges are imports. The label tells why ("build", "findings"). A two-way pair is one dashed edge with `startArrow`. Lazy (in-function) imports use a dashed line.
- If you cannot route an edge without a crossing, leave it out and say so in the box text (for example "storage + quality only"). Never accept a crossing.

## 4. Worked example — one record followed (`examples/acme-working-example.drawio`)

- Question: what happens to one concrete input, cell by cell?
- Zones, all at y=110 h=420:
  - 1 WORKSHEET blue (x40 w570)
  - 2 TRANSFORM orange (x640 w220)
  - 3 STORE green (x890 w470)
- 4 READER purple band at y=560 h=200, with 4 result boxes ~290 wide.
- Worksheet: use `Page.cell_grid()` with column letters and row numbers.
  - The banner row is grey italic. The header row is blue bold.
  - Show the row that you follow in orange. Show the source cell of a rule in red.
  - A note below the grid explains the rows.
- Store boxes show the actual rows that the run wrote (values from a real run on fictitious data). Reader boxes show the actual return values.
- Orange is the followed row in all places (cells, store boxes, reader boxes).
- Use only values that a real run printed. Make long cell text shorter, and say so.
