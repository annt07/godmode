# Before / After Examples

## Part 1 — Official STE Examples

These examples show real ASD-STE100 rules. They come from public secondary sources (see `references/writing-rules.md`). Each example gives the rule in other words. It is not a quote from the standard.

<!-- ste:off -->
| Rule | Before | After | Why |
|---|---|---|---|
| One meaning per word | "Verify the system." / "Check the connections." / "Confirm receipt." | "Make sure the system is correct." (one approved term used consistently) | Three near-synonyms force the reader to guess whether they mean the same action. |
| One part of speech per word | "Oil the valve." | "Apply oil to the valve." | If "oil" is approved only as a noun, using it as a verb breaks the one-word-one-role guarantee. |
| Precise verb meaning | "Follow the safety instructions." | "Obey the safety instructions." | "Follow" can mean "come after" or "obey" — STE picks the unambiguous one. |
| Simple tense only | "We have received the technical reports from HQ." | "We received the technical reports from HQ." | Present perfect adds a second parse ("received, and still relevant now?") that simple past avoids. |
| Verb, not noun | "Perform an inspection of the filter." | "Inspect the filter." | The noun form hides the action and adds a filler verb that carries no meaning. |
| No phrasal verbs | "Take off the access panel." | "Remove the access panel." | "Take off" also means "depart" and "deduct" — the two words together do not predict the meaning. |
<!-- ste:on -->

## Part 2 — Applied to Agent Output

These examples are new. They show the use of this skill: a rewrite of AI agent output. After the rewrite, another agent, a translation layer or a non-native reader can read the text with one meaning only. The examples do not come from a real system.

Word counts below are whitespace-separated tokens (`text.split()`), punctuation not counted separately. A different tokenizer will produce a different number.

### Example A — Tool description

**Before:**
<!-- ste:off -->
> This tool will attempt to synchronize state across the various backends that have been configured, and if a conflict is detected it may resolve it automatically depending on the strategy that has been set, or otherwise it will surface the conflict for manual review.
<!-- ste:on -->

**Violations flagged:**
- Two instructions in one sentence (sync + resolve/surface).
- Present perfect in the relative clauses ("have been configured", "has been set").
- 44 words, far over the 25-word descriptive cap.

Note what is *not* flagged: "will attempt to" and "may resolve". Those are hedges, not violations. The tool is not promised to succeed, and the rewrite must not promise it either.

**After:**
> The tool tries to synchronize state across the configured backends. If it finds a conflict, it reads the configured strategy. If the strategy allows automatic resolution, the tool may resolve the conflict without a user. If the tool does not resolve the conflict, it reports the conflict for manual review.

The last sentence branches on whether the tool resolved the conflict, not on what the strategy allows. That is what "or otherwise" meant in the original: the fallback covers a permitted resolution that still did not happen.

### Example B — Error message

**Before:**
<!-- ste:off -->
> An error may have occurred while processing your request due to a possible mismatch in the expected data format, which could be caused by an outdated client version.
<!-- ste:on -->

**Violations flagged:**
- One sentence carrying three separate claims (an error occurred, a format mismatch, a client version).
- 28 words, over the descriptive cap.

Not flagged: "may have occurred" and "could be caused by". A system that does not know what went wrong writes the message. Both hedges report that lack of knowledge accurately.

**After:**
> Your request may have failed. The cause may be a data format that does not match what the server expects. An outdated client can cause this mismatch. Verify your client version.

**This example is the reason the modality rule exists.** An earlier version of this file rewrote the first sentence as "The request failed". It rewrote the third sentence as "an outdated client **is the most common cause**". Both read better. Both are wrong. The first states a failure that the system only suspects. The second adds a frequency that the input does not give. A rewrite that adds a cause, a frequency or a mechanism is not a rewrite.

Note also that "may have failed" keeps a compound verb form that the simple-tense rule would otherwise remove. **When the tense rule and the modality rule conflict, modality wins** — if you remove the auxiliary here, you also remove the uncertainty.

### Example C — Inter-agent instruction

**Before:**
<!-- ste:off -->
> Once the upstream job has completed and assuming no errors were raised, the downstream agent should proceed to consume the output artifact, though it is worth noting that partial artifacts are sometimes produced under timeout conditions.
<!-- ste:on -->

**Violations flagged:**
- Present perfect ("has completed") and subordinate-clause stacking ("assuming...", "though it is worth noting...").
- One sentence, three separate facts (completion condition, next action, edge-case warning).
- 36 words, over the 20-word instruction cap.

**After:**
> Wait for the upstream job to finish with no errors. Then read the output artifact. Warning: a timeout can produce a partial artifact. Before you use the artifact, verify that it is complete.

Two deliberate calls worth stating rather than hiding:
- "should proceed to consume" became the imperative "read". STE permits this for instructions, where a recommendation addressed to the executing agent is a command. Do not make the same move in descriptive text.
- The final sentence is **new**. The original warned about partial artifacts without saying what to do about it. The added check gives the reader an action. But it is new content, so this note names it, and the example does not show it as part of the rewrite. If the source's silence was deliberate, drop the sentence.

### Example D — README prose (STE-flavored mode)

**Before:**
<!-- ste:off -->
> Our caching layer is designed to slot seamlessly into your existing stack with minimal friction and no vendor lock-in; it leverages semantic similarity to dramatically reduce the cache misses that traditionally plague LLM workloads.
<!-- ste:on -->

**Violations flagged:**
- Marketing adjectives and claims without measurement ("seamlessly", "minimal friction", "dramatically").
- Semicolon joining two separate ideas.
- Nominalization and soft phrasing ("is designed to slot into", "leverages").
- 34 words, over the 25-word descriptive cap.

**After:**
> A normal cache matches requests by exact text, so a small change in wording causes a cache miss. This cache compares the meaning of a new prompt against the prompts it already holds. It runs alongside your current stack and stores no data outside it.

Flavored mode kept the explanatory rhythm and did not force one fixed term per concept. It still cut the marketing adjectives, the semicolon, and the length.

## How to Read These Examples

Part 1 shows the rules that this skill uses. Part 2 shows the same rules on a different text. These rules are one meaning for each word, active voice, simple tense, one instruction in each sentence and conditions first. They make text safer to read for machines and for readers of other languages, not only in aircraft manuals.
