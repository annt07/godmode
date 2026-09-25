---
name: research
description: Use when a factual question needs primary-source investigation before implementation decisions are made. Use when official docs, source code, or API facts need to be gathered, or when reading legwork should be delegated to a background agent.
---

# Research

Spin up a **background agent** to do the research, so you keep working while it reads.

## Process

### 1. Frame the Question

State the question precisely before dispatching. A vague question produces a vague answer. Good framing: "Does [library] version [X] support [feature], and what is the documented behavior when [edge case]?" Bad framing: "How does [library] work?"

### 2. Dispatch the Research Agent

The agent's job:

1. Investigate the question against **primary sources** (official docs, source code, specs, first-party APIs), not a secondary write-up of them. Follow every claim back to the source that owns it.
2. For each finding, record: the claim, the primary source URL or file path, and the exact version or commit the source applies to.
3. If the primary source is ambiguous or contradicts another primary source, report both and flag the contradiction.

### 3. Output Format

The agent writes findings to a single Markdown file. Save it where the repo already keeps research notes; match the existing convention. If there is none, put it in `docs/research/<topic>-<YYYY-MM-DD>.md` and report the path.

The file must follow this structure:

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

The research is done when the original question has a direct answer in the Conclusion section, every claim in Findings cites a primary source, and the file is committed or saved. Report the file path to the controller.

## What Counts as a Primary Source

- Official documentation for the technology (MDN, Python docs, official framework docs)
- The library or tool's source code itself
- First-party API specifications (OpenAPI specs, GraphQL schemas)
- RFCs and standards documents
- Official release notes and changelogs

What does NOT count: blog posts, Stack Overflow answers, AI-generated summaries, tutorials. These may be used as navigation aids to find the primary source, but every claim must trace back to a primary.

## When to Use

- "Is this API available in version X?" before writing code that depends on it
- "What does this library actually do when Y happens?" before assuming behavior
- "What are the performance characteristics of Z?" before making architectural choices
- Any factual question where implementation risk is non-trivial if the answer is wrong

## Red Flags

| Thought | Reality |
|---------|---------|
| "I am fairly confident this is how it works" | Confidence is not a source. Spin up the research agent. |
| "The docs are probably up to date" | Verify against the version in use. |
| "A blog post explained this clearly" | Follow the blog post's claim back to the primary source. |
