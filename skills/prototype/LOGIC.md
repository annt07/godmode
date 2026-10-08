# Logic Prototype

A logic prototype is a single, self-contained HTML file (a **shareable demo**). Anyone can operate a state model in it with button clicks. Use it when the question is about **business logic, state transitions, or data shape**. These things can look reasonable on paper but feel wrong when you move them through real cases.

It is one file with nothing to install. Thus you can give it to a non-developer (a designer, a PM, a domain expert), and they can feel the model for themselves. So it uses their language, not the language of the code.

## When this is the right shape

- "I'm not sure if this state machine handles the edge case where X then Y."
- "Does this data model actually let me represent the case where..."
- "I want to feel out what the API should look like before writing it."
- Any case where someone wants to **press buttons and watch state change**.

If the question is "what should this look like," this is the wrong branch. Use [UI.md](UI.md).

## Process

### 1. State the question

Before you write code, write the state model and the question of the prototype. Write one paragraph at the top of the demo, in a visible intro, not only in a comment. A logic prototype that answers the wrong question is pure waste. Thus make the question explicit, so that someone can verify it later. The user can watch now or come back to it AFK.

### 2. Isolate the logic in a portable module

Put the actual logic (the part that answers the question) in a single `<script>` block. Write it as a small, pure module that you could later move into the real codebase. The page around it is throwaway. This module is not.

The right shape depends on the question:

- **A pure reducer**: `(state, action) => state`. Good when actions are discrete events and state is a single value.
- **A state machine**: explicit states and transitions. Good when "which actions are even legal right now" is part of the question.
- **A small set of pure functions** over a plain data type. Good when there is no implicit current state, only transformations.
- **A class or module with a clear method surface** when the logic really owns internal state that continues over time.

Select the shape that best fits the question, *not* the shape that is easiest to connect to a page. Keep it pure: no DOM, no `document`, and no button handlers that go inside it. The page calls the module. Nothing goes in the other direction. This makes the prototype useful after its own lifetime. When the question has an answer, the verified reducer, machine or function set moves into the real module without more work.

### 3. Build the shareable HTML file

Make one file with plain HTML/CSS/JS. Use no framework, no bundler and no server. Put everything inline, so that it opens with a double-click and still works after people send it by email. Anyone should be able to run it when they open it.

Write it for a non-developer. Write each label in **domain language**, not in code. Buttons and state should read like the business, not like the reducer. Tell in plain words what occurs.

Use a clean hierarchy, from top to bottom:

1. **Title and one-line explanation** of what this demo lets you explore (the question from step 1).
2. **Current state**: the full relevant state in a readable panel (fields with labels, not a raw JSON dump). Render it again after each click, so that the change is visible. Where it helps a non-developer, show what just changed.
3. **Free-play buttons**: one button for each action, always available, so that anyone can try the model in any order. Each click dispatches its action and renders the state again.
4. **Guided walkthroughs**: a set of **scenarios**, one in each tab. Each tab has a short plain-language description of the scenario: the situation that it sets up and what to look for. Under the description are the **buttons to press** for that scenario, in order. Each step is a real button. A click does that action and goes to the next step. When a walkthrough starts, it resets to a known initial state, so that the scenario runs the same way each time.

Select scenarios that show the awkward cases that are hard to think through on paper. Include the happy path, a difficult edge case, and an attempt at something that should be illegal.

Make it attractive but restrained: clean typography, a lot of space, one accent color. Use no animations and no gimmicks: nothing that competes with the state and the buttons.

### 4. Hand it over

Send the file to them, or open it for them. They will click through the walkthroughs and use free-play when they have time. The interesting moments are when they say "wait, that shouldn't be possible" or "huh, I assumed X would be different". Those are the bugs in the _idea_, and they are the full purpose. If they want new actions or a new scenario, add them. Prototypes change over time.

### 5. Capture the answer and the prototype

When the prototype answers its question, record the answer. Then keep the prototype as the [SKILL](SKILL.md) describes. For a logic prototype, the verified reducer, machine or function set moves into the real module (the decision, absorbed). The HTML shell goes with it to the throwaway branch, which keeps the prototype as a primary source. It is one self-contained file, so it stays easy to run again there.

## Anti-patterns

- **Don't add tests.** A prototype that needs tests is no longer a prototype.
- **Don't wire it to the real database.** Use in-memory state, unless the question is specifically about persistence.
- **Don't generalise.** No "what if we wanted to support X later." The prototype answers one question.
- **Don't blur the logic and the page together.** If the pure module refers to the DOM, `document`, or button handlers, you can no longer move it. Keep the page as a thin shell over a pure module.
- **Don't reach for a framework, bundler, or server.** Make one file that the recipient double-clicks. A React app or a dev server defeats "shareable".
- **Don't ship the HTML shell into production.** The page is for manual clicks. The logic module behind it is the part to keep.
