---
name: architecture-ablation
description: |
  Load before deciding whether a component, service, cache, queue, table, or storage layer should
  exist; before changing data ownership or a deployment boundary; and before simplifying a system
  or choosing between architecture options. Load it even if you think you know it; the file is the
  source of truth. Test each piece by removing or replacing it against a baseline.
  Also load when the user says 架构 / 选型 / 要不要上 / 该不该拆 / 服务拆分 / 存储选型 /
  元数据与对象存储 / 数据放哪 / 过度设计 / 简化 / 合并 / 去掉这层.
  Not for local refactoring, function extraction, or module layout (codebase-design).
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
"both variants fail" is not evidence that a simplification passed. If a new requirement
invalidates the baseline, rebuild it as if the requirement had been a day-one assumption; do not
ablate against a baseline that no longer holds.

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

The first candidate is deletion: remove dead code, redundant validators, and stub references
before adding a replacement. Cut before polishing.

The deletion test (defined in `codebase-design`) is the module-level version of this question: delete
the module and see whether complexity vanishes or reappears across callers. Here the same question
becomes an experiment against the baseline.

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
  comparable measurements, and report ranges and limitations when the numbers are noisy. If the
  repo has a `verify-<app>` skill, use its feature journeys as the scenario and keep the evidence
  path. The generator (`create-verification-skill`) is explicit-only, so point at the generator
  rather than assuming you can invoke it.
- **Still in design**: walk both designs through the same business scenario step by step — data,
  state, side effects, failure recovery. Label the result a design walkthrough. If one state model
  is the uncertainty a walkthrough cannot settle, build a throwaway prototype: the logic in a pure,
  liftable module, no persistence, no tests. Once the question is answered, lift the validated
  module into the real code.
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

Spend rigor where the decision is one-way; a two-way door does not need the full comparison. An
inconclusive comparison is not a passing simplification: leave the mechanism in place and name the
evidence that would settle it.

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
paragraph; fold it into the existing design doc, or an ADR that already covers the area, rather
than generating a duplicate report. Record deferrals with their re-entry trigger, in the existing
design doc, ADR, or the reply, so they can be found later.

For each decision, record `Door: one-way / two-way`. A one-way door needs stronger evidence than a
two-way door.

Write an ADR only when all three conditions hold: the decision is one-way (hard to reverse),
surprising without context, and the result of a real trade-off. Otherwise fold it into the existing
design doc or the reply. Skip the ADR when one condition is missing.

## Handoff

- If the question is "is this interface the right shape?" rather than "should this mechanism
  exist?", use `codebase-design`. This skill decides existence; that skill decides shape.
- If the decision needs a figure, use `tech-diagrams`; a comparison of three or fewer candidates
  is usually a table.

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
