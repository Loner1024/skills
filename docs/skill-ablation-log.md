# Skill ablation log

This log applies `architecture-ablation` to the skill design itself. The baseline is the full port outline in `docs/skill-analysis-architecture.md`; each experiment removes or replaces one mechanism and compares the result against the baseline. Evidence is a design walkthrough unless stated otherwise.

## Baseline

`codebase-design`: 1 SKILL.md + 6 references:

| File | Lines | Job |
| --- | --- | --- |
| `SKILL.md` | written during the experiments; final 136 | vocabulary, design, review, handoff |
| `deepening.md` | 37 | dependency categories, seam discipline, replace-don't-layer |
| `design-it-twice.md` | 44 | parallel alternative interfaces |
| `red-flags.md` | 60 | 8 red flags + reader load |
| `shape.md` | 45 | data shape, boundary, type/test/migration notes |
| `reader-load.md` | 18 | two-axis diagnostic |
| `scan.md` | ~40 (not written) | hot spots, five friction signals, strength grading |

`architecture-ablation`: existing 165-line skill + 6 proposed additions (handoff, LOGIC prototype, ADR conditions, rigor level, three-valued verdict, door/blast radius).

`create-verification-skill`: PR #1 as-is + one cross-reference.

## `codebase-design` experiments

### E1. Remove `design-it-twice.md`, inline the method

**Variant:** an 8-line section in `SKILL.md` with four briefs (minimise the interface, maximise flexibility, optimise for the common caller, design around ports and adapters) and a "recommend one design" rule.

**Result:** the skill still produces structurally different interfaces. The reference's fourth constraint (ports & adapters) is kept inline; the seam table gives it a home, so the reference's prose was redundant, not the constraint. The hybrid-recommendation paragraph is a presentation detail, not a mechanism.

**Decision:** remove the reference, keep the four constraints inline. The main file grows by 8 lines, less than the context cost of a separate file.

### E2. Remove `deepening.md`, inline dependency categories and replace-don't-layer

**Variant:** a 4-row table in `SKILL.md` (in-process, local-substitutable, remote-owned, true external), one sentence on preferring an existing seam, and the "test behaviour" section in `shape.md`.

**Result:** seam placement and the testing strategy remain. The reference's prose repeats the table and the shape reference.

**Decision:** remove the reference.

### E3. Merge `reader-load.md` into `red-flags.md`

**Variant:** a "Reader load" section at the end of `red-flags.md`: two axes, collapse rules, state-scope ladder, 30-second test.

**Result:** the review mode keeps the diagnostic. A separate file adds a link and a load without a distinct mode. The review lens now points at the merged section instead of restating its collapse and state-scope rules.

**Decision:** merge.

### E4. Defer `scan.md` to P2

**Variant:** no scan mode in P0; design and review only.

**Result:** design and review work. Scan is a "find work" job, not a design or review step; it would add a third mode and a separate report format. The report already rates it P2.

**Decision:** defer. Add it only if "where do I start?" becomes a repeated request.

### E5. Remove `shape.md`

**Variant:** design mode only covers interface depth and seam placement; the data-shape and boundary guidance is gone.

**Result:** the skill can still judge depth, but it cannot guide the data shape or where validation lives. That is half of the "shape behind the seam" job, and the main file only gestures at it.

**Decision:** keep. This is the reference that earns its place most clearly.

### E6. Remove `red-flags.md`, inline the 8 flags

**Variant:** inline all 8 flags with symptom and fix into `SKILL.md`.

**Result:** the main file grows by roughly 50 lines and the design steps get buried. The design mode only needs the names; the review mode needs the symptom/fix detail.

**Decision:** keep as a reference, trimmed to symptom and fix. The main file lists the names and links.

### E7. Remove `CREDITS.md` or `LICENSE`

**Result:** the text is adapted from two MIT-licensed sources; the copyright and permission notices are required. Neither file is loaded by the skill.

**Decision:** keep both.

### E8. Remove `agents/openai.yaml`

**Result:** every skill in this repository carries interface metadata; without it the display name, triggers, and not-triggers are missing.

**Decision:** keep.

### E9. Remove the vocabulary block

**Variant:** drop the eight term definitions and use plain words.

**Result:** the design steps lose the shared language; "deep", "shallow", "seam", and "leverage" become ambiguous, and the review lenses cannot be stated precisely. The vocabulary is the skill's interface, not decoration.

**Decision:** keep. It is the most expensive prose block, but removing it makes the rest of the skill vaguer, not shorter.

### E10. Remove the rationale template

**Variant:** drop the six bullets (Problem, Usage, Shape, Tradeoffs, Alternatives, Open questions) and ask for "a short rationale".

**Result:** the design mode still produces prose, but the output loses a consistent, checkable artifact; different runs omit different sections.

**Decision:** keep. It is six lines and it makes the design output reviewable.

## `architecture-ablation` experiments

### A1. Remove the Handoff section

**Result:** `codebase-design` and `architecture-ablation` both trigger on "is this abstraction necessary?". Without the handoff, the routing collision is unresolved.

**Decision:** keep (2 bullets).

### A2. Remove the LOGIC prototype method

**Result:** the skill says "build a minimal prototype" but gives no method; the reader has to invent the artifact. The method is 4 lines and fills a real gap.

**Decision:** keep, trimmed to: pure liftable module, no persistence, no tests, lift the validated module.

### A3. Remove the ADR three conditions

**Result:** "fold into an ADR" is a dangling instruction. The three conditions are 3 lines and make it actionable.

**Decision:** keep.

### A4. Remove rigor level and the inconclusive verdict

**Result:** the skill still works, but loses "spend rigor where the decision is one-way" and "inconclusive is not a pass". Both are one sentence.

**Decision:** keep.

### A5. Remove the door marker

**Result:** the decision table still works. The one-way/two-way marker is a one-line risk frame that replaces the excluded `blast-radius` skill; it is cheap and useful.

**Decision:** keep.

### A6. Add the 5-level evidence ladder from `blast-radius`

**Result:** the existing 3 labels (`measured`, `design walkthrough`, `unverified`) cover design-stage evidence. The 5-level ladder is for a diff's safety fact, a different job. Adding it would blur the scope and duplicate the excluded skill.

**Decision:** do not add. The gap is documented: no diff-level negative proof.

## `create-verification-skill` experiment

### C1. Keep PR #1 as-is, add one cross-reference

**Variant:** one sentence in the feature-map maintenance section: update the map when an architecture decision removes or replaces a feature.

**Result:** one sentence, no new mode. The maintenance loop has an owner instead of a dangling `maintain-verification-skill` reference.

**Decision:** keep.

## Smoke test: design mode on a real module

Question: should `tech-diagrams/scripts/self_check.py` keep one `check()` function or expose a registry of checks?

- Usage: CLI `self_check.py <source> [--png] [--strict] [--json]`; Python `check(source, png, strict, standalone) -> (findings, stats)`.
- Shape: `Finding` + `Stats`; one `check()` orchestrates private helpers grouped by check type. The public surface is small; the implementation is large.
- Seam: the source string and optional PNG path; in-process, no adapter. The test surface is `check()` and the CLI.
- Four briefs: minimise the interface (one `check()`), maximise flexibility (a registry of `Check` objects), optimise for the common caller (the CLI plus `check()`), and design around ports and adapters (not applicable; no cross-seam dependency).
- Alternatives: the registry adds an extension point no caller needs; a pipeline of stages adds a layer without variation. Both lose the deletion test.
- Red flags:
  - Shallow module: no; the public surface is one `check()`.
  - Information leakage: no; the XML tree and helpers are internal; `Finding` is the output type.
  - Temporal decomposition: no; helpers are grouped by check type, not execution order.
  - Pass-through: no; `main` is a thin shell and `check` orchestrates real work.
  - Split ownership: no; the checker owns the findings.
  - Two ways: the CLI and Python API are two surfaces, but one is a shell, not a second implementation.
  - Importable internals: the script is a single-file CLI; all functions are importable in Python, but the public surface is the CLI. A caveat, not a module boundary.
  - Hand-synced list: no duplicated list.
- Decision: keep the single `check()`; add a registry only when a second implementation or an external extension need appears.

This is a design walkthrough, not a measured run. It ran the four briefs and the full eight-flag screen; the result supports the claim that the skill can reach a decision with the two remaining references.

## Final measurements

| Item | Baseline | Final | Change |
| --- | --- | --- | --- |
| `codebase-design` files | 1 SKILL + 6 refs + 3 meta | 1 SKILL + 2 refs + 3 meta | -4 refs |
| `codebase-design` lines | ~379 | 241 | ~-138 |
| `architecture-ablation` lines | 165 | 197 | +32 |
| `create-verification-skill` lines | 47 | 47 | +1 sentence |
| New skills | 1 | 1 | 0 |
| Total skills | 6 -> 7 (or 7 -> 8 with PR #1) | same | no extra |

The line count is not the goal. The goal is that every remaining file has a job. The removed files either repeated the main file, served a mode that is not in the P0 job, or belonged to a different skill.
