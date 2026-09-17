# Type family: narrative

Covers **timelines / Gantt**, **2x2 quadrants**, and **comparison matrices**. Pattern sources:
Vercel's numbered figure sequences, Cursor's overlap timelines, OpenAI's `Figure NN · Title`
convention.

## Timeline / Gantt

Use for plans, phases, and overlapping execution (compute/communication overlap, rollout windows,
migration stages).

- Rows are resources or actors; columns are time. Row labels left, 11-13px, aligned to a shared
  left edge.
- Blocks are rounded 4px rects; a block that overlaps another in the same row gets a lower
  opacity so the overlap is visibly an overlap.
- Mark the critical path or the decision point with the accent - one block, not five.
- Time axis: hairline baseline with 3-5 ticks; if the scale is illustrative, say so
  (`illustrative, not to scale`) rather than faking precise ticks.
- Annotate phases above the plot (`01 Initial burst`, `02 Reusing connections`, `03 Outcome`),
  never inside the blocks.

## Quadrant (2x2)

Use to position options against two forces. This is a decision figure, not decoration.

- Axis ends are labelled with the *direction of goodness*: `lower cost` -> `higher cost`,
  `worse` -> `better`. A quadrant with bare `Low/High` is unfinished.
- Quadrant names state the conclusion in sentence case (`higher quality, lower cost`), and the
  preferred quadrant may take a soft accent wash (6-10% opacity) - never a loud fill.
- Points need direct labels; more than ~8 labelled points means this wants to be a table.
- The chosen option gets the accent dot plus its label; everything else stays neutral.
- Keep the origin marker if the axes have a meaningful zero; otherwise say the axes are relative
  (`relative to <baseline>`).

## Comparison matrix

- Use a real `<table>` in the document unless the matrix *is* the figure (a slide, a poster).
- If drawn: rows and columns of equal width, header row on `#16181C`, 1px hairlines, dots or
  checks in `text` colour; the recommended column gets the accent wash and its header keeps
  readable contrast.
- Never encode a value with colour alone: pair it with a mark or a number.

## Sequence of figures (multi-figure posts)

When a document carries several figures, keep them a family:

- Shared canvas width; if figures vary in height, top-align their content on the same baseline
  grid.
- Number them `Figure 01`, `Figure 02` in the caption when the document is a numbered technical
  post; skip numbering for a single inline figure.
- Reuse the same palette roles across figures: the focal colour means the same kind of thing in
  every figure, and a zone label keeps the same case and size.
- Escalate detail deliberately: overview -> mechanism -> measured result. Do not repeat the same
  figure at the same fidelity twice.

## Worked example: quadrants with direction labels

```xml
<svg role="img" aria-labelledby="quad-title quad-desc" viewBox="0 0 720 420" width="720" height="420"
     xmlns="http://www.w3.org/2000/svg"
     font-family="Inter, PingFang SC, Hiragino Sans, Heiti SC, Noto Sans CJK SC, sans-serif">
  <title id="quad-title">Routing policy positions: satisfaction against cost</title>
  <desc id="quad-desc">A scatter plot places three routing policies; the shipped policy sits in the higher-satisfaction, lower-cost quadrant.</desc>
  <rect width="720" height="420" fill="#0A0A0B"/>
  <rect x="120" y="72" width="264" height="140" fill="#5E6AD2" opacity=".08"/>
  <line x1="120" y1="72" x2="120" y2="352" stroke="#7C8389" stroke-width="1"/>
  <line x1="120" y1="352" x2="600" y2="352" stroke="#7C8389" stroke-width="1"/>
  <line x1="360" y1="72" x2="360" y2="352" stroke="rgba(255,255,255,.08)" stroke-width="1"/>
  <line x1="120" y1="212" x2="600" y2="212" stroke="rgba(255,255,255,.08)" stroke-width="1"/>
  <text x="600" y="376" fill="#7C8389" font-size="11" text-anchor="end">higher cost</text>
  <text x="120" y="376" fill="#7C8389" font-size="11">lower cost</text>
  <text x="112" y="80" fill="#7C8389" font-size="11" text-anchor="end">better</text>
  <text x="112" y="348" fill="#7C8389" font-size="11" text-anchor="end">worse</text>
  <text x="136" y="96" fill="#7C8389" font-size="11">higher quality, lower cost</text>
  <circle cx="264" cy="132" r="5" fill="#5E6AD2"/>
  <text x="278" y="136" fill="#EDEDF0" font-size="11">routed policy</text>
  <circle cx="452" cy="164" r="4" fill="#9BA1A6"/>
  <text x="466" y="168" fill="#9BA1A6" font-size="11">frontier model</text>
  <circle cx="332" cy="286" r="4" fill="#9BA1A6"/>
  <text x="346" y="290" fill="#9BA1A6" font-size="11">small model</text>
  <text x="120" y="404" fill="#7C8389" font-size="11">Relative to the frontier baseline; higher is better on both axes.</text>
</svg>
```

Caption / alt: "Three routing policies plotted by user satisfaction and cost; the shipped policy
sits in the higher-satisfaction, lower-cost quadrant relative to the frontier baseline."

## Mistakes to avoid

- Quadrants labelled `Q1..Q4` or with bare `Low/High` axes.
- Timelines that are really milestone lists (use bullets) or that fake precise ticks.
- A second figure at the same fidelity as the first - escalate detail or cut one.
