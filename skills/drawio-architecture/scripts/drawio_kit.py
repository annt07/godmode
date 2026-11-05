"""Build hand-designed, colourful draw.io pages (stdlib only).

You choose every coordinate; the kit only writes consistent styles.

    from drawio_kit import Page
    p = Page("Title", "One-line takeaway.")
    p.zone("z1", "1 · INPUTS", "blue", 40, 110, 260, 460)
    p.box("orders", "<b>Order files</b><br>csv", "blue", 70, 180, 200, 90, shape="file")
    p.edge("e1", "orders", "build", "read", "blue", exit=(1, .5), entry=(0, .5))
    p.legend("<b>Legend</b> ...")
    p.save("docs/diagrams/x.drawio")
"""

from __future__ import annotations

import math
import re
import sys
import xml.etree.ElementTree as ET
from html import escape
from pathlib import Path

PALETTE = {
    # key: header, zone tint, key-box fill, box fill, font, edge-label colour
    "blue": ("#1E6FD9", "#EAF2FD", "#CFE2FF", "#CFE2FF", "#0B2E59", "#1E6FD9"),
    "orange": ("#E07B00", "#FFF4E5", "#FFD8A8", "#FFE8CC", "#4A2500", "#B35F00"),
    "teal": ("#138D90", "#E6F6F6", "#B8E6E7", "#B8E6E7", "#063B3C", "#138D90"),
    "green": ("#1E9E5A", "#E8F7EF", "#BFEBD2", "#D8F3E3", "#0B3B22", "#1E9E5A"),
    "purple": ("#7B3FB5", "#F3ECFA", "#E0CCF5", "#E0CCF5", "#2E1150", "#7B3FB5"),
    "red": ("#C0392B", "#FDEDEC", "#F9C6C1", "#F9C6C1", "#5A0E06", "#C0392B"),
    "grey": ("#5B6770", "#F2F4F5", "#DDE1E4", "#DDE1E4", "#1E2529", "#5B6770"),
}

SHAPES = {
    "process": "rounded=1;arcSize=12;",
    "file": "shape=document;boundedLbl=1;size=0.15;",
    "config": "shape=note;size=16;",
    "store": "shape=cylinder3;boundedLbl=1;size=10;",
    "cloud": "ellipse;shape=cloud;",
    "plugin": "shape=hexagon;perimeter=hexagonPerimeter2;size=0.1;",
}


class Page:
    def __init__(self, title: str, takeaway: str, width: int = 1400, height: int = 880,
                 name: str = "Page 1", page_id: str = "page") -> None:
        self.width, self.height, self.name, self.page_id = width, height, name, page_id
        self.cells: list[str] = []
        inner = width - 80
        self._v("title", title, "text;html=1;fontSize=24;fontStyle=1;fontColor=#1F3864;align=center;verticalAlign=middle;", 40, 20, inner, 36)
        self._v("takeaway", takeaway, "text;html=1;whiteSpace=wrap;fontSize=14;fontStyle=2;fontColor=#404040;align=center;verticalAlign=middle;", 40, 56, inner, 28)

    def _v(self, id_, value, style, x, y, w, h):
        self.cells.append(
            f'        <mxCell id="{id_}" value="{escape(value, quote=True)}" style="{style}" vertex="1" parent="1">\n'
            f'          <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" />\n        </mxCell>')

    def zone(self, id_, label, color, x, y, w, h, header=34):
        c = PALETTE[color]
        self._v(id_, label, f"swimlane;html=1;whiteSpace=wrap;startSize={header};fontSize={14 if header >= 34 else 13};fontStyle=1;fontColor=#ffffff;fillColor={c[0]};strokeColor={c[0]};swimlaneFillColor={c[1]};rounded=1;arcSize=4;", x, y, w, h)

    def box(self, id_, html, color, x, y, w, h, shape="process", key=False, dashed=False, font=None, fill=None):
        c = PALETTE[color]
        size = font or (14 if key else 12)
        style = (SHAPES[shape] + "whiteSpace=wrap;html=1;align=center;verticalAlign=middle;"
                 f"fillColor={fill or (c[2] if key else c[3])};strokeColor={c[0]};strokeWidth={3 if key else 2};"
                 f"fontSize={size};fontColor={c[4]};" + ("shadow=1;" if key else "") + ("dashed=1;" if dashed else ""))
        self._v(id_, html, style, x, y, w, h)

    def text(self, id_, html, x, y, w, h, color="#404040", size=12, italic=False, align="center"):
        self._v(id_, html, f"text;html=1;whiteSpace=wrap;fontSize={size};fontColor={color};align={align};verticalAlign=middle;" + ("fontStyle=2;" if italic else ""), x, y, w, h)

    def cell_grid(self, prefix, x, y, col_widths, row_heights, rows, styles=None, header_h=22, rownum_w=30):
        """Spreadsheet grid. rows[i] = list of cell texts; styles[(r, c)] = extra style."""
        styles = styles or {}
        base = "whiteSpace=wrap;html=1;align=center;verticalAlign=middle;fontSize=10;"
        head = base + "fillColor=#DCE6F2;strokeColor=#9DB3CF;fontStyle=1;fontColor=#33475B;"
        self._v(f"{prefix}_corner", "", head, x, y, rownum_w, header_h)
        cx = x + rownum_w
        for j, w in enumerate(col_widths):
            self._v(f"{prefix}_col{j}", chr(65 + j), head, cx, y, w, header_h)
            cx += w
        cy = y + header_h
        for i, (h, vals) in enumerate(zip(row_heights, rows)):
            self._v(f"{prefix}_row{i + 1}", str(i + 1), head, x, cy, rownum_w, h)
            cx = x + rownum_w
            for j, w in enumerate(col_widths):
                extra = styles.get((i + 1, j), "fillColor=#FFFFFF;strokeColor=#B7C6D8;fontColor=#1B2733;")
                self._v(f"{prefix}_{chr(65 + j)}{i + 1}", vals[j] if j < len(vals) else "", base + extra, cx, cy, w, h)
                cx += w
            cy += h
        return cy

    def edge(self, id_, src, dst, label="", color="blue", exit=(1, 0.5), entry=(0, 0.5), points=(),
             dashed=False, dotted=False, both=False, width=2.5, label_bg="#ffffff"):
        c = PALETTE[color]
        style = ("edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;"
                 f"strokeColor={c[0]};strokeWidth={width};endArrow=block;endFill=1;"
                 + ("startArrow=block;startFill=1;" if both else "")
                 + ("dashed=1;" if dashed or dotted else "") + ("dashPattern=2 3;" if dotted else "")
                 + f"fontSize=11;fontColor={c[5]};labelBackgroundColor={label_bg};"
                 f"exitX={exit[0]};exitY={exit[1]};entryX={entry[0]};entryY={entry[1]};")
        pts = ""
        if points:
            pts = '\n            <Array as="points">' + "".join(f'<mxPoint x="{a}" y="{b}" />' for a, b in points) + "</Array>\n          "
        self.cells.append(
            f'        <mxCell id="{id_}" value="{escape(label, quote=True)}" style="{style}" edge="1" parent="1" source="{src}" target="{dst}">\n'
            f'          <mxGeometry relative="1" as="geometry">{pts}</mxGeometry>\n        </mxCell>')

    def legend(self, html, y=None):
        self._v("legend", html, "text;html=1;whiteSpace=wrap;fontSize=12;fontColor=#404040;align=center;verticalAlign=middle;", 40, y or self.height - 50, self.width - 80, 30)

    def xml(self) -> str:
        return ('<mxfile host="drawio" agent="drawio-architecture">\n'
                f'  <diagram id="{self.page_id}" name="{escape(self.name, quote=True)}">\n'
                f'    <mxGraphModel dx="{self.width}" dy="{self.height}" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{self.width}" pageHeight="{self.height}" math="0" shadow="0">\n'
                '      <root>\n        <mxCell id="0" />\n        <mxCell id="1" parent="0" />\n'
                + "\n".join(self.cells) + "\n      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>\n")

    def save(self, path) -> Path:
        out = Path(path)
        out.write_text(self.xml(), encoding="utf-8", newline="\n")
        return out


# ---------------------------------------------------------------- text fit

_TAG = re.compile(r"<[^>]+>")
_BR = re.compile(r"<br\s*/?>", re.I)
_USABLE = {"cloud": 0.6, "hexagon": 0.85}


def _style(s: str) -> dict:
    return dict(p.split("=", 1) for p in s.split(";") if "=" in p) | {p: "" for p in s.split(";") if p and "=" not in p}


def text_fit_problems(path) -> list[str]:
    """Estimate label size against its box; return the labels that would clip."""
    import html as _h
    probs = []
    for cell in ET.parse(path).iter("mxCell"):
        value, raw = cell.get("value") or "", cell.get("style") or ""
        geo = cell.find("mxGeometry")
        if cell.get("vertex") != "1" or not value or geo is None:
            continue
        st = _style(raw)
        w, h = float(geo.get("width", 0)), float(geo.get("height", 0))
        fs = float(st.get("fontSize", 12))
        if "swimlane" in st:
            start = float(st.get("startSize", 23))
            need = len(_h.unescape(_TAG.sub("", value))) * fs * 0.62 + 20
            if need > w:
                probs.append(f"{cell.get('id')}: zone header needs ~{need:.0f}px, has {w:.0f}px")
            continue
        shape = st.get("shape", "")
        factor = next((f for k, f in _USABLE.items() if k in shape), 1.0)
        usable = w * factor - 16
        lines = 0
        for part in _BR.split(value):
            bold = "<b>" in part.lower() or st.get("fontStyle") == "1"
            txt = _h.unescape(_TAG.sub("", part)).replace("\u00a0", " ").strip()
            cw = fs * (0.6 if bold else 0.55)
            longest_word = max((len(t) for t in txt.split()), default=0) * cw
            if longest_word > usable and not raw.startswith("text;"):
                probs.append(f"{cell.get('id')}: word too wide ({longest_word:.0f}px > {usable:.0f}px) in {txt[:40]!r}")
            lines += max(1, math.ceil(len(txt) * cw / max(usable, 1)))
        need_h = lines * fs * 1.25
        avail = h * (0.75 if factor < 1 else 1.0) - 6
        if need_h > avail:
            probs.append(f"{cell.get('id')}: {lines} lines need ~{need_h:.0f}px, box has {avail:.0f}px")
    return probs


if __name__ == "__main__":
    bad = 0
    for f in sys.argv[1:]:
        for p in text_fit_problems(f):
            print(f"{f}: {p}")
            bad += 1
    sys.exit(1 if bad else 0)
