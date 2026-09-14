# Task Intake and MATT Routing

Use this when a request has a gap that could materially change the deliverable.
Do the factual lookup yourself before asking the user to decide.

## Decide whether clarification is needed

Check the intended output, audience, evidence, applicable requirements, and
completion criteria against the current task and relevant owner documents.
Examples of material gaps include an unspecified submission target, conflicting
school requirements, a changed denominator, a request to write findings without
data, or acceptance criteria that cannot be verified with available inputs.

For a routine reversible choice, use the established convention and proceed.
For a material ambiguity, briefly explain the likely defect, recommend a
specific resolution, and ask only the decision needed to proceed. Continue
independent work while it is unresolved. Do not rewrite the user's intent or
turn every short prompt into a review exercise.

## Use MATT where it helps

- For one unresolved decision, use the `grilling` principle: investigate facts,
  offer a recommendation, and clarify the decision's consequences.
- For several dependent decisions, use a small decision tree. Ask only the
  questions whose prerequisites are settled, then revisit the remaining
  branches after the answer. This is the useful part of `grill-with-docs` for
  this project; a long interview is not required for every task.
- Record settled domain terminology in `CONTEXT.md` and substantive design
  decisions in the relevant existing plan or ADR. Distinguish a proposal from
  the user's accepted decision; record only material decisions.
- Use the full `ask-matt` / `grill-with-docs` / specification flow when the user
  requests it or a substantial unresolved design benefits from it. Respect
  user-invocation restrictions on installed skills. If those wrappers are not
  available, use the decision-tree method directly.
- An already scoped task can proceed to implementation and appropriate
  verification. Reopen settled decisions only when new evidence changes them.

The user's request to avoid repeated reminders authorizes relevant checks and
routine repairs. It does not turn uncertain evidence into an accepted scientific
decision or require an extra approval for every implementation step.
