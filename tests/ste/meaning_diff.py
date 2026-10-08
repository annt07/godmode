"""Compare the structure of skill files with a base git ref.

Usage: python tests/ste/meaning_diff.py BASE_REF FILE...

Reports a change in: the frontmatter name, the presence of the description key,
code blocks and inline code, links, godmode: references, numbers in prose, the
number of table rows (header counts, separator does not), the number of list
items per section, and the words REQUIRED, STOP, MUST and Never.
Exit 0 when nothing changed, 1 when a file reports a change.
"""
import collections
import re
import subprocess
import sys

FRONT = re.compile(r"^---\n(.*?)\n---\n", re.S)
SEPARATOR = re.compile(r"^\|?[\s:|-]+\|?$")


def facts(text):
    text = text.replace("\r\n", "\n")
    fm = FRONT.match(text)
    body = text[fm.end():] if fm else text
    f = collections.OrderedDict()
    f["name"] = re.findall(r"^name:\s*(.+)$", fm.group(1), re.M) if fm else []
    f["description-key"] = [bool(fm and re.search(r"^description:", fm.group(1), re.M))]
    fences = re.findall(r"^(?:```|~~~).*?^(?:```|~~~)", body, re.S | re.M)
    no_fence = re.sub(r"^(?:```|~~~).*?^(?:```|~~~)", " ", body, flags=re.S | re.M)
    f["code"] = sorted(fences + re.findall(r"`[^`\n]+`", no_fence))
    f["link"] = sorted(re.findall(r"\]\(([^)]+)\)", no_fence))
    f["godmode-ref"] = sorted(re.findall(r"godmode:[a-z0-9-]+", body))
    prose = re.sub(r"`[^`\n]+`|\]\([^)]+\)", " ", no_fence)
    f["number"] = sorted(re.findall(r"(?<![\w.-])\d+(?:\.\d+)?%?(?![\w-])", prose))
    rows = [l.strip() for l in no_fence.splitlines() if l.strip().startswith("|")]
    f["table-rows"] = [sum(1 for l in rows if not SEPARATOR.match(l))]
    sections, current = collections.Counter(), "(top)"
    for line in no_fence.splitlines():
        if line.startswith("#"):
            current = line.strip()
        elif re.match(r"^\s*(?:[-*+]|\d+[.)])\s", line):
            sections[current] += 1
    f["list-items"] = sorted(sections.items())
    f["strong-words"] = sorted(re.findall(r"\b(REQUIRED|STOP|MUST|Never)\b", body))
    return f


def compare(old, new):
    a, b = facts(old), facts(new)
    out = []
    for key in a:
        if a[key] != b[key]:
            if isinstance(a[key], list) and key not in ("table-rows", "description-key", "list-items"):
                lost = sorted((collections.Counter(a[key]) - collections.Counter(b[key])).elements())
                added = sorted((collections.Counter(b[key]) - collections.Counter(a[key])).elements())
                out.append(f"{key}: removed {lost!r} added {added!r}"[:800])
            else:
                out.append(f"{key}: {a[key]!r} -> {b[key]!r}"[:800])
    return out


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    base, files, changed = argv[0], argv[1:], 0
    if not re.fullmatch(r"[A-Za-z0-9._/-]+", base) or base.startswith("-"):
        print(f"error: base ref {base!r} is not a plain git ref")
        return 2
    for path in files:
        old = subprocess.run(["git", "show", f"{base}:{path}"], capture_output=True,
                             text=True, encoding="utf-8").stdout
        new = open(path, encoding="utf-8").read()
        changes = compare(old, new) if old else ["new file (no base version)"]
        for c in changes:
            print(f"{path}: {c}")
        changed += bool(changes)
    print(f"{changed} of {len(files)} files changed structure")
    return 1 if changed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
