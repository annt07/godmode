---
name: to-questionnaire
description: Change a decision that you cannot fully answer into a questionnaire for a different person to fill in.
disable-model-invocation: true
---

Change something that the user cannot answer alone into a **questionnaire**. A questionnaire is a Markdown document. The user gives it to one person to fill in async, or they fill it in together in a meeting. The recipient has knowledge that the user does not have. The questionnaire gets that knowledge from the recipient.

**Grill the send, not the subject.** Interview the user only about the _send_, because the user can always answer it: who gets it, and what the user needs back. The questions in the document then aim at the **gap** between what the recipient knows and what the user needs.


1. **Who is it going to?** In one exchange, ask for the role and expertise of the recipient, and the relationship of the recipient to the user. This sets the tone of the questionnaire and how much context it must contain. Done when you know who the recipient is and what they know that the user does not.

2. **What do you need back?** In one exchange, ask for the specific decisions or facts that the user cannot resolve alone and needs from this person. Done when you have a concrete list of what the user must be able to do or decide at the end.

3. **Write the questionnaire.** Write questions that aim at the gap from steps 1–2. Follow the Document structure below. Write it to `to-questionnaire-<slug>.md` in the current directory (slug from the topic). Report the path. Done when the file exists and a question covers each item that the user named in step 2.

## Document structure

Write the document as a **discovery questionnaire**: the user does not have the context, and the recipient has it. Put the most important questions first, because async means you may get only one pass. When there are more than a few questions, group them under `##` headings by theme. Use the template below.

<questionnaire-template>

# <Questionnaire title>

**Purpose:** why this questionnaire exists and the decision that depends on it.

**From:** <the user>, **To:** <the recipient>, **How your answers will be used:** <where they go>

## Context

One paragraph that gives context to a recipient who does not know what the user thinks. Enough to answer well, not a page.

## How to answer

Deadline and approximate effort. Partial answers and "I don't know" are useful: flag anything that you are not sure of. Do not skip it.

## <Theme heading>

One `##` section for each theme. Under each section, put its questions, the most important first. Each question is one idea, never compound, with an answer stub directly below it. Add a one-line _why this matters_ only where a reader could misread the question or give a careless answer.

<question-example>
### What load must the system handle at the start of production?

_Why this matters: it decides whether we provision for burst traffic now or defer it._

>
</question-example>

## Anything else?

A final catch-all: anything that we did not ask but should know?

</questionnaire-template>
