Read `prompts/analyst-common.md` first. It gives your role, inputs,
context-safety rules, and the return format. This file adds the dimension.

Dimension: Quality evidence

Compare the process with its own claims. This is not a code review. Do
not evaluate the code that the session produced.

1. Tests: find each test run with its result line. A test run is a command
   that contains `test`, `pytest`, `npm test`, `cargo test`, `go test`,
   `bats`, `bash tests/…`, or the project runner that the instruction files
   name. Report the runs that failed and what the assistant did next.
2. Verification behind claims: find assistant text that claims done, fixed,
   passing, verified, works, complete. For each claim, look back in the same
   turn for a tool result that shows it (a test run, a command output, a
   diff). Report the claims that have no supporting result in that turn.
3. Commits: find each `git commit` with its message. Compare each message
   with the tool calls in the turn(s) before it. Report the commits with a
   message that claims work that no tool call did. Also report work that
   nobody committed when the agreed plan said that a commit would occur.
4. Review feedback: when a reviewer (human or subagent) raised points,
   find the response. Report the points that the assistant acknowledged but
   did not act on. Report the points that it dismissed without a stated
   reason.
5. Acceptance criteria: the problem statement of the case file or the
   agreed plan can state criteria. If it does, report each criterion as
   met / not met / not examined, with the evidence line.
