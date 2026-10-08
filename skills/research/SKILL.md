---
name: research
description: Use when a factual question needs primary-source investigation before you make implementation decisions. Use when you must collect facts from official docs, source code or an API, or when a background agent should do the reading work.
---

# Research

Start a **background agent** to do the research, so that you can continue your work while it reads.

## Process

### 1. Frame the Question

Before you dispatch the agent, state the question precisely. A vague question gives a vague answer. Good framing: "Does [library] version [X] support [feature], and what is the documented behavior when [edge case]?" Bad framing: "How does [library] work?"

### 2. Dispatch the Research Agent

The work of the agent:

1. Examine the question against **primary sources** (official docs, source code, specs, first-party APIs), not against a secondary text about them. Follow each claim back to the source that owns it.
2. For each finding, record the claim, the primary source URL or file path, and the exact version or commit of the source.
3. If the primary source is ambiguous or contradicts a different primary source, report both and flag the contradiction.

### 3. Output Format

The agent writes the findings to a single Markdown file. Save it where the repo already keeps research notes, and use the existing convention. If there is no such location, put it in `docs/research/<topic>-<YYYY-MM-DD>.md` and report the path.

The file must have this structure:

```markdown
# Research: [Question]

**Date:** YYYY-MM-DD
**Version investigated:** [library/tool version]

## Findings

### [Finding 1 title]

[Claim]. Source: [URL or file path, section, version].

### [Finding 2 title]

[Claim]. Source: [URL or file path, section, version].

## Contradictions or Gaps

[Any source conflict or unanswered aspect of the question.]

## Conclusion

[Direct answer to the original question, in one or two sentences.]
```

### 4. Completion Criterion

The research is complete when all of these conditions are true:

- The Conclusion section gives a direct answer to the original question.
- Each claim in Findings cites a primary source.
- The agent committed or saved the file.

Report the file path to the controller.

## What Counts as a Primary Source

- Official documentation for the technology (MDN, Python docs, official framework docs)
- The source code of the library or tool itself
- First-party API specifications (OpenAPI specs, GraphQL schemas)
- RFCs and standards documents
- Official release notes and changelogs

These do NOT count: blog posts, Stack Overflow answers, AI-generated summaries, tutorials. You may use them as navigation aids to find the primary source. But each claim must go back to a primary source.

## When to Use

- "Is this API available in version X?" before you write code that depends on it
- "What does this library actually do when Y happens?" before you assume a behavior
- "What are the performance characteristics of Z?" before you make architectural choices
- Any factual question where a wrong answer gives a non-trivial implementation risk

## Red Flags

| Thought | Reality |
|---------|---------|
| "I am fairly confident this is how it works" | Confidence is not a source. Start the research agent. |
| "The docs are probably up to date" | Verify them against the version that you use. |
| "A blog post explained this clearly" | Follow the claim of the blog post back to the primary source. |
