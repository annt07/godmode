# House style (hand-designed .drawio)

This file gives the approved look of `examples/*.drawio`. `scripts/drawio_kit.py` writes these styles. The values are here, so that you can also edit the XML.

## Canvas and composition

- Uncompressed XML: `mxfile` → one `diagram` in each file, `gridSize=10`.
- The page is 1400 px wide (880 tall is typical), with 40 px margins. Thus the content width is 1320. Use coordinates that are multiples of 10 where possible.
- Centre all items:
  - The title, the takeaway and the legend go across x=40..1360 with `align=center`.
  - The zone block has equal left and right margins.
  - Each label is `align=center;verticalAlign=middle`.
- Title: `fontSize=24;fontStyle=1;fontColor=#1F3864` at y=20, h=36.
- Takeaway: one sentence, `fontSize=14;fontStyle=2;fontColor=#404040` at y=56.
- Zones start at y=110. The legend is at the bottom (`fontSize=12`).
- Use approximately 14 boxes on a page at most. If you need more, divide the page.

## Palette (kit colour keys)

| Key | Zone header | Zone tint | Key-box fill | Box fill | Text | Typical use |
|---|---|---|---|---|---|---|
| blue | `#1E6FD9` | `#EAF2FD` | `#CFE2FF` | `#CFE2FF` | `#0B2E59` | inputs, start, worksheet |
| orange | `#E07B00` | `#FFF4E5` | `#FFD8A8` | `#FFE8CC` | `#4A2500` | build, extract, transform, the followed row |
| teal | `#138D90` | `#E6F6F6` | `#B8E6E7` | `#B8E6E7` | `#063B3C` | linking, core |
| green | `#1E9E5A` | `#E8F7EF` | `#BFEBD2` | `#D8F3E3` | `#0B3B22` | stores, bundles, publish |
| purple | `#7B3FB5` | `#F3ECFA` | `#E0CCF5` | `#E0CCF5` | `#2E1150` | consumption, reader, public API |
| red | `#C0392B` | `#FDEDEC` | `#F9C6C1` | `#F9C6C1` | `#5A0E06` | external services, LLM, cache |
| grey | `#5B6770` | `#F2F4F5` | `#DDE1E4` | `#DDE1E4` | `#1E2529` | writes on disk, tools, public band |

## Zones

- `swimlane;rounded=1;arcSize=4;startSize=34` (30 for low bands), with a white bold header (`fontSize=14`, 13 for bands). `swimlaneFillColor` is the tint.
- Number the headers in reading order: "1 · INPUTS", "2 · BUILD". When the zone is a loop, add "×N per file".
- Never use a vertical header (`horizontal=0`). It cuts long labels.

## Boxes

- Fill is the box fill, and stroke is the zone header colour. Use `strokeWidth=2`, `html=1;whiteSpace=wrap` and `fontSize=12` (11 for dense pages).
- Key boxes (3 at most): key-box fill, `strokeWidth=3`, `shadow=1`, `fontSize=14`.
- Select the shape by its meaning:
  - `shape=document` for a file
  - `shape=note` for config
  - `shape=cylinder3` for a store or a cache
  - `ellipse;shape=cloud` for an LLM or an external API
  - `shape=hexagon` for a plug-in or a step that you can extend
  - `rounded=1` for a process, a command or a module
  - A dashed border shows an optional or legacy item.
- Label: `<b>name</b><br>role<br><font color="#555">file.py · function</font>`. Add the file line only where it gives information. Numbered steps start with ①–⑨.

## Edges

- `edgeStyle=orthogonalEdgeStyle;rounded=1;endArrow=block;endFill=1`, with `strokeWidth=2.5` (2 for secondary edges). The stroke is the colour of the source zone. Use `fontSize=11`. `fontColor` is the colour of the zone label. `labelBackgroundColor` is white or the zone tint.
- Solid is control flow or data flow. `dashed=1` is a write to disk, an external call, an optional item or a legacy item. `dashPattern=2 3` is maintenance or "or".
- Always set `exitX/exitY` and `entryX/entryY`. Add `<Array as="points">` waypoints, so that no edge crosses a different edge or goes through a box.
- Route long edges through the gaps between zones (for example x = the centre of a zone gap) or through the page margin. Keep 8–12 px between parallel edges.
- Short verb labels: "read", "write", "each shop", "miss: prompt".

## Text fit

- Each character needs approximately 0.55 × fontSize px (0.6 for bold).
- Each line must fit in the box width − 16 px (clouds 60 %, hexagons 85 %).
- Lines × fontSize × 1.25 must fit in the box height − 6 px.
- `scripts/check.py` applies these rules. When it reports a hit, make the text shorter or the box larger. Never make the font smaller than 10.
