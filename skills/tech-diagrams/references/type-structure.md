# Type family: structure

Covers **architecture topology**, **data flow**, **layers / nesting**, and **loop / flywheel**.
Pattern sources: Anthropic's pattern catalog (one figure per named pattern), Vercel's request
lifecycle, Cursor's protocol diagrams, OpenAI's Habitat figures.

## Architecture topology

Use when the reader must see who connects to whom and where things run.

- Partition with **zone bands** (uppercase 11px mono tags): `CLIENT`, `EDGE`, `REGION`, `ORIGIN`.
- Left-to-right or top-to-bottom flow only; pick one axis per figure.
- Solid arrow = data plane (a request, a write). Dashed arrow = control plane, optional path,
  async, or a return leg. State the dashed meaning in the caption.
- Real names in nodes (`Postgres`, `Turbopuffer`, `envoy`), never "Service A".
- Max 9 nodes. A tenth means split into overview + detail, or drop a node the caption can carry.

Layout recipe (1100x480 canvas): bands at x=88/448/808, three columns of 184px nodes, 24px gaps,
one row per tier; put the focal node (the change under discussion) in the middle column with the
accent treatment.

### Arrows carry the argument

Direction is the whole claim, so it has to survive a reader who starts at any node:

- One arrow per relationship. If two boxes both give and take, draw two arrows or label the single
  one `claim / fence` - never leave the reader to guess which way the intent runs.
- The head points at the **consumer** of the payload, not at the producer. A "worker hands the
  runner a pinned spec" relationship therefore points *up* into the runner, and the tail sits on
  the worker's edge.
- The tail sits on the source's edge. If a relationship has no visible source in the figure, it is
  not a relationship - either draw the node, or drop the arrow. A comment or `desc` naming a node
  that the figure does not contain (a "sandbox" that was never drawn) is a defect the reader cannot
  see and the linter cannot check, so read the `desc` against the boxes before delivering.
- Label every arrow whose direction is not obvious from reading order: right-to-left returns,
  bottom-to-top writes, anything into a store. `self_check.py` warns about unlabelled connectors
  under 48px.
- A short arrow with no label and no visible attachment is worse than no arrow: it reads as a
  smudge between two boxes. Delete it, or make both ends land and give it a word.

## Data flow

Use when data is transformed, aggregated, or split across stages.

- Stages left to right; each stage shows input -> output, or the key it produces.
- Stores get a distinct shape (accent bar / top hairlines) plus a mono key label
  (`shard-04f2`, `pk=path`).
- Encode volume when it matters: a thicker stroke or a small numeric label (`200 KB`,
  `1.2M keys`). Do not draw Sankey widths by hand without labelling them.
- Fan-in/fan-out is a merge/split point, not a node.

## Layers / nested

Use for abstraction layers, render trees, container and scope relationships.

- Draw only adjacent layers' interactions; skip the connections a reader can infer.
- Layer names left-aligned, 11px mono, uppercase.
- Four layers is the practical maximum; five means the figure is two figures.
- Containment is expressed with a band + inset, never with nested rounded cards.

## Loop / flywheel

Use for feedback systems: agent loop, evaluator-optimizer, retry/backoff, RL.

- Cycle layout: nodes on a ring or a two-row racetrack with the return arc drawn as an arc.
- **The condition lives on the arc**: `"Until tests pass"`, `"More research needed?"`, `"retry
  once"`. No unlabelled arcs.
- The decision node names both exits: `hit` / `miss`, `(x) Exit loop` / `(v) Continue loop`.
- Show where state accumulates (memory, checkpoint) as a node the arc passes through.

## Worked example: sharded lookup (architecture + data flow)

```xml
<svg role="img" aria-labelledby="lookup-title lookup-desc" viewBox="0 0 1100 320" width="1100" height="320"
     xmlns="http://www.w3.org/2000/svg"
     font-family="Inter, PingFang SC, Hiragino Sans, Heiti SC, Noto Sans CJK SC, sans-serif">
  <title id="lookup-title">Sharded metadata lookup</title>
  <desc id="lookup-desc">A request checks the edge cache, misses, fetches one 200 KB shard, and binary-searches its index for the path.</desc>
  <rect width="1100" height="320" fill="#0A0A0B"/>
  <rect x="88" y="88" width="456" height="152" rx="8" fill="#16181C" opacity=".55"/>
  <text x="104" y="110" fill="#7C8389" font-size="11" font-family="Menlo, SF Mono, monospace" letter-spacing="0.8">EDGE</text>
  <!-- connectors first -->
  <path d="M 304 164 H 448" fill="none" stroke="#9BA1A6" stroke-width="1" marker-end="url(#arrow)"/>
  <path d="M 632 164 H 776" fill="none" stroke="#5E6AD2" stroke-width="1" marker-end="url(#arrow-accent)"/>
  <g class="edge-label">
    <rect class="mask" x="328" y="144" width="96" height="16" rx="3" fill="#111214"/>
    <text x="376" y="160" fill="#9BA1A6" font-size="11" text-anchor="middle">cache miss</text>
  </g>
  <g class="node">
    <rect x="120" y="132" width="184" height="64" rx="8" fill="#111214" stroke="rgba(255,255,255,.08)"/>
    <text x="136" y="158" fill="#EDEDF0" font-size="13" font-weight="500">Edge cache</text>
    <text x="136" y="178" fill="#9BA1A6" font-size="11" font-family="Menlo, SF Mono, monospace">cache-hit</text>
  </g>
  <g class="node focal">
    <rect x="448" y="132" width="184" height="64" rx="8" fill="#171A2B" stroke="#5E6AD2"/>
    <text x="464" y="158" fill="#EDEDF0" font-size="13" font-weight="500">Shard lookup</text>
    <text x="464" y="178" fill="#A7AEF8" font-size="11" font-family="Menlo, SF Mono, monospace">200 KB · O(log n)</text>
  </g>
  <g class="node">
    <rect x="776" y="132" width="184" height="64" rx="8" fill="#111214" stroke="rgba(255,255,255,.08)"/>
    <text x="792" y="158" fill="#EDEDF0" font-size="13" font-weight="500">Origin</text>
    <text x="792" y="178" fill="#9BA1A6" font-size="11" font-family="Menlo, SF Mono, monospace">on cold miss</text>
  </g>
</svg>
```

Caption / alt for it: "A request checks the edge cache, misses, and fetches one bounded 200 KB
shard whose index is binary-searched in O(log n), so only the matching record is parsed."

## Mistakes to avoid

- Every node styled identically, so the reader cannot find the change under discussion.
- Mixing abstraction levels (a process next to a function call) without zone bands.
- Connectors that run behind unrelated nodes or share a path.
- A dashed arrow whose meaning is never stated.
