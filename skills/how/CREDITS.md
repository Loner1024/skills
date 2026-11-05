# Credits

`how` is Lauren Tan's `how` skill from [cursor/plugins](https://github.com/cursor/plugins), at
`pstack/skills/how/SKILL.md` (commit `bb68f2365eceafa0cb2d253112f675acf5f144cc`).

The body of `SKILL.md` is upstream's except one paragraph: Cursor's `Task`/`readonly` setup and
the per-role model lines are replaced with portable subagent guidance, including what to do when
the environment has no subagents. The two reference prompts, `explorer-prompt.md` and
`explainer-prompt.md`, are byte-identical to upstream.

The frontmatter drops `disable-model-invocation` so the skill can fire on its own trigger, and the
description is rewritten for model invocation with Chinese triggers; upstream writes it for user
invocation only.

MIT license and copyright notice in [LICENSE](LICENSE).
