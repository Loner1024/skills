# Type family: data

Covers **benchmark bars**, **trend / percentile charts**, **before-after pairs**, **trade-off
curves**, and their **table fallback**. Pattern sources: OpenAI's GPT-5 benchmark charts, Cursor's
"title is the claim" charts, Vercel's measured p99 figures and real HTML tables, Linear's
chart-plus-table-plus-`N=` habit.

## Universal chart rules

- **The title is the claim**, not the metric name: "Indexed shards cut p99 lookup latency by 91%".
  A one-line gloss under the title carries the unit and the comparison basis.
- Direct labels beat legends. A legend is allowed only when direct labelling is impossible, and
  then it sits centred under the plot, wrapped, 11px.
- No top/right frame, no vertical gridlines, gridlines never bolder than the axis baseline.
- Three series maximum. More than three series is a small-multiples figure or a table.
- Report the denominator and the window in the footnote: `n = 477`, `Aug 5-12, 2026`, `p99 over
  24 h`. **Never invent a number** - if the user did not supply it, leave the label out or ask.
- Do not truncate a bar axis to exaggerate a difference; if the delta is small, show the delta
  explicitly on a shared scale (this is the honest alternative to a cropped axis).
- Tabular numerals for values; align value labels to a shared right edge.

## Benchmark bars

- Group by entity (model, region, version), one bar per condition; the winner takes the accent,
  the rest stay neutral grey - do not colour every bar differently.
- Value label above each bar (11px, `text-2`); the decisive value may be accent-coloured.
- Baseline at the bottom, 1px; category labels under the axis, 11px, may wrap to two lines.
- Sort by value unless the order carries meaning (then say so in the gloss).

## Trend and percentile

- Two or three series maximum; each line gets a direct end label (`p99 shards`, `p99 per-path`).
- Percentile figures must name the statistic on the axis (`p50`, `p95`, `p99`) - a "latency"
  axis without a percentile is unreadable.
- Mark the intervention: a vertical hairline with a small mono date label at the change point.
- Log scale only when the range demands it, and then say `log` on the axis.
- A zoomed inset (the last 10% of the series) is better than a squashed full range when the
  conclusion lives at the end - label the inset window (`step 9832`).

## Before / after pairs

- Two panels, identical scale, identical layout, identical series count. The only difference is
  the mechanism.
- Label the panels `before` / `after` in 11px mono above each, not "Figure A/B".
- Ship the mechanism change as a diagram *and* the measured result as a chart when the story is
  "we changed X and it got faster". A chart alone hides the cause; a diagram alone hides the
  magnitude.

## Trade-off curves and quadrants

- Axes are the two quantities the decision trades between, each with a unit.
- Mark the chosen point with the accent plus a label (`~200 KB`); annotate the knee, not every
  sample.
- Quadrant axes must be labelled with their ends (`lower cost` -> `higher cost`) and the
  quadrant names must state conclusions (`higher quality, lower cost`), never `Q1..Q4`.
- Scatter points need direct labels when fewer than ~8 of them; more than 12 points means it
  wants to be a curve or a table.

## Table fallback (do not draw a table)

Use a real `<table>` in the document when the content is `>= 4` columns, row-by-row lookup, or
mixed types (a name plus three metrics plus a link). Rules that keep tables from looking wrong:

- Numeric columns right-aligned, including their headers; text columns left-aligned.
- Peer units and precision consistent; no fake precision.
- One category per column only when it changes how rows are read (avoid repeating a constant).
- Highlight a recommended row only if the source supports the recommendation.

## Worked example: single-series bars with the claim as title

```xml
<svg role="img" aria-labelledby="bars-title bars-desc" viewBox="0 0 720 360" width="720" height="360"
     xmlns="http://www.w3.org/2000/svg"
     font-family="Inter, PingFang SC, Hiragino Sans, Heiti SC, Noto Sans CJK SC, sans-serif">
  <title id="bars-title">Indexed shards cut p99 lookup latency by 91%</title>
  <desc id="bars-desc">Two bars compare p99 metadata lookup latency: 215.8 milliseconds before and 19.1 milliseconds after indexing.</desc>
  <rect width="720" height="360" fill="#0A0A0B"/>
  <text x="48" y="44" fill="#EDEDF0" font-size="14" font-weight="500">p99 lookup latency, before vs after</text>
  <line x1="48" y1="296" x2="688" y2="296" stroke="#7C8389" stroke-width="1"/>
  <line x1="48" y1="96" x2="688" y2="96" stroke="rgba(255,255,255,.06)" stroke-width="1"/>
  <line x1="48" y1="196" x2="688" y2="196" stroke="rgba(255,255,255,.06)" stroke-width="1"/>
  <text x="40" y="100" fill="#7C8389" font-size="11" text-anchor="end">200</text>
  <text x="40" y="200" fill="#7C8389" font-size="11" text-anchor="end">100</text>
  <text x="40" y="300" fill="#7C8389" font-size="11" text-anchor="end">0</text>
  <rect x="240" y="88" width="88" height="208" rx="4" fill="#2A2D34"/>
  <text x="284" y="76" fill="#9BA1A6" font-size="11" text-anchor="middle">215.8 ms</text>
  <text x="284" y="320" fill="#9BA1A6" font-size="11" text-anchor="middle">per-path</text>
  <rect x="408" y="276" width="88" height="20" rx="4" fill="#5E6AD2"/>
  <text x="452" y="265" fill="#A7AEF8" font-size="11" text-anchor="middle">19.1 ms</text>
  <text x="452" y="320" fill="#9BA1A6" font-size="11" text-anchor="middle">indexed shards</text>
  <text x="48" y="340" fill="#7C8389" font-size="11">Measured on production traffic, 24 h window.</text>
</svg>
```

Caption / alt: "p99 metadata lookup latency fell from 215.8 ms to 19.1 ms after routing began
fetching indexed shards, measured over the same 24-hour production window."

## Mistakes to avoid

- Two bars coloured with two loud colours (the loser stays neutral grey).
- A "latency" axis with no percentile or window.
- A cropped axis that turns a 10% win into a 3x visual win.
- Chart titles like "Latency by version" - that is a label, not a claim.
