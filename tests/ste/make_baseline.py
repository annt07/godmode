"""Write tests/ste/advisory-baseline.json: advisory counts per file and rule.

Run once at the ste-base tag (before the rewrite). Later, lower entries by hand
when a reviewer accepts the remaining advisory findings of a file.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests"))
import test_ste_conformance as c  # noqa: E402

counts = {}
for path, text in c.targets():
    for f in c.lint(text, path):
        if f["rule"] in c.ADVISORY:
            counts.setdefault(path, {r: 0 for r in sorted(c.ADVISORY)})[f["rule"]] += 1
out = ROOT / "tests/ste/advisory-baseline.json"
out.write_text(json.dumps(counts, indent=1, sort_keys=True) + "\n", encoding="utf-8")
print(f"{len(counts)} files with advisory findings -> {out}")
