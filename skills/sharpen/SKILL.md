---
name: sharpen
description: |
  Make a task deeper, not bigger, then rewrite the prompt. Ask what a top professional in the
  field would do that the request does not ask for, what raw material they would start from
  instead of the digested version, which methods and tools they would use, and what outside the
  agent and the user would show the result is right.
  Use for /sharpen.
disable-model-invocation: true
---

I want a deeper version of this task, not a bigger one. Before rewriting it, do four things:

1. Say what a top professional in this field would do here that I'm not asking for.
2. Name the rawest material they would start from instead of what has already been digested for me.
3. Name the specific methods and tools they would use.
4. Say what, other than you or me, would show the result is right.

Then rewrite my prompt to ask for exactly that.

Leave choices that are mine to make open instead of deciding them.
