---
name: tech-diagrams
description: |
  Produce publication-quality technical figures: a self-contained HTML preview plus a single-file
  SVG. Covers architecture topology, data flow, layers/nesting, loop/flywheel, sequence, request
  lifecycle, state machine, swimlane, benchmark bars, trend/percentile charts, before/after and
  trade-off figures, timelines, 2x2 quadrants, and terminal/IDE window frames. Also decides when
  NOT to draw (use a table or prose), picks a style register (technical dark by default), writes
  caption plus alt text, and verifies the figure programmatically before delivery.
  Use when the user asks to 画图 / 绘图 / 做图表 / 架构图 / 数据流图 / 流程图 / 时序图 / 状态机图 /
  对比图 / 基准图 / 终端截图示意, or asks for a diagram, figure, or visual for docs, a README,
  a blog post, or a deck. NOT for photo or illustration generation (use imagegen), and NOT for
  full slide decks or documents (use the powerpoint or document skills).
version: 0.1.0
---

# Technical diagrams

Turn a technical claim into a figure a reader understands faster than prose, at the quality bar
of the Linear / Cursor / Vercel / Anthropic / OpenAI engineering blogs. These rules are the
distilled result of a close reading of those five; this skill is self-contained and needs nothing
outside its own folder. The per-company evidence behind a rule, if you want to check one against
its source, is published separately from this skill at
`https://github.com/Loner1024/skills/tree/main/research`.

## What you deliver

| Artifact | Purpose |
| --- | --- |
| `<slug>.html` | Self-contained preview: inline SVG + inlined tokens, no external requests, opens offline |
| `<slug>.svg` | Single-file deliverable for embedding (docs, README, blog, slide) |

Plus, in your reply: the **caption line** (which doubles as the image `alt`) and one sentence on
what the figure deliberately leaves out.

Default register is **technical dark**. Light, blueprint, and window-frame variants are defined in
[`references/registers.md`](references/registers.md).

## Workflow

0. **Decide whether to draw.** Run the ladder in
   [`references/when-to-draw.md`](references/when-to-draw.md). If a table or a paragraph does the
   job better, say so and stop. Never draw a figure that restates the surrounding prose.
1. **Report the plan in one short message** before authoring: chosen type, register, canvas size,
   and what the density budget will force you to cut. If the user is unreachable, proceed and
   state the assumptions next to the deliverable.
2. **Author the HTML preview** by copying `assets/template-dark.html` (or `-light.html`) and
   replacing the SVG body. Load tokens from `assets/tokens.css` and inline them.
   Follow the type reference plus the shared primitives:
   [`references/primitives.md`](references/primitives.md).
3. **Export the SVG**: the same `<svg>` subtree as a standalone file with an explicit `viewBox`,
   explicit `width`/`height`, inlined font stacks, `<title>` first, `<desc>` next, `role="img"`,
   and `aria-labelledby` pointing at both ids.
4. **Verify**: run `scripts/render.sh` to rasterize, then
   `python3 scripts/self_check.py <source> --png <render>` on the source (pass `--strict` to make
   warnings fail). Fix every error and re-run. Render + geometry checks catch clipping, overflow,
   diagonal connectors, budget overruns, missing a11y, low contrast, and font-stack gaps.
5. **Deliver** the two files, the caption/alt line, and any paired light/dark export the target
   needs (see [`references/export.md`](references/export.md)).

State the truth about verification: the script checks structure and geometry; **visual taste
(line weight, optical alignment, font character) still needs a human eye.** If you cannot view
images in this session, say so and hand the rendered PNG to the user for the final look.

## Routing: type -> reference

| If the content is... | Type | Reference |
| --- | --- | --- |
| Components + connections + boundaries | Architecture topology | [`references/type-structure.md`](references/type-structure.md) |
| Data transformed across stages | Data flow | same |
| Abstraction layers, containment, scope | Layers / nested | same |
| Feedback loops (agent loop, evaluator) | Loop / flywheel | same |
| Actors exchanging messages | Sequence | [`references/type-sequence.md`](references/type-sequence.md) |
| Request/build lifecycle, pipeline stages | Lifecycle | same |
| States + transitions + guards | State machine | same |
| Handoffs across roles (client/edge/origin) | Swimlane | same |
| Comparing quantities (quality, cost, throughput) | Benchmark bars | [`references/type-data.md`](references/type-data.md) |
| Change over time, p50/p95/p99 | Trend / percentile | same |
| Before vs after, trade-offs | Paired figure / curve / quadrant | same |
| Plan, phases, overlapping execution | Timeline / Gantt | [`references/type-narrative.md`](references/type-narrative.md) |
| Two-axis positioning of options | Quadrant / matrix | same |
| Something shown inside a terminal, IDE, or browser | Window frame | [`references/type-ui.md`](references/type-ui.md) |

## Hard rules (non-negotiable)

- One accent colour, at most two focal elements. Everything else is hairline + neutral text.
- A comparison between two to four parallel items (paths, lanes, options, series) may give each item
  its own hue instead: 100-step fill, stroke at the lightest step clearing 3:1, grey for what they
  share. The accent then drops to the point they all land on, or leaves.
- No decorative gradients, glows, blobs, glass, drop shadows, or textured backgrounds.
- Orthogonal connectors only, 8px corner radius; no diagonals, no shared or overlapping paths.
- Both ends of an arrow land on something visible: the tail on its source's edge, the head on its
  target's edge (or 8-10px short of a sequence lifeline). Never start or stop in empty space, never
  aim at a corner, never run a line through a box that is not an endpoint.
- Arrow labels sit on an opaque mask that either clears the stroke's ink by 1px (the default) or
  swallows the stroke whole. A label that cuts its wire must be centred on the line and on the
  middle of the run; never leave a mask edge inside the stroke.
- A mask is opaque paint, so it must match the tone of its backdrop (canvas, or a zone band / node
  fill composited over it) or it shows as a patch. The light register exposes this first.
- <= 9 nodes per figure; >= 2 crossings means split the figure.
- 4px grid for origins, sizes, and gaps; radii <= 8px; strokes 1px.
- Mono is for identifiers, commands, keys, ports, and values only - never a decorative "dev" font.
- Sentence-case headings; short noun phrases inside boxes; conditions go on the arrows.
- Caption equals alt text and states a takeaway, not "Figure 1: architecture".
- `prefers-reduced-motion` must be honoured if anything animates; static remains the default.

## Supporting files

- `references/when-to-draw.md` - decision ladder, anti-cases, caption/alt rules.
- `references/registers.md` - palettes, type ramps, CJK font stacks, register switching.
- `references/primitives.md` - token list, SVG defs, markers, routing, masks, zone bands.
- `references/type-*.md` - per-family grammar and worked snippets.
- `references/verification.md` - render commands, check list, what only a human can judge.
- `references/export.md` - SVG/PNG export, light/dark pairs, sizing presets.
- `assets/template-*.html`, `assets/tokens.css` - starting points.
- `scripts/render.sh` - rasterize: SVG via rsvg-convert, HTML via headless Chrome; `--inset`
  measures the figure's canvas margins for the preview's `--td-figure-inset`.
- `scripts/self_check.py` - lint one figure (structure, budget, geometry, connector ports, labels,
  contrast); add `--png <render>` to also check the raster.
- `scripts/lint_docs.py` - lint the SVG snippets inside these reference files.
- `examples/` - seven finished figures spanning the four type families and the window frame, each
  passing the checks.

## What not to do

- Do not fabricate product screenshots, benchmark numbers, or logos. Stylised window chrome is
  fine; a fake screenshot of someone's real product is not.
- Do not render Mermaid and call it a day: block layout from a generic engine reads as tool
  output. Hand-place nodes on a grid (use Mermaid only when the user explicitly asks for it).
- Do not ship a figure the script fails. Report the failure instead of hiding it.
