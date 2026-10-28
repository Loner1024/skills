---
name: deslop
description: |
  Load before git commit, git push, opening a PR, or reporting a code change complete. Load it even
  if you think you know it; the file is the source of truth. Remove AI-generated code slop from the
  branch diff: comments that restate the line, defensive checks on trusted paths, `any` casts, deep
  nesting, and patterns that disagree with the surrounding file. Apply it even when the user did
  not mention slop or style.
  Also load when the user says 提交 / 推送 / 开 PR / 清理分支 / 清理 AI 生成的代码 / 去掉多余注释 /
  代码去噪 / 简化嵌套 / 清理防御性检查.
  Not for prose (use unslop), architecture decisions, or behavior changes.
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
