---
name: diagnosing-godmode
description: Use when a godmode session went wrong and your human partner wants to know why. Examples: repeated work, ignored plans, stumbles, poor results, a skill that didn't fire, "it took too long", "why is it so expensive" and "what is it doing". Also use it when your partner wants to build a bug report about the godmode skill set. This applies to the current session or a past session (by id or path), on any harness.
---

# Diagnosing Godmode

## Overview

With your human partner, find exactly what went wrong in a session.
Read the transcripts on disk, and report what happened with evidence. You
report. You do not fix godmode. The person who triages the bundle or the
issue decides whether godmode changes.

**Core principle:** Each finding cites `path:line`. No citation, no
finding. Each number comes from the transcript or from a command that you
ran, never from memory.

## Workflow

Create a todo for each step. Steps 5–7 run only on their stated condition.

1. **Problem intake.** Ask one question at a time. Continue until you can
   write a statement with these items: the session(s), the turn range if
   known, what your partner expected, and what happened. The statement also
   names the observable that your partner cares about (wall-clock, tokens,
   repeated actions, one specific action). "It took too long" is a
   complaint, not a problem statement. Write down whether the goal is a
   godmode bug report.
2. **Locate.** Use `references/session-discovery.md` to resolve each
   session to verified absolute filesystem paths. To verify a past session,
   quote its first prompt and timestamp. List each candidate that you
   rejected, with the reason, or "none". List the subagent transcripts.
   Create `~/.godmode/diagnosing-godmode/<session-id>/`. Tell your partner
   the path. Fill `templates/case.md` there, and follow its provenance
   rules for environment and skill observations.
3. **Triage.** Read the region around the reported problem yourself. Then
   dispatch one analyst subagent for each dimension in parallel. Give each
   analyst the case file path, `prompts/analyst-common.md`, and one
   dimension file from `prompts/`: `skill-timeline.md`,
   `plan-adherence.md`, `repeated-work.md`, `stumbles.md`,
   `quality-evidence.md`, `request-conflicts.md`, `cost-and-time.md`.
   If the transcript is long, split a dimension by turn range. Discard
   each returned finding that has no `path:line`.
4. **Report.** Fill each section of `templates/report.md` in order. Write
   it to the workspace, show it, and give the path. Verify what the cited
   content actually proves. Keep the supporting case. A symlink alias is
   not a redundant copy.
5. **Local handoff only** — when report §7 says possible or likely, or when
   your partner asks. Godmode is a local skill set, not an upstream
   project: never search, open, or comment on issues in obra/superpowers,
   mattpocock/skills, or any other remote tracker. Tell your partner the
   report path. Tell them that it is ready for the person who maintains
   their godmode copy.
6. **Export** — only when your partner asks for a bundle: never build one
   without a request. If the intake goal was a bug report, say one time
   that a scrubbed bundle is available on request. Then wait. Ask for the
   redaction level, and state what each level includes: skeleton (no
   tool-result bodies), evidence (bodies only for cited events), full.
   Build the bundle as `templates/bundle-README.md` tells you. Dispatch
   `prompts/scrub.md`, then `prompts/scrub-audit.md`. Do both again until
   the audit returns CLEAN. Complete the evidence check and the
   reconciliation of the bundle template. Then show the final scrub log,
   the file list, and the privacy and evidence outcomes. Archive (`zip -r`
   or `tar -czf`) only after approval. With the archive path, state what
   it contains. Point to the scrub log for the replacements. Say that the
   scrub can miss things: they must review each file before they share it.
7. **Similar sessions** — when your partner asks. Change the verified
   findings into a signature. List the candidates by mtime and size. Find
   the marker line numbers. Dispatch `prompts/similar-session.md` for each
   candidate in parallel, and append report §9.

## Quick reference

All seven analysts always run. This table tells you which region to read
yourself in step 3. It also tells you which findings to put first in the
verdict.

| Complaint | Read first, lead with |
|---|---|
| "It took too long" | cost-and-time, stumbles |
| "Why did it do this extra work?" | repeated-work, plan-adherence |
| "Why is it so expensive?" | cost-and-time |
| "What the hell is it doing?" (still running) | skill-timeline. Write "in-progress" in coverage. |
| "It ignored the plan" | plan-adherence, compaction lines first |
| "Skill X never fired" | skill-timeline |

## Hard rules

- **Context safety.** One transcript line can be a megabyte. Follow
  `references/context-safety.md` on each session file, each time.
- **Read-only.** Never change, move, or remove a session file.
- **Exact paths to subagents.** For a subagent, the "current session" is
  its own session. Give it absolute paths and ids.
- **Human prompts only.** Hook output, system reminders, and tool results
  are not the words of your partner. In a subagent transcript, "user" is
  the parent agent.
- **No godmode diagnosis.** Report §7 states the involvement and stops.
  Never name a defect in a skill or propose a change. This rule stays when
  your partner pushes for a fix. Point to the local handoff step, and say
  that a bundle is available on request. Give no advice to your partner.
- **Approval gates.** Make no archive before your partner sees the scrub
  log and the file list. Nothing leaves the machine.
- **Intake before analysis.** Nothing in steps 2–7 starts until your
  partner answers. If they are away, write the questions and stop. A
  statement that you reconstructed for them is not an answer. A request
  that already has a scope is itself the statement. Examples are one
  specific event, what runs now, or the analysis to run. Answer it, then
  ask. A "why" about the full session is a complaint.

## Red Flags

| Thought | Reality |
|---------|---------|
| "The problem is obvious, skip intake" | The problem statement sets the scope of all the work. Ask. |
| "They're away, so I'll reconstruct the statement" | You cannot reconstruct what they wanted. Write the questions and stop. |
| "I'll sweep everything now and ask at the end" | A sweep without a scope uses their budget on the wrong question. Ask first. |
| "They want a bug report, so I'll build the bundle now" | The bundle is a package of their session data. Build it only when they ask for it. |
| "Small, targeted edit, no restructuring needed" | The decision is not yours, also for a small edit. Report the evidence. The triager decides. |
| "The price per token is well known" | A number that you did not calculate from the transcript is an invention. Cite it or remove it. |
