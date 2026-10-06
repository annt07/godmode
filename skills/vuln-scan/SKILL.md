---
name: vuln-scan
description: Security vulnerability scan of code you own. Use as the security pass of every code review (requesting-code-review, MR/PR reviews, final branch reviews), scoped to the changed files. Also use when the user asks to scan a codebase or directory for vulnerabilities, check for security issues, secrets, injection, or PHI/PII exposure, or wants a threat model.
---

# Vulnerability Scan

A threat-model-first scan in four stages: **threat model → find → triage → report**. It has two modes:

| Mode | When | Scope | Prompts? |
|---|---|---|---|
| **Review** | Called from a code review (`requesting-code-review`, `mr-full-review`, the final review in `subagent-driven-development` / `executing-plans`) | The review's diff range: changed files plus the call sites and entry points they touch | None. The code under review is your human partner's own repo, so authorization is implied; never stop the review to ask. |
| **Full** | Your human partner asks to scan a codebase or directory | The target directory | Confirm authorization once, then show the threat-model draft and ask whether to refine it before Stage 2 |

## Output location

Write artifacts outside tracked files: `.godmode/security/<YYYYMMDD-HHMM>-<scope>/` at the repo root (create `.godmode/security/.gitignore` containing `*` if it doesn't exist). Never write `THREAT_MODEL.md` or reports into the scanned source tree. Outside a git repo, use the system temp directory and report the path.

## Stage 1: Threat model

Survey with read-only tools (read, grep, glob). In review mode, start from the diff (`git diff <base>...<head> --stat`, then the changed hunks) and widen only to the entry points and callers those hunks touch.

Identify:
- **Entry points:** where attacker- or user-controlled data enters (HTTP handlers, CLI args, files, queues, LLM prompts and tool outputs, uploaded documents, environment).
- **Trust boundaries:** privileges the code runs with; what crosses process, network or tenant boundaries.
- **Assets at risk:** credentials, tokens, PHI/PII, claims and financial data, files, network access, model/tool permissions.

Write `THREAT_MODEL.md` (output location above):

```
# Threat Model: <system or change>
## 1. System context
## 2. Assets
| asset | description | sensitivity |
## 3. Entry points & trust boundaries
| entry_point | description | trust_boundary | reachable_assets |
## 4. Threats
| id | threat | surface | asset | impact | likelihood |
## 5. Open questions
```

Full mode only: show the draft and ask whether to refine it before Stage 2.

## Stage 2: Find

Read-only: no shell commands that execute project code. Search each category, prioritising the entry points from Stage 1.

**HIGH VALUE (always report):**
- Injection: SQL, NoSQL, OS command (`shell=True`, string-built commands), template, LDAP, XPath
- Code execution: `eval`/`exec`, unsafe deserialization (`pickle`, `yaml.load` without `SafeLoader`, `marshal`), dynamic imports from input
- Path traversal and unsafe file handling (user input in paths, zip-slip, world-writable temp files)
- SSRF and open redirects (user-controlled URLs fetched server-side)
- Broken authentication/authorization: missing checks, IDOR, privilege escalation, JWT/session misuse
- Hardcoded secrets, tokens, keys, connection strings; secrets written to logs, errors or reports
- **PHI/PII exposure:** patient or member identifiers, names, DOB, addresses, claim details in logs, exceptions, LLM prompts sent to external services, cached files, or outputs without masking
- Crypto and transport: disabled TLS verification (`verify=False`, `ssl-no-revoke` used beyond its documented reason), weak hashing for secrets, predictable randomness for tokens
- **LLM/agent risks:** prompt injection from documents or tool output reaching tool calls or file/shell actions, model output executed or trusted as code/SQL, missing allow-lists on agent tools
- Memory safety (C/C++/unsafe code): buffer overflows, use-after-free, integer overflow into sizes, format strings
- Dependency changes: new or upgraded packages with known vulnerabilities, unpinned or typo-squat-looking names, license changes

**LOW VALUE (note, keep searching):**
- Missing security headers, verbose errors without sensitive data, DoS-only issues, assertion failures

Emit each candidate:
```xml
<finding>
<id>F-NN</id>
<file>path/to/file.py:line</file>
<category>command-injection | phi-exposure | ...</category>
<description>Root cause, how an attacker (or untrusted input) controls the trigger, and the trigger condition.</description>
</finding>
```

## Stage 3: Triage

Re-read each finding's source lines independently of Stage 2. For each:
- Confirm it is real; cite the exact `file:line`. Drop anything you cannot confirm.
- Assess reachability across the trust boundaries from Stage 1.
- Assign severity: **critical** (reachable RCE, auth bypass, mass PHI/PII or secret exposure), **high** (privilege escalation, significant data leak, injection with limited reach), **medium** (limited-impact leak, SSRF to internal metadata blocked elsewhere, DoS), **low** (defense in depth).
- Collapse duplicates that share a root cause.

## Stage 4: Report

Write `vulnerability_report.json` (output location above). Every field is required; use `null` when not applicable.

```json
{
  "mode": "review | full",
  "scope": "<diff range or directory>",
  "findings": [
    {
      "id": "F-01",
      "category": "<category>",
      "severity": "critical | high | medium | low",
      "file": "path/to/file:line",
      "description": "<root cause, attacker control, trigger>",
      "recommendation": "<concrete fix>"
    }
  ]
}
```

Then print a summary table (`ID | Category | Severity | File`) and the report path.

**In review mode**, hand the result back to the calling review as its `## Security` section: the table, one line per finding with the fix, and a verdict (**Clean**, **Fix before merge** if any critical/high, **Non-blocking** for medium/low only). Critical and high findings are Important or Critical review findings: they enter the fix loop like any other blocking finding. Describe leaked secrets or PHI instead of quoting them.

## Notes

- Never run the code under review to "confirm" a vulnerability; triage by reading.
- For a large full-mode scan with several independent entry points, scan them in parallel with subagents, one entry point each, then triage together.
- `scripts/vuln_agent.py` runs the same pipeline outside an agent session through an agent SDK (see the script header for its requirements): `uv run --with-requirements scripts/requirements.txt scripts/vuln_agent.py <target_dir>`. Optional; the stages above are the skill.
