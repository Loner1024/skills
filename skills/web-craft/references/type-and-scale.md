# Type and scale

Floors, not directions. A module owns the job and its craft; these numbers hold underneath every
route, and the module's own rule wins where the two disagree. Measure the built result, not the
intent.

## Contrast

| Text | Floor |
| --- | --- |
| Body, labels, placeholder, table text | 4.5:1 |
| 24px and up, or 18.66px bold and up | 3:1 |
| Icons, control borders, focus rings | 3:1 |

Placeholder text is text: the grey that looks right in a mockup is usually around 2:1. On a tinted
band, a colored card, or a photo, measure against the composite the glyphs actually sit on, not the
page background. Secondary copy takes a further step of the surface's own hue; grey ink on color
reads washed out.

## Sizes

| Surface | Body | Floor |
| --- | --- | --- |
| Screen | 16px | 14px in dense UI, 12px for meta and labels, 11px for functional text |
| Slide at 1920×1080 | 24px | 24px is a projection floor, not a target; titles and numbers run much larger |
| Print | 12pt | 10pt only for legal lines and footnotes |

Touch targets are 44×44 CSS px on touch (WCAG 2.5.5 AAA, Apple's 44pt). 24×24 is the WCAG 2.2 AA
floor; take it only for a control that is not the primary action.

Body measure is 65–75 characters per line. Under 45 the line breaks too often, over 90 the eye
loses the return.

## Fixed size versus fluid

A fixed-format surface — slide, print page, device frame, exported image — keeps its pixel
dimensions and scales as one piece. Everything else reflows: `max-width` on the container,
`minmax(0, 1fr)` tracks, and no fixed height or `nowrap` on a text container.

## CJK

- **Latin first in the stack, CJK after it.** `-apple-system, "SF Pro Text", "PingFang SC",
  "Noto Sans SC", sans-serif` gives each script its native glyphs; a CJK-first stack sets Latin in
  letterforms drawn for Hanzi.
- **More leading.** Hanzi carry more ink per em: 1.7–1.8 for reading text and 1.5 for dense UI,
  against 1.4–1.6 for Latin.
- **Half the character count.** A hanzi is roughly twice the width of a Latin character, so the
  65–75-character Latin measure is 32–38 hanzi. Set the column by width, not by counting characters.
- **Tag the language on the element, not only the document.** `lang="zh-CN"` / `lang="en"` decides
  font choice, line breaking, and quotation marks; reach for `:lang(zh)` when an override differs
  by script.
- **A Latin serif needs a CJK serif beside it.** Most reading serifs ship no Hanzi and the fallback
  to a sans is silent: `"Newsreader", "Songti SC", "Noto Serif SC", serif`.
- **No synthetic italic.** Browsers slant Hanzi into a shape no type designer drew; emphasize with
  weight, color, or a mark instead of `font-style: italic`.
- **Break by the script's rules.** `line-break: strict` for prose, and keep `word-break: normal` so
  Latin words inside Chinese text stay whole.
