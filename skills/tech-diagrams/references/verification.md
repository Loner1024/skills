# Verification

Two layers, and you must be honest about which one ran.

| Layer | Who | Catches |
| --- | --- | --- |
| Geometry + structure | `scripts/self_check.py` (automated) | broken XML, missing a11y, node/edge budget, diagonals, grid drift, text overflow, low contrast, decorative effects, missing CJK fallback, clipping |
| Rasterisation | `scripts/render.sh` (automated) | viewBox/size mismatch, missing fonts at render time, blank or near-blank output |
| Text placement | `self_check.py --png` (automated) | a text block sitting visibly high or low inside its box (measured from the render, since geometry maths cannot see font metrics) |
| Canvas padding | `self_check.py --png` (automated) | content coming within 16px of a canvas edge: blown-in text, a footnote jammed against the bottom |
| Connector ports | `self_check.py` (automated) | an arrow end floating in space or landing inside a box, a stroke running through a box that is not its endpoint, a label a box paints over, an unlabelled stub, a label mask that shaves or mis-cuts its stroke, or one whose colour differs from its backdrop |
| Taste | a human eye | line weight, optical alignment, font character, whether the figure actually persuades |

**This session may not be able to view images.** If so, say it plainly: hand over the rendered PNG
and ask for the visual check instead of claiming you looked at it.

## Commands

```bash
# rasterise (SVG -> PNG at 2x; HTML -> PNG via headless Chrome)
./scripts/render.sh figures/shard-lookup.svg --scale 2
./scripts/render.sh figures/shard-lookup.html --width 1100 --height 480

# lint the source
python3 scripts/self_check.py figures/shard-lookup.svg
python3 scripts/self_check.py figures/shard-lookup.html --strict

# lint and check the render in one pass (also verifies the file is not blank)
python3 scripts/self_check.py figures/shard-lookup.svg --png figures/shard-lookup.png

# machine-readable, for CI or for iterating without re-reading prose
python3 scripts/self_check.py figures/shard-lookup.svg --json

# lint the SVG snippets inside these reference files (keeps the docs from teaching defects)
python3 scripts/lint_docs.py
```

Exit codes: `0` clean, `1` errors present (or warnings, under `--strict`), `2` the file could not be
read/parsed. Lines printed as `note` are informational and never change the exit code; `--json`
puts them in a separate `notes` array.

`render.sh` prints the dominant background colour and the share of the canvas that was drawn on
(`content=`, measured against that background so a dark register reads correctly). A dark figure
sits around 1-10%; `0%` means nothing rendered, and above ~40% the canvas is usually cramped.

## Pre-delivery checklist

Run it in this order and fix the first failure before moving on.

1. **Structure** - well-formed XML; `<svg role="img" aria-labelledby="...">`; `<title>` is the
   first child; `<desc>` present; ids are slug-prefixed.
2. **Budget** - `<= 9` nodes; `<= 2` crossings; no node wider than the canvas minus padding.
3. **Geometry** - origins/sizes/gaps on the 4px grid; radii `<= 8`; strokes `1` (1.5 max).
4. **Connectors** - every segment axis-aligned; no shared paths; every edge label has a mask that
   either clears its stroke's ink by 1px or swallows the stroke whole (and a cut sits centred on
   the line and on the middle of the run); both ends of every arrow land on a box edge, a lifeline,
   or a start dot; no stroke runs through a box that is not its endpoint. `self_check.py` fails the
   whole of this list as `port` / `hidden` / `label-cut` / `mask` / `label`.
5. **Text** - labelled nodes fit their box (estimated width/height); no text outside the canvas
   padding; no text below 11px; CJK text has a CJK font in the stack.
6. **Colour** - one accent in use, `<= 2` focal elements, or `<= 4` categorical tints when the
   figure's argument is a comparison between parallel items (the two layers do not stack - see
   `registers.md`); contrast >= 4.5:1 for body text, >= 3:1 for large text and non-text marks; no
   gradients, filters, or drop shadows.
7. **Content** - caption written and equal to the intended `alt`; caption states a takeaway;
   figure introduced in prose; deliberate omissions stated.
8. **Render** - PNG produced at the expected dimensions; `render.sh` reports a sensible
   `background=`/`content=` pair (blank is 0%, a cramped canvas is far higher; a run of `□` tofu
   boxes shows up as an unusually regular pattern, so when in doubt check the CJK line
   specifically). `--png` on `self_check.py` makes the blank/density call for you and reports any
   `center` finding: text sitting more than ~2px off the middle of its box, which is a typography
   defect the geometry maths cannot see.

9. **Preview alignment** - in the HTML preview, the title, deck and caption start at the figure's
   visible content edge (see [`export.md`](export.md)); the value comes from
   `render.sh <figure>.svg --inset`, not from another figure. The preview carries the same margin
   on all four sides, because `render.sh` crops to the page's ink and re-pads it.

## Reading a failed check

- `overflow: <id>` - a label is wider/taller than its node. Shorten the label, widen the node on
  the grid, or move the detail into the caption.
- `diagonal: <id>` - a connector with both dx and dy. Re-route as two axis-aligned segments with
  an 8px fillet.
- `grid: <id> <attr>` - an attribute not divisible by 4. Snap it.
- `contrast: <id>` - text on a fill below the threshold. Use `text`/`text-2` instead of `text-3`,
  or lift the fill.
- `budget: nodes` - split the figure (overview + detail) rather than shrinking type.
- `a11y: title-order` - `<title>` must be the first child of `<svg>`.
- `fonts: cjk` - the file contains CJK but the root stack has no CJK family.
- `center: <label>` - the text sits more than ~2px off the middle of its box. Move the baselines
  up/down together (a 13px name plus an 11px sublabel in a 64px box centres on `y+26`/`y+46`).
- `edge: content touches the canvas edge on the right and sits inside the 16px canvas padding (...)`
  - ink has reached (or passed) a canvas boundary, or stops within 16px of one. A node border on
  the boundary loses half its stroke, so widen the canvas, move the tick labels inward, or lift the
  footnote.
- `port: <connector> start|arrowhead (x,y) attaches to nothing: the nearest node <id> is Npx away` -
  the end floats. Snap it onto that node's border, or onto the stroke it was meant to branch from.
  An 8px offset is the usual cause, and it is the single most common way an architecture figure
  becomes ambiguous about who feeds whom.
- `port: ... lands inside node <id>` - the arrowhead overshoots the boundary. Pull it back to the
  edge; a head inside a box points at nothing.
- `port: ... lands on a corner of node <id>` (warning) - slide the tip onto the middle of one edge.
- `hidden: <connector> passes behind node <id> (Npx inside the box)` - the box paints over the line.
  Route around the box, or make it an endpoint of that connector. If the connector is drawn *after*
  the box the message reads `runs through`.
- `hidden: edge label '<text>' sits inside node <id>` - the label disappears under the box (or
  collides with the box's own text). Move it into the gap between the boxes.
- `label-cut: the mask of edge label '<text>' has an edge inside the Npx stroke of <connector>, so
  the line paints half-thick under the glyphs` - the mask's edge landed on the wire. Lift it 1px
  clear of the stroke's ink, or extend it to swallow the stroke whole.
- `label-cut: ... cuts <connector> Npx off the line's axis` - the label is cutting a stroke it is
  not centred on; the wire reads as broken and the text as detached. Centre the mask on the line
  (within 2px) or move the label beside it.
- `label-cut: ... does not cut <connector> in the middle: Npx of stroke on one side, Mpx on the
  other` - a cut has to sit mid-run (>= 8px left each side, stubs within 8px). This is the defect
  where a 128px wire keeps 48px above the gap and 60px below: the eye reads damage, not a label.
- `mask-tone: the mask of edge label '<text>' is #AABBCC over a #DDEEFF backdrop, so it paints a
  patch over the band` - the mask is opaque, so its colour is the colour of the rectangle the
  reader sees. Give it the tone of what is behind it: the canvas, or a zone band / node fill
  composited over the canvas (measure the render; do not trust the band's own fill value, its
  `opacity` still has to be applied). Light figures show this first.
- `mask: the mask of edge label '<text>' overlaps node <id> ...` - a mask drawn after a box erases
  part of that box's border. Offset the mask.
- `label: <connector> is a Npx connector with no label` - a short arrow with no label is ambiguous.
  Label it, or delete it if the reader can infer it from the boxes alone.

## What still needs eyes

- Whether the focal element is where attention lands first (the squint test).
- Whether connector lengths and whitespace create rhythm rather than a sparse or cramped field.
- Whether the label wording is the reader's vocabulary.
- Whether the figure duplicates the paragraph above it.

If you cannot do this yourself, say so and hand it to the user with the PNG. Do not write
"verified visually" when it was not.
