"""
Vulnerability Detection Agent — multi-stage pipeline using the Claude Agent SDK.

Pipeline:
  canary/ (or TARGET_DIR) → [Threat Model] → THREAT_MODEL.md
                                                    ↓
                                          [Find Agent (read-only loop)]
                                                    ↓
                                          [Triage Agent (re-verify)]
                                                    ↓
                                          [Report Agent → JSON]

Usage:
  uv run vuln_agent.py <target_dir> [output_dir]

Artifacts (THREAT_MODEL.md, vulnerability_report.json) go to output_dir,
default <target_dir>/.godmode/security/<timestamp>/ (git-ignored), never
into the scanned source tree itself.

Requires:
  claude-agent-sdk >= 0.1
  python-dotenv
  ANTHROPIC_API_KEY in environment or .env
"""

import asyncio
import json
import sys
from collections.abc import AsyncIterator
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    Message,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    query,
)

load_dotenv()

MODEL = "claude-opus-4-8"

ENGAGEMENT_CONTEXT = """\
## Engagement context
This is authorized security research conducted as a defensive security
assessment. The target is read-only source code. Findings are collected
for responsible-disclosure workflow testing.
"""

THREAT_MODEL_SCHEMA = """\
# Threat Model: <system name>
## 1. System context
## 2. Assets
| asset | description | sensitivity |
## 3. Entry points & trust boundaries
| entry_point | description | trust_boundary | reachable_assets |
## 4. Threats
| id | threat | surface | asset | impact | likelihood |
## 5. Open questions
"""

FIND_PROMPT_TEMPLATE = """\
Find memory-safety and security bugs in the target source tree using the file tools.

## Threat model
{threat_model}

## Quality tiers

**HIGH VALUE (report these):**
- Heap buffer overflow (unchecked memcpy/strcpy into fixed-size buffers)
- Use-after-free / double-free
- Stack buffer overflow
- Integer overflow feeding into allocation sizes or copy lengths
- Format string injection
- SQL / command injection
- Hardcoded credentials or secrets
- Insecure deserialization
- Path traversal

**LOW VALUE (note but keep looking):**
- Assertion failures (clean abort, no corruption)
- Stack exhaustion from recursion (DoS only)
- Null-pointer deref at fixed small offsets

## Output format
<finding>
<id>F-NN</id>
<file>path:line</file>
<category>heap-buffer-overflow | stack-buffer-overflow | use-after-free | ...</category>
<description>one paragraph: root cause, attacker control, trigger condition</description>
</finding>
"""

TRIAGE_PROMPT_TEMPLATE = """\
Triage these findings against the source and the threat model.
For each: verify it is real (cite the line), derive severity from
reachability across trust boundaries, and collapse duplicates by root cause.

## Threat model
{threat_model}

## Raw findings
{findings}
"""

REPORT_SCHEMA = {
    "type": "object",
    "properties": {
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id":             {"type": ["string", "null"]},
                    "category":       {"type": ["string", "null"]},
                    "severity":       {"type": "string", "enum": ["critical", "high", "medium", "low"]},
                    "file":           {"type": ["string", "null"]},
                    "description":    {"type": ["string", "null"]},
                    "recommendation": {"type": ["string", "null"]},
                },
                "required": ["id", "category", "severity", "file", "description", "recommendation"],
            },
        }
    },
    "required": ["findings"],
}

REPORT_PROMPT_TEMPLATE = """\
Convert the triaged findings into strict JSON conforming to this schema.
Every field is required; use null for not-applicable.
Respond with JSON only — no surrounding prose or code fences.

## Schema
{schema}

## Triaged findings
{triaged}
"""


async def collect(stream: AsyncIterator[Message]) -> str:
    final = ""
    async for msg in stream:
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, ToolUseBlock):
                    args = str(block.input)
                    if len(args) > 120:
                        args = args[:120] + "...}"
                    print(f"  [tool] {block.name} {args}")
                elif isinstance(block, TextBlock) and block.text.strip():
                    final += block.text
        elif isinstance(msg, ResultMessage) and msg.is_error:
            raise RuntimeError(msg.result)
    return final


async def run(target_dir: Path, out_dir: Path) -> dict:
    print(f"\n=== Stage 1: Threat Model ({target_dir}) ===")

    tm_options = ClaudeAgentOptions(
        model=MODEL,
        cwd=str(target_dir),
        system_prompt={"type": "preset", "preset": "claude_code", "append": ENGAGEMENT_CONTEXT},
        allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"],
        disallowed_tools=["Bash"],
        permission_mode="acceptEdits",
    )

    bootstrap_prompt = (
        f"You are bootstrapping a threat model from source code alone. "
        f"Read the source files in this directory and emit a draft threat model "
        f"in the schema below. Note in section 5 what you could NOT determine "
        f"from the code alone. Do not write any files yet.\n\n"
        f"## Schema\n{THREAT_MODEL_SCHEMA}"
    )

    threat_model_path = out_dir / "THREAT_MODEL.md"
    write_prompt = (
        f"Now write the refined threat model to `{threat_model_path.as_posix()}`. "
        "Do not write anywhere else."
    )

    async with ClaudeSDKClient(options=tm_options) as tm_agent:
        await tm_agent.query(bootstrap_prompt)
        draft = await collect(tm_agent.receive_response())
        print(f"  Draft threat model: {len(draft)} chars")

        await tm_agent.query(write_prompt)
        await collect(tm_agent.receive_response())

    threat_model = threat_model_path.read_text() if threat_model_path.exists() else draft

    print(f"\n=== Stage 2: Find ===")
    find_options = ClaudeAgentOptions(
        model=MODEL,
        cwd=str(target_dir),
        system_prompt={"type": "preset", "preset": "claude_code", "append": ENGAGEMENT_CONTEXT},
        allowed_tools=["Read", "Grep", "Glob"],
        disallowed_tools=["Bash"],
    )
    findings_text = await collect(
        query(
            prompt=FIND_PROMPT_TEMPLATE.format(threat_model=threat_model),
            options=find_options,
        )
    )
    print(f"  Raw findings: {len(findings_text)} chars")

    print(f"\n=== Stage 3: Triage ===")
    triage_options = ClaudeAgentOptions(
        model=MODEL,
        cwd=str(target_dir),
        system_prompt={"type": "preset", "preset": "claude_code", "append": ENGAGEMENT_CONTEXT},
        allowed_tools=["Read", "Grep"],
        disallowed_tools=["Bash"],
    )
    triaged_text = await collect(
        query(
            prompt=TRIAGE_PROMPT_TEMPLATE.format(
                threat_model=threat_model,
                findings=findings_text,
            ),
            options=triage_options,
        )
    )
    print(f"  Triaged findings: {len(triaged_text)} chars")

    print(f"\n=== Stage 4: Report ===")
    report_options = ClaudeAgentOptions(
        model=MODEL,
        system_prompt={"type": "preset", "preset": "claude_code", "append": ENGAGEMENT_CONTEXT},
        allowed_tools=[],
    )
    report_json_text = await collect(
        query(
            prompt=REPORT_PROMPT_TEMPLATE.format(
                schema=json.dumps(REPORT_SCHEMA, indent=2),
                triaged=triaged_text,
            ),
            options=report_options,
        )
    )

    report = json.loads(report_json_text.strip())
    report_path = out_dir / "vulnerability_report.json"
    report_path.write_text(json.dumps(report, indent=2))
    print(f"  Report written to {report_path}")

    return report


def print_summary(report: dict) -> None:
    findings = report.get("findings", [])
    print(f"\n{'='*60}")
    print(f"VULNERABILITY REPORT — {len(findings)} finding(s)")
    print(f"{'='*60}")
    print(f"{'ID':<8} {'Severity':<10} {'Category':<30} {'File'}")
    print(f"{'-'*8} {'-'*10} {'-'*30} {'-'*30}")
    for f in findings:
        print(f"{f['id']:<8} {f['severity']:<10} {(f['category'] or ''):<30} {f['file'] or ''}")
    print()


async def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <target_directory> [output_directory]")
        sys.exit(1)

    target_dir = Path(sys.argv[1]).resolve()
    if not target_dir.is_dir():
        print(f"Error: {target_dir} is not a directory")
        sys.exit(1)

    if len(sys.argv) > 2:
        out_dir = Path(sys.argv[2]).resolve()
    else:
        security_root = target_dir / ".godmode" / "security"
        out_dir = security_root / datetime.now().strftime("%Y%m%d-%H%M")
        security_root.mkdir(parents=True, exist_ok=True)
        ignore = security_root / ".gitignore"
        if not ignore.exists():
            ignore.write_text("*\n")
    out_dir.mkdir(parents=True, exist_ok=True)

    report = await run(target_dir, out_dir)
    print_summary(report)


if __name__ == "__main__":
    asyncio.run(main())
