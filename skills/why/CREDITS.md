# Credits

`why` is Lauren Tan's `why` skill from [cursor/plugins](https://github.com/cursor/plugins), at
`pstack/skills/why/SKILL.md` (commit `bb68f2365eceafa0cb2d253112f675acf5f144cc`).

The body of `SKILL.md` is upstream's except the runtime paragraphs: model routing,
`Task`/readonly access, Cursor's MCP discovery, and the per-role model lines are replaced with
portable guidance. Everything else, including the operating posture, the seven evidence
categories, the investigator roster, the skip rules, and the output contract, is unchanged.

All twelve files under `references/` are upstream's. One placeholder link in
`synthesizer-prompt.md`, `[PR #123](url)`, became plain `PR #123` because this repository's link
checker reads `url` as a relative path; nothing else changes.

The frontmatter drops `disable-model-invocation` so the skill can fire on its own trigger, and the
description is rewritten for model invocation with Chinese triggers; upstream writes it for user
invocation only.

MIT license and copyright notice in [LICENSE](LICENSE).
