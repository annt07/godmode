Read `prompts/analyst-common.md` first. It gives your role, inputs,
context-safety rules, and the return format. This file adds the dimension.

Dimension: Skill timeline

Build the record of skill and plugin use for each human turn. Then look for
gaps.

1. List the human prompts with line numbers and timestamps.
2. Use the skill-invocation and attribution meanings that the case file
   established. List each explicit invocation, each active-skill
   attribution, and each read of a file named `SKILL.md`. Record the line,
   the skill name, and the human turn where it occurred.
3. List each non-godmode plugin, skill, agent type, MCP server, or hook
   that the session used. Use only the evidenced tool, attribution,
   agent-dispatch, MCP, and hook meanings that the case file records.
   Identify the values that belong to something other than `godmode`.
4. For each human turn, compare the request text with the trigger
   descriptions of the installed godmode skills. Read the `description`
   lines in the frontmatter of `<install root>/skills/*/SKILL.md`. The case
   file gives the install root. Report as findings:
   - a skill invoked, with the request before it. If there are few
     invocations, one finding for each invocation is acceptable. If there
     are many, make groups by skill.
   - a turn with a request that matches the trigger description of a
     skill, with no invocation in that turn. State which description
     matched and quote the request.
   - a skill invoked one or more turns after the matching request (late).
   - each non-godmode plugin/skill/tool used, with where.

Do not say whether a missed or late trigger was wrong. Report the match
and the absence. The reader decides.
