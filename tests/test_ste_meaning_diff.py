"""Meaning seam: tests/ste/meaning_diff.py reports structural changes between two versions of a file."""
import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("meaning_diff", ROOT / "tests/ste/meaning_diff.py")
md = importlib.util.module_from_spec(spec)
spec.loader.exec_module(md)

OLD = ("---\nname: x\ndescription: d\n---\n# A\n- Use `cmd` 3 times.\n"
       "- See [doc](d.md) and `godmode:grilling`.\n\n| a | b |\n|---|---|\n| 1 | 2 |\n\nYou MUST stop.\n")


def test_identical_structure_reports_nothing():
    new = OLD.replace("- Use `cmd` 3 times.", "- Run `cmd` 3 times.")
    assert md.compare(OLD, new) == []


def test_each_structural_change_is_reported():
    cases = {
        "name": OLD.replace("name: x", "name: y"),
        "description-key": OLD.replace("description: d\n", ""),
        "code": OLD.replace("`cmd`", "`cmd2`"),
        "number": OLD.replace("3 times", "4 times"),
        "link": OLD.replace("(d.md)", "(e.md)"),
        "godmode-ref": OLD.replace("godmode:grilling", "godmode:brainstorming"),
        "table-rows": OLD.replace("| 1 | 2 |\n", "| 1 | 2 |\n| 3 | 4 |\n"),
        "list-items": OLD.replace("- See", "See"),
        "strong-words": OLD.replace("You MUST stop.", "You stop."),
    }
    for kind, new in cases.items():
        assert any(c.startswith(kind) for c in md.compare(OLD, new)), kind
