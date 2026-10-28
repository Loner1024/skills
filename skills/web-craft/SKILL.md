---
name: web-craft
description: |
  Load before writing or changing any web UI, even a small one: page layout, components, CSS,
  theme, color, typography, spacing, motion, responsive behavior, or a design review. Load it even
  if you think you know it; the file is the source of truth. It routes to the module that owns the
  job (polish, motion, review, performance, mobile).
  Also load when the user says 重做前端 / 改版 / 界面 / 页面 / 样式 / 主题 / 浅色 / 深色 / 配色 /
  排版 / 间距 / 太丑 / 太挤 / 看着不对 / 加动效 / 动画 / 交互 / 手机端 / dashboard / 后台 /
  组件 / 设计评审.
  Not for backend, API, data-fetching, or state-management work on its own; load it for the UI layer
  of a full-stack task.
metadata:
  version: "0.1.0"
---

# Web design engineering

One entry point, fourteen modules. This file does one thing: classify the job and route to the
module that owns it. The modules carry the standards, and they are
[Emil Kowalski's design-engineering skill set](https://github.com/emilkowalski/skills), carried
verbatim under `modules/` — the entry point adds routing and overrides nothing.

## Initial Response

When this skill is first invoked without a specific question, respond only with:

> I'm ready to design and build web interfaces with you — design, motion, review, or platform
> fixes. What are we working on?

Do not provide any other information until the user asks a question.

## How to dispatch

1. **Classify by the job, not the words.** "Make this popover feel right" is a motion build;
   "why does my drawer stutter" is performance; "review the motion in this diff" is a critique.
   Use the routing table below.
2. **Read the module in full before acting** — `modules/<module>/MODULE.md`. Read its sibling files
   only when the module tells you to; each module names its own references.
3. **The module is the standard.** Its gates, hard rules, output formats, and refusals apply
   unchanged. If a module says "don't animate this", that is the answer — this file does not soften
   it, and having an entry point is never a reason to skip a gate.
4. **A routed module's Initial Response does not fire.** Those greetings are for a bare invocation
   of the module on its own. When this entry point routed a concrete task to it, start the work.
5. **Explicit-only modules stay explicit.** `review-animations`, `prototype`, and `pick-ui-library`
   are entered only when it is explicit: the user asks for that job (a critique, variants, a
   library pick), the user names the module, or the module you already routed to tells you to
   invoke it — `animate` does exactly that when the task turns out to need a component. This entry
   point never adds one on its own initiative.
6. **The user naming a module wins.** If they ask for `prototype` or `review-animations` by name,
   route straight there; the table below is for jobs they describe instead.
7. **Load one module at a time.** A chain of five modules is a few thousand lines of context. Read
   the module that owns the job; the next one only when its turn comes.
8. **A module's own variants and handoffs beat this file's sequences.** Where a module defines
   `execute <plan>`, `keep <variant>`, or a handoff of its own, that path wins over "Combining
   modules" below.
9. **State the route in one line** before the work starts — "Motion build → `animate`".
10. **Nothing matches?** Say so and work from your own judgment. Do not force a module.

## Routing table

### Build

| The user wants | Module | Comes back |
| --- | --- | --- |
| Build or change a piece of UI — a page, a component, a polish pass | [`emil-design-eng`](modules/emil-design-eng/MODULE.md) | Design decisions plus implementation at the house bar |
| Add or change motion on a named component — animate it, build a transition | [`animate`](modules/animate/MODULE.md) | Implementation: tool, properties, curve, duration, reduced motion |
| The same, in a React Native or Expo app | [`animate-expo`](modules/animate-expo/MODULE.md) | Reanimated and Gesture Handler implementation |
| Several genuinely different versions to flip through and pick one | [`prototype`](modules/prototype/MODULE.md) *(explicit only)* | Variants behind a visual picker |
| Pick a UI library — "which one should I use", "should I install X" | [`pick-ui-library`](modules/pick-ui-library/MODULE.md) *(explicit only)* | One curated pick, or a clear "not covered" |
| Sonner toasts — setup, styling, or toasts that misbehave | [`ask-sonner`](modules/ask-sonner/MODULE.md) | Working setup, recipes, troubleshooting |

### Review and harden

| The user wants | Module | Comes back |
| --- | --- | --- |
| Review UI or design code that is not motion | [`emil-design-eng`](modules/emil-design-eng/MODULE.md) | Findings in its required Before/After/Why table |
| A motion review of a diff or a file, against a strict craft bar | [`review-animations`](modules/review-animations/MODULE.md) *(explicit only)* | Tiered findings against ten standards |
| Audit all motion in a codebase and plan the fixes | [`improve-animations`](modules/improve-animations/MODULE.md) | Prioritized audit plus self-contained plans any agent can execute |
| Sweep a page or a codebase for what should animate — and what should not | [`find-animation-opportunities`](modules/find-animation-opportunities/MODULE.md) | A short, high-conviction list with exact recipes, read-only |
| Stress-test a component with worst-case data | [`break-ui`](modules/break-ui/MODULE.md) | What broke, behind a demo/worst-case toggle, with fixes |

### Diagnose

| The user wants | Module | Comes back |
| --- | --- | --- |
| Motion drops frames, stutters, feels janky | [`animation-performance`](modules/animation-performance/MODULE.md) | The named cause plus the fix, and what still needs a real device |
| The same, in a React Native or Expo app — `animation-performance` is web-only | [`animate-expo`](modules/animate-expo/MODULE.md) | Reanimated and Gesture Handler implementation |
| A web app feels wrong on a phone | [`mobile-native`](modules/mobile-native/MODULE.md) | Symptom → fix, across the platform layer |

### Foundations

| The user wants | Module | Comes back |
| --- | --- | --- |
| The principles behind fluid, gesture-driven interaction — why a drag, sheet, or spring feels right | [`apple-design`](modules/apple-design/MODULE.md) | Interaction design at the platform level |
| A name for a motion effect — "what's it called when…" | [`animation-vocabulary`](modules/animation-vocabulary/MODULE.md) | The term, quoted from the glossary |

## Combining modules

One module owns the job; the others inform it. The sequences that come up most:

- **A new page or feature** — `emil-design-eng` for the design decisions, then `animate` for the
  motion. `pick-ui-library` only when the user asks for a library pick or `animate` hands off to
  it; `break-ui` as an offer before shipping, not a step; `review-animations` only on request.
- **"This animation feels off"** — `animate` by default, because that is a build question;
  `animation-performance` when it drops frames; `review-animations` only when the user asks for a
  critique. Three different questions; do not substitute one for another.
- **A codebase-wide motion pass** — `improve-animations`; once it has written the plans, use its
  own `execute <plan>` variant, which dispatches the executor and reviews the diff against the
  `review-animations` bar.
- **A phone pass** — `mobile-native` removes the platform tells, then `animate` handles the motion
  itself.
- **An undecided design direction** — `prototype` to diverge, then its own `keep <variant>` to
  promote the winner and delete the harness.

These are defaults, not a pipeline: a module's own invocation variants and handoffs win, and each
module is loaded only when its turn comes.

When two modules claim the same job, the specialist wins: `animation-performance` over
`emil-design-eng` on jank, `review-animations` over `animate` on a critique.

## Not this skill

- System or architecture decisions — that is `architecture-ablation`.
- Technical figures and diagrams — that is `tech-diagrams`.
- Handing work to an external agent — that is `external-agent-handoff`.

## Attribution

Everything under `modules/` is [Emil Kowalski](https://github.com/emilkowalski/skills)'s work,
carried verbatim under the MIT license kept at
[`modules/LICENSE.txt`](modules/LICENSE.txt). Route to the modules; never edit one to fit a task —
if a module is wrong for the job, the route was wrong.

Four mechanical changes keep the single entry point single and the skill loadable where Amp serves
it:

- each module's `SKILL.md` is renamed `MODULE.md` — agents discover any file named `SKILL.md` as a
  skill of its own, which would turn one entry point into fifteen;
- the two module-internal references to that filename were updated to match;
- the upstream `LICENSE` gains a `.txt` extension, so every file in the skill has one;
- the two literal U+FFFD characters in `break-ui` are written as the escape `\uFFFD`. Upstream uses
  the replacement character to illustrate a broken surrogate pair, and hosted serving refuses a
  skill whose files contain one — this alone kept the whole skill out of the index.

Module text is otherwise byte-identical to upstream.
