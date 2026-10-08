---
name: wizard
description: Generate an interactive bash wizard that guides a human through steps that only the human can do. Use it to provision infrastructure or to set up credentials or CI secrets. Also use it to go through an unfamiliar third-party dashboard, or to run a one-off migration or cutover. Do not invoke this for steps that the agent can do itself.
---

# Wizard

A **wizard** is a bash script that guides a human, step by step, through a manual procedure. The procedure is tedious to do by hand and tedious to explain again to an AI each time. The wizard opens each URL and says exactly what to click and copy. It captures the values and writes them to their location (`.env`, GitHub secrets). It asks for approval at each stage and shows how many stages remain. It might configure third-party services, run a one-off migration, or move the project from one state to a different state.

[template.sh](template.sh) already gives the good UX:

- progress for each stage
- approval gates
- URL opening on all platforms (including WSL)
- hidden secret entry
- idempotent `.env` upserts
- `gh secret`/`gh variable` writes
- a closing summary

**Your job is only to scope the procedure and author its stages.** The library above the `STAGES` marker is identical in each wizard. That consistency is the point. Do not edit it by hand.

By default, a wizard is temporary. You build it for one run, save it to a scratch or `scripts/` path, and remove it when the job ends. Commit it only when the user wants a repeatable setup path in the repo.

## Process

### 1. Scope the procedure

Find each manual step that the human must do and each value that the wizard captures. First read the repo. Do not ask without context:

- For setup: `.env`, `.env.example`, `.env.*`, `README`, `docker-compose*`, framework config, and `.github/workflows/*` (each `secrets.*` / `vars.*` reference is a value that the wizard must produce).
- For a migration or transition: the current state, the target state, and the irreversible actions between them.

Then show the user the ordered list of stages and the values that each stage produces. Get the approval of the user. The user may add, remove, or reorder stages.

**Done when:** each stage has a name, in order. For each captured value, you know these three things:

- (a) where the human gets it
- (b) where the wizard writes it (`.env`, a GitHub secret, both, or nowhere). Some stages are only actions.
- (c) whether it is secret (hidden entry) or public

### 2. Map the journey of each stage

For each stage, write the exact path that a human follows. Include which URL to open, what to do there, where a value shows, and which variable it fills. For example: "Dashboard → Developers → API keys → Reveal test key → copy". If you do not know the current UI or the exact command, say so. Then ask the user or read the docs. Do not invent steps that may not exist.

**Done when:** each stage has concrete instructions that a stranger could follow.

### 3. Author the wizard

Copy `template.sh` to the target path. Replace the example stage with one `stage` for each step, in dependency order. Use the library helpers: `stage`, `say`/`step`, `open_url`, `ask`/`ask_secret`, `write_env`, `set_secret`/`set_var`, `pause`/`confirm`. Set `TOTAL_STAGES` to the number of stages that you wrote.

Keep the standard of the template:

- Open the URL before you ask for its value.
- Use `ask_secret` for each secret value.
- Use `write_env` for each persisted value.
- Use `set_secret` only for the values that CI needs.
- Use `confirm` before each irreversible action.

Each `stage` clears the screen, so only the current step shows. Keep each stage to one focused task, so that nothing that the human needs scrolls away. Do not touch the library above the marker.

Write the instructions that the wizard shows to the human in procedural STE (`godmode:ste-writing`).

### 4. Verify and hand off

- `bash -n <script>`. If `shellcheck` is available, run it.
- `chmod +x <script>`.
- Do not run the full script yourself. It opens browsers and waits for human input. Trace it statically instead. Each value from step 1 must be captured and go where step 1 said. Each `set_secret` name must agree exactly with a `secrets.*` reference in CI.
- Tell the user how to run it. If it is a repeatable setup path, commit it and link it from the README. Then the next person runs the script and does not ask an AI.
