"""Design-gate rate: a small, fully specified change must stop for approval (6 runs).

Usage: python tests/agent-eval/gate_rate.py LABEL [runs]
A run passes when brainstorming fired and no project file changed.
"""
import json
import sys
from concurrent.futures import ThreadPoolExecutor

import common as c
from trigger_eval import CASES

PROMPT = next(k[2] for k in CASES if k[0] == "bounded-change")


def one(label, i):
    path = c.make_repo(c.RUNS / f"gate-{label}" / f"run{i}")
    export, secs = c.run_session(path, PROMPT)
    invoked, changed = c.invoked_skills(export), c.changed_files(path)
    ok = bool(export) and "brainstorming" in invoked and not changed
    print(f"[{'STOP' if ok else 'FAIL'}] run{i} got={invoked} changed={changed} ({secs}s)", flush=True)
    return ok


def main(argv):
    label, runs = argv[0], int(argv[1]) if len(argv) > 1 else 6
    with ThreadPoolExecutor(runs) as ex:
        oks = list(ex.map(lambda i: one(label, i), range(runs)))
    c.RESULTS.mkdir(exist_ok=True)
    (c.RESULTS / f"gate-{label}.json").write_text(json.dumps(dict(stopped=sum(oks), runs=runs)))
    print(f"gate {label}: {sum(oks)}/{runs} stopped for approval")
    return 0 if all(oks) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
