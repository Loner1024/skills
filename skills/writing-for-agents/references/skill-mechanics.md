# Skill mechanics

The skill-specific branch of [`writing-for-agents`](../SKILL.md): what changes when the document is a skill (frontmatter, the invocation choice, and router skills). Everything else about writing it is the universal reference in `SKILL.md`.

## Invocation

Two choices, trading the two loads:

- A **model-invoked** skill keeps a `description`, so the agent can fire it autonomously, and other skills can reach it. You can still type its name: model-invocation always _includes_ user reach; a description only ever adds agent discovery, never removes the human's. The description is the skill's top-level context pointer, forced to stay loaded at all times: permanent context load in exchange for discoverability. A model-invoked skill whose content is all reference is also one home for shared reference: another skill can invoke it, so reference needed by several skills lives in one place. Mechanics: omit `disable-model-invocation`, and write a model-facing description carrying the trigger branches (the pointer-writing rules in `SKILL.md` apply in full).
- A **user-invoked** skill strips the description from the agent's reach: only the human typing its name can invoke it, and no other skill can. Zero context load, but it spends cognitive load: you are the index that must remember it exists. Mechanics: set `disable-model-invocation: true`; the `description` becomes human-facing: a one-line summary, trigger lists stripped.

Pick model-invocation only when the agent must reach the skill on its own, or another skill must. If it only ever fires by hand, make it user-invoked and pay no context load.

Shared reference that two user-invoked skills both need can live in neither: with no descriptions, neither can fire the other. Push it to a plain file outside the skill system: external reference any skill can point at.

## Splitting by invocation

The invocation cut of splitting (the sequence cut lives in `SKILL.md`): split off a model-invoked skill when you have a distinct leading word that should trigger it on its own (a trigger word you actually use in your prompts), or another skill must reach it. You pay context load for the new always-loaded description, so that independent reach has to be worth it.

## Router skills

When user-invoked skills multiply past what you can remember, that piled-up cognitive load is cured by a **router skill**: one user-invoked skill that names the others and when to reach for each, so the human has one skill to remember instead of many. It can only hint, never fire them: user-invoked skills have no description, so nothing but the human can reach them.

## Porting a skill

When the source is someone else's — a published skill, a product prompt, a plugin — the port is a fork with a debt: it drifts. Three records make the drift visible.

- **The revision you took.** The upstream repository and commit, in the skill's own files. Without it, "byte-identical to upstream" is a claim nobody can check, and the next sync cannot tell a deliberate edit from a stale copy.
- **Every mechanical change.** The renames, the removed sections, the extension added to a licence file. A reader comparing the two needs to know which differences are yours, or they will restore upstream's behaviour by accident.
- **What no longer fires.** Host-coupled pieces survive a port and silently stop working: a panel that waits for a message the new harness never sends, a tool call with no local equivalent, a link scheme that only exists on the host. Name the dead hook where the reader will meet it, and give the local replacement or say there is none.

The upstream snapshot is the cheapest receipt: keep it beside the adapted file, and the next sync becomes a diff instead of a reread.

## Testing a description

A description is a classifier over user messages, so test it as one. Build a **menu**: the candidate description beside its neighbours', one user message, and a record of whether the model reached for the skill. The menu is what makes the result mean anything; with one description in context there is nothing to route against. An **activation** is the model calling the skill; a miss is it working the request itself or reaching for a neighbour.

Cases come from branches, not synonyms. Positives cover every command family and artifact shape the description claims; negatives cover work outside the domain and the sibling whose territory is one word away. A false activation on a sibling's request is what the test exists to find, so gate it at zero. Recall is noisier: gate it per model and read category totals rather than cells, because one case swings between 0/3 and 3/3 across runs while a category that moves 30 points is telling you about the edit.

Length is the lever you will pull. Every clause is another branch competing for the selection, so the shorter description is often the higher-recall one: a rewrite from 118 to 81 words moved one model from 35% to 55% recall with false activations unchanged. Cut identity the body already carries, and synonyms that rename one branch, before adding triggers.

Run it when the description changes. It costs model calls, so it stays out of the deterministic check; the deterministic half belongs in whatever checker the skills repo runs: two skills listing the same trigger phrase must name each other in their descriptions (this repo's `scripts/check-skills.py` enforces it).
