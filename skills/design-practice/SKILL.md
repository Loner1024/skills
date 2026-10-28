---
name: design-practice
description: |
  Product design work that happens around the code: critique a screen or mockup, audit or document a
  design system, write a developer handoff spec, write or review UX copy, plan user research, or
  synthesize transcripts and usability notes into themes. Six modules carried from Anthropic's design
  plugin, routed by the artifact in hand.

  Use when the user brings a design artifact — a Figma link, a screenshot, a mockup, a component
  library, a spec, a transcript, survey rows, or a line of interface copy — and wants judgment,
  documentation, or a deliverable: 设计评审 / 设计走查 / 设计系统 / 交接标注 / UX 文案 /
  用户研究 / 访谈整理. For visual craft, motion, and performance in running code, use web-craft.
---

# Design practice

Six routes over one body of design work that is not implementation. The modules under `modules/`
are [Anthropic's design plugin](https://github.com/anthropics/knowledge-work-plugins), carried under
Apache-2.0 (`modules/LICENSE.txt`) with their accessibility sections removed. This file routes by
the artifact in hand and says how to read a slash command as a module.

## Route

| The user brings | Module | It returns |
| --- | --- | --- |
| A screen, flow, Figma link, or screenshot to judge | `design-critique` | First impression, usability, hierarchy, consistency, priority fixes |
| A component library, tokens, or one component to audit, document, or extend | `design-system` | Naming and token coverage, state completeness, component documentation, new-pattern spec |
| A finished design that needs an engineering spec | `design-handoff` | Measurements, tokens, props, states, responsive behaviour, edge cases, motion |
| Page copy — a headline, CTA, error, empty state, confirmation, or onboarding text | `ux-copy` | Recommended copy, alternatives with tone, rationale, localization notes |
| Transcripts, survey rows, usability notes, or tickets to distill | `research-synthesis` | Themes with prevalence, insight→opportunity table, segments, recommendations |
| A study to plan — questions, method, guide, sample | `user-research` | Method choice, interview guide, analysis framework, deliverables |

Two pairs look alike. Pick by what the user brought:

- **One screen vs. the system behind it.** Critique judges a single artifact against usability and
  design principles. `design-system` audits the repeated parts — naming, tokens, states, docs.
- **Data in hand vs. a study to run.** Synthesis when there are transcripts or rows to read; research
  when the method, questions, or guide are still open.

## Rules

1. **Route by the artifact, not the vocabulary.** "Look at this" with a screenshot is a critique;
   with a component library it is a system audit; with a transcript it is synthesis. State the route
   in one line — "Screenshot → `design-critique`" — before the work starts.

2. **The module is the standard.** Read it in full before acting. Its framework, output format, and
   thresholds apply unchanged; this file adds routing and the reading rules below, and nothing else.
   Where the input cannot support a step — a two-second first impression from a paragraph — answer
   from what it does support and label the inference. Where the step needs a measurement, mark it
   unchecked: a screenshot supports a judgment; it does not produce a number.

3. **Read the command framing as prose, with one exception.** `design-system`'s
   `audit | document | extend` is a real mode selector: choose the mode from the ask, and when the ask
   spans two, deliver the audit and name the other as a follow-up pass. Everything else the plugin
   left behind is inert — `argument-hint`, `## Usage`, `$ARGUMENTS`, `@$1`, and a `## Tips` section
   addressed to the person who typed the command. The design reference is whatever the task supplied,
   and the Tips are the user's advice, not yours. A module's "What I Need From You" is an intake
   checklist: fill it from context, and ask in one batch only for what is missing and would change the
   answer. When a module says "otherwise ask the user for the design", a screen the task already
   describes is the design.

4. **Connectors are optional and never assumed.** `~~design tool` and friends resolve to whatever is
   actually connected — see [`CONNECTORS.md`](CONNECTORS.md). Work from what the user supplied, and
   open the output with one line saying what was supplied rather than retrieved; that line, alongside
   the metadata a module's output already starts with, is the only addition the output shape allows.
   Pulling from a tool you cannot reach is a fabricated finding.

5. **The modules are fixed.** If a module is wrong for the job, the route was wrong: pick another, or
   work outside this skill. Editing one to fit a task breaks the standard the next reader relies on.

6. **One module at a time.** A page runs copy → build → critique → handoff: the build is
   `web-craft`'s, the rest are modules here. Run each in turn and keep each module's own output
   shape, plus the provenance line rule 4 allows. Do not merge two outputs into one improvised
   format.

7. **The module's Output section is the deliverable.** A chat summary that skips it is unfinished
   work. When the output runs past a screen, write it to a file the user can keep and name the path.

8. **No artifact, no critique — but copy and specs still work.** A page that does not exist yet has
   nothing for `design-critique` or `design-system` to judge; say so rather than inventing a screen.
   `ux-copy` and `design-handoff` work from a brief, and the build itself belongs to `web-craft`.

## With web-craft

A page designed from scratch is a build job: `web-craft` owns layout, type, spacing, motion, and the
code. This skill owns the parts decided in words:

- `ux-copy` before the layout settles — the copy decides how much room a section needs, so set its
  length targets and state them in Rationale instead of asking for limits that do not exist yet.
- `design-critique` once the page renders — screenshot it and judge first impression, hierarchy,
  usability, and consistency. Findings that need code go back to `web-craft`.
- `design-handoff` only when a separate engineer implements the design.
