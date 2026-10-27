---
name: retro
description: "Conduct a retrospective on a coding session and turn it into ranked proposals for the agent's environment: navigation pointers, automated checks, reviewer rules, leaner steering files, cheaper tool calls. Invoke as /retro."
disable-model-invocation: true
---

# Retro

A retrospective with the agent's **environment** as its subject, not the code it wrote. The question is not what the code got wrong but what the environment made expensive: steering files the agent had to find its way through, a check that would have caught the failure, a rule the reviewer did not hold, a tool call that cost more than the fact it returned.

It delivers a ranked list of proposals. The user picks which ones to apply; this skill does not edit steering files on its own.

Read the `writing-for-agents` skill before you word a pointer or touch a steering file. Its vocabulary (context pointer, context load, two loads, no-op) is the one this skill reasons in.

## 1. Read the session

Default to the current session. If the user names another, search the session logs on this machine for it. Read the transcript of every tool call, failure, retry, and dead end, together with the steering files the agent worked under and the checks the repo actually runs.

Done when the session's friction is on the table as specific moments: a search that took six calls, a failure a type check would have caught, a rule the reviewer let through. A suspicion with no moment behind it is a guess; drop it.

## 2. Hunt in seven places

Each place names the fix it usually wants and the observation that makes it worth a look.

- **Navigation.** How many calls did it take to find one fact? Did the agent have to read file A to learn that file B exists? *Use when* a run of calls went into locating something. The fix is usually a **navigation pointer** in `AGENTS.md`: name the file, and name the branch that reaches it.
- **Automated checks.** Read the repo's own check command first (`lint`, `typecheck`, `test` in `package.json`, the Makefile, or the CI workflow). A check that exists but is unwired, or silently failing, is the finding; writing a new one is the fallback. A repo with no guardrail at all (no pre-commit hook, no CI job running its checks) is itself a finding. *Use when* the agent made a mistake a check could have caught.
- **Coding standards.** A violation the reviewer missed. Classify it before writing a rule: a **mechanical** violation (a fixed syntactic pattern, a banned API, an import shape, a file-location rule) gets a deterministic check, full stop, in whichever form is cheapest here: a linter rule, a pre-commit hook, a CI job. Only a genuine **judgement call** (cross-file consistency, "matches the surrounding style") belongs in the standards doc the reviewer reads. Default to the check. *Use when* the reviewer let something through.
- **`AGENTS.md` size.** Instructions that belong in a standards doc, a check, or a skill instead of the always-loaded file. *Use when* the file is large, in this repo or in the user's global scope.
- **Tool economy.** Expensive calls that could have been one: a full read where a search would do, an MCP tool whose output is mostly noise, a build run for a fact the source already states. *Use when* one call dominated the session's token cost.
- **No-ops.** A line the model already obeys by default, or one that contradicts another line, or a rule with no branch where it changes the outcome. *Use when* the steering files are long enough that a pruning pass is worth the trip.
- **Information access.** A fact the agent needed and could not get: dev server logs it could not tail, a read-only credential it did not have, a service it could not query. *Use when* the session guessed at something observable.

## 3. Rank and present

Severity is how often the cost recurred times what each occurrence cost. A small waste on every turn outranks a big one-off; an unwired check that would have caught today's bug outranks a rule for a mistake nobody made.

Each proposal carries:

- **Moment.** The session evidence: the calls, the failure, the miss.
- **Change.** The file and the edit, exact enough to apply without reopening the session.
- **Payoff.** The cost it removes, and how often that cost comes back.
- **Cost.** What the change adds to maintain: a new check, a new file, one more always-loaded line.

Done when every proposal has all four, the list is ordered, and the user has it. Then stop. Applying the changes is a separate request.

## Reference

### Implementation versus review

All work passes through two stages, and they carry different context pressure. The **implementation** agent explores, writes, and debugs, so its window is the scarce resource. The **review** agent receives a diff, so exploration is already paid for and it can afford to hold rules.

Consequence: the reviewer enforces standards. A rule pushed into implementation competes with the work itself; the same rule given to the reviewer costs nothing until review runs. That is also why a mechanical rule goes to a check rather than either agent: no window is spent, and the rule cannot be forgotten.

### Where each change lands

| File | When it is read | What belongs there |
| --- | --- | --- |
| `AGENTS.md` / `CLAUDE.md` | Every turn, every agent | Navigation pointers only, plus the few constraints that must hold before any file is opened |
| The standards doc | At review | Judgement calls the reviewer applies |
| `docs/` | By pointer, on the branch that needs it | Reference too long or too narrow for the standards doc |
| Skills | On a trigger, or when the user types the name | A procedure, or reference the agent must reach on its own |
| Checks | On every run, automatically | Anything mechanical |

A standards file past roughly a thousand lines wants navigation pointers of its own. A skill used once a month is cheaper as a doc reached by pointer; a skill the agent must reach without being told needs a description sharp enough to fire.
