#!/usr/bin/env node
// Install, update or remove the godmode skills, and write the bootstrap block that makes them auto-fire.
// Node >= 18, no dependencies. Run via `npx github:annt07/godmode <command>` or `node install.mjs <command>`.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

export const BEGIN = "<!-- godmode:begin (managed by setup-godmode; edit outside this block) -->";
export const END = "<!-- godmode:end -->";
export const MANIFEST = ".godmode-manifest.json";
export const USER_ONLY = ["wait-what", "handoff", "grill-me", "to-questionnaire", "teach", "mr-full-review", "setup-godmode"];

// Where each tool looks for skills and for local / user-level instructions.
// This table is the only place harness-specific knowledge lives.
const TOOLS = {
  agents: { dir: ".agents", local: "AGENTS.local.md", globalSkills: () => path.join(os.homedir(), ".agents", "skills"), globalInstr: null },
  claude: { dir: ".claude", local: "CLAUDE.local.md", globalSkills: () => path.join(os.homedir(), ".claude", "skills"), globalInstr: () => path.join(os.homedir(), ".claude", "CLAUDE.md") },
  devin: {
    dir: ".devin", local: "AGENTS.local.md",
    globalSkills: () => path.join(devinHome(), "skills"), globalInstr: () => path.join(devinHome(), "AGENTS.md"),
  },
};
const SHARED_INSTRUCTION_FILES = ["AGENTS.md", "CLAUDE.md", "GEMINI.md", ".github/copilot-instructions.md"];

const COMPETING = {
  "using-superpowers": "Superpowers router", "using-agent-skills": "agent-skills router", "ask-matt": "Matt Pocock router",
  tdd: "Matt Pocock original (merged into test-driven-development)", "diagnosing-bugs": "Matt Pocock original (merged into systematic-debugging)",
  "code-review": "Matt Pocock original (merged into requesting-code-review)", "grill-with-docs": "Matt Pocock original (merged into grilling)",
  implement: "Matt Pocock original (merged into executing-plans)", "to-tickets": "Matt Pocock original (merged into writing-plans)",
  triage: "Matt Pocock tracker skill", wayfinder: "Matt Pocock tracker skill",
  "spec-driven-development": "agent-skills workflow (overlaps brainstorming/to-spec)",
  "incremental-implementation": "agent-skills workflow (overlaps executing-plans)",
  "debugging-and-error-recovery": "agent-skills workflow (overlaps systematic-debugging)",
  "code-review-and-quality": "agent-skills workflow (overlaps requesting-code-review)",
};
const COMPETING_TEXT = [/Superpowers skills\W+opt-in/i, /Only invoke Superpowers skills/i, /Always use Matt Pocock skills/i, /Global Agent Skills\W+MANDATORY/i];

function devinHome() {
  return process.platform === "win32"
    ? path.join(process.env.APPDATA || path.join(os.homedir(), "AppData", "Roaming"), "devin")
    : path.join(os.homedir(), ".config", "devin");
}

class Fail extends Error {}
const exists = (p) => fs.existsSync(p);
const isDir = (p) => exists(p) && fs.statSync(p).isDirectory();
const posix = (p) => p.split(path.sep).join("/");

function git(cwd, ...args) {
  try {
    return { ok: true, out: execFileSync("git", ["-C", cwd, ...args], { encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] }).trim() };
  } catch {
    return { ok: false, out: "" };
  }
}

// ------------------------------------------------------------------ arguments
export function parseArgs(argv) {
  const o = { command: "install", global: false, repo: process.cwd(), tool: null, dryRun: false, force: false, subagents: true, source: null, skillsDir: null, instructions: null };
  const rest = [...argv];
  if (rest[0] && !rest[0].startsWith("-")) o.command = rest.shift();
  const need = (flag) => { const v = rest.shift(); if (v === undefined) throw new Fail(`${flag} needs a value`); return v; };
  while (rest.length) {
    const a = rest.shift();
    if (a === "--global" || a === "-g") o.global = true;
    else if (a === "--repo") o.repo = need(a);
    else if (a === "--tool") o.tool = need(a);
    else if (a === "--dry-run" || a === "-n") o.dryRun = true;
    else if (a === "--force") o.force = true;
    else if (a === "--no-subagents") o.subagents = false;
    else if (a === "--source") o.source = need(a);
    else if (a === "--skills-dir") o.skillsDir = need(a);
    else if (a === "--instructions-file") o.instructions = need(a);
    else if (a === "--help" || a === "-h") o.command = "help";
    else throw new Fail(`unknown option ${a} (see --help)`);
  }
  if (["init", "update", "add"].includes(o.command)) o.command = "install";
  if (["remove", "uninstall"].includes(o.command)) o.command = "uninstall";
  if (!["install", "uninstall", "doctor", "help"].includes(o.command)) throw new Fail(`unknown command ${o.command} (see --help)`);
  if (o.tool && !TOOLS[o.tool]) throw new Fail(`--tool must be one of: ${Object.keys(TOOLS).join(", ")}`);
  return o;
}

const HELP = `godmode installer

  npx github:annt07/godmode [install|update|uninstall|doctor] [options]

Project install (default): skills go into <repo>/<tool dir>/skills and the bootstrap block goes into a
LOCAL instructions file (AGENTS.local.md, or CLAUDE.local.md for --tool claude). Both are added to
.git/info/exclude, so nothing becomes tracked. Shared AGENTS.md / CLAUDE.md are never modified.

Options
  --repo <path>          repository (default: current directory)
  --tool <agents|claude|devin>
                         agents (default): .agents/skills, read by most agents
                         claude: .claude/skills + CLAUDE.local.md
                         devin:  .devin/skills
  --global, -g           install for every repo instead (requires --tool claude or devin)
  --dry-run, -n          show what would change, change nothing
  --force                replace same-named skills godmode doesn't own (backed up first)
  --no-subagents         omit the standing subagent permission from the bootstrap block
  --source <path>        godmode repo or skills folder (default: the copy this script belongs to)
  --skills-dir <path>    override the skills folder
  --instructions-file <path>  override the local instructions file
`;

// ------------------------------------------------------------------ locations
export function resolveTargets(o) {
  const tool = o.tool || (o.global ? null : "agents");
  if (o.global) {
    if (!tool || !TOOLS[tool].globalInstr) throw new Fail("--global needs --tool claude or --tool devin (no shared user-level instructions file exists for 'agents')");
    return {
      tool, repo: null,
      skillsDir: path.resolve(o.skillsDir || TOOLS[tool].globalSkills()),
      instr: path.resolve(o.instructions || TOOLS[tool].globalInstr()),
    };
  }
  const start = path.resolve(o.repo);
  const top = git(start, "rev-parse", "--show-toplevel");
  const repo = top.ok ? path.resolve(top.out) : start;
  return {
    tool, repo,
    skillsDir: path.resolve(o.skillsDir || path.join(repo, TOOLS[tool].dir, "skills")),
    instr: path.resolve(o.instructions || path.join(repo, TOOLS[tool].local)),
  };
}

export function resolveSource(o) {
  let src = o.source ? path.resolve(o.source) : path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
  if (isDir(path.join(src, "skills")) && !exists(path.join(src, "SKILL.md"))) src = path.join(src, "skills");
  if (!exists(path.join(src, "using-godmode", "SKILL.md"))) throw new Fail(`${src} is not a godmode skills folder (no using-godmode/SKILL.md)`);
  return src;
}

const listSkills = (dir) => (isDir(dir) ? fs.readdirSync(dir).filter((n) => exists(path.join(dir, n, "SKILL.md"))).sort() : []);

function sourceVersion(src) {
  const pkg = path.join(src, "..", "package.json");
  const v = exists(pkg) ? JSON.parse(fs.readFileSync(pkg, "utf8")).version : null;
  const sha = git(path.dirname(src), "rev-parse", "--short", "HEAD");
  return [v && `v${v}`, sha.ok && sha.out].filter(Boolean).join(" ") || "unversioned";
}

// ------------------------------------------------------------------ bootstrap block
export function renderBlock(t, subagents) {
  const where = t.repo && t.skillsDir.startsWith(t.repo + path.sep) ? posix(path.relative(t.repo, t.skillsDir)) : posix(t.skillsDir);
  const lines = [
    BEGIN, "## Godmode skills", "",
    `At the start of every session, before responding, read \`${where}/using-godmode/SKILL.md\` and follow it. It routes all work through the godmode skills in \`${where}\`. A reference to \`godmode:<name>\` means the skill in \`${where}/<name>/SKILL.md\`.`,
    "",
    "**Design gate.** For any new feature or behaviour change, invoke `godmode:brainstorming` and get the user's approval of its design before writing any test or code, even when the request reads like a complete spec. Approval is a reply the user sends after seeing the design, so end your turn after presenting it; the original request never counts as approval. Bug fixes start with `godmode:systematic-debugging`.",
    "",
  ];
  if (subagents) lines.push(
    "**Subagents are permitted.** The user explicitly and permanently allows subagents whenever a godmode skill calls for them (subagent-driven-development, dispatching-parallel-agents, research, the parallel reviewers in requesting-code-review, large vuln-scan runs). Treat this line as the user's explicit request to use subagents for those steps.",
    "");
  lines.push(`User-only commands run only when the user types them: ${USER_ONLY.map((n) => `\`/${n}\``).join(", ")}.`, END);
  return lines.join("\n");
}

function readText(p) {
  if (!exists(p)) return { text: "", bom: false, nl: os.EOL };
  const raw = fs.readFileSync(p);
  const bom = raw[0] === 0xef && raw[1] === 0xbb && raw[2] === 0xbf;
  const text = raw.toString("utf8").replace(/^\uFEFF/, "");
  return { text: text.replace(/\r\n/g, "\n"), bom, nl: text.includes("\r\n") ? "\r\n" : "\n" };
}
function writeText(p, { text, bom, nl }) {
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, (bom ? "\uFEFF" : "") + text.replace(/\n/g, nl), "utf8");
}
const BLOCK_RE = new RegExp(`${BEGIN.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}[\\s\\S]*?${END.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\n*`);
export const upsertBlock = (text, block) => (BLOCK_RE.test(text) ? [text.replace(BLOCK_RE, block + "\n\n"), "replaced"] : [block + "\n\n" + text, "added"]);
export const removeBlock = (text) => text.replace(BLOCK_RE, "");

// ------------------------------------------------------------------ git exclude
export function excludeLocally(repo, rels, dry) {
  const gd = git(repo, "rev-parse", "--git-common-dir");
  if (!gd.ok) return [];
  const exclude = path.resolve(repo, gd.out, "info", "exclude");
  const current = exists(exclude) ? fs.readFileSync(exclude, "utf8") : "";
  const have = new Set(current.split(/\r?\n/));
  const missing = rels.filter((r) => !have.has(r));
  if (missing.length && !dry) {
    fs.mkdirSync(path.dirname(exclude), { recursive: true });
    const sep = current && !current.endsWith("\n") ? "\n" : "";
    fs.appendFileSync(exclude, `${sep}# godmode (local install, never tracked)\n${missing.join("\n")}\n`);
  }
  return missing;
}
const isTracked = (repo, rel) => git(repo, "ls-files", "--error-unmatch", rel).ok;

// ------------------------------------------------------------------ conflicts
function scanConflicts(t, godmodeNames) {
  const warn = [];
  const dirs = [];
  if (t.repo) for (const k of Object.keys(TOOLS)) dirs.push(path.join(t.repo, TOOLS[k].dir, "skills"));
  for (const k of Object.keys(TOOLS)) dirs.push(TOOLS[k].globalSkills());
  const seen = new Set();
  for (const d of dirs) {
    const key = path.resolve(d).toLowerCase();
    if (seen.has(key) || !isDir(d) || key === t.skillsDir.toLowerCase()) continue;
    seen.add(key);
    const names = new Set(listSkills(d));
    for (const n of Object.keys(COMPETING)) if (names.has(n)) warn.push(`${path.join(d, n)}: ${COMPETING[n]}. Two routers or two versions of a workflow make skills misfire.`);
    const dup = godmodeNames.filter((n) => names.has(n));
    if (dup.length) warn.push(`${d}: ${names.has("using-godmode") ? "another godmode install" : "same-named skills"} (${dup.length}). Keep one version: a project copy usually shadows a user-level one.`);
  }
  const files = [t.instr, ...(t.repo ? SHARED_INSTRUCTION_FILES.map((f) => path.join(t.repo, f)) : [])];
  for (const f of files) {
    if (!exists(f)) continue;
    const text = fs.readFileSync(f, "utf8");
    if (f !== t.instr && BLOCK_RE.test(text)) warn.push(`${f}: contains a godmode block from an older install. This installer never edits shared files; remove that block by hand if you want the local file to be the only one.`);
    const body = removeBlock(text);
    for (const rx of COMPETING_TEXT) {
      const m = rx.exec(body);
      if (m) warn.push(`${f}:${body.slice(0, m.index).split("\n").length}: competing routing rule ('${m[0]}'). It tells the agent to prefer other skills over godmode.`);
    }
  }
  return warn;
}

// ------------------------------------------------------------------ commands
function loadManifest(dir) {
  const p = path.join(dir, MANIFEST);
  return exists(p) ? JSON.parse(fs.readFileSync(p, "utf8")) : null;
}

export function install(o, log = console.log) {
  const t = resolveTargets(o);
  const src = resolveSource(o);
  if (path.resolve(src).toLowerCase() === t.skillsDir.toLowerCase()) throw new Fail("source and target are the same folder; pass --source pointing at the godmode repo");
  const names = listSkills(src);
  const manifest = loadManifest(t.skillsDir) || {};
  const owned = new Set(manifest.installed || []);
  const existing = new Set(isDir(t.skillsDir) ? fs.readdirSync(t.skillsDir).filter((n) => isDir(path.join(t.skillsDir, n))) : []);
  const adopt = !manifest.installed && existing.has("using-godmode");
  const actions = names.map((n) => [!existing.has(n) ? "add" : owned.has(n) || adopt ? "update" : o.force ? "replace-foreign" : "skip-foreign", n]);
  const stale = adopt ? [] : [...owned].filter((n) => !names.includes(n)).sort();
  const stamp = new Date().toISOString().replace(/[-:]/g, "").replace("T", "-").slice(0, 15);
  const backupRoot = path.join(path.dirname(t.skillsDir), `.godmode-backup-${stamp}`);

  log(`Source:       ${src}  (${sourceVersion(src)})`);
  log(`Skills dir:   ${t.skillsDir}`);
  log(`Instructions: ${t.instr}${t.repo ? "  (local, untracked)" : ""}`);
  const labels = { add: "add", update: "update", "replace-foreign": "replace (backed up, --force)", "skip-foreign": "SKIP: not godmode's, use --force to replace" };
  for (const k of Object.keys(labels)) {
    const g = actions.filter(([a]) => a === k).map(([, n]) => n);
    if (g.length) log(`  ${labels[k]} (${g.length}): ${g.join(", ")}`);
  }
  if (stale.length) log(`  remove stale godmode skills (${stale.length}): ${stale.join(", ")}`);
  if (adopt) log("  adopting an earlier godmode copy found here (no manifest): old copies are backed up");

  if (t.repo && isTracked(t.repo, posix(path.relative(t.repo, t.instr)))) throw new Fail(`${t.instr} is tracked by git; refusing to edit a shared file. Pass --instructions-file with an untracked path.`);

  const block = renderBlock(t, o.subagents);
  const file = readText(t.instr);
  const [newText, how] = upsertBlock(file.text, block);
  log(`  bootstrap block: ${how} at the top of ${t.instr}${exists(t.instr) ? "" : " (new file)"}`);

  let excluded = [];
  if (t.repo) {
    const rels = [posix(path.relative(t.repo, t.skillsDir)) + "/", posix(path.relative(t.repo, t.instr))].filter((r) => !r.startsWith(".."));
    excluded = excludeLocally(t.repo, rels, o.dryRun);
    if (excluded.length) log(`  .git/info/exclude: ${o.dryRun ? "would add" : "added"} ${excluded.join(", ")}`);
    const trackedSkills = git(t.repo, "ls-files", posix(path.relative(t.repo, t.skillsDir))).out;
    if (trackedSkills) log(`  note: some files under ${posix(path.relative(t.repo, t.skillsDir))} are already tracked; exclude doesn't untrack them (git rm --cached to stop tracking).`);
  }

  if (!o.dryRun) {
    fs.mkdirSync(t.skillsDir, { recursive: true });
    for (const [kind, n] of actions) {
      if (kind === "skip-foreign") continue;
      const dst = path.join(t.skillsDir, n);
      if (exists(dst)) {
        if (kind === "replace-foreign" || adopt) {
          fs.mkdirSync(backupRoot, { recursive: true });
          fs.renameSync(dst, path.join(backupRoot, n));
        } else fs.rmSync(dst, { recursive: true, force: true });
      }
      fs.cpSync(path.join(src, n), dst, { recursive: true, filter: (s) => !/__pycache__|\.pyc$/.test(s) });
    }
    for (const n of stale) fs.rmSync(path.join(t.skillsDir, n), { recursive: true, force: true });
    fs.writeFileSync(path.join(t.skillsDir, MANIFEST), JSON.stringify({
      installed: actions.filter(([a]) => a !== "skip-foreign").map(([, n]) => n).sort(),
      version: sourceVersion(src), source: src, scope: t.repo ? "project" : "global", tool: t.tool, date: new Date().toISOString(),
    }, null, 2) + "\n");
    writeText(t.instr, { ...file, text: newText });
  }

  const warnings = scanConflicts(t, names);
  if (warnings.length) { log("\nWarnings (not changed):"); for (const w of warnings) log(`  - ${w}`); }
  if (!o.dryRun && exists(backupRoot)) log(`\nBackups of replaced folders: ${backupRoot}`);
  log(o.dryRun ? "\n(dry run: nothing changed)" : "\nDone. Open a NEW agent session: the bootstrap loads at session start.");
  return { t, actions, stale, warnings };
}

export function uninstall(o, log = console.log) {
  const t = resolveTargets(o);
  const m = loadManifest(t.skillsDir);
  if (!m) log(`No godmode manifest in ${t.skillsDir}; no skills removed.`);
  else {
    log(`Removing ${m.installed.length} godmode skills from ${t.skillsDir}`);
    if (!o.dryRun) { for (const n of m.installed) fs.rmSync(path.join(t.skillsDir, n), { recursive: true, force: true }); fs.rmSync(path.join(t.skillsDir, MANIFEST)); }
  }
  if (exists(t.instr)) {
    const f = readText(t.instr);
    const text = removeBlock(f.text);
    if (text !== f.text) {
      log(`Removing the godmode block from ${t.instr}`);
      if (!o.dryRun) { if (text.trim()) writeText(t.instr, { ...f, text }); else fs.rmSync(t.instr); }
    }
  }
  log(o.dryRun ? "(dry run: nothing changed)" : "Done.");
}

export function doctor(o, log = console.log) {
  const t = resolveTargets(o);
  const m = loadManifest(t.skillsDir);
  log(`Skills dir:   ${t.skillsDir}  ${m ? `(godmode ${m.version}, ${m.installed.length} skills)` : "(no godmode install)"}`);
  log(`Instructions: ${t.instr}  ${exists(t.instr) && BLOCK_RE.test(fs.readFileSync(t.instr, "utf8")) ? "(bootstrap block present)" : "(NO bootstrap block: skills fire only when named)"}`);
  const w = scanConflicts(t, m ? m.installed : []);
  if (w.length) { log("Warnings:"); for (const x of w) log(`  - ${x}`); } else log("No conflicts found.");
}

export function main(argv = process.argv.slice(2), log = console.log) {
  try {
    const o = parseArgs(argv);
    if (o.command === "help") return log(HELP), 0;
    ({ install, uninstall, doctor })[o.command](o, log);
    return 0;
  } catch (e) {
    if (e instanceof Fail) { console.error(`error: ${e.message}`); return 1; }
    throw e;
  }
}

const invokedDirectly = (() => {
  try { return fs.realpathSync(process.argv[1]) === fs.realpathSync(fileURLToPath(import.meta.url)); } catch { return false; }
})();
if (invokedDirectly) process.exitCode = main();
