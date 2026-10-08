---
status: reviewed (4 independent review rounds), waiting for user approval
date: 2026-10-08
sources: asd-ste100-skill v0.4.0 (MIT, Dustin Yuchen Teng). Research note docs/research/asd-ste100-official-2026-10-08.md.
---

# Spec: STE writing in godmode

## Problem Statement

The godmode skills tell an agent what to do. The agent cannot ask the author when a sentence has two possible meanings.

The skill text now has long sentences, semicolons, passive voice with no actor, and several words for one action. The STE linter finds 492 findings in the 33 `SKILL.md` files. These files have 41,222 words. The 40 support files (prompts, references, templates) are not in this count.

The text that the agent writes has the same problems. Specs, plans, subagent briefs, review reports, ledger lines and chat replies go to other agents and to people. These readers also cannot ask the writer what the text means.

The user wants one controlled language for all godmode text: ASD-STE100 Simplified Technical English (STE). STE prevents the misreading of maintenance instructions. An agent that reads a skill has the same problem as a maintenance technician.

## Solution

1. Add a godmode skill with the name `ste-writing`. It holds the STE rules, the godmode glossary and the linter. Its source is `asd-ste100-skill`, with the corrections that the official sources require.
2. Rewrite every godmode skill file in STE. The rewrite keeps every rule, gate, number, red-flag row and hedge. Only the form of the text changes.
3. Make STE the default for all text that an agent writes when it uses godmode. The router gives this rule. The skills that write documents tell the agent to lint each document.
4. Add tests that lint all skill files. A new or changed skill must pass them.

## User Stories

1. As a godmode user, I want every skill in short, active sentences with one meaning, so that the agent does what I meant.
2. As a godmode user, I want specs, plans and review reports in STE, so that people and agents read them quickly and correctly.
3. As a godmode user, I want a separate `ste-writing` skill, so that I can ask for an STE rewrite of any text.
4. As a skill author, I want a linter in the test suite, so that new text cannot add semicolons, long sentences or synonym rotation again.
5. As a skill author, I want a glossary of godmode technical nouns and technical verbs, so that each term has one meaning in all files.
6. As a skill author, I want quoted text, code and bad examples to stay unchanged. Then red-flag quotes and examples still show the wrong thought or the wrong text.
7. As a godmode user, I want the skills to behave the same after the rewrite, so that the tested gates and triggers still work.
8. As a reviewer, I want each hedge ("may", "can", "usually") to stay, so that no rewrite changes a possibility into a fact.
9. As a godmode user, I want the skill to state its limits, so that nobody thinks that the text is certified STE.
10. As a subagent, I want my brief in procedural STE, so that each step is one clear command.

## Implementation Decisions

### D1. The `ste-writing` skill

1. `ste-writing` is a new model-invoked godmode skill. The name does not contain "ASD" or "ASD-STE100", because ASD owns the trademark (EU trade mark 017966390). The skill text says: "based on ASD-STE100 Issue 9, not certified".
2. Its description triggers only on explicit requests: "make this STE", "rewrite in STE", "simplify this text", "disambiguate". The router rule in D6 makes STE the default for other output. Thus the description does not fire on each turn.
3. The content comes from `asd-ste100-skill` v0.4.0. The MIT notice and the author credit go into the skill folder and into the godmode `LICENSE` file.
4. These changes to the upstream skill come from the research note:
   1. Two **text types** replace the two upstream modes. **Procedural** text is steps, commands, briefs and checklists. It uses the imperative, one instruction in each sentence, a maximum of 20 words in each sentence, and the condition first. **Descriptive** text is explanations, specs, reports and chat replies. It uses a maximum of 25 words in each sentence and puts the key information first.
   2. Passive voice is permitted **only when the actor is unknown**. The upstream skill also permits it when the actor is "irrelevant". That permission is removed. Procedural text never uses passive voice.
   3. New rule: **conditions first**. If the reader must know a condition before a step, the sentence starts with the condition.
   4. New rule: **no -ing verb forms**. An -ing word is permitted only as a noun or as part of a technical noun. Skill names (for example, "brainstorming", "grilling") are technical nouns.
   5. **Technical nouns** and **technical verbs** replace "domain terms". A term that is not plain English must be in the godmode glossary (D3) or in the project glossary (`CONTEXT.md`). Use these terms as little as possible.
   6. The public sources do not confirm some rule numbers and limits: Rule 8.1, Rule 9.3, Rule 3.7, the 3-word noun cluster and the 6-sentence paragraph. These rules stay, but the text does not show the rule numbers as official.
   7. A "Limits" section says three things. Text that looks like STE is not verified STE. A linter cannot change text into STE. The skill does not contain the ASD dictionary. This follows the STEMG AI White Paper (June 2026).
   8. Spelling and word meanings follow American English (Merriam-Webster), as the standard says.
   9. The upstream exception for present perfect stays. Keep a compound tense only when the simple tense loses meaning (for example, "may have failed"). The skill says that this exception is a departure from the standard.
5. The godmode router catalog, the README skill catalog and the README skill count get one new entry. The installer needs no change, because it copies all skill folders.

### D2. The linter

The linter `ste-lint.py` is copied into `ste-writing/scripts/`. Its upstream selftest stays. Godmode adds these changes. Each change has a unit test.

1. **Frontmatter.** The linter skips the YAML frontmatter, but it lints the `description` value. It gets the value as a YAML parser does:
   - A double-quoted or single-quoted value loses its outer quotes, and the linter applies the YAML escapes.
   - A plain value stays as it is.
   - A block value (`>` or `|`) and a value that continues on more lines are joined with spaces.

   After that, the quote rule in item 2 applies to the value. Thus a user phrase in quotes inside a description is exempt ("check for security issues"), and the rest of the description is linted.
2. **Quotes.** The linter skips text between a pair of double quotes on one line, the same as inline code. Straight quotes (`"`) and curly quotes (`“ ”`) both count. If a line has an unmatched quote, the linter skips nothing on that line. Thus a quote that continues on more lines is not exempt. Put such a quote between off markers (item 3). The linter applies this rule to each table cell separately. This rule exempts red-flag thoughts, example prompts and user phrases.
3. **Off markers.** The linter skips all lines between `<!-- ste:off -->` and `<!-- ste:on -->`. The official tools page says that checkers use markup to select the text that they examine. Use the markers for a bad example that has more than one line.
4. **Synonym groups.** "check" leaves the group check/verify/confirm/validate, because STE approves "check" only as a noun ("do a check"). "correct" leaves the group fix/repair/correct, because godmode uses it as an adjective ("the correct seam").
5. **New hard rule `check-verb`.** The linter flags "check" used as a verb. The godmode verb for this action is "verify". The noun stays permitted ("a check", "the check", "checklist", "spot check"). When "check" comes after a, an, the, this, that, each, every, no, one or a possessive word (my, your, its, our, their), the linter treats it as a noun and does not flag it. Otherwise, the rule uses these patterns, not case-sensitive:
   - "checks" or "checked" as a word
   - "check" followed by: the, that, whether, if, for, each, every, it, them, its, your, their, all, any
   - "check" as the first word of a sentence or a list item
   - "-check" after a hyphen, as in "sanity-check" and "double-check"

   The rule can give false findings. Put text with a false finding in quotes or between off markers, and give the reason in the batch review. A reviewer finds the verb uses that the patterns miss.
6. **Option `--max-words N`.** The default stays 25. The linter cannot tell procedural text from descriptive text. Thus a reviewer, not the linter, verifies the 20-word limit for procedural text.
7. **Option `--glossary FILE`.** The linter reads the glossary's list of words not to use (D3). To read this list, it reads the glossary file as raw text, because the list is between off markers. Then it flags each of these words as a hard finding in the files that it lints. This search uses the same text as the other rules. Thus code, inline code, links, quoted text and text between off markers are exempt. This rule finds synonym rotation between files, which the per-file rule cannot find.
8. **Sentences on more than one line.** The linter joins the lines of one paragraph before it counts the words of a sentence. It removes the `>` prefix of a blockquote line before it joins the line. A paragraph ends at a blank line, a heading, a list marker, a table row, a code fence, a line that starts with `<!--`, or the start or end of a blockquote. Thus a wrapped sentence is counted as one sentence. The finding shows the line where the sentence starts.
9. **Output.** The linter output says that a finding can be wrong and that a clean result does not prove STE.

### D3. The godmode glossary

1. `ste-writing/glossary.md` lists the godmode technical nouns and technical verbs. Each term has one meaning. Examples: skill, router, seam, ledger, frontier, grilling, spec, plan, task, brief, controller, implementer, reviewer, red, green, bounded, architectural, spike.
2. It gives one word for each action that the baseline found in two or more forms. It also lists the words not to use. The linter reads this list (D2, item 7). The glossary puts this table between off markers, because the table must name the words not to use.

   <!-- ste:off -->
   | Use | Do not use |
   |---|---|
   | verify (the agent tests a fact) | confirm, validate, check (verb) |
   | approve (the user agrees) | confirm |
   | remove | delete, erase |
   | start | begin, launch, initiate |
   | change | modify, alter |
   | fix | repair, correct (verb) |
   | use | utilize, employ |
   | get | retrieve, obtain |
   | show | display |
   <!-- ste:on -->

   The list is final only after the baseline lint of each file. The plan can add a pair when the baseline shows more synonym rotation.

   "confirm" has two meanings in the current text. When the agent tests a fact, the rewrite uses "verify". When the user agrees to a design, a seam or a step, the rewrite uses "approve" or "agree". The rewrite never uses "verify" for an approval, because that changes who acts and can make a gate weaker. The linter cannot find "correct" as a verb, because godmode also uses "correct" as an adjective. A reviewer finds these cases.
3. The "leading words" of `writing-for-agents` (for example, *tight*, *red*) go into the glossary as technical nouns or technical verbs. STE permits project words in this way.
4. An -ing word goes into the glossary only when it is a technical noun that godmode uses often. Otherwise, the rewrite uses a verb.

### D4. Hard rules and advisory rules

"Hard" means that the text must obey the rule. "Advisory" means that the writer obeys the rule but can make an exception with a reason.

| Rule | Skill files | Agent output |
|---|---|---|
| No semicolon | Hard. The linter must find 0. | Hard |
| Sentence length | Hard at 25 words. The linter must find 0. A reviewer verifies 20 words for procedural text. | Hard |
| One instruction in each sentence | Hard. A reviewer verifies it. | Hard for procedural text |
| Active voice | Advisory in the linter. A reviewer accepts each remaining passive only for an unknown actor. | Hard |
| Simple tenses | Advisory in the linter. A reviewer accepts each remaining present perfect only with a reason. | Hard |
| No -ing verb forms | Hard. A reviewer verifies it. | Hard |
| Conditions first | Hard. A reviewer verifies it. | Hard |
| No phrasal verbs, no nominalization, no marketing adjectives | Hard. The linter must find 0. | Hard |
| Synonym rotation and the glossary list | Hard. The linter must find 0. | Hard |
| `check-verb` | Hard. The linter must find 0. | Hard |
| No dangling conjunction in list items | Hard. The linter must find 0. | Hard |
| Noun cluster of 3 words or fewer, paragraph of 6 sentences or fewer | Advisory. A reviewer verifies it. | Advisory |
| Words from the approved dictionary | Advisory. No dictionary is available. | Advisory |

The rules for agent output are hard in the skill text. The tests do not lint each output. Two controls apply. First, the skills that write files run the linter on each file (D6, item 3). Second, the behavior seam measures the output (Testing Decisions, seam 4). Chat replies, briefs and ledger lines are not linted one by one. This is a known gap.

### D5. Rewrite of the skill files

1. The scope is all 33 `SKILL.md` files and every `.md` file under `skills/` that an agent reads: prompts, references, templates and examples. The new `ste-writing` files also obey the rules. Its bad examples are between off markers. The `short_description` value in each `agents/openai.yaml` file is also in scope. The conformance test (seam 2) gets each value from its file and lints only that value, as descriptive text, with the same rules as a frontmatter description (D2, item 1). The test does not lint the other YAML keys. Text in scripts (for example, `--help` output) is out of scope.
2. Each sentence keeps its meaning. The rewrite does not remove or add a rule, a gate, a number, a condition, a red-flag row or an example. Each hedge keeps its strength.
3. Each description keeps its trigger words. Before the rewrite, the plan records the trigger phrases of each description in a file. A test verifies that each rewritten description still contains them. A trigger phrase that breaks a hard rule (for example, "check for security issues") stays as a user phrase in quotes, which the linter exempts (D2, item 1).
4. Code blocks, inline code, file paths, commands, skill names, links and quoted text stay unchanged.
5. The document design rules of `writing-for-agents` stay in force: pointers, information hierarchy and pruning. STE controls the form of each sentence. `writing-for-agents` controls the structure of the document. "Do not X" stays permitted when no positive form works. STE also uses this form in warnings.
6. The rewrite occurs in batches of about 5 skills. Each batch gets a lint pass, the meaning-diff check and a meaning review (Testing Decisions, seams 2 and 3) before the next batch starts.

### D6. STE as the default for agent output

1. The router (`using-godmode`) gets one short rule: all text that the agent writes when it uses godmode follows `godmode:ste-writing`. Procedural text follows the procedural rules. All other text follows the descriptive rules. Quoted user text, code, logs and error output stay unchanged.
2. These skills tell the agent to use `ste-writing` at the step where they write text:
   - `brainstorming` (design)
   - `to-spec` (spec)
   - `writing-plans` (plan)
   - `subagent-driven-development` and `executing-plans` (briefs, ledger, reports)
   - `requesting-code-review` and its reviewer prompt (review reports)
   - `mr-full-review` (report)
   - `research` (research note)
   - `wizard` (script text)
   - `handoff` (handoff document)
   - `domain-modeling` (`CONTEXT.md`, ADRs)
   - `finishing-a-development-branch` (commit and PR text)
3. Some skills write a Markdown file: `to-spec`, `writing-plans`, `research`, `mr-full-review` and `domain-modeling`. Each of these skills adds a step. In that step, the agent runs the `ste-writing` linter on the file and fixes each hard finding.
4. `writing-skills` and `writing-for-agents` require a pass of the linter before a skill change is complete.
5. The bootstrap block from the installer does not change. The router has the rule, and the router loads in every session.

### D7. Upstream sources

1. The `asd-ste100-skill` folder stays unchanged. Godmode keeps its own copy.
2. Future changes from Superpowers or Matt Pocock come in through `writing-skills`, which now requires the linter. The user accepted this drift.

### D8. Decisions that the user can change at spec review

1. "check" as a verb is not permitted (D2, item 5), because STE approves it only as a noun.
2. The advisory baseline is per file (Testing Decisions, seam 2).
3. Fresh reviewer subagents do the meaning review (Testing Decisions, seam 3).
4. "confirm" splits into "verify" (the agent tests a fact) and "approve" (the user agrees) (D3, item 2).
5. The `short_description` values in `agents/openai.yaml` are in scope (D5, item 1).

## Testing Decisions

A good test verifies external behavior: what the linter reports, and what the agent does in a real session. It does not test how the code applies a rule.

1. **Linter seam (unit).** The tests use the `lint()` function and the command line of the godmode linter. They cover each godmode change in D2. The upstream `--selftest` must still pass. Prior art: `tests/test_review_request.py` (pytest).
2. **Conformance seam (repository).** A pytest test lints every `.md` file under `skills/` with the glossary.
   1. At the end of the plan, each file must have 0 hard findings.
   2. A baseline file in `tests/` records the advisory count (passive voice, present perfect) for each file and each rule. The plan records this file before the first batch, from the original files. The test fails when a count in a file is higher than its baseline. A file without a baseline entry has a baseline of 0. Thus a new file must have no advisory findings, or the change must add its entry with a reason. After a reviewer accepts the remaining advisory findings of a file, the plan lowers the baseline of that file.
   3. During the rewrite, files that are not yet in a finished batch are exempt from item 1. A list in the test names the finished files. At the end, the list contains all files.
   4. A second test verifies that each description still contains its recorded trigger words (D5, item 3).
3. **Meaning seam (diff check and review).**
   1. A script compares each rewritten file with its original. It reports each change in these items:
      - the frontmatter `name`, and the presence of the `description` key
      - code blocks and inline code
      - links and `godmode:` references
      - numbers
      - the number of table rows (the header row counts, the separator row does not)
      - the number of list items in each section
      - the lines that contain "REQUIRED", "STOP", "MUST" or "Never"

      The batch cannot finish while the script reports an unexplained change.
   2. A fresh reviewer subagent compares each file with its original. It uses this checklist:
      - Each step is present.
      - Each gate and approval rule is present.
      - Each condition (if, when, unless) is present.
      - Each hedge has the same strength.
      - Each red-flag row keeps its idea.
      - The description keeps its trigger meaning.
      - No rule is new.

      A finding stops the batch until the fix is done.
4. **Behavior seam (real sessions).**
   1. The trigger eval now exists only outside the repository, as a temporary script with 17 cases. The plan moves it into the repository under `tests/agent-eval/`, with its case list. It runs real agent sessions with the godmode installer. It gets two new cases for `ste-writing`: an explicit rewrite request must fire it, and an ordinary task must not. Thus it has 19 cases.
   2. After the rewrite, the eval must hit 19 of 19 cases.
   3. The design-gate check (a small, fully specified change, 6 times) must stop for approval 6 of 6 times.
   4. The eval lints the final reply of each session with the same linter rules, including the quote rule. The plan records this output baseline before the rewrite. After the rewrite, the semicolon count must be 0, and the hard findings for each 100 words must be lower than the baseline.
   5. The eval is a manual run, not part of the automatic tests, because each case starts a real agent session.
   6. Four pressure scenarios run again after the rewrite: the design gate (S1), no new seam (S2), the blocked task (S4) and the user-only command (S7). Each must choose the same answer as before.

## Out of Scope

- The ASD approved dictionary. The skill does not contain it, and the linter does not check word approval.
- Certification. Godmode text obeys STE rules but is not certified STE.
- Code, code comments, scripts and their output strings.
- Repository documents for people (`README.md`, `INSTALL.md`, `INSTALL-LOCAL-PROJECT.md`), except the README skill catalog entry and skill count in D1. A later change can rewrite them.
- A disclaimer on each agent output. The White Paper recommends disclaimers for content that AI helped to write. The `ste-writing` skill states the limit once.
- Changes to the upstream `asd-ste100-skill` repository.

## Further Notes

- The rewrite is large: about 41,000 words in `SKILL.md` files and 40 support files. The batches in D5 keep each review small.
- Risk: a rewrite can make a red-flag row or a gate weaker. The meaning seam and the pressure scenarios are the controls.
- Risk: a changed description can stop a skill from firing. The trigger-word test and the trigger eval are the controls.
- Risk: STE text can be longer, because it keeps articles and splits sentences. Longer skills cost context. The plan reports the word count before and after. A growth of more than 15% in a file needs a reason in the batch review.
- Open item: the exact rule text of Issue 9 is in the PDF only. The user can request it from the official downloads page. The spec does not depend on it.
