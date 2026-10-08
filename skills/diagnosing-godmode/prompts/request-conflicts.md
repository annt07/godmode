Read `prompts/analyst-common.md` first. It gives your role, inputs,
context-safety rules, and the return format. This file adds the dimension.

Dimension: Request conflicts

1. List each human prompt with its line and turn. For each prompt, extract
   the instructions that it contains (imperatives, constraints, "don't",
   "always", "never", "only", scope statements).
2. Report:
   - two human instructions that the assistant cannot both follow. Quote
     both, with lines, and say what the assistant did.
   - a human instruction that conflicts with an instruction file that the
     session loaded (AGENTS.md or any other agent instructions file). The
     case file gives the paths. Quote both.
   - a human instruction to skip, ignore, or override a step, skill, or
     rule. Say what happened after it.
   - an instruction that the assistant asked to make clear, and the answer,
     when the answer changed the scope.
3. Do not judge whether your human partner was right. Report the conflict
   and the resolution of the assistant.
