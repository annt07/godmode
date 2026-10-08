"""Shared parts of the godmode agent eval: fixtures, one real agent session, and result parsing.

Each case gets a fresh git repository with a small Python project, a godmode install from
this working tree (skills/setup-godmode/scripts/install.mjs --source skills), and one
non-interactive `devin -p` session. The ATIF export shows which skills the agent invoked.
"""
import importlib.util
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNS = HERE / "runs"
RESULTS = HERE / "results"
CONFIG = HERE / "devin-test-config.json"
INSTALLER = ROOT / "skills/setup-godmode/scripts/install.mjs"
USER_ONLY = {"wait-what", "handoff", "grill-me", "to-questionnaire", "teach", "mr-full-review", "setup-godmode"}

_spec = importlib.util.spec_from_file_location("ste_lint", ROOT / "skills/ste-writing/scripts/ste-lint.py")
ste_lint = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ste_lint)
GLOSSARY = ste_lint.load_glossary(ROOT / "skills/ste-writing/glossary.md")

SHOP = {
    "shop/__init__.py": "",
    "shop/totals.py": 'def invoice_total(lines):\n    """Sum of quantity * unit_price for each line."""\n    return sum(l["quantity"] * l["unit_price"] for l in lines)\n',
    "shop/accounts.py": '# "account" is used for both the login user and the billing customer.\nACCOUNTS = {}\n\ndef create_account(email, company=None):\n    ACCOUNTS[email] = {"email": email, "company": company, "balance": 0}\n    return ACCOUNTS[email]\n',
    "shop/checkout.py": 'import json, urllib.request\nfrom shop.totals import invoice_total\n\ndef checkout(email, lines):\n    total = invoice_total(lines)\n    urllib.request.urlopen(urllib.request.Request("https://api.stripe.example/charge", data=json.dumps({"email": email, "amount": total}).encode()))\n    return total\n',
    "tests/__init__.py": "",
    "tests/test_totals.py": 'from shop.totals import invoice_total\n\ndef test_total_sums_lines():\n    assert invoice_total([{"quantity": 2, "unit_price": 5.0}, {"quantity": 1, "unit_price": 3.5}]) == 13.5\n',
    "pyproject.toml": '[project]\nname = "shop"\nversion = "0.1.0"\nrequires-python = ">=3.10"\n\n[dependency-groups]\ndev = ["pytest>=8"]\n\n[tool.pytest.ini_options]\npythonpath = ["."]\n',
    ".gitignore": "__pycache__/\n.venv/\n",
}


def git(d, *args):
    return subprocess.run(["git", "-c", "user.name=eval", "-c", "user.email=eval@localhost", *args],
                          cwd=d, capture_output=True, text=True)


def write(d, files):
    for rel, body in files.items():
        p = pathlib.Path(d, *rel.split("/"))
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8", newline="\n")


# ------------------------------------------------------------------ fixtures
def branch_with_change(d):
    git(d, "checkout", "-qb", "feature/sms")
    write(d, {"shop/notify.py": 'import subprocess\n\ndef notify(order, channel, phone):\n    if channel == "sms":\n        subprocess.run(f"send-sms {phone} order {order}", shell=True)\n    elif channel == "email":\n        return f"email:{order}"\n'})
    git(d, "add", "-A")
    git(d, "commit", "-qm", "feat: sms notifications")


def unstaged_change(d):
    write(d, {"shop/totals.py": SHOP["shop/totals.py"] + "\ndef refund(x):\n    return eval(x)\n"})


def failing_test(d):
    write(d, {"tests/test_bug.py": 'from shop.totals import invoice_total\n\ndef test_three_dimes():\n    assert invoice_total([{"quantity": 3, "unit_price": 0.1}]) == 0.3\n'})
    git(d, "add", "-A")
    git(d, "commit", "-qm", "add failing test")


def remote_branch(d):
    bare = pathlib.Path(str(d) + "-remote.git")
    shutil.rmtree(bare, ignore_errors=True)
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(bare)], capture_output=True)
    git(d, "remote", "add", "origin", str(bare))
    git(d, "push", "-q", "origin", "main")
    git(d, "checkout", "-qb", "feature/discount")
    write(d, {"shop/totals.py": 'def invoice_total(lines, discount_percent=0):\n    total = sum(l["quantity"] * l["unit_price"] for l in lines)\n    return total * (1 - discount_percent / 100)\n'})
    git(d, "commit", "-qam", "feat: discount")


def agents_md(d):
    write(d, {"AGENTS.md": "# Agents\n"})
    git(d, "add", "-A")
    git(d, "commit", "-qm", "agents doc")


# ------------------------------------------------------------------ one session
def make_repo(path, fixture=None):
    shutil.rmtree(path, ignore_errors=True)
    path.mkdir(parents=True)
    git(path, "init", "-q", "-b", "main")
    write(path, SHOP)
    git(path, "add", "-A")
    git(path, "commit", "-qm", "initial")
    r = subprocess.run(["node", str(INSTALLER), "install", "--repo", str(path), "--source", str(ROOT / "skills")],
                       capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"install failed: {r.stdout}{r.stderr}")
    if fixture:
        fixture(path)
    return path


def run_session(path, prompt, timeout=900, cont=False):
    """Run one devin -p turn in path. Return (export dict or None, seconds)."""
    if not CONFIG.exists():
        subprocess.run([sys.executable, str(HERE / "make_config.py")], check=True)
    export = pathlib.Path(str(path) + (".t2" if cont else "") + ".json")
    log = pathlib.Path(str(path) + (".t2" if cont else "") + ".log")
    cmd = ["devin", *(["-c"] if cont else []), "-p", prompt, "--permission-mode", "smart",
           "--respect-workspace-trust", "false", "--export", str(export), "--config", str(CONFIG)]
    start = time.time()
    with log.open("w", encoding="utf-8") as fh:
        p = subprocess.Popen(cmd, cwd=path, stdout=fh, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
        try:
            p.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            p.kill()
    try:
        return json.loads(export.read_text(encoding="utf-8")), round(time.time() - start)
    except Exception:
        return None, round(time.time() - start)


def invoked_skills(export):
    """Skills invoked through the skill tool or read as SKILL.md, in first-use order."""
    out = []
    for step in (export or {}).get("steps", []):
        for tc in step.get("tool_calls") or []:
            args = tc.get("arguments") or {}
            if tc.get("function_name") == "skill" and args.get("skill"):
                out.append(args["skill"].split(":")[-1])
            m = re.search(r"[\\/]skills[\\/]([^\\/]+)[\\/]SKILL\.md$", str(args.get("file_path", "")))
            if tc.get("function_name") == "read" and m:
                out.append(m.group(1))
    return list(dict.fromkeys(out))


def final_reply(export):
    msgs = [s.get("message") or "" for s in (export or {}).get("steps", []) if s.get("source") == "agent"]
    msgs = [m for m in msgs if m.strip()]
    return msgs[-1] if msgs else ""


def lint_reply(text):
    findings, words = ste_lint.lint(text, "<reply>", glossary=GLOSSARY)
    hard = [f for f in findings if f["level"] == "advisory-free"]
    return {"words": words, "hard": len(hard), "semicolons": sum(f["rule"] == "semicolon" for f in hard)}


def changed_files(path):
    return [l for l in git(path, "status", "--porcelain").stdout.splitlines()
            if not re.search(r"uv\.lock|\.agents/|AGENTS\.local\.md", l)]
