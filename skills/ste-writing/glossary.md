# Godmode glossary

STE permits project words as technical nouns and technical verbs. This file lists the godmode terms. Each term has one meaning. Use a term only with the meaning that this file gives. Use these terms as little as possible. A project can add its own terms in its `CONTEXT.md`.

## One word for each action

Use the word in the first column. The linter flags the words in the second column (`--glossary`). A word with "(verb)" needs a reviewer, because the linter cannot tell a verb from a noun or an adjective.

<!-- ste:off -->
| Use | Do not use |
|---|---|
| verify (the agent tests a fact) | confirm, validate, check (verb) |
| approve (the user agrees) | confirm |
| remove | delete, erase |
| start | begin, launch, initiate |
| change | modify, alter |
| fix | repair, correct (verb) |
| use | utilize, employ |
| get | retrieve, obtain |
| show | display |
<!-- ste:on -->

## Technical nouns

| Term | Meaning |
|---|---|
| skill | A folder with a `SKILL.md` file that tells an agent how to do one kind of work. |
| router | The skill `using-godmode`. It tells the agent which skill to use. |
| bootstrap block | The text in an instructions file that makes the agent read the router at the start of a session. |
| spec | A document that states a design: problem, solution, decisions and tests. |
| plan | A document that divides a spec into tasks. |
| task | One unit of a plan, with its own test cycle and its own commit. |
| brief | The text that tells an implementer what one task needs. |
| ledger | The file that records the progress, rulings and findings of a plan. |
| ruling | A decision that the agent makes and records in the ledger, with its reason and its cost if wrong. |
| controller | The agent that runs a plan and sends tasks to other agents. |
| implementer | The agent that does one task. |
| reviewer | The agent that reviews work that a different agent did. |
| subagent | An agent that another agent starts for one job. |
| seam | The public interface where a test observes behavior without access to the inside of a module. |
| module | A unit of code with an interface and an implementation. |
| interface | The part of a module that other code can use. |
| depth | How much behavior a module gives for the size of its interface. |
| adapter | A module that changes one interface into a different interface. |
| frontier | In grilling, the set of questions that the user can answer now. |
| grilling | A set of question rounds that makes requirements clear before design. The skill `grilling` gives the method. |
| brainstorming | The work that changes a request into an approved design. The skill `brainstorming` gives the method. |
| spike | A short test of a design question with code that the team does not keep. |
| bounded | A change to a flow that already exists in the repository. |
| architectural | A change that makes a new project or subsystem, or changes how components fit together. |
| red flag | A thought that shows that the agent is about to skip a rule. |
| tracer bullet | A task that goes through all layers of a change. When the task is complete, you can show it. |
| prefactoring | A change to the structure of code that makes the next feature easy. The team does it before that feature. |
| finding | A problem that a reviewer or a linter reports. |
| pressure test | A test that puts an agent under pressure (time, authority, cost) to show whether a skill holds. |
| sediment | Old text in a document that is no longer true but stays because nobody removes it. |
| no-op | An instruction that does not change what the agent does. |
| lesson | Knowledge that a skill gives to every future run. |
| fog of war | The state where the agent cannot see the parts of the work that are not in its context. |

## Technical verbs and adjectives

| Term | Meaning |
|---|---|
| red (adjective) | A test that fails because the feature is missing. |
| green (adjective) | A test that passes. |
| tight (adjective) | A feedback loop that is fast, deterministic and cheap to run. |
| lint (verb) | Run the linter on a text. |
| ledger (verb) | Write a line in the ledger. |
| dispatch (verb) | Start a subagent with a brief. |
