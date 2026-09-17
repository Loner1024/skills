# SVG primitives and geometry rules

Everything here is copy-paste ready. Colours come from `registers.md`; substitute the light
values when the register is `light`.

## Grid and canvas

- Place every origin, width, and gap on a **4px** grid (`x="24"`, `width="184"`, gap `16|24|32`).
- Canvas has >= 16px padding on all four sides.
- Pick the canvas from the content, not the other way round:

| Canvas | viewBox | Use |
| --- | --- | --- |
| Doc inline | `0 0 720 360` | figures that sit in a document column |
| Standard | `0 0 1100 480` | architecture, lifecycle, data flow |
| Wide banner | `0 0 1200 500` | hero figure, 2.4:1 |
| Tall | `0 0 760 900` | deep pipelines, nested layers |

## Canonical defs

```xml
<defs>
  <marker id="arrow"        markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#9BA1A6"/>
  </marker>
  <marker id="arrow-strong" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#EDEDF0"/>
  </marker>
  <marker id="arrow-accent" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#5E6AD2"/>
  </marker>
</defs>
```

Three markers, three meanings: `arrow` = default data flow, `arrow-strong` = primary path,
`arrow-accent` = the focal path (max one or two in a figure). Dashed strokes mean control plane,
optional, asynchronous, or return.

## Node

```xml
<g class="node">
  <rect x="120" y="80" width="184" height="64" rx="8" fill="#111214" stroke="rgba(255,255,255,.08)"/>
  <text x="136" y="106" fill="#EDEDF0" font-size="13" font-weight="500">Edge cache</text>
  <text x="136" y="126" fill="#9BA1A6" font-size="11" font-family="Menlo, SF Mono, monospace">cache-hit</text>
</g>
```

Focal node: `fill="#171A2B" stroke="#5E6AD2"` and the sublabel in `#A7AEF8`. Only 1-2 per figure.
Store node: add a 3px accent bar on the left edge, or two hairlines near the top to hint at a
cylinder - do not draw a full 3D cylinder. External node: dashed hairline border. Optional /
async node: `stroke-dasharray="4 3"`.

## Orthogonal connector with an 8px fillet

Right-edge to left-edge, different y (turn down then across):

```xml
<path d="M 304 112 V 196 Q 304 204 312 204 H 456" fill="none"
      stroke="#9BA1A6" stroke-width="1" marker-end="url(#arrow)"/>
```

Rules:

- Every segment is axis-aligned. **Diagonals are a defect**; `self_check.py` fails them.
- Leave the fillet radius at 8px (`Q` command); 6px minimum for tight layouts.
- Two connectors must never share a path or overlap. Cross at a single point at most.
- Draw connectors **before** nodes so lines sit behind boxes.
- Never route behind a node that is not an endpoint.

## Ports: where a connector is allowed to end

Both ends of a connector are claims about the system: this box feeds that box. An end that stops
in empty space makes the reader guess, so every end lands somewhere visible.

- **Tail on the source, head on the target.** The head's tip sits on the target's border (`x`/`y`
  equal to the box edge, ±2px); the tail starts on the source's border the same way. `self_check.py`
  fails a floating end as `port`.
- **Never aim at a corner.** A tip on a corner points at two edges at once; slide it onto the middle
  of one edge (the linter warns).
- **Never aim into a box.** A head that lands inside a rect, or a stroke that runs through a box
  that is not its endpoint, is reported as `hidden` - the box paints over the line and the arrow
  points at nothing.
- Offsets are the common cause: a route that turns down 20px above the target's top edge, or a
  return path that starts 12px below a box, reads as unattached. Snap the end to the border.
- Sequence lifelines are the one exception: an arrow stops 8-10px short of the dashed lifeline
  (the tolerance the linter allows for ends that land on a line rather than a box).
- A connector shorter than ~48px carries no readable payload: label it or drop it, unless it comes
  off an initial-state dot.

## Edge label with mask

Label *above* its wire: the mask ends 4px short of the stroke, so the line runs unbroken.

```xml
<path d="M 336 212 H 480" fill="none" stroke="#9BA1A6" stroke-width="1" marker-end="url(#arrow)"/>
<g class="edge-label">
  <rect class="mask" x="336" y="188" width="96" height="20" rx="3" fill="#0A0A0B"/>
  <text x="384" y="203" fill="#9BA1A6" font-size="11" text-anchor="middle">tool call</text>
</g>
```

The mask keeps the stroke from bleeding through the glyphs, and it has exactly two ways to meet
that stroke: leave the ink alone, or swallow it whole. Anything in between is a defect.

- **Clear the stroke**: the mask's edge stays outside the stroke's ink, so the line runs unbroken
  under the label. 1px is the floor; because a 1px stroke only occupies its own grid line, the
  next grid value (4px away) is where a mask edge usually lands in practice. This is the default,
  and the label simply sits above or beside the wire.
- **Cut the stroke**: the mask extends at least 1px past the ink on both sides, so the wire stops
  cleanly for the label's width. A cut is a claim - the label belongs to that wire - so it must be
  **centred on the line** (mask centre within 2px of the axis) and sit **in the middle of the run**
  (>= 8px of stroke left on each side, the two stubs within 8px of each other). A cut that misses
  the middle reads as damage: the wire looks broken, not labelled.
- **Take the tone of what is behind you.** A mask is an opaque rect: it is invisible over a bare
  canvas, and a visible patch over anything tinted (a zone band, a node fill). Measure the backdrop
  and give the mask that value - the canvas, or the band composited over it: `#111214` for the dark
  zone, `#F2F2F2` for the light one (`gray-200` at .55 over the `#FAFAFA` canvas). The light
  register exposes this first, because its whole scale sits between 90% and 98% lightness: a mask
  that keeps the canvas colour while sitting on a band is off by 8 levels, and 8 levels read as a
  grey box around the words. The linter warns as `mask-tone`.
- A mask edge *inside* the ink band shaves the stroke to half thickness under the glyphs. The
  linter reports all three of these as `label-cut`.
- Cutting a dashed stroke restarts its dash cadence on both sides, so the run has to be long enough
  for the two stubs to read as one wire (a 200px run cut in the middle is fine); on a short dashed
  run, keep the label beside the line instead.
- Place labels in the gap between boxes. A label that overlaps a box is reported as `hidden`: if
  the box is drawn after it the label disappears, and if it is drawn before, the glyphs collide
  with the box's own text.
- A mask drawn *after* a box punches a hole in that box's border whatever its colour; the linter
  warns (`mask`) - same defect as `mask-tone`, seen from the paint order.

## Zone band (grouping without a box)

```xml
<rect class="zone" x="88" y="56" width="456" height="160" rx="8" fill="#16181C" opacity=".55"/>
<text class="zone-label" x="104" y="76" fill="#7C8389" font-size="11"
      font-family="Menlo, SF Mono, monospace" letter-spacing="0.8">EDGE NETWORK</text>
```

Zone tags are uppercase 11px mono. Use a zone instead of nested cards; never nest cards inside
cards.

## Decision node

```xml
<path d="M 380 224 L 420 256 L 380 288 L 340 256 Z" fill="#111214" stroke="rgba(255,255,255,.16)"/>
<text x="380" y="260" fill="#EDEDF0" font-size="12" text-anchor="middle">cached?</text>
```

A diamond is a **shape**, not a connector: because it is filled, the diagonal-segment check
skips it (any filled path counts as a shape; a connector keeps `fill="none"`). If a diagonal is
genuinely intended elsewhere, mark that element `data-diagonal="ok"` and say why in a comment.
Exits are labelled on the outgoing arrows (`hit`, `miss`, `(x) Exit loop`) - never leave a branch
unlabelled.

## Loop arc

Draw the return path as a curved arc above or below the row, label the condition on the arc:
`"Until tests pass"`. Loops are cycles, not a straight line that happens to point backwards.

## Chart primitives (see also `type-data.md`)

- Axis: 1px `#7C8389` baseline; ticks 11px `#7C8389`; no top/right frame.
- Leave >= 16px of canvas padding left of the tick labels and below the footnote. Text that lands
  within 8px of the edge reads as a mistake even when nothing is clipped, and the `--png` render
  check reports it (`edge`).
- Gridlines: horizontal only, `rgba(255,255,255,.06)`, never bolder than the baseline.
- Series: series 1 = `#5E6AD2` (accent), series 2 = `#9BA1A6`, series 3 = `#7C8389`; more than
  three series means the chart wants a different form (small multiples or a table).
- Direct labels at the end of each line/beside each bar; a legend only when direct labels are
  impossible, and then it is centred under the plot.
- Value labels: 11px tabular numerals, `#9BA1A6`; the decisive value may take the accent colour.
- Every chart carries: title (the claim), optional one-line gloss, and an asterisk footnote for
  caveats (sample size, measurement window, tool access).

## Accessibility block (required on both artifacts)

```xml
<svg role="img" aria-labelledby="slug-title slug-desc" viewBox="0 0 1100 480" width="1100" height="480"
     xmlns="http://www.w3.org/2000/svg"
     font-family="Inter, PingFang SC, Hiragino Sans, Heiti SC, Noto Sans CJK SC, sans-serif">
  <title id="slug-title">Sharded metadata lookup</title>
  <desc id="slug-desc">A request reaches the edge cache, misses, and fetches one 200 KB shard whose index is binary-searched for the path.</desc>
  ...
</svg>
```

`<title>` is the first child (assistive tech may ignore later ones); ids are slug-prefixed so two
inline figures cannot collide.
