# Godmode session diagnosis bundle

<!-- ste:off -->
Session: <session-id>
Harness: <name> <version> (<provenance label>)    Godmode: <version> (<sha or "not a checkout">; <provenance label>)
Redaction level: skeleton | evidence | full
Built: <ISO timestamp>
<!-- ste:on -->

Qualify each version field in the header as historical evidence,
unverified snapshot, current observation, or unknown. `environment.json`
carries the same provenance distinctions for each environment field and
its supporting location.

## What this is

This is a scrubbed record of a coding-agent session that had godmode
installed and went wrong. With it, an agent or person who was not present
can decide whether godmode contributed. If it did, they can decide what to
change. The report inside states what happened, with `path:line` evidence.
By design, it contains no diagnosis of godmode and no proposed fix. That is
the job of the reader.

## Files

- `report.md` — the diagnosis report (problem statement, verdict,
  environment, sessions, timeline, findings, involvement, coverage notes).
- `case.md` — the case file that the analysts used.
- `environment.json` — a machine-readable copy of the environment section.
- `timeline.md` — the timeline for each turn.
- `findings/<dimension>.md` — the raw analyst findings for each dimension.
- `transcripts/<session-id>.md` — a condensed rendering, turn by turn, of
  each examined session (never the raw JSONL). Tool-result bodies by level:

  | Level | Tool-result bodies |
  |---|---|
  | skeleton | intentionally limited. Each body becomes `[tool result: <tool>, <bytes> bytes, exit <code>]`. |
  | evidence | kept for cited events, including the commands and results that are necessary to support findings |
  | full | all kept |
- `scrub-log.md` — each placeholder that the scrub used, and its category
  (never the original value).

## How to read it

Start with `report.md` §1–2. Then read §7 (involvement) and the evidence
lines that it cites. Then read the matching turns in `transcripts/`. The
`path:line` references point to the original files on the machine of the
reporter. The condensed transcripts keep the same line numbers as `[L<n>]`
markers.

## Redaction

Placeholders have this shape: `<EMAIL-1>`, `<PERSON-2>`, `<SECRET-3>`,
`<HOST-4>`, `<REPO-5>`, `<ORG-6>`, `<PROPRIETARY-7>`. The scrub rewrites
home paths to `~/…`. In this bundle, the same placeholder always refers to
the same original value.

## Producer instructions

In a completed bundle, the actual results replace these instructions.

After the scrub, verify each material exported finding. Use only this
bundle:

1. Resolve its citation to an included transcript/source marker.
2. Read the cited command/result or quotation.
3. Verify that it supports the claim.

It is not sufficient that the path and the line exist. If the redaction
level or a necessary withholding removes support, record the specific
limitations.

Reconcile the report, case, environment, findings, README and any local
issue draft. Count the scrub-log entries again against the final files. Do
not include the log itself. Remove old export statements. Keep the bundle
preparation separate from the archive delivery. Keep a mapping from
historical anchors to included evidence.

Record the independent privacy audit separately from the usefulness of the
evidence:
- Privacy audit: CLEAN or unresolved misses.
- Evidence support: supported or limited, with affected findings and reasons.

If the content changes after a check, do each affected check again. For the
existing archive approval, show the final log, the file list and both
outcomes. Archive the reviewed files. Verify that the delivered archive
matches them. Record the archive delivery outside the reviewed bundle. Do
not change its contents after approval. A scrub is not a full privacy
certification.
