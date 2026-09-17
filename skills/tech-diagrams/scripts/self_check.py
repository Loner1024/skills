#!/usr/bin/env python3
"""Lint a tech-diagrams figure (standalone .svg or the inline <svg> inside .html).

Checks the rules that can be checked mechanically, so the human eye only has to judge taste:
structure and a11y, node/edge budget, grid alignment, diagonal connectors, connector ports and
routing, edge-label masks (how they meet their stroke, and whether their tone matches the backdrop),
estimated text overflow, canvas clipping, contrast, decoration bans, accent discipline, CJK font
fallback, and (optionally) that the rendered PNG is not blank.

    python3 scripts/self_check.py figures/shard-lookup.svg
    python3 scripts/self_check.py figures/shard-lookup.html --strict --json
    python3 scripts/self_check.py figures/shard-lookup.svg --png figures/shard-lookup.png

Exit codes: 0 clean, 1 errors (or warnings with --strict), 2 unreadable/unparseable.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import signal
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

CJK_RE = re.compile(r"[\u2e80-\u9fff\uf900-\ufaff\uff00-\uffef\u3000-\u303f]")
CJK_FAMILIES = ("pingfang", "hiragino", "heiti", "noto sans cjk", "noto sans sc", "source han", "songti")
GRID = 4
NODE_BUDGET = 9
FOCAL_BUDGET = 2
MIN_FONT = 11
MAX_RADIUS = 8
MAX_STROKE = 1.5
TITLE_MAX = 70


@dataclass
class Finding:
    severity: str  # error | warning | info (info never affects the exit code)
    code: str
    message: str


@dataclass
class Stats:
    nodes: int = 0
    edges: int = 0
    focal: int = 0
    texts: int = 0
    max_depth: int = 0
    fonts: list[str] = field(default_factory=list)


def strip_ns(tag: str) -> str:
    return tag.split("}", 1)[1] if "}" in tag else tag


def num(value: str | None, default: float = 0.0) -> float:
    if not value:
        return default
    m = re.search(r"-?\d+(?:\.\d+)?", value)
    return float(m.group(0)) if m else default


def frac(value: str | None, default: float = 1.0) -> float:
    """Parse an SVG opacity: `.55`, `0.55`, `55%`. num() cannot: it reads `.55` as 55."""
    if not value:
        return default
    text = value.strip()
    try:
        f = float(text[:-1]) / 100.0 if text.endswith("%") else float(text)
    except ValueError:
        m = re.search(r"-?\d*\.?\d+", text)
        f = float(m.group(0)) if m else default
    return max(0.0, min(1.0, f))


def parse_color(value: str | None):
    """Return (r, g, b, a) with 0-255 channels and 0-1 alpha, or None if not a solid colour."""
    if not value:
        return None
    v = value.strip().lower()
    if v in {"none", "transparent", "currentcolor", "inherit"}:
        return None
    named = {"white": (255, 255, 255, 1.0), "black": (0, 0, 0, 1.0)}
    if v in named:
        r, g, b, a = named[v]
        return (r, g, b, a)
    m = re.fullmatch(r"#([0-9a-f]{3,8})", v)
    if m:
        h = m.group(1)
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        if len(h) == 6:
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 1.0)
        if len(h) == 8:
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16) / 255)
        return None
    m = re.fullmatch(r"rgba?\(([^)]+)\)", v)
    if m:
        parts = [p.strip() for p in re.split(r"[,\s/]+", m.group(1)) if p.strip()]
        try:
            r, g, b = (float(parts[i]) for i in range(3))
            a = float(parts[3]) if len(parts) > 3 else 1.0
        except (ValueError, IndexError):
            return None
        return (int(r), int(g), int(b), max(0.0, min(1.0, a)))
    return None


def composite(fg, bg):
    r, g, b, a = fg
    R, G, B, _ = bg
    return (r * a + R * (1 - a), g * a + G * (1 - a), b * a + B * (1 - a), 1.0)


def luminance(rgb) -> float:
    def chan(c: float) -> float:
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = rgb[0], rgb[1], rgb[2]
    return 0.2126 * chan(r) + 0.7152 * chan(g) + 0.0722 * chan(b)


def contrast(fg, bg) -> float:
    l1, l2 = luminance(fg), luminance(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def text_width(text: str, size: float) -> float:
    """Rough advance-width estimate: CJK ~1.0em, latin ~0.55em."""
    w = 0.0
    for ch in text:
        w += 1.0 if CJK_RE.match(ch) else 0.55
    return w * size


def elem_id(el: ET.Element) -> str:
    """A readable handle for a finding: the id, else the class, else the tag and position."""
    if el.get("id"):
        return el.get("id")
    cls = (el.get("class") or "").split()
    if cls:
        return f".{cls[0]}"
    tag = strip_ns(el.tag)
    x = el.get("x") or el.get("x1") or el.get("cx")
    y = el.get("y") or el.get("y1") or el.get("cy")
    if x is None and y is None and el.get("d"):
        start = re.match(r"\s*[Mm]\s*(-?[\d.]+)[\s,]+(-?[\d.]+)", el.get("d") or "")
        if start:
            x, y = start.group(1), start.group(2)
    if x is None and y is None:
        return f"<{tag}>"
    return f"<{tag} at {x},{y}>"


def classes(el: ET.Element) -> set[str]:
    return set((el.get("class") or "").split())


def has_class(el: ET.Element, *needles: str) -> bool:
    cs = classes(el)
    return any(n in cs for n in needles)


def iter_children(root: ET.Element):
    for child in root.iter():
        if child is not root:
            yield child


def style_prop(el: ET.Element, prop: str) -> str | None:
    style = el.get("style") or ""
    for part in style.split(";"):
        if ":" in part:
            k, v = part.split(":", 1)
            if k.strip() == prop:
                return v.strip()
    return None


def effective_font_family(el: ET.Element, parents: dict) -> str | None:
    return inherited(el, parents, "font-family")


def inherited(el: ET.Element, parents: dict, prop: str) -> str | None:
    """Resolve an inheritable presentation attribute or style up the ancestor chain.

    SVG inherits `font-family`, `font-size` and `fill` from an enclosing <g>, so a checker that
    only reads the element itself both over- and under-estimates text.
    """
    cur = el
    while cur is not None:
        val = cur.get(prop) or style_prop(cur, prop)
        if val:
            return val
        cur = parents.get(id(cur))
    return None


def collect_text(el: ET.Element) -> str:
    parts = [el.text or ""]
    for sub in el:
        parts.append(sub.text or "")
    return "".join(parts).strip()


def svg_from_file(path: str) -> tuple[str, str | None]:
    raw = open(path, encoding="utf-8", errors="replace").read()
    if path.lower().endswith((".html", ".htm")):
        m = re.search(r"<svg\b.*?</svg>", raw, re.S | re.I)
        if not m:
            return raw, "no inline <svg> found in HTML"
        return m.group(0), None
    return raw, None


def rect_of(el: ET.Element):
    t = strip_ns(el.tag)
    try:
        if t in {"rect", "image"}:
            x, y = num(el.get("x")), num(el.get("y"))
            return x, y, num(el.get("width")), num(el.get("height"))
        if t in {"circle"}:
            r = num(el.get("r"))
            return num(el.get("cx")) - r, num(el.get("cy")) - r, 2 * r, 2 * r
        if t == "ellipse":
            rx, ry = num(el.get("rx")), num(el.get("ry"))
            return num(el.get("cx")) - rx, num(el.get("cy")) - ry, 2 * rx, 2 * ry
    except Exception:
        return None
    return None


PATH_ARG_COUNT = {"H": 1, "V": 1, "M": 2, "L": 2, "T": 2, "Q": 4, "S": 4, "C": 6}


def path_parts(d: str):
    """Yield every piece of a path as (x1, y1, x2, y2, kind).

    `kind` is "line" for a straight M/L/H/V run and "curve" for a corner fillet (Q/C), reported
    as its two half-chords through the control point. Straight pieces carry all the geometry this
    skill cares about; fillets are tracked so the parser keeps reading past them and so a path's
    real endpoints can be recovered.
    """
    tokens = re.findall(r"[A-Za-z]|-?\d*\.?\d+", d)
    x = y = 0.0
    cmd = None
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if re.fullmatch(r"[A-Za-z]", t):
            cmd = t
            i += 1
            continue
        need = PATH_ARG_COUNT.get((cmd or "").upper())
        if need is None:
            break
        args = []
        while len(args) < need and i < len(tokens) and not re.fullmatch(r"[A-Za-z]", tokens[i]):
            args.append(float(tokens[i]))
            i += 1
        if len(args) < need:
            break
        rel = cmd.islower()
        if cmd in "Mm":
            x, y = (x + args[0], y + args[1]) if rel else (args[0], args[1])
        elif cmd in "Ll":
            nx, ny = (x + args[0], y + args[1]) if rel else (args[0], args[1])
            yield x, y, nx, ny, "line"
            x, y = nx, ny
        elif cmd in "Hh":
            nx = x + args[0] if rel else args[0]
            yield x, y, nx, y, "line"
            x = nx
        elif cmd in "Vv":
            ny = y + args[0] if rel else args[0]
            yield x, y, x, ny, "line"
            y = ny
        elif cmd in "Qq":
            cx, cy, ex, ey = args
            if rel:
                cx, cy, ex, ey = x + cx, y + cy, x + ex, y + ey
            yield x, y, cx, cy, "curve"
            yield cx, cy, ex, ey, "curve"
            x, y = ex, ey
        elif cmd in "Cc":
            c1x, c1y, c2x, c2y, ex, ey = args
            if rel:
                c1x, c1y, c2x, c2y, ex, ey = x + c1x, y + c1y, x + c2x, y + c2y, x + ex, y + ey
            yield x, y, c1x, c1y, "curve"
            yield c1x, c1y, c2x, c2y, "curve"
            yield c2x, c2y, ex, ey, "curve"
            x, y = ex, ey
        else:
            break


def path_segments(d: str):
    """The straight, axis-aligned pieces of a path as (x1, y1, x2, y2)."""
    return [(a, b, c, e) for a, b, c, e, kind in path_parts(d) if kind == "line"]


def dist_point_segment(px: float, py: float, x1: float, y1: float, x2: float, y2: float) -> float:
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def dist_point_rect(px: float, py: float, rect) -> float:
    """Distance from a point to a rectangle's outline (0 on the edge, positive inside and out)."""
    x, y, w, h = rect
    dx = max(x - px, px - (x + w), 0.0)
    dy = max(y - py, py - (y + h), 0.0)
    if dx == 0 and dy == 0:
        return min(px - x, x + w - px, py - y, y + h - py)
    return math.hypot(dx, dy)


def point_in_rect(px: float, py: float, rect, inset: float = 0.0) -> bool:
    x, y, w, h = rect
    return x + inset <= px <= x + w - inset and y + inset <= py <= y + h - inset


def overlap_area(a, b) -> float:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return max(0.0, min(ax + aw, bx + bw) - max(ax, bx)) * max(0.0, min(ay + ah, by + bh) - max(ay, by))


def inside_length(x1: float, y1: float, x2: float, y2: float, rect, inset: float = 2.0) -> float:
    """How much of an axis-aligned segment lies inside a rect, ignoring `inset` on every side."""
    x, y, w, h = rect
    x0, y0, x1r, y1r = x + inset, y + inset, x + w - inset, y + h - inset
    if x1r <= x0 or y1r <= y0:
        return 0.0
    if abs(y2 - y1) < 0.01:  # horizontal
        if not y0 <= y1 <= y1r:
            return 0.0
        lo, hi = sorted((x1, x2))
        return max(0.0, min(hi, x1r) - max(lo, x0))
    if abs(x2 - x1) < 0.01:  # vertical
        if not x0 <= x1 <= x1r:
            return 0.0
        lo, hi = sorted((y1, y2))
        return max(0.0, min(hi, y1r) - max(lo, y0))
    return 0.0


def dist_box_segment(box, seg) -> float:
    """Shortest distance between a rectangle and a segment (0 when they touch or cross)."""
    if inside_length(*seg, box, 0.0) > 0.02:
        return 0.0
    x, y, w, h = box
    x1, y1, x2, y2 = seg
    d = min(dist_point_rect(x1, y1, box), dist_point_rect(x2, y2, box))
    for cx, cy in ((x, y), (x + w, y), (x, y + h), (x + w, y + h)):
        d = min(d, dist_point_segment(cx, cy, x1, y1, x2, y2))
    return d


def mask_stroke_relation(mask_box, seg, width: float):
    """How a label mask meets one stroke segment, or None when it leaves the ink alone.

    A label either sits clear of the stroke's ink or swallows it whole:
      cuts   - the mask covers the ink band with >= 1px to spare on both sides: a clean cut, which
               then has to be centred on the line and on the middle of the run.
      shaved - a mask edge lands inside the ink band, so the line paints half-thick under the
               glyphs for the label's whole width.
    """
    x1, y1, x2, y2 = seg
    horiz, vert = abs(y2 - y1) < 0.5, abs(x2 - x1) < 0.5
    if not (horiz or vert):
        return None
    axis = y1 if horiz else x1
    band_lo, band_hi = axis - width / 2, axis + width / 2
    mx, my, mw, mh = mask_box
    lo_a, hi_a = (min(x1, x2), max(x1, x2)) if horiz else (min(y1, y2), max(y1, y2))
    lo_m, hi_m = (mx, mx + mw) if horiz else (my, my + mh)
    lo_t, hi_t = (my, my + mh) if horiz else (mx, mx + mw)
    cut_lo, cut_hi = max(lo_a, lo_m), min(hi_a, hi_m)
    if cut_hi <= cut_lo:
        return None                              # mask does not sit along this segment
    if hi_t <= band_lo or lo_t >= band_hi:
        return None                              # ink untouched: the label sits clear
    kind = "cuts" if (lo_t <= band_lo - 1.0 and hi_t >= band_hi + 1.0) else "shaved"
    return {
        "kind": kind,
        "perp": abs((my + mh / 2) - axis) if horiz else abs((mx + mw / 2) - axis),
        "stubs": (cut_lo - lo_a, hi_a - cut_hi),
    }


def hex_of(rgb) -> str:
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(c))) for c in rgb[:3])


def backdrop_tone(px: float, py: float, canvas_bg, rects_before):
    """The colour actually behind a point: the canvas, plus every filled rect painted before it.

    A label mask is canvas-coloured by default, which is invisible over a bare canvas and a visible
    patch over anything tinted (a zone band, a node fill). Compositing the rects that cover the
    point in document order gives the tone the mask has to match.
    """
    tone = canvas_bg
    for el, box in rects_before:
        if not point_in_rect(px, py, box):
            continue
        fill = parse_color(el.get("fill"))
        if not fill:
            continue
        alpha = min(1.0, fill[3] * frac(el.get("opacity") or style_prop(el, "opacity"))
                    * frac(el.get("fill-opacity")))
        if alpha > 0.004:
            tone = composite((fill[0], fill[1], fill[2], alpha), tone)
    return tone


def render_stats(png: str) -> tuple[float, str, tuple[int, int]]:
    """Read a rendered PNG back: (content fraction, background colour, size).

    "Content" is the share of pixels that differ from the figure's dominant colour, i.e. the
    pixels the author actually drew. Comparing against the dominant colour instead of against
    white keeps this register-agnostic: a near-black canvas is background, not 94% ink.
    """
    hist = subprocess.run(
        ["magick", png, "-colorspace", "sRGB", "-depth", "8", "-format", "%c", "histogram:info:-"],
        capture_output=True, text=True, timeout=60, check=True,
    ).stdout
    best_count, best_bg = -1, None
    for line in hist.splitlines():
        head, _, rest = line.partition(":")
        m = re.search(r"#([0-9A-Fa-f]{6})", rest)
        if not m:
            continue
        count = int(re.sub(r"\D", "", head) or 0)
        if count > best_count:
            best_count, best_bg = count, m.group(1)
    if not best_bg:
        raise RuntimeError("could not read a colour histogram")

    # Pixels within 8% of the background colour are treated as background (this also drops the
    # antialiased fringe), so what remains is the drawn content.
    content = subprocess.run(
        ["magick", png, "-fuzz", "8%", "-transparent", f"#{best_bg}", "-alpha", "extract",
         "-format", "%[fx:mean]", "info:"],
        capture_output=True, text=True, timeout=60, check=True,
    ).stdout.strip()
    size = subprocess.run(
        ["magick", "identify", "-format", "%w %h", png], capture_output=True, text=True, check=True,
    ).stdout.split()
    return float(content or 0), f"#{best_bg}", (int(size[0]), int(size[1]))


def node_text_offsets(png: str, nodes, scale: float):
    """Measure each node's text block against its box, from the render.

    Returns (element, vertical offset in px, box height). Positive offset means the text sits low.
    Reads the ink only, so it also sees metrics the geometry estimates cannot know about.
    """
    results = []
    inset = 8.0 * scale  # clears the 1px border and the 4px inset of a terminal-state border
    for el in nodes:
        rect = next((c for c in el if strip_ns(c.tag) == "rect"), None)
        if rect is None:
            continue
        x, y = num(rect.get("x")), num(rect.get("y"))
        w, h = num(rect.get("width")), num(rect.get("height"))
        cw, ch = w * scale - 2 * inset, h * scale - 2 * inset
        if cw <= 8 or ch <= 8:
            continue
        out = subprocess.run(
            ["magick", png,
             "-crop", f"{int(cw)}x{int(ch)}+{int(x * scale + inset)}+{int(y * scale + inset)}",
             "+repage", "-fuzz", "8%", "-trim", "-format", "%w %h %X %Y", "info:"],
            capture_output=True, text=True, timeout=30, check=True,
        ).stdout.split()
        if len(out) != 4:
            continue
        th, ty = int(out[1]), int(out[3])
        results.append((el, ((ty + th / 2) - ch / 2) / scale, h))
    return results


def ink_margins(png: str, bg: str, size: tuple[int, int], scale: float):
    """Measured distance from the drawn content to each canvas edge, in figure pixels."""
    out = subprocess.run(
        ["magick", png, "-fuzz", "8%", "-transparent", bg, "-trim",
         "-format", "%w %h %X %Y", "info:"],
        capture_output=True, text=True, timeout=30, check=True,
    ).stdout.split()
    if len(out) != 4:
        return []
    w, h, x, y = (int(v) for v in out)
    W, H = size
    return [("left", x / scale), ("right", (W - x - w) / scale),
            ("top", y / scale), ("bottom", (H - y - h) / scale)]


def check(source: str, png: str | None, strict: bool, standalone: bool = True) -> tuple[list[Finding], Stats]:
    """Lint one figure. `standalone` is False for the inline <svg> of an HTML preview, where the
    render includes page chrome and pixel coordinates no longer match the SVG's."""
    findings: list[Finding] = []
    stats = Stats()

    def err(code: str, msg: str):
        findings.append(Finding("error", code, msg))

    def warn(code: str, msg: str):
        findings.append(Finding("warning", code, msg))

    def note(code: str, msg: str):
        findings.append(Finding("info", code, msg))

    if "<!--" in source:
        source = re.sub(r"<!--.*?-->", "", source, flags=re.S)

    try:
        root = ET.fromstring(source)
    except ET.ParseError as exc:
        err("xml", f"not well-formed XML: {exc}")
        return findings, stats
    if strip_ns(root.tag) != "svg":
        err("root", f"root element is <{strip_ns(root.tag)}>, expected <svg>")
        return findings, stats

    # ---- structure + a11y ----
    if root.get("role") != "img":
        err("a11y", '<svg> needs role="img"')
    labelled = root.get("aria-labelledby") or root.get("aria-label") or ""
    if not labelled:
        warn("a11y", "no aria-labelledby/aria-label on <svg>")
    children = list(root)
    if not children or strip_ns(children[0].tag) != "title":
        err("a11y", "<title> must be the first child of <svg>")
    title = next((c for c in children if strip_ns(c.tag) == "title"), None)
    desc = next((c for c in children if strip_ns(c.tag) == "desc"), None)
    if title is None:
        err("a11y", "missing <title>")
    elif len((title.text or "").strip()) > TITLE_MAX:
        warn("a11y", f"<title> is {len(title.text.strip())} chars; keep it under {TITLE_MAX}")
    if desc is None:
        err("a11y", "missing <desc>")
    ids = {el.get("id") for el in iter_children(root) if el.get("id")}
    ids.update({c.get("id") for c in children if c.get("id")})
    for ref in labelled.split():
        if ref and ref not in ids:
            err("a11y", f'aria-labelledby references missing id "{ref}"')

    vb = [num(p) for p in (root.get("viewBox") or "").split()]
    if len(vb) != 4:
        err("canvas", "viewBox must have four numbers")
        vb = [0, 0, 1100, 480]
    if not root.get("width") or not root.get("height"):
        warn("canvas", "set explicit width and height on <svg> for standalone files")

    parents = {id(child): parent for parent in root.iter() for child in parent}
    root_font = root.get("font-family") or style_prop(root, "font-family") or ""

    # ---- budget ----
    nodes = [el for el in iter_children(root) if has_class(el, "node", "td-node")]
    stats.nodes = len(nodes)
    if stats.nodes > NODE_BUDGET:
        err("budget", f"{stats.nodes} nodes exceeds the budget of {NODE_BUDGET}; split the figure")
    focal = [el for el in nodes if has_class(el, "is-focal", "focal")]
    stats.focal = len(focal)
    if stats.focal > FOCAL_BUDGET:
        err("accent", f"{stats.focal} focal nodes; at most {FOCAL_BUDGET} are allowed")

    edges = [
        el
        for el in iter_children(root)
        if strip_ns(el.tag) in {"line", "path", "polyline"}
        and (el.get("marker-end") or el.get("marker-start") or has_class(el, "edge", "td-edge"))
    ]
    stats.edges = len(edges)

    # ---- decoration bans ----
    banned = {"linearGradient": "gradient", "radialGradient": "gradient", "filter": "filter effect"}
    for el in root.iter():
        tag = strip_ns(el.tag)
        if tag in banned and el.get("data-decor") != "allowed":
            err("decor", f"<{tag}> is banned ({banned[tag]}); emphasise with border colour and weight")

    # ---- geometry ----
    for el in iter_children(root):
        tag = strip_ns(el.tag)
        if tag not in {"rect", "line", "path", "circle", "ellipse", "polygon"}:
            continue
        skip_grid = el.get("data-grid") == "off"
        for attr in ("x", "y", "width", "height", "x1", "y1", "x2", "y2"):
            if el.get(attr) is None or skip_grid:
                continue
            val = num(el.get(attr))
            if abs(val - round(val / GRID) * GRID) > 0.01:
                warn("grid", f"{elem_id(el)} {attr}={val:g} is off the {GRID}px grid")
        rx = num(el.get("rx")) if el.get("rx") else 0
        if rx > MAX_RADIUS and not has_class(el, "pill"):
            warn("radius", f"{elem_id(el)} rx={rx:g} exceeds {MAX_RADIUS}px")
        sw = num(el.get("stroke-width"), 0)
        if sw > MAX_STROKE:
            warn("stroke", f"{elem_id(el)} stroke-width={sw:g} exceeds {MAX_STROKE}")

        if tag == "line":
            dx = num(el.get("x2")) - num(el.get("x1"))
            dy = num(el.get("y2")) - num(el.get("y1"))
            if dx and dy and el.get("data-diagonal") != "ok":
                err("diagonal", f"{elem_id(el)} connector is diagonal; use two axis-aligned segments")
        if tag == "path":
            d = el.get("d") or ""
            # A filled path is a shape (diamond, chevron, arrowhead); connectors keep fill="none".
            # Only connectors are held to the orthogonal rule.
            is_shape = (el.get("fill") or "").strip().lower() not in ("", "none")
            if el.get("data-diagonal") != "ok" and not is_shape:
                for x1, y1, x2, y2 in path_segments(d):
                    if abs(x2 - x1) > 0.5 and abs(y2 - y1) > 0.5:
                        err("diagonal", f"{elem_id(el)} has a diagonal segment ({x1:g},{y1:g})->({x2:g},{y2:g})")
                        break

    # ---- edge labels need masks ----
    # Their boxes are kept for the connector pass below: a label that a later node paints over is
    # invisible, and a mask that neither covers its stroke nor clears it reads as a stray hole.
    label_boxes = []
    for el in iter_children(root):
        if not has_class(el, "edge-label", "td-edge-label"):
            continue
        mask_el = next((c for c in el.iter() if c is not el and has_class(c, "mask")), None)
        if mask_el is None:
            err("edge-label", f"{elem_id(el)} has no mask rect; the stroke will bleed through the text")
        for t in el.iter():
            if strip_ns(t.tag) != "text":
                continue
            content = collect_text(t)
            size = num(inherited(t, parents, "font-size"), 0) or num(style_prop(root, "font-size"), 16)
            w = text_width(content, size)
            anchor = t.get("text-anchor") or "start"
            tx, ty = num(t.get("x")), num(t.get("y"))
            left = tx - w if anchor == "end" else tx - w / 2 if anchor == "middle" else tx
            label_boxes.append({
                "text": content, "box": (left, ty - size, w, size * 1.4), "group": el, "mask": mask_el,
                # The mask is the label's visual footprint, so it is what "sits on this arrow" means.
                "span": (rect_of(mask_el) if mask_el is not None else (left, ty - size, w, size * 1.4)),
            })

    # ---- text: size, overflow, clipping, font stack, contrast ----
    canvas_rect = None
    for el in iter_children(root):
        r = rect_of(el)
        if r and abs(r[2] - vb[2]) < 2 and abs(r[3] - vb[3]) < 2 and parse_color(el.get("fill")):
            canvas_rect = parse_color(el.get("fill"))
            break
    canvas_bg = canvas_rect or (10, 10, 11, 1.0)

    for el in iter_children(root):
        if strip_ns(el.tag) != "text":
            continue
        stats.texts += 1
        content = collect_text(el)
        size = num(inherited(el, parents, "font-size"), 0) or num(
            style_prop(root, "font-size"), 16
        )
        if size < MIN_FONT:
            err("type", f"text '{content[:28]}' is {size:g}px; minimum is {MIN_FONT}px")
        if content and CJK_RE.search(content):
            fam = (effective_font_family(el, parents) or root_font).lower()
            if not any(f in fam for f in CJK_FAMILIES):
                err("fonts", f"CJK text '{content[:16]}' has no CJK family in its font stack")

        x, y = num(el.get("x")), num(el.get("y"))
        est_w = text_width(content, size)
        est_h = size * 1.4
        anchor = el.get("text-anchor") or "start"
        left = x - est_w if anchor == "end" else x - est_w / 2 if anchor == "middle" else x
        if left < -0.5 or left + est_w > vb[2] + 0.5 or y - est_h < -0.5 or y > vb[3] + 0.5:
            err("clip", f"text '{content[:28]}' is outside the canvas (viewBox {vb[2]:g}x{vb[3]:g})")

        # overflow inside the enclosing node rect
        parent = parents.get(id(el))
        while parent is not None and not has_class(parent, "node", "td-node"):
            parent = parents.get(id(parent))
        if parent is not None:
            box = next((rect_of(c) for c in parent if rect_of(c)), None)
            if box:
                bx, by, bw, bh = box
                pad = 12.0
                if left < bx + pad - 0.5 or left + est_w > bx + bw - pad + 0.5:
                    err("overflow", f"label '{content[:28]}' does not fit node {elem_id(parent)} "
                                    f"(needs {est_w:.0f}px, has {bw - 2 * pad:.0f}px)")
                if y > by + bh:
                    err("overflow", f"label '{content[:28]}' sits below node {elem_id(parent)}")
                bg = parse_color(next((c.get("fill") for c in parent if strip_ns(c.tag) == "rect"), None))
                if bg and bg[3] < 1.0:
                    bg = composite(bg, canvas_bg)
            else:
                bg = canvas_bg
        else:
            bg = canvas_bg
        fg = parse_color(inherited(el, parents, "fill"))
        if fg and bg:
            if fg[3] < 1.0:
                fg = composite(fg, bg)
            ratio = contrast(fg, bg)
            need = 3.0 if size >= 18 else 4.5
            if ratio < need:
                err("contrast", f"text '{content[:28]}' has contrast {ratio:.1f}:1, needs {need}:1")

    # ---- connectors: ports, routing, labels ----
    # An arrow has to land on something the reader can see it come from or point at: a node edge,
    # another stroke, or a start marker. An end that stops in empty space, and a stroke that runs
    # through a box that is not its own endpoint, are what make a topology figure ambiguous.
    NODE_TOL, LINE_TOL = 6.0, 10.0
    LONG_CONNECTOR, LABEL_REACH = 48.0, 24.0
    kids = list(iter_children(root))
    order = {id(el): i for i, el in enumerate(kids)}

    node_boxes = []
    for el in kids:
        if has_class(el, "node", "td-node"):
            box = next((r for r in (rect_of(c) for c in el) if r), None)
            if box:
                node_boxes.append((el.get("id") or elem_id(el), box, order[id(el)]))

    strokes = []  # everything an arrow end is allowed to land on, besides a node edge
    round_anchors = []  # small round markers, e.g. the start dot of a state machine
    for el in kids:
        tag = strip_ns(el.tag)
        if tag == "line":
            strokes.append((el, [(num(el.get("x1")), num(el.get("y1")), num(el.get("x2")), num(el.get("y2")))]))
        elif tag in {"path", "polyline"} and (el.get("fill") or "").strip().lower() in ("", "none"):
            strokes.append((el, path_segments(el.get("d") or "")))
        elif tag == "circle":
            round_anchors.append((num(el.get("cx")), num(el.get("cy")), num(el.get("r"))))

    def segments_of(el):
        if strip_ns(el.tag) == "line":
            return [(num(el.get("x1")), num(el.get("y1")), num(el.get("x2")), num(el.get("y2")))]
        return path_segments(el.get("d") or "")

    def nearest_anchor(px, py, self_el):
        best = (float("inf"), "nothing")
        for name, box, _ in node_boxes:
            d = dist_point_rect(px, py, box)
            if d < best[0]:
                best = (d, f"node {name}")
        for wire, segs in strokes:
            if wire is self_el:
                continue
            for s in segs:
                d = dist_point_segment(px, py, *s)
                if d < best[0]:
                    best = (d, f"stroke {elem_id(wire)}")
        for cx, cy, r in round_anchors:
            d = abs(math.hypot(px - cx, py - cy) - r)
            if d < best[0]:
                best = (d, "start marker")
        return best

    # A figure with no boxes is a chart or a doc fragment: a bare connector there is a glyph,
    # not a claim about which node feeds which, so the topology checks have nothing to judge.
    checked_edges = edges if node_boxes else []

    for el in checked_edges:
        segs = segments_of(el)
        if not segs:
            continue
        ends = (("arrowhead" if el.get("marker-start") else "start", segs[0][0], segs[0][1]),
                ("arrowhead" if el.get("marker-end") else "tail", segs[-1][2], segs[-1][3]))
        for role, px, py in ends:
            dist, what = nearest_anchor(px, py, el)
            if dist <= (NODE_TOL if what.startswith("node ") else LINE_TOL):
                continue
            inside = next((n for n, box, _ in node_boxes if point_in_rect(px, py, box, 2.0)), None)
            if inside:
                err("port", f"{elem_id(el)} {role} ({px:g},{py:g}) lands inside node {inside}; an end "
                            f"points at a boundary, never into a box")
            else:
                err("port", f"{elem_id(el)} {role} ({px:g},{py:g}) attaches to nothing: the nearest "
                            f"{what} is {dist:.0f}px away; land it on a node edge or on another stroke")

        # A tip that touches a corner reads as pointing at two edges at once.
        end_x, end_y = ((segs[0][0], segs[0][1]) if el.get("marker-start") and not el.get("marker-end")
                        else (segs[-1][2], segs[-1][3]))
        for name, box, _ in node_boxes:
            bx, by, bw, bh = box
            corners = ((bx, by), (bx + bw, by), (bx, by + bh), (bx + bw, by + bh))
            if min(math.hypot(end_x - cx, end_y - cy) for cx, cy in corners) <= 6:
                warn("port", f"{elem_id(el)} arrowhead ({end_x:g},{end_y:g}) lands on a corner of node "
                             f"{name}; slide it onto the middle of one edge")

        hit = 0.0
        crossed = None
        for name, box, nidx in node_boxes:
            inside_len = max((inside_length(*s, box) for s in segs), default=0.0)
            if inside_len > hit:
                hit, crossed = inside_len, (name, nidx)
        if crossed and hit > 6:
            name, nidx = crossed
            where = ("passes behind node " + name if nidx > order[id(el)] else "runs through node " + name)
            err("hidden", f"{elem_id(el)} {where} ({hit:.0f}px inside the box); connectors only touch a "
                          f"box they start from or point at")

    for lab in label_boxes:
        text, box = lab["text"], lab["box"]
        gidx = order[id(lab["group"])]
        for name, nbox, nidx in node_boxes:
            if overlap_area(box, nbox) <= 0.2 * max(box[2] * box[3], 1.0):
                continue
            how = "the box paints over it" if nidx > gidx else "it collides with the box's own text"
            err("hidden", f"edge label '{text}' sits inside node {name}: {how}; move it into the gap "
                          f"between the boxes")
        if lab["mask"] is None:
            continue
        mask_box = rect_of(lab["mask"])
        # How the mask meets the stroke it names. A label either leaves the ink alone or swallows
        # the stroke whole; an edge inside the ink band paints a half-thick line under the glyphs,
        # and a cut that misses the middle of the run reads as damage rather than a label.
        hit = None
        for el in edges:
            width = num(el.get("stroke-width") or style_prop(el, "stroke-width"), 1.0) or 1.0
            for s in segments_of(el):
                rel = mask_stroke_relation(mask_box, s, width)
                if rel is not None:
                    hit = (el, width, rel)
                    break
            if hit:
                break
        if hit:
            el, width, rel = hit
            if rel["kind"] == "shaved":
                warn("label-cut", f"the mask of edge label '{text}' has an edge inside the {width:g}px "
                                  f"stroke of {elem_id(el)}, so the line paints half-thick under the "
                                  f"glyphs; clear the stroke by 1px or swallow it whole")
            elif rel["perp"] > 2:
                warn("label-cut", f"the mask of edge label '{text}' cuts {elem_id(el)} "
                                  f"{rel['perp']:.0f}px off the line's axis; a label that cuts a stroke "
                                  f"sits centred on it, or beside it")
            else:
                a, b = rel["stubs"]
                if min(a, b) < 8 or abs(a - b) > 8:
                    warn("label-cut", f"the mask of edge label '{text}' does not cut {elem_id(el)} in "
                                      f"the middle: {a:.0f}px of stroke on one side, {b:.0f}px on the "
                                      f"other; centre the label on the run")

        # A mask hides what is behind the glyphs, so it has to be the tone of its backdrop. The
        # default canvas colour is invisible over the canvas and a patch over a zone band or a node.
        mid_x, mid_y = mask_box[0] + mask_box[2] / 2, mask_box[1] + mask_box[3] / 2
        behind = backdrop_tone(mid_x, mid_y, canvas_bg,
                               [(c, rect_of(c)) for c in kids[:order[id(lab["mask"])]]
                                if strip_ns(c.tag) == "rect" and rect_of(c)])
        fill = parse_color(lab["mask"].get("fill"))
        if fill and fill[3] > 0.9 and max(abs(fill[i] - behind[i]) for i in range(3)) > 2.5:
            warn("mask-tone", f"the mask of edge label '{text}' is {hex_of(fill)} over a "
                              f"{hex_of(behind)} backdrop, so it paints a patch over the band; give the "
                              f"mask the tone of what is behind it")
        for name, nbox, nidx in node_boxes:
            if overlap_area(mask_box, nbox) > 0 and nidx < order[id(lab["mask"])]:
                warn("mask", f"the mask of edge label '{text}' overlaps node {name} and is drawn after "
                             f"it, so it erases part of the box outline")
                break

    # A short arrow carries no readable payload of its own: unless a label sits on it, the reader
    # has to guess what it means and which way the intent runs.
    for el in checked_edges:
        segs = segments_of(el)
        if not segs:
            continue
        xs = [s[0] for s in segs] + [s[2] for s in segs]
        ys = [s[1] for s in segs] + [s[3] for s in segs]
        span = max(max(xs) - min(xs), max(ys) - min(ys))
        if span >= LONG_CONNECTOR:
            continue
        anchored = any(abs(math.hypot(px - cx, py - cy) - r) <= LINE_TOL
                       for px, py in ((segs[0][0], segs[0][1]), (segs[-1][2], segs[-1][3]))
                       for cx, cy, r in round_anchors)
        if anchored:
            continue
        reach = min((dist_box_segment(lab["span"], s) for lab in label_boxes for s in segs),
                    default=float("inf"))
        if reach > LABEL_REACH:
            warn("label", f"{elem_id(el)} is a {span:.0f}px connector with no label; a short arrow "
                          f"without one is ambiguous, so label it or drop it")

    # ---- optional render check ----
    if png:
        bg = ""
        size = (0, 0)
        if not shutil.which("magick"):
            warn("render", "ImageMagick not found; skipped the blank-render and centring checks")
        else:
            try:
                content, bg, size = render_stats(png)
                if content < 0.002:
                    err("render", f"{png} looks blank (content {content:.3%} over background {bg})")
                elif content > 0.75:
                    warn("render", f"{png} looks very dense (content {content:.1%} over background {bg})")
                else:
                    note("render", f"{png}: {size[0]}×{size[1]} · background {bg} · content {content:.1%}")
            except Exception as exc:  # pragma: no cover
                warn("render", f"render check failed: {exc}")

            # Geometry maths cannot see font metrics, so ask the render where the text
            # actually sits inside each box.
            if standalone and nodes and size[0] and vb[2]:
                try:
                    for el, dy, box_h in node_text_offsets(png, nodes, size[0] / vb[2]):
                        texts = [c for c in el if strip_ns(c.tag) == "text"]
                        who = el.get("id") or (collect_text(texts[0])[:24] if texts else elem_id(el))
                        if abs(dy) > 4:
                            err("center", f"{who}: text block sits {dy:+.1f}px off the centre of "
                                          f"a {box_h:g}px box; shift the baselines to even the padding")
                        elif abs(dy) > 2:
                            warn("center", f"{who}: text block sits {dy:+.1f}px off the centre of "
                                           f"a {box_h:g}px box")
                except Exception as exc:  # pragma: no cover
                    warn("center", f"node-centring check failed: {exc}")

            # Content that touches or comes within a hair of the canvas edge reads as a mistake
            # even when nothing is technically clipped: a border on the boundary is half-clipped.
            if standalone and size[0] and bg:
                try:
                    scale = (size[0] / vb[2]) if vb[2] else 1.0
                    margins = ink_margins(png, bg, size, scale)
                    touching = [side for side, gap in margins if gap <= 1]
                    tight = [f"{side} {gap:.0f}px" for side, gap in margins if 1 < gap < 16]
                    if touching or tight:
                        parts = []
                        if touching:
                            parts.append(f"touches the canvas edge on the {', '.join(touching)}")
                        if tight:
                            parts.append(f"sits inside the 16px canvas padding ({', '.join(tight)})")
                        warn("edge", f"content {' and '.join(parts)}; a border on the boundary is "
                                     f"half-clipped, and 16px is the minimum margin")
                except Exception as exc:  # pragma: no cover
                    warn("edge", f"edge-padding check failed: {exc}")

    # ---- local font availability (soft; only the primary family of each stack matters) ----
    if shutil.which("fc-list"):
        primaries = set()
        for el in root.iter():
            fam = el.get("font-family") or style_prop(el, "font-family")
            if fam:
                first = fam.split(",")[0].strip().strip('"').lower()
                if first and first not in {"sans-serif", "serif", "monospace", "system-ui"}:
                    primaries.add(first)
        try:
            listing = subprocess.run(["fc-list", ":family"], capture_output=True, text=True, timeout=20).stdout.lower()
            for fam in sorted(primaries):
                if fam not in listing:
                    warn("fonts", f'primary font "{fam}" not found locally; the rasteriser will substitute '
                                  f"a fallback (fine for a preview, worth checking before an exact-fidelity export)")
        except Exception:
            pass

    return findings, stats


def main() -> int:
    ap = argparse.ArgumentParser(description="Lint a tech-diagrams figure.")
    ap.add_argument("path")
    ap.add_argument("--png", help="rendered PNG to smoke-check for blankness")
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    ap.add_argument("--json", action="store_true", dest="as_json")
    args = ap.parse_args()

    try:
        source, problem = svg_from_file(args.path)
    except OSError as exc:
        print(f"Cannot read {args.path}: {exc}", file=sys.stderr)
        return 2
    if problem:
        print(f"{args.path}: {problem}", file=sys.stderr)
        return 2

    standalone = not args.path.lower().endswith((".html", ".htm"))
    findings, stats = check(source, args.png, args.strict, standalone=standalone)
    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]
    notes = [f for f in findings if f.severity == "info"]
    ok = not errors and (not warnings or not args.strict)

    if args.as_json:
        print(json.dumps({
            "file": args.path,
            "ok": ok,
            "stats": {"nodes": stats.nodes, "edges": stats.edges, "focal": stats.focal, "texts": stats.texts},
            "errors": [{"code": f.code, "message": f.message} for f in errors],
            "warnings": [{"code": f.code, "message": f.message} for f in warnings],
            "notes": [{"code": f.code, "message": f.message} for f in notes],
        }, indent=2))
    else:
        for f in errors:
            print(f"ERROR  {f.code}: {f.message}")
        for f in warnings:
            print(f"warn   {f.code}: {f.message}")
        for f in notes:
            print(f"note   {f.code}: {f.message}")
        if ok:
            print(f"OK  {args.path}: {stats.nodes} nodes · {stats.edges} edges · {stats.focal} focal · "
                  f"{stats.texts} labels · {len(warnings)} warnings")
        else:
            print(f"FAILED  {args.path}: {len(errors)} errors, {len(warnings)} warnings")
    return 0 if ok else 1


if __name__ == "__main__":
    # Behave like a normal CLI when piped into head/less instead of dumping a traceback.
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    sys.exit(main())
