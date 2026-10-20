# Design red flags

Screen every candidate before committing. A red flag is a reason to revise or reject the shape. Assume the next contributor is an agent that sees only the files it opened, copies the nearest example, and takes the shortest path that compiles.

## Shallow module

The interface exposes a large surface while hiding little complexity. Callers coordinate several methods to complete one operation; public options expose internal stages; learning the interface does not save the caller from learning the implementation.

Fix: pull the operation behind one entry point, shrink the surface, and move policy into the callee.

## Information leakage

A representation, policy, or protocol detail appears in more than one module. Changing it requires coordinated edits. Public re-exports of transport, storage, framework, or wire types are leakage.

Fix: parse external data into domain types at the boundary. Keep storage schemas, framework objects, and protocol details private.

## Temporal decomposition

Modules are organised by execution order (load, validate, transform, save) instead of the knowledge they own. One representation and its invariants repeat across several boundaries.

Fix: group code around domain knowledge and ownership. Methods that run at different times can still belong to one module when they protect the same decisions.

## Pass-through method

A method forwards the same arguments to another method with the same shape. It adds a layer without hiding complexity.

Fix: remove it or move responsibility to the module that can complete the operation. Keep a forwarding boundary only when it adds policy, adaptation, or a distinct abstraction.

## Split ownership

More than one module writes the same state or keeps its own copy. An agent that edits one writer cannot see the others, so their rules diverge.

Fix: give each piece of state one owner. Other modules read it or ask the owner to change it.

## Two ways to do one task

The design supports more than one way to do the same task. An agent copies whichever way it finds first, so every way keeps gaining callers.

Fix: keep one way. Move callers off the others and delete them in the same change.

## Importable internals

A caller can import a module's internals. An agent takes the shortest path that compiles, so it imports them directly and they become part of the interface.

Fix: make internals unreachable from outside the module, so an import from outside fails the build.

## Hand-synced list

Two or more places list the same items, and adding an item means editing every list. An agent that sees one list updates only that one.

Fix: keep one list and derive the others from it. If a list cannot be derived, make the build fail when the lists disagree.

## Reader load

Maintainability is the work a reader must do to understand the code. Two independent axes:

- **Layers to trace.** Indirections between the question and the answer. Collapse one-caller wrappers, adapters with no second implementation, and speculative indirection. A layer that repeats the same methods and arguments adds reader load without compression.
- **State to hold.** Hidden or mutable context the reader must keep in their head. Prefer pure functions over mutation, locals over fields, fields over module state, and module state over globals. Derive instead of sync.

Name the invariant at the boundary, not in every consumer, so the reader learns it once. The test: can a new reader answer "where does X come from?" and "what can change X?" in under 30 seconds? If not, cut layers or cut state.
