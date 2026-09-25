# Installing Godmode

Godmode is one skill set built from two sources. Superpowers drives the pipeline (brainstorm, plan, execute, review, finish). Matt Pocock's engineering skills plug into that pipeline at fixed stages (grilling, codebase design, domain modeling, TDD at seams, two-axis review, prototype, research, merge conflicts, architecture improvement). You never call a pipeline skill by hand: a session-start hook loads the `using-godmode` router, and the router takes it from there.

Five of Matt Pocock's productivity skills ship as **programmer commands** that only you can run: `/wait-what`, `/handoff`, `/grill-me`, `/to-questionnaire`, `/teach`. They are marked user-invoked (`disable-model-invocation: true`, plus `agents/openai.yaml` for Codex), so the agent never fires them and they cost nothing in its context. They only work where the harness exposes skills as slash commands (Claude Code, Codex). Elsewhere, ask for them by name.

To install godmode into one repository only (no plugin system, no admin rights), see [INSTALL-LOCAL-PROJECT.md](INSTALL-LOCAL-PROJECT.md).

## What you are installing

```
combined/
  skills/                  30 skills, one folder each (SKILL.md plus support files):
                           25 model-invoked, 5 user-invoked programmer commands
    using-godmode/         the router the hook injects at session start
  hooks/
    session-start          bash script that injects using-godmode into the session
    run-hook.cmd           Windows/Unix wrapper that finds bash and runs the script
    hooks.json             SessionStart registration (Claude Code format)
    hooks-cursor.json      SessionStart registration (Cursor format)
  .claude-plugin/          Claude Code manifest and local marketplace
  .cursor-plugin/          Cursor manifest
  .codex-plugin/           Codex manifest
  .devin-plugin/           Devin CLI manifest
  .agents/plugins/         local marketplace entry
```

## Before you install

1. **Remove or disable Superpowers and mattpocock-skills in the same harness.** Godmode already contains what it needs from both. Two routers in one session fight over which skill fires first.
2. **Windows: install Git for Windows.** The hook runs through bash. `run-hook.cmd` looks for `C:\Program Files\Git\bin\bash.exe` first, then any `bash` on `PATH`. If it finds no bash, it exits quietly: the skills are still installed, but nothing loads them automatically.
3. **Keep the folder somewhere stable.** Plugin installs may point at this folder. If you move it, reinstall.

The examples below use `GODMODE` for the absolute path of this `combined` folder:

```powershell
# PowerShell
$GODMODE = "C:\Users\<you>\...\skill\combined"
```

```bash
# bash
GODMODE="$HOME/path/to/skill/combined"
```

---

## Option A: Install as a plugin (recommended)

Plugin installs register the skills and the session-start hook in one step.

### Claude Code

```text
/plugin marketplace add <GODMODE>
/plugin install godmode@godmode-local
```

Restart Claude Code. The plugin's `hooks/hooks.json` is discovered automatically, so the manifest does not declare it again (declaring it twice makes Claude Code reject the plugin with a duplicate-hooks error).

### Devin CLI

```powershell
devin plugins install $GODMODE
```

Add `--local` to install on this machine only. After editing any file in `combined/`, reinstall with the same command.

**Windows:** installing from a local path makes Devin create a symlink, which fails without Developer Mode or admin rights (`os error 1314`), and `file:///C:/...` URLs are misread. Install from a git remote instead; any git URL works, including one you serve locally with no network exposure:

```powershell
# Snapshot a copy of this folder into its own git repo (your own repo is left untouched)
$SERVE = "$env:TEMP\godmode-serve"
Remove-Item -Recurse -Force $SERVE -ErrorAction SilentlyContinue
robocopy $GODMODE "$SERVE\work" /E /XD .git /NFL /NDL /NJH /NJS | Out-Null
git -C "$SERVE\work" init -q -b main
git -C "$SERVE\work" add -A
git -C "$SERVE\work" -c user.name=godmode -c user.email=godmode@localhost commit -qm "godmode snapshot"
git clone -q --bare "$SERVE\work" "$SERVE\godmode.git"

# Serve it on localhost only, install, then stop the server
Start-Process git -ArgumentList 'daemon','--listen=127.0.0.1','--export-all',"--base-path=$SERVE","$SERVE" -WindowStyle Hidden
devin plugins install --local -y "git://127.0.0.1/godmode.git"
# git daemon runs as child processes, so stop every process serving this folder
Get-CimInstance Win32_Process |
    Where-Object { $_.Name -in 'git.exe','git-daemon.exe' -and $_.CommandLine -like "*godmode-serve*" } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
```

Devin clones the repo into its plugin cache, so the server only needs to run during the install. To update later, repeat the snapshot, start the server, and run `devin plugins update godmode`. Tested: Devin loads all 30 skills and runs the session-start hook, which injects the router as a system message.

### Cursor

Install `combined/` through Cursor's plugin mechanism, pointed at this folder. `.cursor-plugin/plugin.json` registers `skills/` and `hooks/hooks-cursor.json`.

### Codex

`.codex-plugin/plugin.json` registers `skills/`, but Codex runs no session-start hook for it. Also add the bootstrap line from Option B, step 3, to `~/.codex/AGENTS.md`, or the router never loads.

---

## Option B: Manual install (no plugin system)

Use this when your harness has no plugin support, or you want full control over the files.

### 1. Copy the whole folder

Keep the folder in one piece: the hook finds the router at `<root>/skills/using-godmode/SKILL.md`.

```powershell
# PowerShell (Claude Code example)
Copy-Item -Recurse -Force $GODMODE "$env:USERPROFILE\.claude\godmode"
```

```bash
# bash
cp -R "$GODMODE" ~/.claude/godmode
```

### 2. Expose the skills to the harness

Copy each skill folder into the harness's personal skills directory:

| Harness | Skills directory |
|---------|------------------|
| Claude Code | `~/.claude/skills/` |
| Codex, Copilot CLI, Gemini CLI | `~/.agents/skills/` (shared alias) |
| Gemini CLI | `~/.gemini/skills/` |

```powershell
# PowerShell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills" | Out-Null
Copy-Item -Recurse -Force "$env:USERPROFILE\.claude\godmode\skills\*" "$env:USERPROFILE\.claude\skills\"
```

```bash
# bash
mkdir -p ~/.claude/skills
cp -R ~/.claude/godmode/skills/* ~/.claude/skills/
```

A manual install has no plugin namespace, so skills load by bare name (`brainstorming`, not `godmode:brainstorming`). The agent maps `godmode:<name>` references in the skill text to `<name>`. If a skill with the same name already exists (for example, from an old Superpowers copy), delete the old one first.

### 3. Load the router at session start

**Claude Code: add a SessionStart hook** to `~/.claude/settings.json`. Merge this into the file's existing `hooks` object instead of replacing the file:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "CLAUDE_PLUGIN_ROOT=\"$HOME/.claude/godmode\" bash \"$HOME/.claude/godmode/hooks/session-start\""
          }
        ]
      }
    ]
  }
}
```

Setting `CLAUDE_PLUGIN_ROOT` makes the script emit the JSON shape Claude Code expects (`hookSpecificOutput.additionalContext`).

**Harnesses without hooks: add a bootstrap line** to the global instructions file (`~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, `~/.gemini/GEMINI.md`, or your harness's equivalent):

```markdown
At the start of every session, before responding, read `~/.claude/godmode/skills/using-godmode/SKILL.md` and follow it. It routes all work through the godmode skills.
```

Change the path to wherever you copied the folder in step 1.

---

## Verify the install

### 1. The hook produces the bootstrap

From Git Bash, or any bash:

```bash
CLAUDE_PLUGIN_ROOT="$GODMODE" bash "$GODMODE/hooks/session-start" | head -c 300
```

You should see JSON with a `"hookSpecificOutput"` object whose `additionalContext` begins with `You have godmode skills active`. `Error reading using-godmode skill` in the output means the folder layout is broken: `skills/using-godmode/SKILL.md` must sit under the root the hook runs from.

### 2. Skills trigger on their own

Open a fresh session and send exactly:

> Let's make a react todo list

A working install:

1. Invokes `brainstorming` before writing any code.
2. Announces a path (this request is Architectural: there is no existing flow to change).
3. Asks its clarifying questions as a `grilling` round: numbered questions, each with a recommended answer.

Two more quick checks:

| Send | Expect |
|------|--------|
| "This test is failing, fix it" | `systematic-debugging` starts by building a feedback loop, not by proposing a fix |
| "I have a merge conflict" | `resolving-merge-conflicts` reads both sides' history before resolving |

If you get code with no skill announcement, the router did not load. Check the hook, or the bootstrap line from Option B, step 3.

---

## Where godmode writes files in your projects

| Artifact | Path |
|----------|------|
| Specs | `docs/godmode/specs/YYYY-MM-DD-<topic>-design.md` |
| Plans | `docs/godmode/plans/YYYY-MM-DD-<feature>.md` |
| Execution ledger and review packages | `.godmode/sdd/<plan>/` (git-ignored scratch) |
| Research notes | `docs/research/<topic>-<date>.md`, unless the repo already has a convention |
| Domain glossary and decisions | `CONTEXT.md`, `docs/adr/` |
| Diagnosis reports | `~/.godmode/diagnosing-godmode/<session-id>/` (local only, never filed upstream) |

`.godmode/sdd/` writes its own `.gitignore` the first time it is created, so it stays out of `git status` without you editing any tracked file.

## Updating

- **Plugin install:** edit `combined/`, then reinstall (`devin plugins install $GODMODE`, or `/plugin install godmode@godmode-local` after `/plugin marketplace update godmode-local` in Claude Code).
- **Manual install:** repeat steps 1 and 2 of Option B. Delete the old skill folders first, so renamed or removed skills don't linger.

## Uninstalling

- **Plugin install:** `/plugin uninstall godmode` (Claude Code) or `devin plugins remove godmode` (Devin CLI).
- **Manual install:** delete `~/.claude/godmode`, the 30 godmode skill folders in your skills directory, and the SessionStart hook entry or bootstrap line you added.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| No skill fires at all | Hook did not run, or no bash was found | Run the verify command above; install Git for Windows |
| Two different routers announce themselves | Superpowers or mattpocock-skills is still installed | Uninstall them from this harness |
| `Error reading using-godmode skill` | The folder was split up during copying | Copy `combined/` whole; keep `skills/` directly under the root |
| Claude Code rejects the plugin with a duplicate-hooks error | A `hooks` entry was added to `.claude-plugin/plugin.json` | Remove it; `hooks/hooks.json` is picked up automatically |
| The hook uses the WSL bash on Windows | Git for Windows is not installed at the default path | Install it at the default path, or put Git's `bin` first on `PATH` |
| Devin shows the plugin's hook but it never runs | A `matcher` was added back to `hooks/hooks.json`. Devin treats `matcher` as a tool-name filter, so Claude Code's `startup\|clear\|compact` never matches | Keep the SessionStart entry without a `matcher`; Claude Code then runs it for every session source |
| Hook or skill scripts fail on macOS/Linux with `$'\r': command not found` or `invalid option name` | The scripts were checked out with CRLF line endings | Keep `.gitattributes` in the repo (it forces LF on scripts) and re-clone, or convert the scripts to LF |
| Plan execution can't run `sdd-workspace` / `task-start` on Windows | A plain `bash` resolved to WSL (`C:\Windows\System32\bash.exe`) | Run them with Git Bash (`C:\Program Files\Git\bin\bash.exe`); the router's Platform Adaptation section tells the agent this |
| `devin plugins install` fails with `os error 1314` | Local-path installs need symlink rights on Windows | Use the git-remote install under Devin CLI above, or [INSTALL-LOCAL-PROJECT.md](INSTALL-LOCAL-PROJECT.md) |
