---
name: architecture-ablation
description: "Test whether each component, layer, or mechanism earns its place by removing or replacing it and comparing the result against a baseline. Use when designing or choosing between system architectures, judging whether an existing system is over-engineered, weighing architecture options against each other, or deciding whether to introduce a new service, cache, queue, or abstraction layer. Changes to deployment boundaries, service communication, state ownership, or consistency coordination trigger it. Local code refactoring, function extraction, and ML model ablation do not. Use when the user asks about 架构设计 / 架构选型 / 系统简化 / 过度设计 / 要不要引入某个服务缓存队列."
---

# Architecture ablation

Test what a component, layer, or mechanism actually contributes by removing or replacing it.
Every piece of complexity that stays must trace back to a specific constraint, and every
simplification must come with comparison evidence.

Stay inside the architecture this decision actually touches. A stack, product capability, or
architecture boundary the user has already fixed is a constraint: you may name what it costs, but
you cannot reach a simpler design by changing the user's goal. Ablation inside a design discussion
can stay at the design level; code and environment changes follow whatever authorization the
current task already carries.

## When to use

**Triggers:**

- Designing a new system, deciding whether a component or layer is worth introducing.
- An existing system raises the question "is this abstraction doing anything?"
- Comparing several architecture options.
- A review challenges whether a mechanism is necessary.

**Does not trigger:**

- Local code cleanup (extract a function, rename, remove duplication) — that is ordinary refactoring.
- Changes that do not move a deployment boundary, service communication, or state ownership.
- ML model ablation experiments — a different field.
- The user asking "how do I simplify this code?" rather than "should this architecture exist?"

## Establish the comparison baseline

Pull the behaviour and acceptance conditions that must survive out of the requirements, the
existing implementation, and decisions already made: the relevant performance, failure recovery,
data consistency, and permission boundaries. Separate hard constraints from preferences, and
committed capacity or evolution needs from speculative ones.

Write anything unknown as an assumption in one fixed shape, so it can be tracked and rechecked:

> `[assumption] <statement> → if false, it affects <which conclusion>`

For example: `[assumption] daily order peak < 10k → if false, it affects "drop the message queue and go synchronous"`

Mark gaps that would change the conclusion as unverified. Do not invent numbers to fill them.

Record the original design's critical call paths, state ownership, and dependencies as the
baseline for later comparison. When an implementation already exists, check how that baseline
behaves in the scenarios at issue. If the baseline itself fails there, record that failure —
"both variants fail" is not evidence that a simplification passed.

## Choose what to ablate

Look first at mechanisms with high maintenance cost, overlapping responsibility, or a mandate
that only ever came from speculation: an extra service, an abstraction layer, a cache, a queue, an
extension framework, a second copy of state. Pick a small set of candidates by decision impact
(three to five usually settles it; more than five means re-examine the scope). When one mechanism
answers the question on its own, ablate only that one.

For each candidate, write down:

- Which specific requirement it claims to serve.
- Which observable behaviour is expected to get worse without it, and the scenario that exposes it.
- Whether it can be deleted outright, or whether a simpler implementation has to take over the
  responsibility that matters.

Compare total complexity: deployment units, dependencies, state and consistency coordination,
comprehension cost, operations, migration cost. Shorter code with harder manual operations or
failure handling may not be a win. Score the removal cost in an existing system separately from
the cost the new design avoids introducing.

## Run the comparison

Starting from the current design, remove or replace one mechanism at a time. An inseparable
dependency can be ablated as a group, but state the group's boundary and attribute the conclusion
only to that group. Complete each variant with the connections or thin replacements it needs, and
record their cost; a build failure caused by leftover references does not prove the original
mechanism was necessary.

Hold requirements, inputs, load, environment, and acceptance criteria constant. Choose scenarios
that separate the variants along the responsibility the mechanism claims, and cover the failure or
recovery paths that go with it. Removing a queue, for example, means comparing task-acceptance
semantics and recovery after a process interruption, not just steady-state request latency.

Pick the validation method the available evidence supports:

- **With an implementation**: run the relevant checks in an isolated local variant or an existing
  test environment, and keep the commands, scenarios, and results. Support performance claims with
  comparable measurements, and report ranges and limitations when the numbers are noisy.
- **Still in design**: walk both designs through the same business scenario step by step — data,
  state, side effects, failure recovery. Label the result a design walkthrough. Build a minimal
  prototype only for the key uncertainty that a walkthrough cannot settle, and only within the
  task's scope.
- **Cannot be verified**: label it unverified, name the missing evidence, and name the smallest
  action that would produce it.

Tag evidence as `measured`, `design walkthrough`, or `unverified`. Never write an expected result
as though it had already passed.

## Decide

| Decision | Basis |
| --- | --- |
| Remove or replace | The comparison shows the variant satisfies the hard constraints and total complexity falls. At design stage, give a provisional conclusion with its assumptions; for an existing implementation, land the change within the evidence's coverage. |
| Keep | Removing it would violate a specific constraint, and no simpler replacement satisfies it either. Write out the failing scenario or counterexample. |
| Defer | The mechanism only serves a need that has not happened and has not been committed to, and a simpler design meets today's requirements. State the observable condition that would bring it back. |
| Unverified | Evidence is not enough to decide. Leave the existing mechanism in place; state the open items for the new design, and treat the unknown as proving neither that it can be removed nor that it is required. |

For guarantees such as security, correctness, and reliability, verify the mechanism or invariant
that carries the responsibility. A normal-path run that never triggers a protection only shows
that this scenario did not exercise it. Necessary guarantees remain acceptance conditions; the
component that implements one may still be modified by ablation.

## Re-verify the combination and converge

After accepting one simplification, update the baseline and evaluate the next one. Individually
passing removals do not add up to a joint removal that passes — mechanisms with overlapping
responsibility need that check most. Run combination experiments only for candidates that have a
dependency or substitution relationship; do not enumerate unrelated pairs.

Compare the final combination against the original design under the same acceptance conditions,
and confirm the complexity did not move into callers, the operations process, or another copy of
state. If the task includes implementation, verify the final artifact; if it is design only, walk
the key scenarios through the final design again.

Stop when the accepted simplifications have evidence, the final combination meets the constraints,
and the complexity that remains has a concrete justification. List the open items. Do not keep
experimenting to reach a deletion count, and do not claim the globally simplest architecture.

## Deliver

Lead with the design you recommend and what it drops relative to the original, then give enough
evidence to recheck the call. A compact table covers several candidates:

| What to ablate, and the replacement | Constraint and scenario | Evidence type and result | Complexity change | Decision |
| --- | --- | --- | --- | --- |

Include the re-verification of the final combination, the assumptions that affect the conclusion
(in the `[assumption]` shape), and the conditions that would reintroduce a deferred mechanism.
Link files or verification records when artifacts exist. A single decision fits in a short
paragraph; fold it into the existing design doc or ADR rather than generating a duplicate report.
Record deferrals in the team knowledge base with their re-entry trigger, so they can be found later.

## Example: removing the dedicated cache from an order service

**Context:** the order service draft runs API layer → cache layer (Redis) → service layer → DB.
About 3,000 orders a day, P99 latency budget < 500 ms.

**Baseline:**

- Hard constraints: P99 < 500 ms, orders eventually consistent, no confirmed order lost to a
  process restart.
- `[assumption] daily order peak < 10k → if false, it affects the "remove the cache layer" conclusion`

**Candidate:** the dedicated Redis cache layer.

| What to ablate, and the replacement | Constraint and scenario | Evidence type and result | Complexity change | Decision |
| --- | --- | --- | --- | --- |
| Drop Redis, read from the DB directly | P99 < 500 ms; simulate 10k queries/day | Design walkthrough: an indexed PostgreSQL lookup is ~5 ms, plus network overhead < 50 ms, well under 500 ms | One fewer deployment unit (Redis), no cache-coherence maintenance, fewer failure points | Remove |

**Conclusion:** under the current traffic assumption the cache layer satisfies no hard constraint,
so it is over-engineering. Recommend reading from the DB directly. Reintroduce a cache if daily
orders pass 10k and the DB lookup P99 approaches 200 ms.
