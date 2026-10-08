---
name: writing-for-agents
description: Write documents for agents. Use when you create or edit skills, or when you change an agent instructions file such as AGENTS.md.
---

This is the reference for each document that an agent reads. Examples are a skill, an agent instructions file such as `AGENTS.md`, or a doc that a pointer reaches. The packaging is different. The writing is the same. The same levers make each one predictable. The agent takes the same _process_ at each run. It does not make the same output at each run.

When the document that you write is a skill, read [`SKILL-MECHANICS.md`](SKILL-MECHANICS.md) for frontmatter, the invocation choice and router skills.

Write the sentences of each agent document in STE (`godmode:ste-writing`). STE controls the form of each sentence. This skill controls the structure of the document. A change is not complete until the linter finds 0 hard findings in each changed file. Run `python <ste-writing>/scripts/ste-lint.py --glossary <ste-writing>/glossary.md <file>`, where `<ste-writing>` is the folder of the `godmode:ste-writing` skill. Fix each hard finding.

## Context pointers

A **context pointer** is a reference in the context of the agent. It names some out-of-context material and encodes the condition to reach it. The description of a skill is one. A line in `AGENTS.md` that names a doc is the same object. The _wording_ of the pointer, not its target, decides when the agent reaches the material, and how reliably. A must-have target behind a weakly worded pointer is a variance bug. Sharpen the wording first. Inline the material only if the sharpened wording fails.

A pointer does two jobs. It states what the material is. It lists the **branches** that should trigger the agent to reach it. A branch is a distinct case that the document handles, so different runs take different paths through it. Each word of an always-loaded pointer costs on each turn. Thus prune a pointer even more strictly than the body:

- **Front-load the leading word**: the pointer is where the word does its triggering work.
- **One trigger per branch.** Synonyms that rename a single branch are one branch written twice. Collapse them and keep only branches that are really distinct.
- **Cut identity the body already carries.**

## The two loads

Each document and each pointer that you add spends one of two budgets:

- **Context load** is the cost of always-loaded material on the window of the agent. Examples are an `AGENTS.md` line, a skill description, or anything else that is in context at each turn. It spends tokens and attention, whether or not it fires.
- **Cognitive load** is the cost on the human: which documents exist and when to use each one. The human is the index. It is not a cost to minimise. It is the price of human agency. Spend it where human judgement is important. Remove it where human judgement is not important.

Material that only a pointer reaches escapes context load. The price is the line of the pointer. Material with no pointer puts all of its cost on cognitive load.

## Information hierarchy

A document contains two content types. **Steps** are the ordered actions that the agent does. **Reference** is definitions, rules and facts that the agent reads on demand. The two types mix freely: all steps (a recipe), all reference (the rules of a review, or this skill), or both. The core decision is where each piece sits on the **information hierarchy**. This is a ladder ranked by how immediately the agent needs the material:

1. **In-file step** is the primary tier: what the agent does, in order.
2. **In-file reference** is what the agent reads on demand. It is often a legitimately flat peer-set, for example each rule of a review on one rung. This arrangement is correct. It is not a smell.
3. **Disclosed reference** is in a separate file. A context pointer reaches it, and the agent loads it only when the pointer fires. It goes from a sibling file in the same folder to fully external reference that lives anywhere, which any document can point at.

If you push too little down, the top becomes too large. If you push too much down, you hide material that the agent actually needs. That tension is the full decision.

**Progressive disclosure** is the move down the ladder: out of the main file and behind a pointer. Thus the top stays legible. It is not primarily a token optimisation. It is how you protect the hierarchy. Branching is the cleanest disclosure test. Inline what each branch needs. Put behind a pointer what only some branches reach. When a document has steps, in-file reference that should be disclosed buries them. Then the agent attends to them only by chance. Thus it is a variance lever, not only a legibility lever.

**Co-location** is the within-file companion. The ladder decides _how far down_ a piece sits. Co-location decides _what sits beside it_ there. Keep the definition, rules and caveats of a concept under one heading. Do not scatter them. Then, when the agent reads one part, it gets the neighbouring parts too. The test: the document should read like documentation written for the agent. Grouped material reads that way. Scattered material does not. Scattering is different from duplication. Duplication repeats one meaning in two places. Scattering divides one meaning across many places.

**Sprawl** is the failure mode here: a document that is too long, even when each line is live and unique. Attention becomes thin across the excess, and each extra line is one more line to keep relevant. The cure is the ladder. Disclose reference behind pointers. Split by branch or by sequence, so that each path carries only what it needs.

## Steps and completion criteria

Each step ends on a **completion criterion**: the condition that tells the agent that the work is done. Two properties make it a lever:

- **Clarity**: can the agent tell done from not-done? A vague bound ("understanding reached") invites **premature completion**. The agent ends the step before it is really done, because its attention moves to _being done_. The visible steps that are still ahead (the **post-completion steps**) supply the pull. The clarity of the criterion is the resistance. Defend in this order. **Sharpen the bound first**, because that is local and cheap. Hide the later steps by a split of the sequence only if the bound is irreducibly fuzzy _and_ you see the rush. Hiding only works across a real context boundary: a hand-off or a subagent dispatch. An inline call leaves the later steps in context and clears nothing.
- **Demand**: how much the criterion requires. "Every modified model accounted for" forces thorough work. "produce a change list" does not. Demand drives **legwork**: the digging that the agent does in the work. Legwork is latent in the wording. It is not written as its own step. Demand is not bound to steps. "every rule applied" binds a body of flat reference, as "every step done" binds a sequence. Thus an all-reference document still carries an exhaustiveness bar.

The strongest criteria are both checkable and exhaustive.

## When to split

A split of one document into two spends one of the two loads. Thus split only when the cut is worth the cost:

- **By sequence**: split a run of steps where the post-completion steps tempt the agent to rush the current step. When you keep them out of view, the agent does more legwork on the current task. Be careful of the reverse. When you merge sequences, each step can see its later steps, and this invites premature completion.
- **By invocation**, skill-specific: see [`SKILL-MECHANICS.md`](SKILL-MECHANICS.md).

## Leading words

A **leading word** is a compact concept that is already in the pretraining of the model. The agent thinks with it while it runs the document (_lesson_, _fog of war_, _tracer bullets_). The godmode glossary (`skills/ste-writing/glossary.md`) records these words as technical nouns. Repeat it as a token, never as a sentence. Then it gets a distributed definition. It anchors a full region of behaviour in the fewest tokens, because it uses priors that the model already holds. You can coin your own word if you define it clearly. But a made-up word uses no priors. You pay in definition tokens what a pretrained word gives free. Thus try an existing word first.

It anchors twice. In the body, it anchors _execution_. The agent uses the same behaviour each time that the word appears. Inside flat reference, it focuses attention on a class of thing to look for. In a pointer, it anchors _invocation_. When the same word is in your prompts, your docs and your codebase, the agent links that shared language to the material. Then it reaches the material more reliably.

Look for opportunities to refactor with leading words. Examples are a triad written in full at three sites, or a pointer that spends a sentence on one idea. Each one is a passage that you can collapse into a single token:

- "fast, deterministic, low-overhead" → _tight_ (a _tight_ loop).
- "a loop you believe in" → _red_. This changes a fuzzy gate into a binary observable state: the loop goes _red_ on the bug, or it does not.

You win twice: fewer tokens, and a sharper hook for the thinking of the agent. Assume that each document carries restatements that leading words can retire. Find them.

**Negation** is the failure mode beside this lever. A prohibition pulls the forbidden behaviour into context and makes it _more_ available, not less. _Don't think of an elephant_, and the elephant is all there is. The negation is a weak modifier, and the strongly activated concept overruns it. Thus the ban half-reads as an instruction to do the thing. Prompt the **positive**. State the target behaviour ("write one-line comments"), so that you never say the banned behaviour. A prohibition is correct only as a hard guardrail that you cannot phrase positively. Even then, pair it with the positive target, so that attention goes to what to do.

## Pruning

- Keep each meaning in a **single source of truth**: one authoritative place. Then a change to the behaviour is an edit in one place. **Duplication** is the same meaning in more than one place. It costs maintenance and tokens. It also makes a meaning more prominent on the ladder than its real rank. Duplication is the accidental inverse of a leading word, which repeats a token on purpose, never the meaning.
- The **environment** is a source of truth too: `package.json` scripts, config files, the directory layout and `--help` output. A document that restates it is a **cache**: a copy of a lookup. A cache is worth its load only when the lookup is expensive. Cache what the agent cannot find when it looks: the unwritten convention, the reason for a choice, the gotcha that no config tells. Leave the one-file and one-command lookups to the environment, where they cannot become stale.
- Verify each line for **relevance**: does it still apply to what the document does? A line can lose relevance in two ways. It never applies to the task (only exposition, or a branch that should be disclosed). Or it becomes stale when the behaviour or the world that it describes changes. Shorter documents are easier to keep relevant. Without a pruning discipline, the default result is **sediment**. Stale layers settle, because to add feels safe and to remove feels risky. At last, you must dig through them to find what is still live.
- Look for **no-ops** in each sentence. A no-op is an instruction that the model already obeys by default, so it pays load to say nothing. The test is: does it change behaviour compared with the default? The test is model-relative, not reader-relative. Two people who disagree about a no-op disagree about the default. They settle it when they run the document, not by debate. When a sentence fails, remove the full sentence. Do not trim words from it. The test also grades leading words. A word that is too weak to beat the default (_be thorough_ when the agent is already thorough-ish) is a no-op. The fix is a stronger word (_relentless_), not a different technique.
