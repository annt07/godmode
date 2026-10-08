# Meaning review brief (STE rewrite)

You are a fresh reviewer. You did not write these files. Read-only: do not change a file.

## Your task

The files below were rewritten in Simplified Technical English (STE). The rewrite must change the form of the text only. Compare each file with its original and find each place where the meaning changed.

For each file:

1. Get the original: `git show ste-base:<path>`.
2. Read the new file at `<path>`.
3. Compare them section by section with the checklist below.

## Checklist

- Each step is present, in the same order.
- Each gate and approval rule is present, with the same actor. Who acts must not change.
- Each condition (if, when, unless, only, before, after) is present.
- Each hedge has the same strength ("may", "can", "usually", "often" must not become a fact, and a fact must not become a hedge).
- Each red-flag row keeps its idea. The quoted thought in the left column must be byte for byte the same.
- The description keeps its trigger meaning.
- No rule is new. No example is removed.
- "confirm" in the original: if the agent tests a fact, the new word is "verify". If the user agrees, the new word is "approve" or "agree". "verify" for a user approval is a finding.
- Numbers, code, commands, paths and skill names are the same.

## Output

```
## <path>
Verdict: PASS | FAIL
Findings:
1. Old: "<original sentence>" / New: "<new sentence>" / Lost or changed: <what changed>
```

Write "Findings: none" for a PASS. Report only changes in meaning, not style.
