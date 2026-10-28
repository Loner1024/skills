# Connectors

Modules name tool dependencies as `~~category` — `~~design tool`, `~~knowledge base`,
`~~project tracker`, `~~user feedback`, `~~product analytics`, `~~chat`. The category, not the
product: `~~design tool` is Figma, Sketch, Framer, or whatever this session has connected.

| Category | Typically | What a module does with it |
| --- | --- | --- |
| `~~design tool` | Figma | Pulls the frame, tokens, and layer structure instead of reading a screenshot |
| `~~knowledge base` | Notion, Confluence | Brand voice, component docs, prior research |
| `~~project tracker` | Linear, Jira, Asana | Files findings, or links a handoff to its ticket |
| `~~user feedback` | Intercom, Productboard, Dovetail | Pulls raw quotes and tickets for synthesis |
| `~~product analytics` | Amplitude, Mixpanel | Checks a qualitative theme against usage data |
| `~~chat` | Slack, Teams | Finds the discussion behind a decision |

A connector is optional. Without one the module works from what the user pasted, and the output
says which inputs were supplied rather than retrieved. Never describe a tool's contents you could
not open: "I can't reach Figma from here — paste the frame or a screenshot" is the answer, not a
plausible guess at what the file holds.
