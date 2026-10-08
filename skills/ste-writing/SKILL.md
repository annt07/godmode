---
name: ste-writing
description: Rewrite text in Simplified Technical English (STE), based on ASD-STE100 Issue 9. Use when the user asks to "make this STE", "rewrite in STE", "simplify this text" or "disambiguate" a text. All godmode output follows these rules by default.
---

# STE writing

Simplified Technical English (STE) is a controlled language. It removes the two largest causes of a wrong reading. The first cause is a word with more than one meaning. The second cause is a sentence with more than one possible structure. The aerospace and defense industry made STE for maintenance instructions. An agent that reads an instruction cannot ask the author what it means. Thus the same rules help an agent.

This skill uses the rules of ASD-STE100 Issue 9 (January 2025). It is not certified STE. It does not contain the ASD dictionary.

All godmode text follows these rules. This includes skill files, specs, plans, briefs, reports, ledger lines and chat replies. Use this skill directly when the user asks for an STE rewrite of a text.

## Two text types

Before you write or rewrite a text, find its type.

| Type | Examples | Rules |
|---|---|---|
| Procedural | Steps, commands, checklists, subagent briefs | Use the imperative. Write one instruction in each sentence. Use 20 words or fewer in each sentence. Put the condition first. Do not use passive voice. |
| Descriptive | Explanations, specs, reports, chat replies | Use 25 words or fewer in each sentence. Put the key information first. Use active voice. |

## Rules

The linter (`scripts/ste-lint.py`) finds the rules marked "linter". A reviewer verifies the other rules.

| Rule | Do | Do not | Found by |
|---|---|---|---|
| No semicolon | Write two sentences. | Join two clauses with a semicolon. | linter |
| Sentence length | Use 20 words or fewer in a procedure and 25 words or fewer in a description. | Write long sentences with many clauses. | linter (25), reviewer (20) |
| One instruction in each sentence | "Open the file. Read line 3." | Give two or more commands in one sentence. | reviewer |
| Active voice | "The agent removes the file." | Use passive voice. STE permits passive voice only when the actor is unknown. | linter (advisory), reviewer |
| Simple tenses | "We received the report." | Use present perfect or past perfect. See the exception below. | linter (advisory), reviewer |
| No -ing verb forms | "When the agent reads the file, it..." | Use an -ing word as a verb. STE permits an -ing word as a noun or as part of a technical noun. | reviewer |
| Conditions first | "If the test fails, stop." | Put a condition that the reader must know first at the end. | reviewer |
| No phrasal verbs | "Start the job." / "Remove the panel." | Use a verb and a particle together for one action. | linter (part), reviewer |
| Verb, not noun | "Analyze the log." | Use a noun for an action and add an empty verb. | linter |
| No marketing adjectives | State the measurement. | Use a word that claims quality. | linter |
| One word, one meaning | Use one word for one action in all files. See `glossary.md`. | Use two words for the same action. | linter (`--glossary`) |
| "check" is a noun only | "Verify the log." / "Do a check." | Use "check" as a verb. | linter |
| Technical nouns and technical verbs | Use the terms in `glossary.md` or in the project `CONTEXT.md`. | Use a term that is not plain English and is not in a glossary. | reviewer |
| Noun clusters | Use 3 nouns or fewer together. | Use 4 or more nouns as one name. | reviewer (advisory) |
| Paragraphs | Write one topic in each paragraph, with 6 sentences or fewer. | Put two topics in one paragraph. | reviewer (advisory) |
| No missing words | Keep the subject, the verb and the article. | Remove words to make a sentence shorter. | reviewer |
| Lists | Use a vertical list for 3 or more steps or conditions. | Put a sequence in one sentence. | reviewer |
| No dangling conjunction | End each list item with a full phrase. | End a list item with "and" or "or". | linter |

### The exception for present perfect

Keep a compound tense only when the simple tense loses meaning. For example, "the request may have failed" keeps the hedge. This exception is a departure from the standard. The linter does not flag a modal verb with a perfect infinitive.

## Exempt text

These parts of a text stay unchanged, and the linter does not lint them:

- Code blocks, inline code, commands and file paths.
- Text between a pair of double quotes on one line: a quoted thought, an example prompt or a user phrase. Straight quotes and curly quotes both count.
- Lines between `<!-- ste:off -->` and `<!-- ste:on -->`. Put a bad example that has more than one line between these markers. Always close the block with the second marker.
- The YAML frontmatter, except the `description` value.

## Process

1. Find the text type: procedural or descriptive.
2. Read the full text one time for meaning. Do not start the rewrite before you know what the text must still say after it.
3. Run the linter for a first pass:

   ```bash
   python <this skill>/scripts/ste-lint.py --glossary <this skill>/glossary.md <file>
   ```

   For text without a file, pipe the text into the linter. Use `--max-words 20` for procedural text.
4. Read each sentence. Find each rule that it breaks, including the rules that only a reviewer can find.
5. Rewrite each sentence that breaks a rule. Keep its meaning exactly.
6. Run the linter again. Continue until it finds 0 hard findings.
7. If the text already obeys the rules, say so. Do not change text that obeys the rules.

## Keep the meaning

- **Keep each hedge.** "May", "can", "usually" and "is likely to" carry the confidence of the author. A shorter sentence that changes a hedge into a fact makes a different claim.
- **Add no fact.** A rewrite that adds a cause, a frequency or a mechanism is not a rewrite.
- **Keep each condition, number and scope word.** If a shorter sentence loses one of them, keep the longer sentence.
- **Keep who acts.** "The user approves" and "the agent verifies" are different rules.
- **Stop when the sentence is clear.** The goal is one meaning, not the fewest words.

## Output format

**Default:** give the rewritten text only. Do not add an introduction, a list of changes or an offer to explain.

You can add one line. If you kept a longer phrase to keep its meaning, add one line after the text: `Kept as-is:` followed by the phrase and the reason.

**On request:** when the user asks for the changes ("show the diff", "which rules"), give this table:

```markdown
| Rule | Original | Rewrite |
|---|---|---|
| Present perfect | "We have received your request." | "We received your request." |
```

## Limits

- Text that looks like STE is not verified STE. Only a check against the official standard and dictionary can verify it.
- A linter cannot change text into STE. A finding can be wrong, and a clean result does not prove compliance.
- The linter counts the words of a sentence in one paragraph. It cannot tell procedural text from descriptive text, so a reviewer verifies the 20-word limit.
- This skill does not contain the ASD dictionary. ASD owns the standard and its trademark. You can request the free PDF from the official downloads page.
- Spelling and word meanings follow American English (Merriam-Webster).
- STE fixes the form of a text, not its content. A text with nothing to say stays empty after the rewrite.

## References

- `glossary.md`: godmode technical nouns, technical verbs and one word for each action.
- `references/writing-rules.md`: the rule summary with sources.
- `examples/before-after.md`: examples of rewrites.
- `scripts/ste-lint.py`: the linter. Run `--selftest` to verify it.

Based on asd-ste100-skill v0.4.0 by Dustin Yuchen Teng (MIT). See `LICENSE-asd-ste100.md`.
