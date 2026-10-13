---
name: deslop
description: |
  Remove AI-generated code slop and clean up code style. Reads the diff against main and strips what a model added without being asked: comments that restate the line, defensive checks on trusted paths, `any` casts, deep nesting, and patterns that disagree with the surrounding file.

  Use when the user asks to 清理 AI 生成的代码 / 去掉多余注释 / 代码去噪 / 简化嵌套 / 清理防御性检查, or asks to deslop a branch, review a diff for AI slop, or tidy up before a PR. Not for prose (that is unslop), and not for behavior changes.
---

# Remove AI code slop

Check the diff against main and remove AI-generated slop introduced in the branch.

## Focus Areas

- Extra comments that are unnecessary or inconsistent with local style
- Defensive checks or try/catch blocks that are abnormal for trusted code paths
- Casts to `any` used only to bypass type issues
- Deeply nested code that should be simplified with early returns
- Other patterns inconsistent with the file and surrounding codebase

## Guardrails

- Keep behavior unchanged unless fixing a clear bug.
- Prefer minimal, focused edits over broad rewrites.
- Keep the final summary concise (1-3 sentences).
