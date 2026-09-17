#!/usr/bin/env python3
"""Lint the SVG snippets inside the skill's own documentation.

The references are copy-paste sources: if a snippet in `references/*.md` would fail
`self_check.py`, the skill is teaching defects. This script extracts every ```xml fence, runs
the same checker over it, and reports the offender by file and line.

    python3 scripts/lint_docs.py           # all docs
    python3 scripts/lint_docs.py -v        # list every snippet, not just failures
    python3 scripts/lint_docs.py --strict  # warnings fail too (the delivery bar for figures)

A fence that is already a full `<svg>` is linted as-is. A fragment is wrapped in a canonical
root (1100x480, CJK-capable stack, canonical defs) so it is judged on the same rules as a real
figure: a snippet using coordinates outside that canvas is a snippet that will be copied into a
broken figure. Fragments are tried on both canvases and judged on the one that fits, so a light
palette - the shipped one or a bespoke one of your own - is not failed by dark-register contrast.

Exit codes: 0 clean, 1 at least one snippet fails, 2 nothing to check.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from self_check import check, luminance, parse_color  # noqa: E402

FENCE = re.compile(r"^```xml\n(.*?)^```", re.S | re.M)

CANONICAL_DEFS = """  <defs>
    <marker id="arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="{arrow}"/>
    </marker>
    <marker id="arrow-strong" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="{arrow_strong}"/>
    </marker>
    <marker id="arrow-accent" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="{arrow_accent}"/>
    </marker>
  </defs>
"""

WRAPPER = (
    '<svg role="img" aria-labelledby="snip-title snip-desc" viewBox="0 0 1100 480" '
    'width="1100" height="480" xmlns="http://www.w3.org/2000/svg"\n'
    '     font-family="Inter, PingFang SC, Hiragino Sans, Heiti SC, Noto Sans CJK SC, sans-serif">\n'
    '  <title id="snip-title">documentation snippet</title>\n'
    '  <desc id="snip-desc">A snippet lifted from the skill references for linting.</desc>\n'
    + CANONICAL_DEFS
    + '  <rect width="1100" height="480" fill="{canvas}"/>\n'
    "{body}\n</svg>\n"
)

# A fragment is wrapped in a canvas so it can be judged on the same rules as a figure. Which
# register that canvas belongs to is decided by the snippet's own colours: contrast is checked
# against the canvas, so a light snippet in a dark wrapper reports contrast errors that are not
# there. Which register a fragment belongs to is decided by linting it in both and keeping the one
# that passes: a snippet is valid in some palette, and naming the register that fitted keeps the
# report readable. When both fit (or neither does) the snippet's own fills pick the label.
REGISTERS = {
    "dark": {"canvas": "#0A0A0B", "arrow": "#9BA1A6", "arrow_strong": "#EDEDF0", "arrow_accent": "#5E6AD2"},
    "light": {"canvas": "#FAFAFA", "arrow": "#4C4C4C", "arrow_strong": "#171717", "arrow_accent": "#0072F5"},
}
# Only ever used to label a snippet, never to judge it: the shipped light register (Vercel/Geist),
# the neutral white some documents need, and the warm editorial palette this register replaced.
LIGHT_MARKERS = ("#fafafa", "#f2f2f2", "#ebebeb", "#e6e6e6", "#c9c9c9", "#a8a8a8", "#171717",
                 "#4c4c4c", "#7d7d7d", "#0072f5", "#0062d1", "#f0f7ff", "#297a3a", "#a35200",
                 "#cb2a2f", "#ffffff", "#f4f4f5", "#eef0fe", "#111113", "#4f46e5", "#dcdce0",
                 "#faf9f5", "#f0eee6", "#f7ece6", "#141413", "#5e5d59", "#6f6e68", "#c96442",
                 "#9f4a26", "#d1cfc5", "#b0aea5")


def prefer_register(snippet: str) -> str:
    """Guess a fragment's palette from its colours, for labelling only (never for judging)."""
    if re.search(r'data-register\s*=\s*["\']light["\']', snippet):
        return "light"
    rects = []
    for m in re.finditer(r"<rect\b([^>]*)>", snippet, re.S):
        attrs = m.group(1)
        fill = re.search(r'fill\s*=\s*"(#[0-9a-fA-F]{6})"', attrs)
        w = re.search(r'width\s*=\s*"([\d.]+)', attrs)
        h = re.search(r'height\s*=\s*"([\d.]+)', attrs)
        if fill and w and h:
            rects.append((float(w.group(1)) * float(h.group(1)), fill.group(1)))
    if rects:
        bg = max(rects)[1]                       # the biggest rect is the band or the canvas
    else:
        fills = re.findall(r'fill\s*=\s*"(#[0-9a-fA-F]{6})"', snippet)
        if fills and "<text" in snippet:
            bg = max(fills, key=lambda c: luminance(parse_color(c)[:3]))   # no rects: the lightest fill is the page
        else:
            low = snippet.lower()
            return "light" if any(m in low for m in LIGHT_MARKERS) else "dark"
    return "light" if luminance(parse_color(bg)[:3]) > 0.5 else "dark"


def lint_snippet(body: str, complete: bool):
    """(register, findings, stats) - a full `<svg>` as authored, a fragment in whichever palette fits."""
    if complete:
        findings, stats = check(body, None, False)
        return "as-authored", findings, stats
    attempts = []
    for reg in ("dark", "light"):
        findings, stats = check(WRAPPER.format(body=body, **REGISTERS[reg]), None, False)
        bad = [f for f in findings if f.severity in ("error", "warning")]
        attempts.append((reg, findings, stats, bad))
    passing = [a for a in attempts if not a[3]]
    reg = passing[0][0] if len(passing) == 1 else prefer_register(body)
    chosen = next(a for a in attempts if a[0] == reg)
    return chosen[0], chosen[1], chosen[2]


def snippets(path: pathlib.Path):
    """Yield (line_number, body, complete) for every ```xml fence in the file."""
    text = path.read_text(encoding="utf-8")
    for match in FENCE.finditer(text):
        body = match.group(1).rstrip("\n")
        line = text.count("\n", 0, match.start()) + 1
        yield line, body, "<svg" in body.split("</svg>")[0]


def main() -> int:
    ap = argparse.ArgumentParser(description="Lint the SVG snippets in the skill docs.")
    ap.add_argument("-v", "--verbose", action="store_true", help="list passing snippets too")
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    ap.add_argument("--root", default=str(pathlib.Path(__file__).resolve().parent.parent))
    args = ap.parse_args()

    root = pathlib.Path(args.root)
    docs = sorted([root / "SKILL.md", *sorted((root / "references").glob("*.md"))])
    total = failed = warned = 0
    for doc in docs:
        if not doc.exists():
            continue
        for line, body, complete in snippets(doc):
            total += 1
            register, findings, stats = lint_snippet(body, complete)
            errors = [f for f in findings if f.severity == "error"]
            warnings = [f for f in findings if f.severity == "warning"]
            rel = doc.relative_to(root)
            kind = "svg" if register == "as-authored" else f"fragment/{register}"
            if errors or warnings:
                if errors:
                    failed += 1
                else:
                    warned += 1
                print(f"{'FAIL' if errors else 'warn'}  {rel}:{line} ({kind}) "
                      f"{len(errors)} errors, {len(warnings)} warnings")
                for f in errors:
                    print(f"        ERROR {f.code}: {f.message}")
                for f in warnings:
                    print(f"        warn  {f.code}: {f.message}")
            elif args.verbose:
                print(f"ok    {rel}:{line} ({kind}) {stats.nodes} nodes · {stats.texts} labels")

    if not total:
        print("no ```xml snippets found", file=sys.stderr)
        return 2
    summary = f"{total - failed - warned}/{total} snippets clean"
    if warned:
        summary += f", {warned} with warnings"
    print(summary)
    if failed or (warned and args.strict):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
