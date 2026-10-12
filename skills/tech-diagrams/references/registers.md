# Registers: palettes, type, fonts

A register is a palette + type ramp + geometry convention. Set it on the figure root:
`<html data-register="dark">` and, for a standalone SVG, copy the matching token values into a
`<style>` block (standalone SVG must not depend on external CSS).

**Default: `technical-dark`.** Switch only when the target document demands it (a light blog
canvas, a printed proposal, a slide).

## Tokens

| Token | dark (default) | light | Use |
| --- | --- | --- | --- |
| canvas | `#0A0A0B` | `#F8FAFC` | figure background |
| surface | `#111214` | `#FFFFFF` | component fill |
| surface-2 | `#16181C` | `#F1F5F9` | neutral band, secondary fill |
| hairline | `rgba(255,255,255,.08)` | `#CAD5E2` | component borders, separators |
| hairline-strong | `rgba(255,255,255,.16)` | `#90A1B9` | focus border, axis |
| text | `#EDEDF0` | `#0F172B` | labels |
| text-2 | `#9BA1A6` | `#45556C` | sublabels, captions |
| text-3 | `#7C8389` | `#62748E` | axis ticks, metadata |
| accent | `#5E6AD2` | `#155DFC` | 1-2 focal elements only |
| accent-soft | `#171A2B` | `#EFF6FF` | focal component fill |
| accent-text | `#A7AEF8` | `#193CB8` | accent-coloured text |
| tint fill | `#0F2420` `#221C2A` `#2A1C12` | `#CBFBF1` `#EDE9FE` `#FEF3C6` | zone band, lane, tinted component |
| tint hairline | the register hairline `rgba(255,255,255,.08)` | `#46ECD5` `#C4B4FF` `#FFD230` | outline of a component on that band |
| tint line | `#53CFBC` `#C9A4F2` `#F3A26A` | `#00786F` `#7008E7` `#BB4D00` | wire, bar, marker that carries the tint |
| tint text | same as tint line | `#0B4F4A` `#4D179A` `#7B3306` | label on the band |
| ok / warn / err | `#3FB950` / `#D29922` / `#F85149` | `#008236` / `#BB4D00` / `#C10007` | state only, never decoration |
| grid | 4px | 4px | all origins, sizes, gaps |
| radius | 8px (max) | 6px (max) | components: dark 6-8px, light 4-6px |

The light register is built on Tailwind v4's ramps (`theme.css` ships every scale as `oklch()`,
hue held constant end to end and stepped finer at the light end - the two properties a tint needs
to sit under a label). The values are the ramps' own published steps; the mapping onto figure
roles is ours, and every pair is measured. Three deliberate choices:

- **The canvas is `slate-50` `#F8FAFC`, not white.** The field carries the accent's hue family at
  chroma 0.003 - enough to sit under a tint without reading as grey, which is what the register
  this replaced did wrong. Components are `#FFFFFF`, so a card is the lightest thing on the page
  and reads as raised without a shadow.
- **Hairline = `slate-300` `#CAD5E2`,** not the UI-default `slate-200` (`#E2E8F0`, 1.18:1 on this
  canvas): a UI card can lean on a shadow to read as elevated, a shadowless figure cannot, so its
  border has to be visible.
- **Three text steps.** `slate-500` `#62748E` measures 4.55:1 on the canvas and 4.76:1 on white, so
  `text-3` is usable for ticks and metadata. It drops under AA on a `slate-100` band, so metadata
  on a band takes `text-2`.

## Colour has three jobs

A figure uses only the jobs its argument needs. They may stack: the identity layer says *where
things are*, the accent says *where the change is* - different questions, different marks.

- **Accent - attention.** The focal component (accent-soft fill + accent border), one accent
  connector, and the traffic lights of a window frame. At most two focal elements; if the accent
  covers much more than a few percent of the canvas the figure is decorating, not arguing.
- **Identity tint - which thing this is.** A hue marks a set of parallel items: the zones of an
  architecture, the lanes of a swimlane, the actors of a sequence, the series of a chart, the
  options of a quadrant. One to three items take hues, assigned in reading order - 1 teal, 2
  violet, 3 amber - except that the scope holding the focal element takes teal, because violet is
  the tint nearest the accent's hue and would compete with it. One tint is enough when the figure
  is about a single scope inside a larger system (the EDGE band in the light template); anything
  shared or unassigned stays neutral. The hue appears as a **fill** (a zone band, a lane, or a
  tinted component), a **hairline** on the components that sit on that fill, a **line** on the
  wires, bars and markers that carry it, and **text** on labels inside it. In the light register
  the band is the tinted area and the components on it are white: white on a tint is 1.1-1.2:1, so
  it is the outline that separates a card from its band. The dark register resolves the same layer
  the other way round - the tinted area is *lighter* than the components on it, so its components
  separate by fill and its tint hairline is the register hairline.
- **State - ok / warn / err.** A dot, a glyph, a label, always paired with a mark or a word, never
  colour alone. Status hues sit well away from the accent in OKLCH: green 149, red 29, the amber
  family 45-95, against the accent's 263. `warn` and the third identity tint are the *same* value
  (`#BB4D00`, over the same `#FEF3C6` fill) - one hue cannot carry two meanings at once, so a
  figure that shows both a warning and an amber-tinted scope carries the warning with a glyph.

A tint is a second carrier, never the only one: the band and its label already say the scope, and
the tint lets the reader scan the figure without reading it. Tint the scopes the argument
distinguishes; a band that groups nothing the figure argues about stays neutral.

Everything else - text, hairlines, wires, ungrouped components, the neutral band - stays neutral.
Fills are always pale; saturation belongs to the accent, to tint lines, and to state marks. More
than three parallel items is a split or a table, not more hues.

**When the tints are the argument** (parallel options, chart series) rather than the scope, the
accent narrows to the point they all land on, or leaves - a fourth hue makes the reader count
instead of look.

## Register notes

**Dark (default).** `#0A0A0B` field, `#111214` components, one indigo accent. The identity layer
is resolved at Oklch(0.78, 80% of the hue's peak chroma) for the line step - `#53CFBC` /
`#C9A4F2` / `#F3A26A`, 9.5-10.4:1 on the canvas, so the same value carries text - and at
Oklch(0.24, 0.028, H) for the fill: `#0F2420` / `#221C2A` / `#2A1C12`, about 0.06 L above the
zone band, which keeps body text at 14:1 and sublabels at 6.2-6.3:1. Tint fills are opaque, never
alpha, so label masks and the contrast checks stay exact.

**Light.** Three hues at four steps each, all Tailwind v4 values: fill 100, hairline 300, line
700, text 900. Measured: line 5.1:1 / 7.0:1 / 4.8:1 on the canvas (4.5-6.2:1 on its own band),
text 8.3:1 / 9.3:1 / 8.1:1 on its own fill, hairline 1.31:1 / 1.56:1 / 1.30:1 on its band - an
outline, not a mark. A hue-coded figure keeps its text, wires and ungrouped components neutral, so
the tints read as scope rather than as a second argument.

**White-ground variant.** For a figure that lands on a white blog page rather than inside a UI:
canvas `#FFFFFF`, neutral bands `slate-50` `#F8FAFC`, components white. The tint bands are already
pale enough to stay as they are. On white every stroke gains contrast (tint lines 5.4:1 / 7.3:1 /
5.0:1, accent 5.3:1) and so does text (ink 17.8:1, text-2 7.6:1). A stroke-only variant - white
fills, colour on borders and connectors alone - is readable up close but loses the coding at a
distance, so reserve it for a figure whose colour is carried by one or two marks.

Geometry conventions: 1px hairlines (1.5px only for an emphasised connector), no shadows, no
gradients, no glow. Emphasise with border colour and weight, never with blur or light.

## Type ramp

| Role | Size | Weight | Family |
| --- | --- | --- | --- |
| Figure title | 20 | 600 | sans |
| Section / zone label | 12 | 600 | mono, uppercase, letter-spacing .08em |
| Node name | 13 | 500 | sans |
| Node sublabel | 11 | 400 | mono (identifiers) or sans (prose fragments) |
| Edge label | 11 | 400 | sans, on an opaque mask |
| Axis / tick / value | 11 | 400 | sans, tabular numerals for values |
| Caption | 12 | 400 | sans, `text-2` colour |

Never go below 11px. Mono appears only for identifiers, commands, keys, ports, and numeric
values - never as a blanket "developer" font.

## Font stacks (verbatim)

```css
--td-font-sans: Inter, "Helvetica Neue", -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
--td-font-mono: Menlo, "SF Mono", SFMono-Regular, Consolas, "Liberation Mono", monospace;
--td-font-cjk:  "PingFang SC", "Hiragino Sans", "Heiti SC", "Noto Sans CJK SC", sans-serif;
```

Rules:

- Any figure containing CJK text must end its sans stack with the CJK stack, because the
  rasteriser (rsvg) resolves fonts through fontconfig and *will not* substitute PingFang on
  every machine. Concretely: `font-family="Inter, PingFang SC, Hiragino Sans, Heiti SC, Noto Sans
  CJK SC, sans-serif"`.
- Never rely on a webfont for a rasterised export. Use stacks (offline-safe); only add a
  `https://fonts.googleapis.com` link in the HTML preview, and never in the `.svg`.
- Inter is the house sans because it matches the Linear register and is broadly available; when
  it is missing, `Helvetica Neue` and `system-ui` keep the figure legible. Geist Sans would be the
  closer match for a Vercel-flavoured light register, but it is a webfont on most machines: do not
  put a family first that the rasteriser cannot resolve.
- Sans and mono only. A serif title belongs to a bespoke editorial palette, not to a shipped
  register.

## Switching register

1. Copy `assets/template-light.html` instead of the dark template.
2. Replace the token block (or swap `data-register`), keep every geometry rule unchanged.
3. Re-run `scripts/self_check.py`: contrast is measured per register, and the mask tone is
   composited from whatever the label sits on, so a palette swap that leaves either behind is
   reported (`contrast`, `mask-tone`).
4. Ship the pair when the target supports both themes: `<slug>-dark.svg` and `<slug>-light.svg`,
   with the caption written once and reused verbatim (caption == alt in both).

## Product/window frames

For figures that show a terminal, IDE, or browser surface, keep the register palette and add the
frame chrome described in [`type-ui.md`](type-ui.md). Frames are stylised, never copies of a real
product's screenshot.
