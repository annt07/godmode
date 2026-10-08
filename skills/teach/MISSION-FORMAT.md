# MISSION.md Format

`MISSION.md` is at the workspace root. It records the _reason_ why the user learns this topic. Each teaching decision (what to teach next, which resources to show, which exercises to design) should come from this document.

## Template

```md
# Mission: {Topic}

## Why
{1-3 sentences. The concrete real-world goal the user is chasing. What changes in their life or work when they have this skill? Avoid abstract framings like "to understand X"; push for the underlying outcome.}

## Success looks like
- {A specific, observable thing the user will be able to do}
- {Another specific thing}
- {…}

## Constraints
- {Time, budget, prior commitments, learning preferences, anything that bounds the approach}

## Out of scope
- {Adjacent topics the user explicitly does not want to chase right now, protecting the zone of proximal development}
```

## Rules

- **One mission per workspace.** If the user wants to learn two unrelated things, use two workspaces.
- **Concrete over abstract.** "Run a half marathon by October" is better than "get fitter." "Ship a Rust CLI to my team" is better than "learn Rust."
- **Do not accept vagueness.** If the user cannot say why, interview them before you write anything. A bad mission is worse than no mission.
- **Revise when reality changes.** Missions change. When the goal of the user moves, update this file. Do not let an old mission guide future sessions.
- **Keep it short.** If `MISSION.md` is longer than a screen, it is no longer a compass. It is a plan.
