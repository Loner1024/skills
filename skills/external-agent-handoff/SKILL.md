---
name: external-agent-handoff
description: |
  Load when implementation or investigation should go to another agent the user will run, not to
  this agent: write the handoff document and a copy-ready prompt, then check the returned work
  against the acceptance criteria. Load it even if you think you know it; the file is the source of
  truth.
  Also load when the user says 交接 / 转发 / 外部 agent / 给另一个 agent 做 / 让别的 agent 跑.
  Not for calling a subagent or doing the work here.
---

# External agent handoff

The current agent fixes the plan and the acceptance criteria, then packs the task so an external agent can run it alone and a later check can verify the result. The user forwards the prompt and brings the result back. The current agent does not call the external agent.

## When to use

**Triggers:**

- The user wants another agent to carry out work, and this agent should prepare the package.
- The user asks for a prompt to forward, a handoff, or 外部 agent 交接.
- The user returns with that agent's output, files, or report, and the handoff is still open.

**Does not trigger:**

- The current agent can finish the task in this session.
- The user wants this agent to call another agent, a subagent, or a remote runtime directly.

## 1. Write the handoff document

Save a Markdown file the user can open. Put it in the workspace unless the user names another path. The external agent must be able to find the work and judge completion from this file alone, without the current conversation.

Include:

- **Goal.** The outcome, stated so a later check can observe it.
- **Start state.** Working directory, and the branch or revision when it matters. List the facts the external agent must treat as given.
- **Write scope and authorization.** Paths it may change, and commands or actions the current task already authorizes. In a shared workspace, name the write boundary in the document.
- **Deliverables.** Files, diffs, or other artifacts it must produce.
- **Acceptance criteria.** One observable check per item. Each check names what to look at and what passing looks like.

Done when the file exists at a path you can name, and every field above is filled with this task's facts. Leave no blank for the external agent to invent.

## 2. Write the prompt

Write one prompt the user can copy and send unchanged. If the external agent can read the handoff document, point the prompt at that path and tell it to follow the file. If it cannot, put the execution content in the prompt.

The prompt tells the external agent to:

- Describe the problem and stop when a decision is ambiguous or outside the write scope.
- On completion, return the artifacts, the files changed, the commands run and their results, and anything left unfinished.

Done when the prompt contains every path, command, and criterion the work needs, and contains no placeholder or "fill this in".

## 3. Hand it to the user

Give the user the document path and the full prompt in the reply. State that the status is waiting for external execution and return.

Stop there. The handoff stays stopped until the user brings a result back.

## 4. Summarize the return

When the user brings a result, open the artifacts and read the execution report. Confirm each claimed artifact is actually present before counting the item complete.

Summarize:

- Work the report marks complete, and whether the artifact is present.
- Commands run, and the results recorded for them.
- Failures and unfinished items.

Mark an item unfinished when its artifact is missing.

## 5. Accept the result

Check each acceptance criterion against the artifact. Run the verification that criterion names, and record the command and the result.

For a failed item, find the cause first. Then fix it inside the allowed scope and run the check again, or write a revision prompt the user can forward. A revision prompt follows steps 1 through 3. Mark an item failed when it cannot be resolved.

Close with three parts:

- An execution summary.
- A verdict for each acceptance criterion: passed, failed, or unfinished, with the evidence.
- Remaining items, including anything a revision prompt still has to cover.

Done when every criterion has a verdict, and the evidence is something you checked.
