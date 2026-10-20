---
name: codebase-design
description: |
  Design and review deep modules: choose the interface, place the seam, and shape what sits behind it. Use when the user asks 模块设计 / 接口设计 / 接缝 / 深模块 / 代码库架构 / 这个模块该怎么拆 / 这个接口是不是太宽, or asks to design a module, review module boundaries, place a seam, or decide where validation and state belong. Also use when another skill needs the deep-module vocabulary.

  Not for system-level mechanism decisions (service, cache, queue, deployment boundary, state ownership). That is architecture-ablation.
---

# Codebase design

Design deep modules: a lot of behaviour behind a small interface, at a clean seam, testable through that interface. Use the same vocabulary for designing a new module and reviewing an existing one.

## Vocabulary

Use these terms exactly. Do not substitute "component", "service", "API", or "boundary".

**Module.** Anything with an interface and an implementation: a function, class, package, or tier-spanning slice. Scale-agnostic.

**Interface.** Everything a caller must know to use the module correctly: the type signature, plus invariants, ordering constraints, error modes, required configuration, and performance characteristics.

**Implementation.** The body of code inside a module.

**Adapter.** A concrete thing that satisfies an interface at a seam. It describes a role, not a substance: a Postgres repository and an in-memory fake can both be adapters.

**Depth.** Leverage at the interface: how much behaviour a caller or test can exercise per unit of interface they must learn. A module is **deep** when a large amount of behaviour sits behind a small interface, **shallow** when the interface is nearly as complex as the implementation.

**Seam** (Michael Feathers). A place where you can alter behaviour without editing in that place; the location at which a module's interface lives. Where to put the seam is a design decision distinct from what goes behind it.

**Leverage.** What callers get from depth: more capability per unit of interface they learn. One implementation pays back across N call sites and M tests.

**Locality.** What maintainers get from depth: change, bugs, knowledge, and verification concentrate in one place instead of spreading across callers.

## The tests

**Deletion test.** Imagine deleting the module. If complexity vanishes, it was a pass-through. If complexity reappears across N callers, it was earning its keep.

**The interface is the test surface.** Callers and tests cross the same seam. If a test has to reach past the interface, the module is probably the wrong shape.

**One adapter means a hypothetical seam; two adapters mean a real one.** Do not introduce a seam unless something actually varies across it. Production plus a test double is the common pair; a single implementation with no variation is indirection.

## Design a module

### 1. Write the caller's usage first

Write the README-style usage and two or three realistic call sites before the types. What the caller imports, calls, and gets back. The usage is the spec; derive the types from it. When usage and sketch disagree, reconcile the sketch to the usage, not the reverse.

### 2. Choose the shape behind the seam

Data structures first. Decide what the module must never allow, how the data is read, and which structure encodes exactly that. Reach for a state machine, a typed model, a map or registry, a discriminated union, or a reducer when the domain calls for it. Keep validation at system boundaries and business logic in pure functions. See [references/shape.md](references/shape.md).

### 3. Place the seam

Classify the dependency that varies:

| Category | Example | Where the seam goes |
| --- | --- | --- |
| In-process | Pure computation, in-memory state | No adapter; merge the modules and test through the new interface |
| Local-substitutable | Postgres via PGlite, in-memory filesystem | Test with the stand-in; the seam is internal |
| Remote but owned | Your own service over HTTP/gRPC/queue | A port at the seam; an HTTP adapter in production, an in-memory adapter in tests |
| True external | Stripe, Twilio, a third party | Inject a port; tests provide a mock adapter |

Do not put transport, storage, framework, or wire types on the public surface. Parse external data into domain types behind the seam.

Prefer an existing seam over a new one. Use the highest seam that can test the behaviour; the fewer seams, the better, and one is the ideal.

### 4. Explore alternatives

Your first interface is unlikely to be the best. Write three briefs for the same module, each with a different constraint:

- Minimise the interface: one to three entry points, maximum leverage per entry point.
- Maximise flexibility: support many use cases and extension.
- Optimise for the most common caller: make the default case trivial.
- Design around ports and adapters for cross-seam dependencies.

If the harness can run parallel subagents, give each brief to one. If it cannot, solve them sequentially, or have one agent wear the four hats in turn. Compare on depth, locality, and seam placement. Recommend one design; do not present a menu.

### 5. Screen the red flags

Before committing, run the checklist in [references/red-flags.md](references/red-flags.md): shallow module, information leakage, temporal decomposition, pass-through, split ownership, two ways to do one task, importable internals, hand-synced list. Revise or reject the shape for each flag that fires.

### 6. Write the rationale

Keep it to one page:

- **Problem.** What the module is for, and what makes the shape non-obvious.
- **Usage.** The caller's view, written first.
- **Shape.** The recommended design, the load-bearing decisions, which invariants live in types, and where validation happens.
- **Tradeoffs.** One line per tradeoff: "we accept X in exchange for Y."
- **Alternatives.** At least one concrete alternative and why it lost.
- **Open questions.** What the user must decide, phrased as questions.

Fold the rationale into the existing design doc or ADR when one exists. Do not generate a duplicate report.

### 7. Agree, then implement

Default: proceed to implementation with the chosen shape. Pause for sign-off only when the user asks for a checkpoint. The sketch is the contract; a deviation is a signal to surface, not friction to absorb silently.

### 8. Scrap when the shape is wrong

A single edge case does not condemn a design. A pattern does:

- The same workaround appears across unrelated code.
- Multiple unrelated edge cases need special-case branches.
- Types need escape hatches (`any`, casts, optional fields always set) to compile.
- Callers must know the module's internal rules to use it.
- Two or more independent implementation deviations share one shape.

When you scrap: re-ground on what was built, redesign as if the new constraints had been day-one assumptions, subtract before adding, and return to step 1.

## Review a module

Read the module and its callers. Report findings in a table:

| Finding | Evidence | Fix | Strength |
| --- | --- | --- | --- |

Cover these lenses:

- **Deletion test.** If the module vanished, where would its complexity go? A pass-through is a removal candidate.
- **Depth.** Is the interface nearly as complex as the implementation? Do callers coordinate several methods to complete one operation? Do public options expose internal stages?
- **Reader load.** How many layers must a reader trace to answer "where does X come from?" and "what can change X?" How much hidden or mutable state must they hold? See the reader-load section in [references/red-flags.md](references/red-flags.md).
- **Validation placement.** Is validation at the system edge, or scattered through the core? Does the public surface expose transport, storage, framework, or wire types?
- **Test surface.** Can a test exercise the behaviour through the interface? If it must mock an internal helper or assert call order, the shape is wrong.

Do not list every possible refactor. Keep the findings that would change a decision, and say what you checked and cleared.

## Handoff

- The question is "should this service, cache, queue, layer, or state boundary exist?" → `architecture-ablation`. This skill judges shape, not existence.
- The module change needs proof through the real app → use the repo's `verify-<app>` skill if it has one; otherwise `create-verification-skill` can generate it, or use the existing test environment.
- A figure would help → `tech-diagrams`.

## Done when

- Design: usage and shape agree; the seam is at a point where behaviour actually varies; the red-flag checklist is clear; at least one alternative was considered; the rationale is written.
- Review: every finding has evidence and a fix; the deletion test has a verdict; the report separates confirmed problems from checked-and-cleared items.
