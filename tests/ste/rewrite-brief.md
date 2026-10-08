# STE rewrite brief (for a batch writer)

You rewrite godmode skill files in Simplified Technical English (STE). Change the form only. The meaning of each sentence must stay the same.

## Read first

1. `skills/ste-writing/SKILL.md`: the rules, the two text types and the exempt text.
2. `skills/ste-writing/glossary.md`: one word for each action, and the technical nouns.
3. One finished example: compare `git show ste-base:skills/grilling/SKILL.md` with `skills/grilling/SKILL.md`.

## Rules for the rewrite

- Procedural text (steps, checklists, briefs, "Reality" cells that give a command): imperative, one instruction in each sentence, 20 words or fewer, condition first, no passive voice.
- Descriptive text: 25 words or fewer, key information first, active voice.
- Keep byte for byte: code blocks, inline code, links, file paths, commands, skill names, numbers, headings, quoted text (text between double quotes), and each "REQUIRED", "STOP", "MUST" and "Never".
- Keep the same number of table rows and list items in each section. If STE needs a new vertical list, you can add one, but say so in your report.
- "confirm": use "verify" when the agent tests a fact. Use "approve" or "agree" when the user agrees. Never use "verify" for a user approval.
- "check" as a verb becomes "verify". "check" as a noun stays ("a check").
- The glossary "Do not use" words become the "Use" word (delete → remove, begin → start, modify → change, and so on).
- Keep each hedge ("may", "can", "should have", "usually", "often") at the same strength. Do not change a hedge into a fact. Do not change an expectation ("it should have been made") into a statement ("it was made").
- Keep who acts. Add no fact, no mechanism and no rule.
- A thought in a red-flag table is a quote. Keep it exactly.
- Keep present perfect only when the simple tense loses meaning.
- For a bad example of more than one line, put it between `<!-- ste:off -->` and `<!-- ste:on -->`.
- In a description, keep each phrase from `tests/ste/triggers.json` for that file.

## Verify before you report

From the repository root:

```bash
uv run python skills/ste-writing/scripts/ste-lint.py --glossary skills/ste-writing/glossary.md <your files>
uv run python tests/ste/meaning_diff.py ste-base <your files>
```

The linter must show 0 hard findings. Each remaining passive voice must have an unknown actor. The diff script must show no change, or only changes that you list with a reason.

Do not commit. Do not change files outside your list.

## Report

- For each file: words before and after, the remaining advisory findings, and each structure change with its reason.
- Each place where you were not sure that the meaning stayed the same.
