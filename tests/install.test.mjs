// Tests for skills/setup-godmode/scripts/install.mjs. Run: node --test tests/
import { test, beforeEach } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { main, BEGIN, MANIFEST } from "../skills/setup-godmode/scripts/install.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
let tmp, home, out;

beforeEach(() => {
  tmp = fs.mkdtempSync(path.join(os.tmpdir(), "godmode-test-"));
  home = path.join(tmp, "home");
  fs.mkdirSync(home);
  process.env.HOME = home;
  process.env.USERPROFILE = home;
  process.env.APPDATA = path.join(home, "AppData", "Roaming");
  out = [];
});

const log = (s) => out.push(s);
const run = (...args) => main(args, log);
const read = (p) => fs.readFileSync(p, "utf8");
const g = (cwd, ...a) => execFileSync("git", ["-C", cwd, ...a], { encoding: "utf8" });

function source(names = ["using-godmode", "brainstorming", "grilling", "old-skill"]) {
  const src = path.join(tmp, "godmode", "skills");
  for (const n of names) {
    fs.mkdirSync(path.join(src, n), { recursive: true });
    fs.writeFileSync(path.join(src, n, "SKILL.md"), `---\nname: ${n}\n---\n${n} v1\n`);
  }
  return src;
}
function repo(name = "repo") {
  const r = path.join(tmp, name);
  fs.mkdirSync(r);
  g(r, "init", "-q");
  return r;
}
const blocks = (p) => read(p).split(BEGIN).length - 1;
const status = (r) => g(r, "status", "--porcelain").trim();

test("project install: .agents/skills + AGENTS.local.md, both excluded, git status clean", () => {
  const src = source(), r = repo();
  assert.equal(run("--repo", r, "--source", src), 0);
  const skills = path.join(r, ".agents", "skills");
  assert.deepEqual(fs.readdirSync(skills).filter((n) => !n.startsWith(".")).sort(), ["brainstorming", "grilling", "old-skill", "using-godmode"]);
  assert.deepEqual(JSON.parse(read(path.join(skills, MANIFEST))).installed.sort(), ["brainstorming", "grilling", "old-skill", "using-godmode"]);
  const local = read(path.join(r, "AGENTS.local.md"));
  assert.ok(local.startsWith(BEGIN));
  assert.ok(local.includes("`.agents/skills/using-godmode/SKILL.md`"));
  assert.ok(local.includes("Subagents are permitted") && local.includes("Design gate"));
  const exclude = read(path.join(r, ".git", "info", "exclude"));
  assert.ok(exclude.includes(".agents/skills/") && exclude.includes("AGENTS.local.md"));
  assert.equal(status(r), "");
});

test("never touches existing shared AGENTS.md or CLAUDE.md", () => {
  const src = source(), r = repo();
  fs.writeFileSync(path.join(r, "AGENTS.md"), "# Team rules\n");
  fs.writeFileSync(path.join(r, "CLAUDE.md"), "# Claude rules\n");
  g(r, "add", "-A"); g(r, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "rules");
  run("--repo", r, "--source", src);
  run("--repo", r, "--source", src, "--tool", "claude");
  assert.equal(read(path.join(r, "AGENTS.md")), "# Team rules\n");
  assert.equal(read(path.join(r, "CLAUDE.md")), "# Claude rules\n");
  assert.equal(blocks(path.join(r, "CLAUDE.local.md")), 1);
  assert.equal(status(r), "");
});

test("appends to an existing local file and stays idempotent", () => {
  const src = source(), r = repo();
  fs.writeFileSync(path.join(r, "AGENTS.local.md"), "my private notes\n");
  run("--repo", r, "--source", src);
  run("--repo", r, "--source", src);
  const text = read(path.join(r, "AGENTS.local.md"));
  assert.equal(blocks(path.join(r, "AGENTS.local.md")), 1);
  assert.ok(text.endsWith("my private notes\n"));
  assert.equal(read(path.join(r, ".git", "info", "exclude")).split("AGENTS.local.md").length - 1, 1);
});

test("refuses to edit an instructions file that is tracked", () => {
  const src = source(), r = repo();
  fs.writeFileSync(path.join(r, "AGENTS.local.md"), "tracked by mistake\n");
  g(r, "add", "-A"); g(r, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x");
  assert.equal(run("--repo", r, "--source", src), 1);
  assert.equal(read(path.join(r, "AGENTS.local.md")), "tracked by mistake\n");
});

test("BOM and CRLF in the local file are preserved", () => {
  const src = source(), r = repo();
  fs.writeFileSync(path.join(r, "AGENTS.local.md"), Buffer.from("\uFEFF# notes\r\nline\r\n", "utf8"));
  run("--repo", r, "--source", src);
  const raw = fs.readFileSync(path.join(r, "AGENTS.local.md"));
  assert.deepEqual([...raw.subarray(0, 3)], [0xef, 0xbb, 0xbf]);
  assert.ok(!raw.toString("utf8").replace(/\r\n/g, "").includes("\n"));
});

test("--tool claude and --tool devin pick their folders", () => {
  const src = source(), r = repo();
  run("--repo", r, "--source", src, "--tool", "claude");
  assert.ok(fs.existsSync(path.join(r, ".claude", "skills", "using-godmode", "SKILL.md")));
  run("--repo", r, "--source", src, "--tool", "devin");
  assert.ok(fs.existsSync(path.join(r, ".devin", "skills", "using-godmode", "SKILL.md")));
  assert.ok(read(path.join(r, "AGENTS.local.md")).includes("`.devin/skills/using-godmode/SKILL.md`"));
});

test("foreign same-named skill skipped, replaced with backup under --force", () => {
  const src = source(), r = repo();
  const foreign = path.join(r, ".agents", "skills", "grilling");
  fs.mkdirSync(foreign, { recursive: true });
  fs.writeFileSync(path.join(foreign, "SKILL.md"), "someone else's\n");
  run("--repo", r, "--source", src);
  assert.equal(read(path.join(foreign, "SKILL.md")), "someone else's\n");
  run("--repo", r, "--source", src, "--force");
  assert.ok(read(path.join(foreign, "SKILL.md")).includes("grilling v1"));
  const backup = fs.readdirSync(path.join(r, ".agents")).find((n) => n.startsWith(".godmode-backup-"));
  assert.equal(read(path.join(r, ".agents", backup, "grilling", "SKILL.md")), "someone else's\n");
});

test("earlier hand-copied install is adopted with backup", () => {
  const src = source(), r = repo();
  for (const n of ["using-godmode", "brainstorming"]) {
    fs.mkdirSync(path.join(r, ".agents", "skills", n), { recursive: true });
    fs.writeFileSync(path.join(r, ".agents", "skills", n, "SKILL.md"), "old\n");
  }
  run("--repo", r, "--source", src);
  assert.ok(read(path.join(r, ".agents", "skills", "brainstorming", "SKILL.md")).includes("v1"));
  assert.ok(fs.readdirSync(path.join(r, ".agents")).some((n) => n.startsWith(".godmode-backup-")));
});

test("update removes stale godmode skills but keeps the user's own", () => {
  const src = source(), r = repo();
  run("--repo", r, "--source", src);
  const mine = path.join(r, ".agents", "skills", "my-skill");
  fs.mkdirSync(mine);
  fs.writeFileSync(path.join(mine, "SKILL.md"), "mine\n");
  fs.rmSync(path.join(src, "old-skill"), { recursive: true });
  run("update", "--repo", r, "--source", src);
  assert.ok(!fs.existsSync(path.join(r, ".agents", "skills", "old-skill")));
  assert.ok(fs.existsSync(path.join(mine, "SKILL.md")));
});

test("dry run changes nothing", () => {
  const src = source(), r = repo();
  run("--repo", r, "--source", src, "--dry-run");
  assert.ok(!fs.existsSync(path.join(r, ".agents")) && !fs.existsSync(path.join(r, "AGENTS.local.md")));
  assert.ok(!(fs.existsSync(path.join(r, ".git", "info", "exclude")) && read(path.join(r, ".git", "info", "exclude")).includes("godmode")));
});

test("uninstall removes owned skills and the block; deletes a local file left empty", () => {
  const src = source(), r = repo();
  run("--repo", r, "--source", src);
  const mine = path.join(r, ".agents", "skills", "my-skill");
  fs.mkdirSync(mine);
  fs.writeFileSync(path.join(mine, "SKILL.md"), "mine\n");
  run("uninstall", "--repo", r);
  assert.deepEqual(fs.readdirSync(path.join(r, ".agents", "skills")), ["my-skill"]);
  assert.ok(!fs.existsSync(path.join(r, "AGENTS.local.md")));
});

test("global install needs a tool with a user-level instructions file", () => {
  const src = source();
  assert.equal(run("--global", "--source", src), 1);
  assert.equal(run("--global", "--tool", "claude", "--source", src), 0);
  assert.ok(fs.existsSync(path.join(home, ".claude", "skills", "using-godmode", "SKILL.md")));
  const instr = read(path.join(home, ".claude", "CLAUDE.md"));
  assert.ok(instr.includes(path.join(home, ".claude", "skills").split(path.sep).join("/")));
});

test("conflicts and old shared-file blocks are reported, not changed", () => {
  const src = source(), r = repo();
  fs.mkdirSync(path.join(r, ".claude", "skills", "ask-matt"), { recursive: true });
  fs.writeFileSync(path.join(r, ".claude", "skills", "ask-matt", "SKILL.md"), "router\n");
  const shared = `${BEGIN}\nold\n<!-- godmode:end -->\n\n**Always use Matt Pocock skills.**\n`;
  fs.writeFileSync(path.join(r, "AGENTS.md"), shared);
  run("--repo", r, "--source", src);
  const text = out.join("\n");
  assert.match(text, /ask-matt.*Matt Pocock router/);
  assert.match(text, /godmode block from an older install/);
  assert.match(text, /competing routing rule/);
  assert.equal(read(path.join(r, "AGENTS.md")), shared);
});

test("doctor reports a missing bootstrap", () => {
  const r = repo();
  run("doctor", "--repo", r);
  assert.match(out.join("\n"), /NO bootstrap block/);
});

test("rejects bad input", () => {
  assert.equal(run("--tool", "vim"), 1);
  assert.equal(run("frobnicate"), 1);
  const bad = path.join(tmp, "bad");
  fs.mkdirSync(path.join(bad, "x"), { recursive: true });
  assert.equal(run("--repo", repo(), "--source", bad), 1);
});

test("the npx entry point runs the installer", () => {
  const r = repo();
  const res = execFileSync(process.execPath, [path.join(ROOT, "bin", "godmode.mjs"), "--repo", r, "--dry-run"], { encoding: "utf8" });
  assert.match(res, /using-godmode|update|add/);
  assert.match(res, /dry run/);
});
