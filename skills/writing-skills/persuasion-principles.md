# Persuasion Principles for Skill Design

## Overview

LLMs respond to the same persuasion principles as humans. When you understand this psychology, you can design more effective skills. The goal is not to manipulate. The goal is to make sure that agents follow critical practices, also under pressure.

**Research foundation:** Meincke et al. (2025) tested 7 persuasion principles with N=28,000 AI conversations. Persuasion techniques more than doubled compliance rates (33% → 72%, p < .001).

## The Seven Principles

### 1. Authority
**What it is:** Deference to expertise, credentials or official sources.

**How it works in skills:**
- Imperative language: "YOU MUST", "Never", "Always"
- Non-negotiable framing: "No exceptions"
- It removes decision fatigue and rationalization

**When to use:**
- Discipline-enforcing skills (TDD, verification requirements)
- Safety-critical practices
- Established best practices

**Example:**
```markdown
✅ Write code before test? Delete it. Start over. No exceptions.
❌ Consider writing tests first when feasible.
```

### 2. Commitment
**What it is:** Consistency with prior actions, statements or public declarations.

**How it works in skills:**
- Require announcements: "Announce skill usage"
- Force explicit choices: "Choose A, B, or C"
- Use tracking: todos for checklists

**When to use:**
- To make sure that agents actually follow skills
- Multi-step processes
- Accountability mechanisms

**Example:**
```markdown
✅ When you find a skill, you MUST announce: "I'm using [Skill Name]"
❌ Consider letting your partner know which skill you're using.
```

### 3. Scarcity
**What it is:** Urgency that comes from time limits or limited availability.

**How it works in skills:**
- Time-bound requirements: "Before proceeding"
- Sequential dependencies: "Immediately after X"
- It prevents procrastination

**When to use:**
- Immediate verification requirements
- Time-sensitive workflows
- To prevent "I'll do it later"

**Example:**
```markdown
✅ After completing a task, IMMEDIATELY request code review before proceeding.
❌ You can review code when convenient.
```

### 4. Social Proof
**What it is:** Conformity to what others do or to what people think is normal.

**How it works in skills:**
- Universal patterns: "Every time", "Always"
- Failure modes: "X without Y = failure"
- It sets norms

**When to use:**
- To document universal practices
- To warn about common failures
- To reinforce standards

**Example:**
```markdown
✅ Checklists without todo tracking = steps get skipped. Every time.
❌ Some people find a todo list helpful for checklists.
```

### 5. Unity
**What it is:** Shared identity, "we-ness", in-group belonging.

**How it works in skills:**
- Collaborative language: "our codebase", "we're colleagues"
- Shared goals: "we both want quality"

**When to use:**
- Collaborative workflows
- To set a team culture
- Non-hierarchical practices

**Example:**
```markdown
✅ We're colleagues working together. I need your honest technical judgment.
❌ You should probably tell me if I'm wrong.
```

### 6. Reciprocity
**What it is:** The obligation to return benefits that you received.

**How it works:**
- Use it sparingly. It can feel manipulative.
- Skills rarely need it.

**When to avoid:**
- Almost always (other principles are more effective)

### 7. Liking
**What it is:** The preference to cooperate with people that we like.

**How it works:**
- **DON'T USE for compliance**
- It conflicts with an honest feedback culture.
- It causes sycophancy.

**When to avoid:**
- Always for discipline enforcement

## Principle Combinations by Skill Type

| Skill Type | Use | Avoid |
|------------|-----|-------|
| Discipline-enforcing | Authority + Commitment + Social Proof | Liking, Reciprocity |
| Guidance/technique | Moderate Authority + Unity | Heavy authority |
| Collaborative | Unity + Commitment | Authority, Liking |
| Reference | Clarity only | All persuasion |

## Why This Works: The Psychology

**Bright-line rules reduce rationalization:**
- "YOU MUST" removes decision fatigue.
- Absolute language removes "is this an exception?" questions.
- Explicit anti-rationalization counters close specific loopholes.

**Implementation intentions cause automatic behavior:**
- Clear triggers + required actions = automatic execution
- "When X, do Y" is more effective than "generally do Y".
- They reduce the cognitive load of compliance.

**LLMs are parahuman:**
- Their training used human text that contains these patterns.
- In training data, authority language comes before compliance.
- Training data frequently models commitment sequences (statement → action).
- Social proof patterns (everyone does X) set norms.

## Ethical Use

**Legitimate:**
- To make sure that agents follow critical practices
- To make effective documentation
- To prevent predictable failures

**Illegitimate:**
- Manipulation for personal gain
- False urgency
- Guilt-based compliance

**The test:** If the user fully understood this technique, would it serve the genuine interests of the user?

## Research Citations

**Cialdini, R. B. (2021).** *Influence: The Psychology of Persuasion (New and Expanded).* Harper Business.
- Seven principles of persuasion
- Empirical foundation for influence research

**Meincke, L., Shapiro, D., Duckworth, A. L., Mollick, E., Mollick, L., & Cialdini, R. (2025).** Call Me A Jerk: Persuading AI to Comply with Objectionable Requests. University of Pennsylvania.
- Tested 7 principles with N=28,000 LLM conversations
- Compliance increased 33% → 72% with persuasion techniques
- Authority, commitment and scarcity were the most effective
- Supports the parahuman model of LLM behavior

## Quick Reference

When you design a skill, ask these questions:

1. **What type is it?** (Discipline vs. guidance vs. reference)
2. **What behavior do I try to change?**
3. **Which principle(s) apply?** (Usually authority + commitment for discipline)
4. **Do I combine too many?** (Do not use all seven)
5. **Is this ethical?** (Does it serve the genuine interests of the user?)
