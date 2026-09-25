# Installing Godmode Into One Project

This guide installs godmode into a single repository: the skills live inside the repo, and only sessions opened in that repo use them. Nothing is written to your user profile, no plugin system is needed, and it works without admin rights or Windows Developer Mode.

Use this when:

- plugin install fails (on Windows, Devin's plugin install needs symlink rights; see Troubleshooting);
- you want godmode in one project without changing your other projects;
- you want the whole team to get godmode by cloning the repo.

For a machine-wide install, see [INSTALL.md](INSTALL.md).

> **Tested on:** Devin CLI on Windows, using `.devin/skills/` plus the `AGENTS.md` bootstrap. The Claude Code and Codex/Gemini paths below follow the same pattern, using each tool's documented project skill folder, but were not run end to end.

---

## What gets added to your project

```
<your-project>/
  .devin/skills/            the 30 godmode skill folders (or .claude/skills/, .agents/skills/)
    using-godmode/SKILL.md  the router
    brainstorming/SKILL.md
    ...
  AGENTS.md                 one bootstrap line (CLAUDE.md for Claude Code)
```

Godmode writes these while you work:

| Artifact | Path |
|----------|------|
| Specs | `docs/godmode/specs/` |
| Plans | `docs/godmode/plans/` |
| Plan ledger and review packages | `.godmode/sdd/`, which git-ignores itself |
| Domain glossary and decisions | `CONTEXT.md`, `docs/adr/` |

---

## Step 1: Pick the skill folder for your tool

| Tool | Project skill folder | Bootstrap file |
|------|----------------------|----------------|
| Devin CLI | `.devin/skills/` (also reads `.agents/skills/`, `.cognition/skills/`) | `AGENTS.md` |
| Claude Code | `.claude/skills/` | `CLAUDE.md` |
| Codex, Gemini CLI, Copilot CLI | `.agents/skills/` | `AGENTS.md` (Gemini: `GEMINI.md`) |

Using more than one tool in the same repo? `.agents/skills/` is read by Devin, Codex, Gemini and Copilot, so put the skills there once and add the bootstrap line to each tool's file.

## Step 2: Copy the skills

Set two paths first: `GODMODE` is this `combined` folder, `PROJECT` is your repo.

**PowerShell (Windows):**

```powershell
$GODMODE = "C:\path\to\skill\combined"
$PROJECT = "C:\path\to\your-project"
$TARGET  = Join-Path $PROJECT ".devin\skills"     # or .claude\skills, .agents\skills

New-Item -ItemType Directory -Force $TARGET | Out-Null
Copy-Item -Recurse -Force "$GODMODE\skills\*" $TARGET
(Get-ChildItem $TARGET -Directory).Count          # expect 30
```

**bash (macOS, Linux, Git Bash):**

```bash
GODMODE="$HOME/path/to/skill/combined"
PROJECT="$HOME/path/to/your-project"
TARGET="$PROJECT/.devin/skills"                   # or .claude/skills, .agents/skills

mkdir -p "$TARGET"
cp -R "$GODMODE/skills/." "$TARGET/"
ls -d "$TARGET"/*/ | wc -l                        # expect 30
```

Copy the `skills/` folder whole. The skills link to each other and to their support files (`../requesting-code-review/fowler-smells.md`, the `scripts/` folders), so they must stay side by side in one folder.

## Step 3: Add the bootstrap line

Without a plugin, no session-start hook runs, so one line in the instructions file tells the agent to load the router. Create the file at the repo root, or add the line to the top of the existing one.

**`AGENTS.md`** (Devin, Codex, Copilot), **`CLAUDE.md`** (Claude Code), or **`GEMINI.md`** (Gemini). Change `.devin/skills` to your folder from Step 1:

```markdown
At the start of every session, before responding, read `.devin/skills/using-godmode/SKILL.md` and follow it. It routes all work through the godmode skills in `.devin/skills/`. A reference to `godmode:<name>` means the skill in `.devin/skills/<name>/SKILL.md`.
```

The last sentence matters. A project install has no plugin namespace, so the agent loads skills by bare name (`brainstorming`, not `godmode:brainstorming`), and this sentence maps one to the other.

### Optional, Claude Code only: a session-start hook

In place of (or as well as) the bootstrap line, Claude Code can inject the router through a project hook. Copy `hooks/` from this folder into the repo at `.claude/godmode-hooks/`, then add this to `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "CLAUDE_PLUGIN_ROOT=\"$CLAUDE_PROJECT_DIR/.claude\" bash \"$CLAUDE_PROJECT_DIR/.claude/godmode-hooks/session-start\""
          }
        ]
      }
    ]
  }
}
```

The script finds the router relative to its own location: it reads `<parent of the hooks folder>/skills/using-godmode/SKILL.md`. With the hooks at `.claude/godmode-hooks/`, the parent is `.claude/`, which holds `skills/`. `CLAUDE_PLUGIN_ROOT` only tells the script to answer in Claude Code's format. On Windows this needs Git for Windows (bash).

## Step 4: Decide whether to commit it

| Choice | Do this |
|--------|---------|
| The whole team uses godmode | Commit `.devin/skills/` (or your folder) and the bootstrap file. Everyone who clones gets it. |
| Only you use it | Add the skill folder and the bootstrap line's file to `.git/info/exclude`, not `.gitignore`, so nothing shows up for teammates. |

`.godmode/sdd/` never needs a gitignore entry: it writes its own the first time it is created.

---

## Step 5: Check it works

### 1. The tool sees the skills

Devin CLI, from the project root:

```powershell
devin skills list
```

Each godmode skill should show a source path inside `.\.devin\skills\`. The five programmer commands show `[user]` (only you can run them); the other 25 show `[user,model]`.

Other tools: open a session and ask "list your available skills".

### 2. The router loads and the gates hold

Run both prompts in a fresh session. Devin's non-interactive mode is handy for this:

```powershell
devin -p "Let's make a react todo list" --respect-workspace-trust false
```

| Send | Expect |
|------|--------|
| "Let's make a react todo list" (in a repo with no app code) | Announces `brainstorming`, calls the task **Architectural**, and asks a round of numbered questions, each with a recommended answer. No files are created. |
| A small, fully specified change to existing code | Calls it **Bounded**, says there is nothing left to ask, shows a short design (files, what the tests call, test cases), and **stops for your yes**. No files change until you say yes. |
| "Yes, go ahead" (after the design) | Invokes `test-driven-development`, writes a failing test first, then the code, then invokes `verification-before-completion` and shows the test run. |

If the agent writes code in the same turn as a fully specified request, the router did not load: check Step 3.

---

## Updating

Godmode files in the project are plain copies, so they do not update themselves.

1. Delete the old skill folders first, so renamed or removed skills don't linger:

   ```powershell
   Get-ChildItem $TARGET -Directory | Where-Object { Test-Path (Join-Path $GODMODE "skills\$($_.Name)") } | Remove-Item -Recurse -Force
   ```

   This removes only folders whose names match a godmode skill, and leaves any skills of your own.
2. Repeat Step 2.

## Removing

1. Delete the godmode skill folders from `.devin/skills/` (or your folder), using the same command as in Updating.
2. Remove the bootstrap line from `AGENTS.md` / `CLAUDE.md` / `GEMINI.md`, and the hook entry from `.claude/settings.json` if you added one.
3. Keep or delete `docs/godmode/`, `CONTEXT.md` and `docs/adr/` as you like: they are your project's documents now.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `devin plugins install` fails with `A required privilege is not held by the client (os error 1314)` | Plugin install creates a symlink, which Windows only allows with Developer Mode or admin rights | Use this project install instead, or turn on Developer Mode |
| `devin plugins install file:///C:/...` says the path "is not a directory" | Windows `file://` URLs are misread | Use this project install, or install from a real git remote |
| No skill fires; the agent codes immediately | The bootstrap line is missing or points at the wrong folder | Check Step 3: the path in the line must match the folder from Step 1 |
| Skills show up, but the agent says `godmode:brainstorming` doesn't exist | The mapping sentence was left out of the bootstrap line | Add "A reference to `godmode:<name>` means the skill in `<folder>/<name>/SKILL.md`." |
| A global skill with the same name (for example an older `test-driven-development`) seems to be used | Name clash with a user-level skill | Run `devin skills list` and check which source path wins. In testing, Devin preferred the project copy; if yours doesn't, rename or remove the global one |
| Two routers announce themselves | Superpowers or mattpocock-skills is also installed | Remove them for this project; godmode already contains what it needs from both |
| `Error reading using-godmode skill` from the Claude Code hook | The hooks folder is not a sibling of `skills/` | Put the hooks at `.claude/godmode-hooks/` next to `.claude/skills/` (see the optional hook section) |
