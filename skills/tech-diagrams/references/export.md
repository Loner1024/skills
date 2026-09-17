# Export and delivery

## Default deliverables

1. `<slug>.html` - self-contained preview (inline `<style>` + inline `<svg>`; no external
   requests). This is the artifact to open in a browser and to hand to a designer.
2. `<slug>.svg` - standalone deliverable. Requirements:
   - explicit `width`, `height`, and `viewBox` on the root `<svg>`;
   - a `<style>` block with the token values inlined (never an external stylesheet);
   - font stacks inlined as attributes on the root (no webfonts);
   - `<title>` first, `<desc>` second, `role="img"`, `aria-labelledby`;
   - no `<script>`, no external `<image>`, no `filter` effects.

## Optional exports (only when asked)

| Need | Export | How |
| --- | --- | --- |
| Slides, chat, print, WeChat-style platforms | PNG at 2x | `./scripts/render.sh f.svg --scale 2` |
| Light/dark pair for a themed site | `<slug>-dark.svg` + `<slug>-light.svg` | author once, swap the token block, lint both |
| Fixed frame (social card, slide) | PNG with exact pixel size | set the canvas to the target size first, then render at 1x |
| Inline in Markdown | the `.svg` plus a `![caption](slug.svg)` line | caption text is the alt; link the editable `.html` next to it |

Do not produce export files unprompted; three artifacts per figure is the ceiling
(`.html`, `.svg`, and one PNG on request).

Naming: `<slug>.png` is always the figure itself (rendered from the `.svg`). The screenshot of the
HTML preview is written next to it as `<slug>.page.png`, so the two never overwrite each other.

## Page layout in the HTML preview

The figure's visible content sits inside its canvas (the worked figure here insets it by 105px of a
1100px canvas), so the preview's title, deck and caption share that inset: they align with the
figure's **content edge**, not with the invisible canvas box. Both templates carry it as
`--td-figure-inset`, a percentage of the figure width so it scales with the figure. Set it to `0`
when the content runs edge to edge.

**Measure it, never copy it from another figure.** A preview that inherits another figure's
percentage puts the title a whole gutter away from the diagram (a 2.9% figure wearing 8.4% is
60px out). Run:

```bash
./scripts/render.sh figures/shard-lookup.svg --inset     # prints all four margins in px and %
```

and paste the `--td-figure-inset:` line it prints. The printed percentage is scale-invariant: the
figure and its inset both scale with the container. To check the result, render the page and
compare the leftmost ink of the title with the leftmost ink of the figure (they should land on the
same x, within the glyph's side bearing).

Text measures: the deck and the caption keep a prose measure (`max-width: 68ch`), not the figure
width. A 1100px caption line is ~95 characters, which is past the readable range; a caption is
prose and follows the prose measure even when the figure is wider.

## Embedding pattern
```markdown
![A request checks the edge cache, misses, and fetches one bounded 200 KB shard whose index is binary-searched.](figures/shard-lookup.svg)

*Rendered source: [`shard-lookup.html`](figures/shard-lookup.html)*
```

- Caption line under the image repeats the alt, or carries the takeaway if the alt already states
  it. Never both a redundant caption and a redundant alt that say different things.
- Keep the editable source next to the export (this repo's convention, borrowed from the
  droid-control plugin: `.excalidraw` source plus exported `.svg`).
- For a numbered technical post, prefix captions `Figure 01 ·` and keep the numbers in document
  order (not in the order you happened to author them).

## Size presets

| Preset | viewBox | Notes |
| --- | --- | --- |
| `doc-inline` | `0 0 720 360` | sits in a paragraph column; test at 640px wide |
| `doc-wide` | `0 0 1100 480` | default for architecture and lifecycle |
| `banner` | `0 0 1200 500` | hero figure under a heading |
| `tall` | `0 0 760 900` | deep pipelines, nested layers |
| `slide-16x9` | `0 0 1280 720` | render at 1x for slides |
| `square` | `0 0 1080 1080` | social; keep the same rules, more padding |

Rule of thumb: the text in the final artifact must stay readable at 50% scale. If it does not,
the figure is carrying too much: split it, or move detail into the caption.

## Verification pairing

Export without verifying is not delivery. After every export run:

```bash
python3 scripts/self_check.py figures/<slug>.svg
./scripts/render.sh figures/<slug>.svg --scale 2
```

Then hand the PNG over for the visual check (see [`verification.md`](verification.md)).
