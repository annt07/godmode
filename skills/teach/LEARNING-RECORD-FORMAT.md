# Learning Record Format

Learning records are in `./learning-records/` and use sequential numbers: `0001-slug.md`, `0002-slug.md`, and so on. Create the directory only when you write the first record.

They are the teaching equivalent of ADRs. They record lessons that are not obvious, key insights, and stated prior knowledge that will guide future sessions. You use them to calculate the zone of proximal development.

## Template

```md
# {Short title of what was learned or established}

{1-3 sentences: what was learned (or what prior knowledge was established), and why it matters for future sessions.}
```

That is the full format. A learning record can be a single paragraph. The value is to record _that_ the user now knows this and _why_ it changes what to teach next. The value is not in sections that you fill.

## Optional sections

Include these only when they add real value. Most records will not need them.

- **Status** frontmatter (`active | superseded by LR-NNNN`): useful when an earlier understanding becomes wrong and a new one replaces it.
- **Evidence**: how the user showed the understanding (a question answered, an exercise completed, prior experience cited). Useful when someone might examine the claim again.
- **Implications**: what this makes possible or excludes for future sessions. Record it when it is not obvious.

## Numbering

Find the highest number in `./learning-records/` and add one.

## When to write a learning record

Write one when one of these is true:

1. **The user showed real understanding of something that is not trivial**: not only exposure, but evidence that they can use the concept correctly. This sets a new minimum for what to teach next.
2. **The user told you their prior knowledge**: "I already know X." Record it, so that future sessions do not teach it again. Also record the _depth_ that the user claimed.
3. **You corrected a misconception**: the user believed something wrong before and now sees why. These records have high value. They predict future problems in related topics.
4. **The mission changed because of learning**: the user found that they cared about something different than they thought. Link to [[MISSION.md]] and update it.

### What does _not_ qualify

- Material that you only covered. Coverage is not learning. Wait for evidence.
- Anything that [[GLOSSARY.md]] already records briefly as a term definition. Do not copy it.
- Activity logs for each session. Learning records are not a journal. They are insights that are good enough for decisions.

## Supersession

A later record can contradict an earlier one (the understanding of the user became deeper or correct). Then mark the old record `Status: superseded by LR-NNNN`. Do not remove it. The history of how understanding changed is itself a useful signal.
