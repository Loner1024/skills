---
name: how
description: |
  Load when the user asks how a subsystem works, wants a code walkthrough before changing it, or
  asks where something lives: "how does X work", "walk me through this", "which package owns
  this", "what layer is this in". It explains architecture and runtime flow at the level of a
  senior engineer onboarding onto the subsystem, enough for a working mental model.
  Also load when the user says 这块代码怎么跑 / 这个子系统怎么工作 / 先讲讲这段代码 / 代码走读 /
  这个逻辑放哪 / 归属哪一层 / 该放哪个包.
  Not for whether the shape is right (codebase-design) or why it was built this way (why).
---

# How

Explore the codebase to answer "how does X work?" questions. Produce architectural explanations at the level of a senior engineer onboarding onto a subsystem, enough to build a working mental model, not so much that it reads like annotated source code.

Every spawn is a read-only subagent. Use the faster model for exploration and the strongest available model for the explanation, and say which ran. If the environment has no subagents, do the exploration inline in the same order and say the explanation was single-agent.

## 1. Assess complexity

If the scope is ambiguous, state your interpretation and explore. The user can redirect.

- **Simple** (a single module, a small utility, a narrow question such as "how does function X work"): no explorers. Spawn one explainer that explores and explains in one pass, built from `references/explainer-prompt.md` without the explorer-findings section. Go to step 4.
- **Complex** (a subsystem spanning multiple files or services, a cross-cutting feature, a full architectural overview): go to step 2.

When in doubt, take the simple path.

## 2. Explore (complex only)

Decompose the question into 2 to 4 angles, each a distinct slice of the subsystem. Spawn all explorers in a single message, each with `references/explorer-prompt.md` and its angle filled in.

## 3. Synthesize (complex only)

Once all explorers have returned, spawn one explainer with `references/explainer-prompt.md` and every explorer's findings filled in.

## 4. Present

Present the explainer's output. Light edits for clarity or context from the conversation are fine. Do not substantially rewrite it.

## Output format

The explanation uses the sections defined in `references/explainer-prompt.md`, dropping any that do not apply: Overview, Key Concepts, How It Works, Where Things Live, Gotchas.
