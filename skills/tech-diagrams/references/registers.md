# Registers: palettes, type, fonts

A register is a palette + type ramp + geometry convention. Set it on the figure root:
`<html data-register="dark">` and, for a standalone SVG, copy the matching token values into a
`<style>` block (standalone SVG must not depend on external CSS).

**Default: `technical-dark`.** Switch only when the target document demands it (a light blog
canvas, a printed proposal, a slide).

## Tokens

| Token | dark (default) | light (Vercel / Geist) | Use |
| --- | --- | --- | --- |
| canvas | `#0A0A0B` | `#FAFAFA` | figure background |
| surface | `#111214` | `#F2F2F2` | node fill |
| surface-2 | `#16181C` | `#EBEBEB` | secondary node / zone band |
| hairline | `rgba(255,255,255,.08)` | `#C9C9C9` | node borders, separators |
| hairline-strong | `rgba(255,255,255,.16)` | `#A8A8A8` | focus border, axis |
| text | `#EDEDF0` | `#171717` | labels |
| text-2 | `#9BA1A6` | `#4C4C4C` | sublabels, captions |
| text-3 | `#7C8389` | `#4C4C4C` | axis ticks, metadata |
| accent | `#5E6AD2` | `#0072F5` | 1-2 focal elements only |
| accent-soft | `#171A2B` | `#F0F7FF` | focal node fill |
| accent-text | `#A7AEF8` | `#0062D1` | accent-coloured text on canvas |
| categorical tint - fill | `#0F2420` `#221C2A` `#2A1C12` | `#EEFCF9` `#F9F0FF` `#FFF6E5` | card fill, 2-4 parallel items |
| categorical tint - stroke | `#53CFBC` `#C9A4F2` `#F3A26A` | `#0D8C7D` `#8E4EC6` `#A35200` | border, its connector, its marker |
| ok / warn / err | `#3FB950` / `#D29922` / `#F85149` | `#297A3A` / `#A35200` / `#CB2A2F` | state only, never decoration |
| grid | 4px | 4px | all origins, sizes, gaps |
| radius | 8px (max) | 6px (max) | nodes: dark 6-8px, light 4-6px |

The light register is Vercel's Geist system. The values are measured from the system's own published
tokens (`vercel.com/geist/colors`: every scale ships ten steps, `gray-100` … `gray-1000`); the
mapping onto figure roles is ours. Three deliberate departures, each one measured:

- **Canvas = `#FAFAFA`, Geist `background-200`,** not `background-100` (`#FFFFFF`): the brief for
  this register is no pure white, and Background 2 is the system's own "subtle differentiation"
  surface.
- **Hairline = `gray-500` `#C9C9C9`,** not the UI-default `gray-400` (`#EBEBEB`, 1.06:1 on this
  canvas): a UI card can lean on a shadow to read as elevated, a shadowless figure cannot, so its
  border has to be visible.
- **Two text steps, not three.** Geist's `gray-800` `#7D7D7D` measures 3.9:1 on this canvas, under
  AA at our 11px floor, so `text-2` and `text-3` both resolve to `gray-900`; the third tier is
  carried by size, weight, and case instead of by tone.
- Ink is `gray-1000` `#171717`. Nothing in the register is `#000000` or `#FFFFFF`; the canvas is
  75% of the light example's pixels, and its only saturated colours are the focal card and one
  connector.

**Where the colour goes.** Colour is a property of a component, never of the field. Two layers, in
priority order:

- **Accent: attention.** The focal node (accent-soft fill + accent border), one accent connector, a
  state dot or state label (`ok` / `warn` / `err`, each paired with the Geist 100 step as its fill -
  `#EFFBEF`, `#FFF6E5`, `#FFF0F0`), and the traffic lights of a window frame. At most two focal
  elements; if the accent covers much more than a few percent of the canvas the figure is
  decorating, not arguing.
- **Categorical tint: identity.** When the figure's argument *is* a comparison between two to four
  parallel items - paths, lanes, options, strategies - each item may own a hue: fill with the hue's
  100 step, stroke the item and its connector with the lightest step that still clears 3:1 against
  the canvas (measured: teal-800 `#0D8C7D` 3.97:1, purple-700 `#8E4EC6` 4.96:1, amber-900
  `#A35200` 5.34:1 - amber-700 `#FFB224` is 1.73:1 and unusable at 1px). Grey means "shared by all
  items". The light register fills with an opaque 100 step. The dark register resolves the same three
  hues at Oklch(0.78, 80% of the hue's peak chroma) - `#53CFBC` / `#C9A4F2` / `#F3A26A`, 9.5-10.4:1
  on the canvas - and fills at Oklch(0.24, 0.028, H): `#0F2420` / `#221C2A` / `#2A1C12`, about 0.06 L
  above the zone band, which keeps body text at 14:1 and sublabels at 6.3:1. Tint fills are opaque in
  both registers, never alpha, so label masks and the contrast checks stay exact; neither register
  tints the field itself.

The layers do not stack. Once tints are in play the accent narrows to the landing point the items
share, or leaves. Measured on the SES overview (1680x1648), light and dark: three tints at 5.9-6.7%
of the canvas each, the shared landing cards at 5.0-5.4%, and half the canvas still neutral - non-grey
pixels rise from 6.0% to 26.1% (light) and 5.4% to 29.6% (dark), of which 0.9% / 0.6% is high-chroma
ink. Ordinary nodes, zone bands, hairlines and wires stay grey either way.

**White-ground variant.** For a figure that lands on a white blog page rather than inside a UI,
invert the two light greys: canvas `background-100` `#FFFFFF`, zone bands `background-200` `#FAFAFA`,
uncoloured cards white. Keep the dark register's two-part pattern - pale fill plus vivid border - so a
coloured card keeps the 100 step of its own scale (`#EEFCF9` / `#F9F0FF` / `#FFF6E5`) under the vivid
stroke. On white every stroke gains contrast (teal 3.97 -> 4.15:1, purple 4.96 -> 5.18:1, amber
5.34 -> 5.58:1, blue 4.26 -> 4.44:1) and so does text (ink 17.2 -> 17.9:1, text-2 8.2 -> 8.6:1),
while the tinted area stays where it was (26.1% of pixels non-grey, the three paths at ~6% each). A
stroke-only variant - white fills, colour on borders and connectors alone - measures 6.7% non-grey,
which is readable up close but loses the coding at a distance, so reserve it for a figure whose
colour is carried by one or two marks.

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
  closer match for the light register, but it is a webfont on most machines: do not put a family
  first that the rasteriser cannot resolve.
- Sans and mono only. Geist ships no serif, so the light register drops the serif allowance; a
  serif title belongs to a bespoke editorial palette, not to a shipped register.

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
