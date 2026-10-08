# Skill mechanics

This file is the skill-specific branch of [`writing-for-agents`](SKILL.md). It tells what changes when the document is a skill: the frontmatter, the invocation choice and router skills. For all other parts of the writing, use the universal reference in `SKILL.md`.

## Invocation

There are two choices. Each choice trades one load for the other load:

- A **model-invoked** skill keeps a `description`. Thus the agent can fire it autonomously, and other skills can reach it. You can still type its name. Model-invocation always _includes_ user reach. A description only adds agent discovery. It never removes the reach of the human. The description is the top-level context pointer of the skill, and it must stay loaded at all times. You pay a permanent context load to get discoverability. A model-invoked skill that contains only reference is also one home for shared reference. Another skill can invoke it, so reference that several skills need lives in one place. Mechanics: omit `disable-model-invocation`. Write a model-facing description that carries the trigger branches. The pointer-writing rules in `SKILL.md` apply in full.
- A **user-invoked** skill removes the description from the reach of the agent. Only the human who types its name can invoke it, and no other skill can. It has zero context load, but it spends cognitive load: you are the index that must remember that it exists. Mechanics: set `disable-model-invocation: true`. The `description` becomes human-facing: a one-line summary without trigger lists.

Pick model-invocation only when the agent must reach the skill on its own, or when another skill must reach it. If it only fires by hand, make it user-invoked and pay no context load.

If two user-invoked skills both need shared reference, the reference can live in neither of them. They have no descriptions, so neither skill can fire the other. Move the reference to a plain file outside the skill system: an external reference that any skill can point at.

## Splitting by invocation

This is the invocation cut of splitting. The sequence cut is in `SKILL.md`. Split off a model-invoked skill in one of these conditions:

- You have a distinct leading word that should trigger it on its own: a trigger word that you actually use in your prompts.
- Another skill must reach it.

You pay context load for the new always-loaded description, so that independent reach must be worth the cost.

## Router skills

User-invoked skills can increase past the number that you can remember. A **router skill** cures that accumulated cognitive load. It is one user-invoked skill that names the other skills and tells when to use each one. Thus the human has one skill to remember instead of many. It can only hint. It can never fire them, because user-invoked skills have no description, so only the human can reach them.
