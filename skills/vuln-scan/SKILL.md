---
name: vuln-scan
description: Security vulnerability scan of code you own. Use it as the security pass of every code review (requesting-code-review, MR/PR reviews, final branch reviews), with the changed files as the scope. Also use it when the user asks to scan a codebase or directory for vulnerabilities. Use it when the user asks to look for security issues, secrets, injection, or PHI/PII exposure, or wants a threat model.
---

# Vulnerability Scan

This is a scan that starts with the threat model. It has four stages: **threat model → find → triage → report**. It has two modes:

| Mode | When | Scope | Prompts? |
|---|---|---|---|
| **Review** | A code review calls it (`requesting-code-review`, `mr-full-review`, the final review in `subagent-driven-development` / `executing-plans`) | The diff range of the review: the changed files, and the call sites and entry points that they touch | None. The code under review is in the repo of your human partner, so the authorization is implied. You never stop the review to ask. |
| **Full** | Your human partner asks to scan a codebase or directory | The target directory | Get approval for authorization one time. Then show the threat-model draft and ask whether to refine it before Stage 2. |

## Output location

Write artifacts outside tracked files, in `.godmode/security/<YYYYMMDD-HHMM>-<scope>/` at the repo root. If `.godmode/security/.gitignore` does not exist, create it with the content `*`. Never write `THREAT_MODEL.md` or reports into the scanned source tree. Outside a git repo, use the system temp directory and report the path.

## Stage 1: Threat model

Examine the code with read-only tools (read, grep, glob). In review mode, start from the diff (`git diff <base>...<head> --stat`, then the changed hunks). Go wider only to the entry points and callers that those hunks touch.

Identify:
- **Entry points:** where data from an attacker or a user comes in. Examples are HTTP handlers, CLI args, files, queues, LLM prompts and tool outputs, uploaded documents, environment.
- **Trust boundaries:** the privileges that the code runs with, and what crosses process, network or tenant boundaries.
- **Assets at risk:** credentials, tokens, PHI/PII, claims and financial data, files, network access, model/tool permissions.

Write `THREAT_MODEL.md` (see the output location above):

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

Use only read-only tools in this stage. Do not use shell commands that run project code. Search each category. Give priority to the entry points from Stage 1.

**HIGH VALUE (always report):**
- Injection: SQL, NoSQL, OS command (`shell=True`, commands built from strings), template, LDAP, XPath
- Code execution: `eval`/`exec`, unsafe deserialization (`pickle`, `yaml.load` without `SafeLoader`, `marshal`), dynamic imports from input
- Path traversal and unsafe file handling (user input in paths, zip-slip, world-writable temp files)
- SSRF and open redirects (URLs that a user controls and that the server gets)
- Broken authentication/authorization: a missing access check, IDOR, privilege escalation, JWT/session misuse
- Hardcoded secrets, tokens, keys, connection strings. Also secrets that the code writes to logs, errors or reports
- **PHI/PII exposure:** patient or member identifiers, names, DOB, addresses, claim details without masking. Look in logs, exceptions, LLM prompts sent to external services, cached files, or outputs
- Crypto and transport: disabled TLS verification (`verify=False`, `ssl-no-revoke` used for more than its documented reason), weak hashing for secrets, predictable randomness for tokens
- **LLM/agent risks:** prompt injection from documents or tool output that gets to tool calls or file/shell actions. Model output that the code runs or trusts as code/SQL. Missing allow-lists on agent tools
- Memory safety (C/C++/unsafe code): buffer overflows, use-after-free, integer overflow into sizes, format strings
- Dependency changes: new or upgraded packages with known vulnerabilities, unpinned names or names that look like typo-squats, license changes

**LOW VALUE (record them, and continue the search):**
- Missing security headers, verbose errors without sensitive data, DoS-only issues, assertion failures

Write each candidate in this format:
```xml
<finding>
<id>F-NN</id>
<file>path/to/file.py:line</file>
<category>command-injection | phi-exposure | ...</category>
<description>Root cause, how an attacker (or untrusted input) controls the trigger, and the trigger condition.</description>
</finding>
```

## Stage 3: Triage

Read the source lines of each finding again, independently of Stage 2. For each finding:
- Verify that it is real. Cite the exact `file:line`. Remove each finding that you cannot verify.
- Find whether an attacker can get to it across the trust boundaries from Stage 1.
- Give a severity. **critical** (reachable RCE, auth bypass, mass PHI/PII or secret exposure). **high** (privilege escalation, significant data leak, injection with limited reach). **medium** (limited-impact leak, SSRF to internal metadata blocked elsewhere, DoS). **low** (defense in depth).
- Merge duplicates that have the same root cause.

## Stage 4: Report

Write `vulnerability_report.json` (see the output location above). Each field is required. Use `null` when a field does not apply.

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

**In review mode**, give the result back to the calling review as its `## Security` section. The section contains the table, one line for each finding with the fix, and a verdict. The verdict is **Clean**, **Fix before merge** if there is a critical or high finding, or **Non-blocking** if there are only medium or low findings. Critical and high findings are Important or Critical review findings. They go into the fix loop like any other blocking finding. Describe leaked secrets or PHI. Do not quote them.

## Notes

- Never run the code under review to "confirm" a vulnerability. Do the triage by reading.
- A large full-mode scan can have several independent entry points. In that case, scan them in parallel with subagents, one entry point for each subagent. Then do the triage together.
- `scripts/vuln_agent.py` runs the same pipeline outside an agent session through an agent SDK (see the script header for its requirements): `uv run --with-requirements scripts/requirements.txt scripts/vuln_agent.py <target_dir>`. It is optional. The stages above are the skill.
