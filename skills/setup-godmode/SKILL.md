---
name: setup-godmode
description: Install, update or remove godmode for one repo or for every repo, and wire the bootstrap so the skills fire on their own instead of only when named.
disable-model-invocation: true
---

# Setup godmode

godmode's skills only fire on their own when the router (`using-godmode`) loads at the start of every session. A plugin install does that with a session-start hook; a copied install needs a **bootstrap block** in an instructions file. Without it, the agent reaches godmode only when the user names a skill.

This skill runs `scripts/install.mjs` (Node 18+, no dependencies). It installs skills and the bootstrap block only; it creates no project docs (`CONTEXT.md`, ADRs and `.scratch/` folders appear later, when the skills that own them need them). Explore, present what you found, confirm, then run.

## Rules the installer enforces

- **Shared instruction files are never modified.** In a repo, the bootstrap block goes into a local instructions file (`AGENTS.local.md` by default; `--help` lists the per-tool names), created if missing and appended to if present.
- **Nothing becomes tracked.** The local file and the skills folder are added to `.git/info/exclude`. It refuses to edit an instructions file git already tracks.
- **Only godmode's own skills are replaced or removed** (listed in `.godmode-manifest.json`); same-named skills of the user's are skipped unless `--force`, which backs them up.

## Process

### 1. Explore

- Which repo the user means (the current directory unless they named one) and whether it is a git repo.
- Which agent the user works with here: `--tool` picks the skills folder and local file it reads. The default, `agents` (`.agents/skills` + `AGENTS.local.md`), is read by most agents; `node <this skill>/scripts/install.mjs --help` lists the other values.
- Run `node <this skill>/scripts/install.mjs doctor --repo <path>`: it shows any existing install, whether a bootstrap block exists, and competing routers or rules (other skill routers, original versions of merged skills, old godmode blocks inside shared files).
- Run the install once with `--dry-run` and the options you plan to recommend.

### 2. Present findings and ask

One question at a time, leading with the recommendation:

1. **Scope:** this repo (recommended; local and untracked), or `--global` for every repo (needs a `--tool` that has a user-level instructions file; `--help` says which).
2. **Tool:** `agents` unless the user's agent reads a different folder.
3. **Subagents:** the block grants standing permission for the steps where godmode skills dispatch subagents, because some agents refuse subagents unless the user asks. Recommend yes; `--no-subagents` omits it.
4. **Conflicts** the doctor reported: ask whether to remove each one. The installer never changes them; do it by hand only on an explicit yes. Shared instruction files stay the user's to edit.

### 3. Confirm and run

Show the exact command and the block the dry run printed. On yes:

```
node "<this skill>/scripts/install.mjs" install --repo <path> [--tool <name>] [--global] [--no-subagents] [--source <godmode repo>]
```

From anywhere, without a local copy: `npx github:annt07/godmode install --repo <path>`. Re-running updates in place; `uninstall` removes only manifest-listed skills and the block.

### 4. Verify

- `node <this skill>/scripts/install.mjs doctor --repo <path>` reports the install and the bootstrap block.
- `git status` shows nothing new.
- Ask the user to open a **new** session (the block loads at session start) and request a small feature: the agent should announce `brainstorming` before writing code.

### 5. Done

Report the scope, the folders and files changed, any backups, and the warnings left for the user.
