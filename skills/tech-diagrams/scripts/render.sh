#!/usr/bin/env bash
# Rasterise a figure. SVG -> PNG via rsvg-convert; HTML -> PNG via headless Chrome.
#
#   ./scripts/render.sh figures/shard-lookup.svg --scale 2
#   ./scripts/render.sh figures/shard-lookup.html --width 1100 --height 480
#   ./scripts/render.sh figures/shard-lookup.svg --inset      # measure the canvas margins
#
# Notes
#  - The SVG path is exact (viewBox drives the pixels). The HTML path is a preview screenshot:
#    Chrome captures the viewport, so it overshoots the height, then crops to the page's ink and
#    re-pads with a uniform 40px margin. Pass --height to pin the window, --no-pad for the raw
#    screenshot.
#  - --inset renders at 1x and reports where the drawn content starts, which is the value the
#    HTML preview's --td-figure-inset must carry (see references/export.md).
#  - curl is unreliable in some sandboxes; this script never touches the network.
set -euo pipefail

usage() {
  sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'
  exit 2
}

[ $# -ge 1 ] || usage
case "$1" in -h|--help) usage ;; esac
INPUT="$1"; shift
SCALE=2
WIDTH=""
HEIGHT=""
OUT=""
NOPAD=""
INSET=""
while [ $# -gt 0 ]; do
  case "$1" in
    --scale) SCALE="$2"; shift 2 ;;
    --width) WIDTH="$2"; shift 2 ;;
    --height) HEIGHT="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    --no-pad) NOPAD=1; shift ;;
    --inset) INSET=1; shift ;;
    -h|--help) usage ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

[ -f "$INPUT" ] || { echo "no such file: $INPUT" >&2; exit 2; }
EXT="${INPUT##*.}"
BASE="${INPUT%.*}"
# An .html preview and its .svg source share a base name, so the page screenshot gets its own
# suffix; the bare .png always means "the figure itself".
if [ -z "$OUT" ]; then
  case "$EXT" in
    html|htm) OUT="${BASE}.page.png" ;;
    *)        OUT="${BASE}.png" ;;
  esac
fi

have() { command -v "$1" >/dev/null 2>&1; }

case "$EXT" in
  svg)
    have rsvg-convert || { echo "rsvg-convert not found (brew install librsvg)" >&2; exit 3; }
    rsvg-convert -z "$SCALE" -o "$OUT" "$INPUT"
    ;;
  html|htm)
    CHROME=""
    for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
             "$(command -v google-chrome || true)" "$(command -v chromium || true)" \
             "$(command -v chromium-browser || true)"; do
      [ -n "$c" ] && [ -x "$c" ] && CHROME="$c" && break
    done
    [ -n "$CHROME" ] || { echo "Chrome/Chromium not found for HTML rendering" >&2; exit 3; }

    if [ -z "$WIDTH" ] || [ -z "$HEIGHT" ]; then
      read -r SW SH <<EOF
$(python3 - "$INPUT" <<'PY'
import re, sys
html = open(sys.argv[1], encoding="utf-8").read()
m = re.search(r"<svg\b[^>]*>", html, re.S)
if not m:
    print("1100 620"); raise SystemExit
tag = m.group(0)
def attr(name):
    mm = re.search(rf'{name}\s*=\s*"([^"]+)"', tag)
    return mm.group(1) if mm else ""
w = attr("width"); h = attr("height")
vb = attr("viewBox").split()
if (not w or not h) and len(vb) == 4:
    w, h = vb[2], vb[3]
def num(v):
    try: return float(re.sub(r"[^0-9.]", "", v) or 0)
    except ValueError: return 0.0
print(int(num(w) or 1100), int(num(h) or 480))
PY
)
EOF
      # page padding (24 sides) + title/deck above + caption below, plus slack: Chrome captures
      # the viewport rather than the page, so overshoot and crop back below instead of clipping.
      [ -n "$WIDTH" ]  || WIDTH=$(( SW + 48 ))
      [ -n "$HEIGHT" ] || HEIGHT=$(( SH + 560 ))
    fi
    "$CHROME" --headless --disable-gpu --hide-scrollbars --force-device-scale-factor="$SCALE" \
      --window-size="${WIDTH},${HEIGHT}" --screenshot="$OUT" "file://$(cd "$(dirname "$INPUT")" && pwd)/$(basename "$INPUT")" 2>/dev/null

    # Crop the overshoot back to the page's actual ink and re-pad it uniformly, so a preview has a
    # deterministic 40px margin instead of whatever slack the window estimate happened to leave.
    # Trim by the page's own corner colour with a tight fuzz and do not touch the pixels in between:
    # a wide fuzz (8%) made every fill within ~20/255 of the canvas "background", which silently
    # erased a light register's card fills (#F2F2F2 on #FAFAFA) from the artifact.
    if [ -z "$NOPAD" ] && have magick; then
      PBG=$(magick "$OUT" -colorspace sRGB -depth 8 -format '%c' histogram:info:- \
            | awk '{c=$1+0; if (c>m) {m=c; line=$0}} END {match(line, /#[0-9A-Fa-f]{6}/); print substr(line, RSTART, RLENGTH)}')
      magick "$OUT" -fuzz 1% -trim +repage -bordercolor "$PBG" -border "$((40 * SCALE))" -alpha off "$OUT"
    fi
    ;;
  *)
    echo "unsupported extension: .$EXT (use .svg or .html)" >&2; exit 2 ;;
esac

[ -s "$OUT" ] || { echo "render produced no output: $OUT" >&2; exit 4; }

# --inset: measure where the figure's drawn content actually starts, so the HTML preview's
# title/deck/caption can share that inset instead of guessing a percentage that silently
# misaligns the page. Prints the four margins in figure pixels and as a share of the canvas.
if [ -n "$INSET" ]; then
  have magick || { echo "--inset needs ImageMagick" >&2; exit 3; }
  have rsvg-convert || { echo "rsvg-convert not found (brew install librsvg)" >&2; exit 3; }
  SRC="$INPUT"
  if [ "$EXT" = html ] || [ "$EXT" = htm ]; then
    SRC="$(mktemp -t td-inset).svg"
    python3 - "$INPUT" "$SRC" <<'PY'
import re, sys
html = open(sys.argv[1], encoding="utf-8").read()
m = re.search(r"<svg\b.*?</svg>", html, re.S)
if not m:
    raise SystemExit("no inline <svg> in the HTML preview")
open(sys.argv[2], "w", encoding="utf-8").write(m.group(0))
PY
  fi
  TMP="$(mktemp -t td-inset).png"
  rsvg-convert -z 1 -o "$TMP" "$SRC"
  read -r FW FH <<EOF
$(python3 - "$SRC" <<'PY'
import re, sys
tag = re.search(r"<svg\b[^>]*>", open(sys.argv[1], encoding="utf-8").read(), re.S).group(0)
def attr(name):
    m = re.search(rf'{name}\s*=\s*"([^"]+)"', tag)
    return m.group(1) if m else ""
def num(v):
    try: return float(re.sub(r"[^0-9.]", "", v) or 0)
    except ValueError: return 0.0
vb = attr("viewBox").split()
w = num(attr("width")) or (num(vb[2]) if len(vb) == 4 else 1100)
h = num(attr("height")) or (num(vb[3]) if len(vb) == 4 else 480)
print(int(w), int(h))
PY
)
EOF
  IBG=$(magick "$TMP" -colorspace sRGB -depth 8 -format '%c' histogram:info:- \
        | awk '{c=$1+0; if (c>m) {m=c; line=$0}} END {match(line, /#[0-9A-Fa-f]{6}/); print substr(line, RSTART, RLENGTH)}')
  read -r IX IY IW IH <<EOF
$(magick "$TMP" -fuzz 8% -transparent "$IBG" -trim -format '%X %Y %w %h' info:)
EOF
  python3 - "$IX" "$IY" "$IW" "$IH" "$FW" "$FH" <<'PY'
import sys
x, y, w, h, fw, fh = (float(v) for v in sys.argv[1:7])
for side, gap, total in (("left", x, fw), ("right", fw - x - w, fw), ("top", y, fh), ("bottom", fh - y - h, fh)):
    print(f"{side:6s} {gap:6.1f}px  {gap / total * 100:5.2f}%")
print(f"preview CSS: --td-figure-inset: {x / fw * 100:.1f}%;")
PY
  rm -f "$TMP"
  [ "$SRC" != "$INPUT" ] && rm -f "$SRC"
  exit 0
fi

# report size + how much of the canvas was actually drawn on, so the caller can spot a blank
# or over-crowded render. Content is measured against the image's dominant colour, so a
# dark-register figure is not misread as ~94% ink. The 8% fuzz is deliberately wide here: it
# counts salient ink (text, borders, saturated fills) and treats near-canvas fills as background,
# so the number stays comparable between registers instead of jumping when a card tint is added.
if have magick; then
  magick identify -format '%f %wx%h\n' "$OUT"
  BG=$(magick "$OUT" -colorspace sRGB -depth 8 -format '%c' histogram:info:- \
       | awk '{c=$1+0; if (c>m) {m=c; line=$0}} END {match(line, /#[0-9A-Fa-f]{6}/); print substr(line, RSTART, RLENGTH)}')
  CONTENT=$(magick "$OUT" -fuzz 8% -transparent "$BG" -alpha extract -format '%[fx:mean]' info:)
  awk -v bg="$BG" -v c="$CONTENT" 'BEGIN {printf "background=%s content=%.2f%%\n", bg, c * 100}'
elif have sips; then
  sips -g pixelWidth -g pixelHeight "$OUT" 2>/dev/null | tail -2
fi
echo "wrote $OUT"
