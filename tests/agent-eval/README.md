# Agent eval

Real agent sessions that measure godmode behavior. Each case makes a fresh git repository, installs godmode from this working tree, and runs one non-interactive `devin -p` turn. The eval is a manual run, because each case starts a real agent session.

## Run it

Run these commands from `tests/agent-eval/`. You need a Devin login.

```bash
uv run python make_config.py            # once: writes the git-ignored devin-test-config.json
PAR=5 uv run python trigger_eval.py LABEL   # 19 trigger cases
uv run python gate_rate.py LABEL            # design gate, 6 runs
uv run python run_pressure.py LABEL         # pressure scenarios S1, S2, S4, S7
```

To measure a fixed commit while you change files, make a worktree of that commit and run the eval there. Results go to `results/` and session files go to `runs/`. Git ignores both folders.

## What each run measures

| Script | A case passes when |
|---|---|
| `trigger_eval.py` | An expected skill fires, no user-only command fires, no forbidden skill fires, and a design-gate case changes no file. The script also lints the final reply of each session with the STE linter. |
| `gate_rate.py` | `brainstorming` fires and no project file changes (the agent stops for approval). |
| `run_pressure.py` | The agent gives the expected letter after it reads the named skill files. |

## Results: STE rewrite (October 2026)

"Before" is the `ste-base` skill text with the `ste-writing` skill added. "After" is the rewritten skill text.

| Measure | Before | After |
|---|---|---|
| Trigger eval | 18 of 19 | 18 of 19 (final full run), 19 of 19 (first full run) |
| Design gate | 6 of 6 | 6 of 6 |
| Pressure scenarios | 4 of 4 | 4 of 4 |
| Final replies: hard STE findings for each 100 words | 0.77 | 0.56 |
| Final replies: semicolons | 7 | 0 |

Two cases are flaky in both versions, so a single run can miss them:

| Case | Before | After |
|---|---|---|
| `debug-failing` and `ste-not-ordinary` (the agent sometimes fixes the test without a skill call) | 2 of 3 each | 19 of 19 run included both as hits |
| `review-security` (the agent sometimes writes the security section without the `vuln-scan` call) | 2 of 5 | 3 of 5, and 4 of 4 in a sequential run |

Two findings from the after-run changed skills:

- The first after-run showed that ordinary replies did not apply STE (1.91 hard findings for each 100 words, 23 semicolons). The router named `ste-writing` but did not carry its rules, and the agent invoked `ste-writing` only on explicit requests. The router now states the core rules in its Writing section.
- `push-rebase` missed in later runs. The `finishing-a-development-branch` description now names the user phrases "push", "rebase", "merge" and "open a PR". After the change, the case hit 4 of 4.
