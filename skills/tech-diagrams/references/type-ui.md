# Type: window frame (an overlay, not a content family)

Covers figures that show something **inside a terminal, IDE, or browser surface** - the move
Linear and Cursor use most. Frames are stylised chrome; they are never copies of a real product's
screenshot, and they must never contain a real product's artwork, logo, or fabricated data.

A frame is applied **on top of** a figure from any of the four content families (structure,
sequence, data, narrative): it changes the chrome, not the grammar. So the taxonomy counts 13
content types in those four families plus this one overlay, 14 rows in all.

## When a frame is right

- The figure is about what a user sees or types (`droid exec`, a config file, a diff, a CLI
  prompt).
- The alternative - a box labelled "CLI" - would hide the syntax that the reader needs.
- Do **not** use a frame to decorate an architecture figure, and do not frame a diagram in a
  fake browser just to add realism.

## Frame grammar

- Window: 1px hairline rounded rect, radius 8px, `surface` fill. Chrome bar 28-32px tall,
  separated by a hairline (no heavy titlebar, no gradient).
- Traffic lights (macOS register): three 10px circles at 8px pitch, in `#F85149`-tinted,
  `#D29922`-tinted, `#3FB950`-tinted colours **at 40-60% opacity** so they never become the
  loudest thing in the figure. Skip them entirely if the register is `blueprint`.
- Title: 11px mono, `text-2`, centred or left after the lights (`droid — zsh`).
- Terminal body: 12px mono, line height 18px, padding 16px. Prompt lines start with `$` in
  `text-3`; the command itself in `text`; output in `text-2`.
- Success/error marks: a 6px dot or a 1px glyph in `ok`/`err`. Never emoji.
- IDE frame: add a left rail (48px, `surface-2`) with 3-4 mono file labels, and a tab strip of
  equal-width tabs where the active tab is `surface` and the others are `canvas`.
- Browser frame: chrome 36px with a pill-shaped URL field (radius 999px is allowed **here only**,
  because it is real UI chrome) showing a mono URL. No bookmarks bar, no extensions.
- Long output: fade the last line with a `canvas`-coloured rect at 0-40% opacity, or truncate with
  `…`; never let text touch the frame edge.

## Fidelity rules

- Show only the lines that carry the point; a wall of output teaches nothing.
- Real commands, real flags, real exit codes if the user supplied them. If not supplied, use
  obviously generic placeholders (`/srv/app`, `pnpm test`) - never invent a product's output.
- Keep the frame's canvas width fixed across a figure family so a document shows one window size.

## Worked example: terminal frame

```xml
<svg role="img" aria-labelledby="term-title term-desc" viewBox="0 0 720 260" width="720" height="260"
     xmlns="http://www.w3.org/2000/svg"
     font-family="Inter, PingFang SC, Hiragino Sans, Heiti SC, Noto Sans CJK SC, sans-serif">
  <title id="term-title">Rendering a figure from the command line</title>
  <desc id="term-desc">A terminal session runs the render script, which writes a 2200x640 PNG and reports the background colour and content coverage, then lints the source.</desc>
  <rect width="720" height="260" fill="#0A0A0B"/>
  <g class="frame">
    <rect x="24" y="24" width="672" height="212" rx="8" fill="#111214" stroke="rgba(255,255,255,.08)"/>
    <line x1="24" y1="56" x2="696" y2="56" stroke="rgba(255,255,255,.08)"/>
    <circle cx="44" cy="40" r="5" fill="#F85149" opacity=".5"/>
    <circle cx="60" cy="40" r="5" fill="#D29922" opacity=".5"/>
    <circle cx="76" cy="40" r="5" fill="#3FB950" opacity=".5"/>
    <text x="360" y="44" fill="#9BA1A6" font-size="11" text-anchor="middle"
          font-family="Menlo, SF Mono, monospace">shard-lookup — zsh</text>
  </g>
  <g font-family="Menlo, SF Mono, monospace" font-size="12">
    <text x="44" y="84" fill="#7C8389">$ <tspan fill="#EDEDF0">./scripts/render.sh figures/shard-lookup.svg --scale 2</tspan></text>
    <text x="44" y="106" fill="#9BA1A6">svg  1100x320  ->  png  2200x640</text>
    <text x="44" y="128" fill="#9BA1A6">wrote figures/shard-lookup.png (41 KB)</text>
    <text x="44" y="154" fill="#7C8389">$ <tspan fill="#EDEDF0">python3 scripts/self_check.py figures/shard-lookup.svg</tspan></text>
    <text x="44" y="176" fill="#9BA1A6">OK  9 nodes · 3 edges · a11y ok · budget ok</text>
    <text x="44" y="206" fill="#7C8389">$</text>
    <rect x="56" y="196" width="8" height="16" fill="#EDEDF0" opacity=".8"/>
  </g>
</svg>
```

Caption / alt: "A terminal session rasterises the figure at 2x and lints it; the script reports
the output dimensions and the check summary."

## Mistakes to avoid

- Fabricating a real product's UI, logo, or output.
- Frames inside frames (an IDE frame inside a browser frame).
- Decorative chrome louder than the content (bright traffic lights, gradients, drop shadows).
- Text running to the frame edge or clipped by the viewBox.
