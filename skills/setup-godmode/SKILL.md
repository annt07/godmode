---
name: setup-godmode
description: Install, update or remove godmode for one repo or for all repos. Connect the bootstrap, so that the skills start automatically and not only when the user names them.
disable-model-invocation: true
---

# Setup godmode

The godmode skills start automatically only when the router (`using-godmode`) loads at the start of each session. A plugin install does that with a session-start hook. A copied install needs a **bootstrap block** in an instructions file. Without it, the agent uses godmode only when the user names a skill.

This skill runs `scripts/install.mjs` (Node 18+, no dependencies). It installs only the skills and the bootstrap block. It creates no project docs. (`CONTEXT.md`, ADRs and `.scratch/` folders come later, when the skills that own them need them.) Explore, show what you found, and get the approval of the user. Then run.

## Rules the installer enforces

- **Shared instruction files are never modified.** In a repo, the installer puts the bootstrap block into a local instructions file (`AGENTS.local.md` by default). `--help` lists the names for each tool. If the file is missing, it creates the file. If the file is present, it adds the block to the end.
- **Nothing becomes tracked.** The installer adds the local file and the skills folder to `.git/info/exclude`. It refuses to edit an instructions file that git already tracks.
- **Only godmode's own skills are replaced or removed** (listed in `.godmode-manifest.json`). The installer skips skills of the user with the same names, unless you use `--force`. That option makes a backup of them.

## Process

### 1. Explore

- Find which repo the user means (the current directory unless they named one). Find whether it is a git repo.
- Find which agent the user works with here. `--tool` selects the skills folder and local file that the agent reads. Most agents read the default, `agents` (`.agents/skills` + `AGENTS.local.md`). `node <this skill>/scripts/install.mjs --help` lists the other values.
- Run `node <this skill>/scripts/install.mjs doctor --repo <path>`. It shows any existing install and whether a bootstrap block exists. It also shows competing routers or rules (other skill routers, original versions of merged skills, old godmode blocks in shared files).
- Run the install one time with `--dry-run` and the options that you plan to recommend.

### 2. Present findings and ask

Ask one question at a time. Start with the recommendation:

1. **Scope:** this repo (recommended, local and untracked), or `--global` for all repos. That option needs a `--tool` that has a user-level instructions file. `--help` says which tools have one.
2. **Tool:** `agents`, unless the agent of the user reads a different folder.
3. **Subagents:** the block gives standing permission for the steps where godmode skills dispatch subagents. Some agents refuse subagents unless the user asks. Recommend yes. `--no-subagents` omits it.
4. **Conflicts** that the doctor reported: ask whether to remove each one. The installer never changes them. Remove one by hand only after an explicit yes. The user edits the shared instruction files.

<!-- ste:off -->
### 3. Confirm and run
<!-- ste:on -->

Show the exact command and the block that the dry run printed. If the user says yes, run:

```
node "<this skill>/scripts/install.mjs" install --repo <path> [--tool <name>] [--global] [--no-subagents] [--source <godmode repo>]
```

From any location, without a local copy: `npx github:annt07/godmode install --repo <path>`. A second run updates in place. `uninstall` removes only the skills in the manifest and the block.

### 4. Verify

- `node <this skill>/scripts/install.mjs doctor --repo <path>` reports the install and the bootstrap block.
- `git status` shows nothing new.
- Tell the user to open a **new** session (the block loads at session start) and to request a small feature. The agent should announce `brainstorming` before it writes code.

### 5. Done

Report the scope, the changed folders and files, any backups, and the warnings that remain for the user.
