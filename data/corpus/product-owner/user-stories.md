# User stories and acceptance criteria

A user story describes a slice of value from the user's perspective so the team
can build, discuss, and validate incrementally.

## Classic format

**As a** [role], **I want** [capability], **so that** [benefit].

The "so that" matters: it ties the story to an outcome, not only to a feature.

## INVEST qualities

Good stories tend to be:

- **Independent** enough to schedule without a brittle chain
- **Negotiable** (conversation, not a contract of UI pixels)
- **Valuable** to a user or the business
- **Estimable** enough for planning
- **Small** enough to finish in a sprint or iteration
- **Testable** via clear acceptance criteria

## Acceptance criteria

Acceptance criteria define "done" for the story. Prefer concrete, checkable
conditions (Given/When/Then or a bullet checklist). They reduce rework and align
PO, design, and engineering.

Example:

- Given a logged-in user on the backlog board
- When they create a card with title and list
- Then the card appears in that list and is visible to other board members

## Product Owner practices

- Split large stories when they hide multiple outcomes.
- Keep a clear distinction between the story (intent) and tasks (implementation).
- Refine with the team before sprint commitment; update criteria when discovery
  changes the definition of success.
- Avoid stories that only say "build X screen" without the user benefit.
