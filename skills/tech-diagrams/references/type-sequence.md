# Type family: sequence and lifecycle

Covers **sequence diagrams**, **request/build lifecycle**, **state machines**, and **swimlanes**.
Pattern sources: Anthropic's MCP figure and coding-agent flow, OpenAI's Codex loop snapshots,
Cursor's step-through protocol diagrams, Vercel's request lifecycle.

## Sequence

Use for message exchanges between named actors (handshakes, tool calls, retries).

- Actor headers are 12-16px above the top message; lifelines are dashed 1px `#7C8389`.
- Message arrows are horizontal, left or right, labelled with the payload name as it appears in
  the protocol (`tools/call`, `tools/call result`, `GET /meta`). Payload names in mono.
- Returns are dashed and slightly lighter; name them too (`result`), never leave a bare arrow.
- **More than 6 messages: do not draw a static sequence.** Either split by phase (connect,
  exchange, settle) or produce a step-through pair of frames. A 12-arrow static sequence is
  unreadable on a doc column.
- Activation bars (the thin rects on a lifeline) are optional; include them only when the reader
  needs to know which side is busy.
- An arrow stops 8-10px short of the dashed lifeline it targets (the one place a gap is deliberate;
  against a box, the tip touches the border). Start and end every arrow on a *named* lifeline - an
  arrow that begins beside a lifeline instead of on it reads as coming from nowhere.
- A self-call comes off the lifeline, turns back into it, and carries its guard (`retry < 3`).

Canvas: one column per actor at 160-200px pitch, lifelines 320-420px tall.

## Lifecycle / pipeline

Use for a request path, build pipeline, deployment chain, or any staged process with one subject.

- Stages left to right on one baseline; optional numbering above the stage (`01`, `02`) in mono.
- One stage may carry the accent (the gate, the new step, the measured bottleneck).
- Add the elapsed/cost annotation under a stage when the story is about where time goes
  (`19.1 ms p99`, `~16.6 s saved`) - numbers come from the user, never invented.
- Stages that run concurrently get stacked in a lane with a shared bracket, not a wider box.

## State machine

Use when the reader must enumerate states, transitions, and the condition that moves you.

- States are rounded rects; the initial state carries a filled dot, terminal states a double
  border. Do not use diamonds here; the diamond is a *decision* primitive.
- Every transition carries its trigger, and its guard when one exists (`retry < 3`).
- Unreachable states are noise: omit them.
- If two transitions share a trigger, that is a missing guard - resolve it before drawing.

## Swimlane

Use for handoffs across roles or trust boundaries (client / edge / origin, or analyst / service).

- One lane per role, header on the left (11px mono uppercase), lanes separated by hairlines, not
  by nested cards.
- Handoffs are the arrows: label the protocol and direction; the crossing point of a boundary is
  the most important pixel in the figure, so give it room.
- A lane never contains a subprocess diagram; if it needs one, that is a separate figure.

## Worked example: retry lifecycle (lifecycle + accents)

```xml
<svg role="img" aria-labelledby="retry-title retry-desc" viewBox="0 0 1100 300" width="1100" height="300"
     xmlns="http://www.w3.org/2000/svg"
     font-family="Inter, PingFang SC, Hiragino Sans, Heiti SC, Noto Sans CJK SC, sans-serif">
  <title id="retry-title">Write path with a bounded retry</title>
  <desc id="retry-desc">A write enters the log, is applied to the primary, and on conflict is replayed up to three times before surfacing an error.</desc>
  <rect width="1100" height="300" fill="#0A0A0B"/>
  <path d="M 248 152 H 344" fill="none" stroke="#9BA1A6" stroke-width="1" marker-end="url(#arrow)"/>
  <path d="M 488 152 H 584" fill="none" stroke="#5E6AD2" stroke-width="1" marker-end="url(#arrow-accent)"/>
  <path d="M 728 152 H 824" fill="none" stroke="#9BA1A6" stroke-width="1" marker-end="url(#arrow)"/>
  <path d="M 636 184 V 240 H 412 V 184" fill="none" stroke="#9BA1A6" stroke-width="1"
        stroke-dasharray="4 3" marker-end="url(#arrow)"/>
  <g class="edge-label">
    <rect class="mask" x="452" y="228" width="148" height="20" rx="3" fill="#0A0A0B"/>
    <text x="526" y="243" fill="#9BA1A6" font-size="11" text-anchor="middle">conflict · retry &lt; 3</text>
  </g>
  <g class="node">
    <rect x="64" y="120" width="184" height="64" rx="8" fill="#111214" stroke="rgba(255,255,255,.08)"/>
    <text x="80" y="146" fill="#EDEDF0" font-size="13" font-weight="500">Write log</text>
    <text x="80" y="166" fill="#9BA1A6" font-size="11" font-family="Menlo, SF Mono, monospace">append-only</text>
  </g>
  <g class="node">
    <rect x="344" y="120" width="144" height="64" rx="8" fill="#111214" stroke="rgba(255,255,255,.08)"/>
    <text x="360" y="146" fill="#EDEDF0" font-size="13" font-weight="500">Replay</text>
    <text x="360" y="166" fill="#9BA1A6" font-size="11" font-family="Menlo, SF Mono, monospace">idempotent</text>
  </g>
  <g class="node focal">
    <rect x="584" y="120" width="144" height="64" rx="8" fill="#171A2B" stroke="#5E6AD2"/>
    <text x="600" y="146" fill="#EDEDF0" font-size="13" font-weight="500">Primary</text>
    <text x="600" y="166" fill="#A7AEF8" font-size="11" font-family="Menlo, SF Mono, monospace">apply</text>
  </g>
  <g class="node">
    <rect x="824" y="120" width="184" height="64" rx="8" fill="#111214" stroke="rgba(255,255,255,.08)"/>
    <text x="840" y="146" fill="#EDEDF0" font-size="13" font-weight="500">Acknowledge</text>
    <text x="840" y="166" fill="#9BA1A6" font-size="11" font-family="Menlo, SF Mono, monospace">commit ts</text>
  </g>
</svg>
```

Caption / alt: "A write is appended to the log, replayed into the primary, and on a conflict
re-enters replay while attempts stay under three; the caller is acknowledged only after commit."

## Mistakes to avoid

- Sequence diagrams with unlabelled arrows or with more than six messages on a doc column.
- Treating a *step* as a *state* (steps are lifecycle; states need guards and re-entry).
- Swimlanes drawn as nested cards instead of labelled lanes.
