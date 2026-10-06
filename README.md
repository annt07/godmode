# Godmode

**Superpowers' autonomous pipeline, with Matt Pocock's engineering skills wired in at every stage.**

Godmode is a skill set for coding agents (Devin CLI, Claude Code, Cursor, Codex, Gemini CLI). It combines two open-source skill libraries into one set with a single router:

- **[Superpowers](https://github.com/obra/superpowers)** (Jesse Vincent) is the driver: brainstorm, plan, execute with subagents, review, finish the branch. It runs autonomously, with approval gates and red-flag tables that stop the agent from talking its way past the process.
- **[Matt Pocock's skills](https://github.com/mattpocock/skills)** supply the engineering depth: grilling, deep-module design, domain modeling, TDD at agreed seams, two-axis code review, prototypes, research.

In short: Superpowers makes the agent disciplined and able to run alone; Matt Pocock's skills keep the human in charge of the decisions that set precision. Godmode automates the running and brings those few decisions back to you at a moment when you're there to make them.

You don't call pipeline skills by hand. A session-start hook (plugin install) or a bootstrap block in your instructions file (manual install, written by `setup-godmode`) loads the `using-godmode` router, and the router invokes the right skill at each step. **Without one of the two, the skills only fire when you name them.**

---

## Contents

- [How it works](#how-it-works)
- [Skills](#skills)
- [Installation](#installation)
- [Check that it works](#check-that-it-works)
- [What godmode writes in your projects](#what-godmode-writes-in-your-projects)
- [Repository layout](#repository-layout)
- [How it was tested](#how-it-was-tested)
- [Design decisions](#design-decisions)
- [Changing a skill](#changing-a-skill)
- [Credits and license](#credits-and-license)

---

## How it works

```
 you ask for something
        │
        ▼
 using-godmode (router, injected at session start)
        │
        ▼
 brainstorming ── classifies the request: Spike / Bounded / Architectural
        │           grilling: numbered questions, each with a recommended answer
        │           domain-modeling: CONTEXT.md + ADRs as terms get settled
        │           codebase-design: modules, interfaces, seams
        │
        ├─ Spike ─────────► prototype (throwaway, captured on a prototype/ branch)
        │
        ├─ Bounded ───────► short design in chat ──► YOUR YES ──► test-driven-development
        │                                                          ──► verification-before-completion
        │
        └─ Architectural ─► to-spec ──► YOUR SPEC APPROVAL ──► writing-plans ──► YOUR PLAN APPROVAL
                                                                  │
                                    ┌─────────────────────────────┘
                                    ▼
                  subagent-driven-development  or  executing-plans
                     (TDD at each task's agreed seam, research on factual gaps,
                      wizard for human-only steps, per-task Spec + Standards review)
                                    │
                                    ▼
                  requesting-code-review (parallel: Standards + Spec + vuln-scan security pass)
                                    │
                                    ▼
                  finishing-a-development-branch ──► resolving-merge-conflicts
```

**Your decisions**, made while you're present: the requirements (grilling), the test seams (the Bounded design, or the spec's Testing Decisions), and the spec and plan approvals.

**Automated**: everything after the plan is approved runs without stopping, reusing those decisions. Only four things stop an automated run: an irreversible or destructive action, a security-sensitive action, a side effect outside the worktree (merge, push, publish), or a plan so broken that every path forward is a guess.

---

## Skills

33 skills: 26 the agent uses on its own, and 7 commands only you can run.

### Pipeline (from Superpowers)

| Skill | What it does | Matt Pocock depth added |
|---|---|---|
| `using-godmode` | Router: loads at session start, maps situations to skills, red flags against skipping them | Lifecycle map, programmer commands, Windows notes |
| `brainstorming` | Spike / Bounded / Architectural classification and approval gates before any code | `grilling` for every question, `codebase-design`, `domain-modeling`, `to-spec`, `prototype` |
| `writing-plans` | Task-by-task plans an agent with no context can execute | Tracer-bullet slicing, Demo + Fails-at-base per task, prefactoring first, expand–migrate–contract, agreed seams |
| `subagent-driven-development` | Fresh implementer subagent per task, task review, fix loop, ledger, final review | Two-axis review (Spec + Standards with Fowler smells), `research`, `wizard`, seam discipline |
| `executing-plans` | The same plan, run inline in one session | Same additions, with a two-axis final review |
| `test-driven-development` | Iron-law RED → GREEN | Test only at pre-agreed seams, vertical slices, refactoring moved to review, mocking guide |
| `systematic-debugging` | Root cause before any fix | Feedback loop first (10 ways to build one), cleanup phase, "no correct seam" → architecture follow-up |
| `requesting-code-review` | Review before merge, and any "review this" request | Standards axis + Spec axis as parallel reviewers, the 12 Fowler smells, plus a required `vuln-scan` security pass |
| `receiving-code-review` | Weigh review feedback technically, not performatively | – |
| `verification-before-completion` | No "done" without fresh evidence | – |
| `finishing-a-development-branch` | Test, choose merge / PR / keep, clean up | Conflict check → `resolving-merge-conflicts` |
| `using-git-worktrees` | Isolated workspace for the work | – |
| `dispatching-parallel-agents` | Parallel subagents for independent problems | – |
| `writing-skills` | TDD for skill documents (pressure tests) | `writing-for-agents` for the prose |
| `diagnosing-godmode` | Evidence-based report on a session that went wrong (local only, never filed upstream) | – |

### Engineering (from Matt Pocock, used automatically)

| Skill | When it runs |
|---|---|
| `grilling` | Every clarifying question: rounds of numbered questions, each with a recommended answer; writes CONTEXT.md and ADRs as it goes |
| `codebase-design` | Module boundaries, interfaces, seams; deep-module vocabulary, deepening guide, design-it-twice |
| `domain-modeling` | Fuzzy or overloaded terms; keeps `CONTEXT.md` and `docs/adr/` current |
| `to-spec` | Writes the structured spec at the end of the Architectural path |
| `prototype` | Throwaway code that answers a feasibility or design question, captured on a `prototype/` branch |
| `research` | Background agent answers factual questions from primary sources, writing a cited Markdown file |
| `resolving-merge-conflicts` | Any merge or rebase conflict: resolves by each side's intent, then runs the checks |
| `improve-codebase-architecture` | "Refactor / make testable" requests: HTML report of deepening opportunities, then grilling on the one you pick |
| `wizard` | A step only a human can do (credentials, CI secrets, dashboards, cutovers): generates a guided script instead of pasting steps or asking for secrets |
| `writing-for-agents` | Writing skills, AGENTS.md, CLAUDE.md, plans and briefs for agent readers |

### Security (used automatically)

| Skill | When it runs |
|---|---|
| `vuln-scan` | The security pass of every code review (diff-scoped, no prompts, artifacts under `.godmode/security/`), and any request to scan code for vulnerabilities. Threat model, find, triage, JSON report. Covers injection, deserialization, authn/authz, secrets, **PHI/PII exposure**, SSRF, TLS/crypto, **LLM/agent risks**, dependencies, memory safety. |

Three more Matt Pocock skills are merged into the pipeline instead of standing alone: `tdd` → `test-driven-development`, `diagnosing-bugs` → `systematic-debugging`, `code-review` → `requesting-code-review`. The ideas from `implement`, `grill-with-docs` and `to-tickets` live inside `executing-plans` / `subagent-driven-development`, `grilling` and `writing-plans`.

### Programmer commands (user-invoked only)

The agent never fires these. They're marked `disable-model-invocation: true` (and `agents/openai.yaml` for Codex), so they cost nothing in the agent's context. The first five come from Matt Pocock.

| Command | Use it when |
|---|---|
| `/wait-what` | The agent's last message didn't land: it re-explains with the missing context, in plain English, using CONTEXT.md terms |
| `/handoff` | The work has to move to a new tool, a new directory, a colleague, or a side session |
| `/grill-me` | You want a grilling session with no repo under it (writes no files) |
| `/to-questionnaire` | A decision needs someone else's knowledge: turns it into a questionnaire for them |
| `/teach` | You want to learn a topic over several sessions |
| `/mr-full-review <url or number>` | A full review of a GitLab MR or a GitHub / Bitbucket (Cloud or Server) PR. The provider is detected from the URL or the `origin` remote. Read-only: it never posts. The report goes to `.scratch/<ticket or mr/pr folder>/<mr\|pr>-<n>-review-round-<N>.md`, and from round 2 it tracks which earlier findings were fixed |
| `/setup-godmode` | Install, update or remove godmode for one repo or for every repo, and write the bootstrap block that makes the skills fire on their own |

With a plugin install on Devin the commands are namespaced, for example `/godmode:grill-me`.

**Tokens for `/mr-full-review`** (set in your environment; the skill never searches for them): `GITLAB_TOKEN` (`read_api`), `GITHUB_TOKEN` or `GH_TOKEN` (pull request read), `BITBUCKET_TOKEN` (Bitbucket Cloud also accepts `BITBUCKET_USERNAME` + `BITBUCKET_APP_PASSWORD`). Hosts whose name doesn't reveal the provider: `GODMODE_GIT_PROVIDERS="git.corp.example=gitlab,code.corp.example=bitbucket-server"`.

**Not included:** `ask-matt` (replaced by the router), `triage` and `wayfinder` (need an issue tracker), `setup-matt-pocock-skills` (replaced by `setup-godmode`).

---

## Installation

**Before you install:**

- Remove Superpowers and mattpocock-skills from the same tool. Godmode already contains what it needs from both, and two routers in one session fight each other.
- On Windows, install [Git for Windows](https://git-scm.com/download/win). The hook and the plan scripts run in Git Bash.

| Setup | Guide |
|---|---|
| **Devin CLI** plugin (all projects) | [INSTALL.md → Devin CLI](INSTALL.md#devin-cli). On Windows, local-path installs need symlink rights, so the guide installs from a localhost git server instead. |
| **Claude Code** plugin | [INSTALL.md → Claude Code](INSTALL.md#claude-code): `/plugin marketplace add <path>`, then `/plugin install godmode@godmode-local` |
| **Cursor**, **Codex** | [INSTALL.md → Option A](INSTALL.md#option-a-install-as-a-plugin-recommended) |
| **`npx github:annt07/godmode`** in any repo (recommended without a plugin) | [Installer](#installer-npx-straight-from-github-no-npm-registry) below |
| **Manual, machine-wide** (any tool) | [INSTALL.md → Option B](INSTALL.md#option-b-manual-install-no-plugin-system) |
| **One project only, by hand** | [INSTALL-LOCAL-PROJECT.md](INSTALL-LOCAL-PROJECT.md) |

### Installer: `npx` straight from GitHub (no npm registry)

Needs Node 18+ and git. Run it inside the repo:

```bash
npx github:annt07/godmode                 # install or update godmode in the current repo
npx github:annt07/godmode --dry-run       # preview every change
npx github:annt07/godmode doctor          # show install state, bootstrap, conflicts
npx github:annt07/godmode uninstall       # remove godmode's skills and its block
npx github:annt07/godmode --help
```

Pin a version with a tag or commit: `npx github:annt07/godmode#v1.1.0`. npm fetches the package from GitHub with git, so private repos work wherever your git credentials do. The package is marked `private`, so it can't be published to the npm registry by accident.

**What it does in a repo:**

| | |
|---|---|
| Skills | `.agents/skills/` (read by most agents). `--tool claude` uses `.claude/skills/`, `--tool devin` uses `.devin/skills/` |
| Bootstrap block | Prepended to a **local** file: `AGENTS.local.md` (`CLAUDE.local.md` for `--tool claude`), created or appended to |
| Git | Both paths go into `.git/info/exclude`, so `git status` stays clean. Nothing becomes tracked |
| Shared files | `AGENTS.md`, `CLAUDE.md`, etc. are **never modified**. It refuses to write to an instructions file git already tracks |
| Your skills | Only skills listed in `.godmode-manifest.json` are replaced or removed. Same-named skills of yours are skipped unless you pass `--force` (backed up first) |
| Conflicts | Competing routers, original Matt Pocock skills, "Always use Matt Pocock skills"-style rules and old godmode blocks in shared files are reported, never changed |
| Project docs | None. `CONTEXT.md`, ADRs and `.scratch/` folders are created later, by the skills that use them |

**Every repo at once:** `npx github:annt07/godmode --global --tool devin` (or `--tool claude`) installs into your user-level skills folder and user-level instructions file.

**Check your agent reads the local file:** the installer relies on your agent loading `AGENTS.local.md` / `CLAUDE.local.md`. If yours doesn't, point it at another untracked file with `--instructions-file <path>`.

The bootstrap block also grants godmode standing permission to use subagents, because some agents refuse them unless you ask. Pass `--no-subagents` to leave that out.

Once godmode is installed, `/setup-godmode` runs the same installer (`skills/setup-godmode/scripts/install.mjs`) conversationally: it explores, recommends, dry-runs, then installs.

---

## Check that it works

Open a fresh session and try these:

| Send | Expect |
|---|---|
| "Let's make a react todo list" (empty folder) | `brainstorming` → **Architectural** → a round of numbered questions with recommended answers. No files created. |
| A small, fully specified change to existing code | **Bounded** → "nothing left to ask" → a short design → it **stops for your yes** |
| "Yes, go ahead" | `test-driven-development` (failing test first) → code → `verification-before-completion` |
| "This test is failing, fix it" | `systematic-debugging` builds a feedback loop before proposing a fix |

On Devin, `devin skills list` (or `devin plugins list`) shows the installed skills. If the agent writes code in the same turn as a fully specified request, the router didn't load: see Troubleshooting in [INSTALL.md](INSTALL.md#troubleshooting).

---

## What godmode writes in your projects

| Artifact | Path |
|---|---|
| Specs | `docs/godmode/specs/YYYY-MM-DD-<topic>-design.md` |
| Plans | `docs/godmode/plans/YYYY-MM-DD-<feature>.md` |
| Plan ledger and review packages | `.godmode/sdd/<plan>/` (writes its own `.gitignore`) |
| Domain glossary and decisions | `CONTEXT.md`, `docs/adr/` |
| Research notes | `docs/research/<topic>-<date>.md`, unless the repo already has a convention |
| Prototypes | `prototype/<name>` branches |
| Architecture reports | `architecture-review-<timestamp>.html` in the system temp folder |
| Diagnosis reports | `~/.godmode/diagnosing-godmode/<session-id>/` |
| Security scan artifacts | `.godmode/security/<timestamp>-<scope>/` (`THREAT_MODEL.md`, `vulnerability_report.json`; self-ignoring) |
| MR/PR review reports (`/mr-full-review`) | `.scratch/<ticket or mr/pr folder>/<mr\|pr>-<n>-review-round-<N>.md` |
| Bootstrap block (installer) | Between `<!-- godmode:begin -->` and `<!-- godmode:end -->` at the top of the untracked `AGENTS.local.md` / `CLAUDE.local.md`, or your user-level instructions file with `--global` |

---

## Repository layout

```
godmode/
├── skills/                    33 skills, one folder each (SKILL.md + support files)
│   ├── using-godmode/         router (harness-neutral: no skill names a specific agent tool)
│   ├── subagent-driven-development/   prompts + scripts/ (task-brief, review-package, sdd-workspace)
│   ├── executing-plans/       scripts/ (task-start, task-done)
│   ├── requesting-code-review/        code-reviewer.md, fowler-smells.md
│   ├── vuln-scan/             scripts/vuln_agent.py (optional Agent SDK runner)
│   ├── mr-full-review/        scripts/review_request.py (GitLab/GitHub/Bitbucket, read-only), references/
│   ├── setup-godmode/         scripts/install.mjs (the installer; Node 18+, no dependencies)
│   └── ...
├── bin/godmode.mjs            npx entry point (calls the installer)
├── package.json               makes `npx github:annt07/godmode` work; private, never published
├── tests/                     node --test tests/ (installer), uv run --with pytest pytest tests (provider script)
├── hooks/
│   ├── session-start          injects the router into every session
│   ├── run-hook.cmd           Windows/Unix wrapper that finds bash
│   ├── hooks.json             SessionStart registration (Claude Code, Devin)
│   └── hooks-cursor.json      SessionStart registration (Cursor)
├── .claude-plugin/            Claude Code manifest + local marketplace
├── .devin-plugin/             Devin manifest
├── .cursor-plugin/            Cursor manifest
├── .codex-plugin/             Codex manifest
├── .agents/plugins/           local marketplace entry
├── .gitattributes             forces LF on scripts (bash breaks on CRLF)
├── INSTALL.md                 plugin and machine-wide installation
├── INSTALL-LOCAL-PROJECT.md   single-project installation
└── LICENSE                    MIT, with the upstream copyright notices
```

---

## How it was tested

- **Pressure tests (the `writing-skills` method):** 12 scenarios, each pitting a changed rule against deadlines, authority and sunk cost. Each scenario was run by a subagent with and without godmode. Every with-godmode run chose the correct option. Two loopholes the runs exposed were closed and re-tested.
- **Real Devin CLI sessions:** godmode installed as a Devin plugin, with no bootstrap line, so the hook alone had to load the router. 23 scenarios covered every model-invoked skill, both invocation checks for the user-only commands, and the hook. **All 23 pass** on this version: the right skill fires, the approval gates hold, tests pass, and the repo is left in the expected state.
- **Trigger eval (real Devin sessions, installed with `setup-godmode`):** 17 real-world phrasings, each of which should fire one specific skill, with design-gate cases also failing if any file changed. **17/17** on this version, including `vuln-scan` on every review request. User-only commands never fired on their own. Without the bootstrap, research and brainstorming were dropped, which is why the installer always writes it. The eval also caught the agent treating "that is the whole spec" as design approval (3 of 4 runs wrote code); after the fix, 6 of 6 runs stopped for approval, and the "yes" turn then ran TDD and verification.
- **`/mr-full-review` without a token:** detects the provider, names the missing variable, never echoes token variables, leaves the repo clean.
- **Unit tests:** 27 offline pytest tests for the provider script (detection for all four providers, normalisation, pagination, CI, read-only) and 16 `node --test` tests for the installer (local-only writes, shared files untouched, tracked-file refusal, git status clean, idempotency, BOM/CRLF, foreign skills, stale removal, uninstall, global scope, conflict reports, the npx entry point). The packed package was also run through `npx` in a scratch repo.
- **Automated file checks:** valid hook JSON for Claude Code, Cursor and generic formats; all shell scripts pass `bash -n`; skill names match their folders; every `godmode:` reference points to a real skill; no broken links.

Problems found and fixed while testing:

- Devin reads a SessionStart `matcher` as a tool-name filter, so the hook now has no matcher.
- Scripts had CRLF line endings; `.gitattributes` now forces LF.
- On Windows a plain `bash` can be WSL; the router now tells the agent to use Git Bash.
- Agents did test-first work without invoking the TDD skill; the router and `executing-plans` now require the skill call.
- Prototypes weren't being captured; `prototype` now has a concrete branch procedure.

**Not yet covered:** a full multi-turn Architectural run from spec to merged branch, and end-to-end runs on Claude Code, Cursor and Codex.

---

## Design decisions

| Decision | Why |
|---|---|
| One router (`using-godmode`), not two | Running both upstream routers at once makes them fight over routing and TDD philosophy |
| Grilling replaces one-question-at-a-time brainstorming | Each round asks everything that's already answerable, with a recommended answer per question |
| Refactoring moves from the TDD loop to review | Matt Pocock's position: keep RED → GREEN tight; the Standards review surfaces the smells |
| Seams are agreed when you approve the design or spec, then reused | Precision decisions stay with the human without stopping automated runs to ask |
| Per-task review: one reviewer with two verdicts; final review: two parallel reviewers | Keeps the per-task cost flat (Superpowers' single task reviewer) while keeping the axes separate (Matt Pocock's two-axis review) |
| `to-spec` and `improve-codebase-architecture` changed from user-invoked to automatic | The pipeline needs them at fixed points; a refactor still goes back through brainstorming's approval gates |
| `diagnosing-godmode` writes local reports only | Godmode is a local skill set; bug reports never go to the upstream trackers |

---

## Changing a skill

Skills are code that shapes agent behaviour. Before changing one:

1. Use `writing-skills`: write a pressure scenario, and watch an agent get it wrong without your change.
2. Make the smallest change that fixes it (`writing-for-agents` covers the prose). Never prune a red-flag row a test showed was needed.
3. Re-run the scenario and the checks in [How it was tested](#how-it-was-tested).
4. Keep the router in sync: a new or renamed skill needs an entry in `using-godmode`, or the router routes to something that doesn't exist.

---

## Credits and license

- Pipeline, discipline skills and hook machinery: **[Superpowers](https://github.com/obra/superpowers)** by Jesse Vincent, MIT.
- Engineering and productivity skills: **[mattpocock/skills](https://github.com/mattpocock/skills)** by Matt Pocock, MIT.

Godmode is released under the MIT License. See [LICENSE](LICENSE), which keeps both upstream copyright notices. Godmode is an independent combination, not affiliated with either project: report problems with it here, not upstream.
