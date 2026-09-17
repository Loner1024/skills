# When to draw (and when not to)

Source: `research/TAXONOMY.md`. This is gate 0 of the workflow.

## The ladder

1. **Does the reader have to *see* it?** Structure, sequence, state space, proportion, or
   topology qualify. A single number, a one-step instruction, or a list of peers does not.
2. **Would the figure restate the prose?** If yes, cut the figure. A figure earns its space by
   showing what prose cannot: who connects to whom, in what order, under what condition, at what
   proportion.
3. **Is the content stable?** A diagram that tracks a fast-moving interface becomes a liability
   with no maintenance plan. Prefer the stable concept over the volatile detail.
4. **Would a table be more precise?** Multi-attribute comparison (>= 4 columns, row-by-row
   lookup) belongs in a real `<table>`. Do not draw a table.
5. **Does it fit the budget?** > 9 nodes or >= 2 connector crossings: split into an overview plus
   a detail figure, or partition with zone bands.

## Anti-cases seen in the wild (all five companies avoid these)

| Anti-case | Do this instead |
| --- | --- |
| Linear procedure drawn as five boxes with arrows | Numbered list |
| Enumerable milestones / principles / options | Bulleted list or table |
| "One box with a label" | Write the sentence |
| Figure that paraphrases the paragraph above it | Delete one of them |
| Trade-off discussion | A table, or a curve/quadrant with the decision point marked |
| Exact multi-dimensional results | Real HTML table |
| Fast-changing UI detail | Screenshot (if available) or skip |

## Choosing between chart, diagram, and table

| Question the reader asks | Form |
| --- | --- |
| "How do the parts connect / where does this run?" | Diagram (architecture, layers) |
| "What happens, in what order, to what?" | Diagram (sequence, lifecycle) |
| "What are the possible states and how do we leave them?" | Diagram (state machine) |
| "How much better / worse?" | Chart (bars for categories, line for time) |
| "Where is the knee in the trade-off?" | Chart (curve, quadrant scatter) |
| "Which option wins on five criteria?" | Table |
| "Why did it get faster?" | Paired before/after diagram + measured chart |

## Caption and alt rules

- The caption **is** the `alt` text: one sentence, states the takeaway, no "Figure 1:" prefix in
  the embedded case (keep the `Figure NN.` prefix only when the surrounding document numbers its
  figures).
- Good: "A per-path cache fill warms one path; a shard fill warms every path assigned to that
  shard." Bad: "Diagram of the cache."
- Describe content and arrow semantics, not geometry: "the dashed arrow applies only when you
  manage the environment yourself" beats "a dashed arrow points left".
- Introduce the figure in the prose before it, without restating the caption.
- Every figure needs both a caption and an `alt`. Empty `alt=""` on a diagram is a defect even
  though some vendor blogs ship it.

## Deliberate omissions

State out loud what the figure leaves out ("this omits retries and the cold-cache path"). A
figure that silently drops a step teaches the reader something false.
