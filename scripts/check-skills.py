#!/usr/bin/env python3
"""Check that every skill in skills/ is complete and installable.

A skill is a directory, so a missing companion file is invisible until someone installs it and
finds the metadata or the attribution gone. This script is the checklist that used to live in
prose: frontmatter, interface metadata, credits, README presence, and relative links.

Two invariants guard behaviour a link check cannot see:

- **Routing.** A trigger phrase two descriptions both claim sends the same request to two skills.
  The fix lives in the descriptions: each names the other, so the agent reading them has a
  tiebreaker. Testing whether a description actually fires needs a model; this catches the half
  that does not.
- **Documentation drift.** A `<!-- check:code -->` tag names a finding the skill's checker can
  emit, so a renamed or deleted check leaves a stale reference instead of a silent one. The
  reverse holds too: every code the checker emits is named somewhere, so no enforcement is
  invisible to the agent reading a failure.

    python3 scripts/check-skills.py

Stdlib only. Exits 1 and lists every problem it finds.
"""

from __future__ import annotations

import re
import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
READMES = ("README.md", "README.zh-CN.md")
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
LINK = re.compile(r"\]\(([^)\s]+)\)")
FENCE = re.compile(r"^\s*(```|~~~)")
TRIGGER_LIST = re.compile(r"(?:\bsays\b|[：:])\s*(.+?)(?:\.(?=\s[A-Z])|\.$|$)")
TAG = re.compile(r"<!--\s*check:([a-z0-9,\s-]+?)\s*-->")
EMIT = re.compile(r'\b(?:err|warn|note)\(\s*"([a-z0-9-]+)"')


def frontmatter(text: str) -> list[str] | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return lines[1:i]
    return None


def top_level(lines: list[str]) -> dict[str, str]:
    """Map top-level keys to their value, joining block scalars."""
    out: dict[str, str] = {}
    key: str | None = None
    buf: list[str] = []
    for line in lines:
        match = re.match(r"([A-Za-z0-9_-]+):(.*)\Z", line)
        if match and not line.startswith(" "):
            if key is not None:
                out[key] = "\n".join(buf).strip()
            key, buf = match.group(1), [match.group(2).strip()]
        elif key is not None:
            buf.append(line.strip())
    if key is not None:
        out[key] = "\n".join(buf).strip()
    return out


def unquote(value: str) -> str:
    return value.strip().strip("\"'").strip()


def yaml_block(text: str, key: str, indent: int) -> list[str] | None:
    """Return the value lines of `key:` at a fixed indent, or None when the key is absent."""
    prefix = " " * indent + key + ":"
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith(prefix):
            rest = line[len(prefix) :].strip()
            if rest:
                return [rest]
            block = []
            for nxt in lines[i + 1 :]:
                if not nxt.strip():
                    continue
                if not nxt.startswith(" " * (indent + 1)):
                    break
                block.append(nxt.strip())
            return block
    return None


def has_items(block: list[str] | None) -> bool:
    return bool(block) and any(item not in ("[]", "{}") for item in block)


def links(text: str) -> list[str]:
    body = []
    in_fence = False
    for line in text.splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            body.append(re.sub(r"`[^`]+`", "", line))
    return LINK.findall("\n".join(body))


def description_of(path: Path) -> str:
    skill_md = path / "SKILL.md"
    if not skill_md.is_file():
        return ""
    data = frontmatter(skill_md.read_text(encoding="utf-8")) or []
    return " ".join(top_level(data).get("description", "").split())


def triggers(description: str) -> list[str]:
    """The slash-separated branches a description lists after 'says' or a colon."""
    found: list[str] = []
    for match in TRIGGER_LIST.finditer(description):
        chunk = match.group(1)
        if "/" not in chunk:
            continue
        for item in chunk.split("/"):
            item = item.strip(" .,")
            if 1 < len(item) < 30:
                found.append(item)
    return list(dict.fromkeys(found))


def mentions(text: str, name: str) -> bool:
    return re.search(rf"(?<![\w-]){re.escape(name)}(?![\w-])", text) is not None


def check_routing(descriptions: dict[str, str]) -> list[str]:
    claims: dict[str, set[str]] = {}
    for name, text in descriptions.items():
        for phrase in triggers(text):
            claims.setdefault(phrase, set()).add(name)

    problems = []
    for phrase, names in sorted(claims.items()):
        for a, b in combinations(sorted(names), 2):
            if not mentions(descriptions[b], a) or not mentions(descriptions[a], b):
                problems.append(
                    f"{a}: trigger {phrase!r} is also claimed by {b}; name each other in the descriptions"
                )
    return problems


def check_rule_tags(path: Path) -> list[str]:
    """Every tag names a code the skill's checker emits, and every emitted code is tagged."""
    tagged: set[str] = set()
    for md in sorted(path.rglob("*.md")):
        for group in TAG.findall(md.read_text(encoding="utf-8")):
            tagged.update(code.strip() for code in group.split(",") if code.strip())

    emitted: set[str] = set()
    scripts = path / "scripts"
    if scripts.is_dir():
        for script in sorted(scripts.glob("*.py")):
            emitted.update(EMIT.findall(script.read_text(encoding="utf-8")))
    if not tagged and not emitted:
        return []
    if tagged and not emitted:
        return [f"{path.name}: {len(tagged)} check tag(s) but no codes in scripts/*.py"]

    problems = [
        f"checker emits {code!r}; add <!-- check:{code} --> where it is documented"
        for code in sorted(emitted - tagged)
    ]
    problems += [
        f"<!-- check:{code} --> names no code the checker emits"
        for code in sorted(tagged - emitted)
    ]
    return [f"{path.name}: {problem}" for problem in problems]


def check_skill(path: Path) -> list[str]:
    problems = []
    skill_md = path / "SKILL.md"
    if not skill_md.is_file():
        return [f"{path.name}: no SKILL.md"]

    data = frontmatter(skill_md.read_text(encoding="utf-8"))
    if data is None:
        problems.append("SKILL.md has no YAML frontmatter")
    else:
        fields = top_level(data)
        name = unquote(fields.get("name", ""))
        if not name:
            problems.append("frontmatter has no name")
        elif name != path.name:
            problems.append(f"frontmatter name {name!r} does not match directory {path.name!r}")
        if not NAME.fullmatch(name):
            problems.append(f"name {name!r} is not lowercase-hyphenated")
        description = fields.get("description", "")
        if unquote(description) in ("", "|", ">", "|-", ">-"):
            problems.append("frontmatter has no description")

    interface = path / "agents" / "openai.yaml"
    if not interface.is_file():
        problems.append("no agents/openai.yaml")
    else:
        text = interface.read_text(encoding="utf-8")
        for key in ("display_name", "short_description", "triggers"):
            if not has_items(yaml_block(text, key, 2)):
                problems.append(f"agents/openai.yaml has no {key}")

    if (path / "CREDITS.md").exists() != (path / "LICENSE").exists():
        problems.append("CREDITS.md and LICENSE must come together")

    for md in sorted(path.rglob("*.md")):
        for target in links(md.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "mailto:", "#", "amp-", "file:")):
                continue
            if not (md.parent / target.split("#")[0]).exists():
                problems.append(f"{md.relative_to(path)} links to missing {target}")

    return [f"{path.name}: {problem}" for problem in problems]


def check_readmes(names: list[str]) -> list[str]:
    problems = []
    for readme in READMES:
        path = ROOT / readme
        if not path.is_file():
            problems.append(f"{readme} is missing")
            continue
        text = path.read_text(encoding="utf-8")
        for name in names:
            if f"(skills/{name})" not in text:
                problems.append(f"{readme}: no table row for {name}")
            if not re.search(rf"(?m)^\s{{2}}{re.escape(name)}/\s", text):
                problems.append(f"{readme}: no layout entry for {name}")
    return problems


def main() -> int:
    if not SKILLS.is_dir():
        print(f"no skills/ directory at {SKILLS}", file=sys.stderr)
        return 1

    dirs = sorted(p for p in SKILLS.iterdir() if p.is_dir())
    problems = [p for path in dirs for p in check_skill(path)]
    problems += check_routing({path.name: description_of(path) for path in dirs})
    problems += [p for path in dirs for p in check_rule_tags(path)]
    names = [path.name for path in dirs]
    problems += check_readmes(names)

    if problems:
        for problem in problems:
            print(problem)
        print(f"\n{len(problems)} problem(s) across {len(dirs)} skills")
        return 1

    print(f"ok: {len(dirs)} skills")
    return 0


if __name__ == "__main__":
    sys.exit(main())
