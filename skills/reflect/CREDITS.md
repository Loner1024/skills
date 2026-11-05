# Credits

`reflect` is Lauren Tan's `reflect` skill from [cursor/plugins](https://github.com/cursor/plugins),
at `pstack/skills/reflect/SKILL.md` (commit `bb68f2365eceafa0cb2d253112f675acf5f144cc`).

This is a rewrite, not a copy. From upstream: the three reviewer lenses (judgment, tooling,
divergent), the synthesizer's admission criteria, the Accepted / Rejected / Backlog output, the
approval gate, and the rule that a body edit needs the session to have used that skill. The four
per-lens prompt files are folded into one section and made portable.

Absorbed from this repository's retired `retro` skill: the seven hunting places, severity as
frequency times cost, the moment / change / payoff / cost contract, the implementation-versus-review
context argument, and the table of where each change lands.

Removed from upstream: Cursor's `Task` and model-routing instructions, fixed transcript paths,
`create-skill` routing, plugin-cache paths, and the devex-tracker assumption. They are replaced
with portable instructions that name `writing-for-agents` for skill edits.

MIT license and copyright notice in [LICENSE](LICENSE).
