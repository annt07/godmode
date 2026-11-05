"""Check hand-designed .drawio pages: validator + text fit, zone noise removed.

Usage: python check.py FILE.drawio [...]   (exit 1 on any real problem)
"""

from __future__ import annotations

import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from drawio_kit import text_fit_problems  # noqa: E402

VALIDATE = HERE / "validate.py"
QUOTED = re.compile(r"'([^']+)'")


def zone_ids(path) -> set[str]:
    return {c.get("id") for c in ET.parse(path).iter("mxCell") if "swimlane" in (c.get("style") or "")}


def main(files: list[str]) -> int:
    bad = 0
    for f in files:
        zones = zone_ids(f)
        run = subprocess.run([sys.executable, str(VALIDATE), f, "--score"], capture_output=True, text=True)
        out = (run.stdout + run.stderr).splitlines()
        real = []
        for line in out:
            if line.startswith("error"):
                real.append(line)
            elif line.startswith("warning"):
                ids = QUOTED.findall(line)
                subjects = ids[1:] if "W-EDGE-THROUGH-VERTEX" in line else ids
                if ("W-OVERLAP" in line or "W-EDGE-THROUGH-VERTEX" in line) and any(i in zones for i in subjects):
                    continue
                real.append(line)
        score = next((l for l in out if l.startswith("score")), "score: ?")
        crossings = re.search(r"(\d+) crossings", score)
        if crossings and crossings.group(1) != "0":
            real.append(f"{crossings.group(1)} edge crossings")
        fit = text_fit_problems(f)
        print(f"== {f}\n   {score}")
        for p in real + [f"text-fit: {p}" for p in fit]:
            print(f"   {p}")
        if not real and not fit:
            print("   OK")
        bad += len(real) + len(fit)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
