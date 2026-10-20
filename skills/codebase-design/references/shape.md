# Shape behind the seam

The interface is half the design. The other half is the data shape and where validation lives.

## Model the domain

Encode the real domain in a data structure instead of scattering it across conditionals. A structure that matches the domain makes invalid states unrepresentable and deletes branches.

Reach for:

- A state machine instead of scattered booleans, phases, or lifecycle checks.
- A typed model instead of loose parameters or repeated shape assumptions.
- A map, registry, lookup table, or discriminated union instead of branching spread across files.
- A reducer or command/event model instead of ad hoc state mutations.
- A module organised around one body of domain knowledge instead of a sequence such as load, validate, transform, and save. Execution order is not ownership.
- A queue, cache, index, graph, tree, or normalized collection where the access pattern calls for it.

Do not force an abstraction. Prefer boring code if the current shape is already clear, local, and unlikely to grow. Be skeptical of an abstraction that adds indirection without removing branches, duplicated rules, invalid states, or lifecycle risk.

The sign that you skipped this: a new feature grows an existing if/else chain by one more branch, or a second boolean that must stay in sync with the first. Temporal decomposition is another sign.

## Put validation at the boundary

Validate, narrow, and handle errors at system boundaries: CLI arguments, config files, external APIs, network protocols. Inside the system, trust the types; do not re-validate. Keep business logic in pure functions and the framework shell thin.

Expose domain concepts, not the boundary's private representation. Do not re-export transport, storage, framework, or wire types through the public surface.

Two tests:

- "Is this data crossing a system boundary right now?" If not, validation is redundant.
- "Can this be a pure function that the shell just calls?" If yes, extract it.

## Make illegal states unrepresentable

Brand semantic primitives: `UserId` and `OrderId` are strings underneath but should not be interchangeable. Validate once at creation, trust the type downstream. Parse external data at every boundary. Exhaust variants; do not leave an unhandled case. Derive from the authoritative schema instead of maintaining a second copy.

## Test behaviour, not implementation

A test is a claim about what the code does for its users: a caller, an end user, or another service. Assert what they can observe through the interface: return values, errors, state they can read back, and effects on other systems. Do not assert private helpers, internal call order, intermediate data, or which collaborator did the work.

If a test has to change when only the implementation changes, it is testing past the interface.

## Migrate callers, then delete the legacy API

When introducing a new internal API while old callers exist, update the callers and delete the old API in the same wave. Do not preserve a compatibility layer unless an external user depends on it. Tests that only protect the pre-refactor implementation go with the old API.
