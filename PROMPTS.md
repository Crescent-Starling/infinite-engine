# Copy/paste prompts for Codex

## Prompt A — First planning pass (recommended before code)

```text
Read AGENTS.md, README.md, PLANS.md, docs/PROJECT_SPEC.md,
docs/ARCHITECTURE.md, docs/DATA_CONTRACTS.md and docs/DEMOS.md.
Do not code yet. Treat the documents as a target product specification, not
proof of implementation. Evaluate feasibility for a local-first solo course
project. Identify unresolved high-impact decisions, dependency and data-model
risks, and a milestone plan with test/acceptance gates. Prioritize the invariant:
knowledge representation, knowledge views and personal cognition are separate.
Keep conversation-first and structure-first as equal user entry points.
Propose no more than 8 questions that genuinely block implementation; document
reversible assumptions for everything else. Produce a short plan and proposed
ADRs. Do not replace the product with a simple PDF chatbot.
```

## Prompt B — Implement the first bounded slice

```text
Read AGENTS.md and tasks/00-repository-foundation.md, and inspect the repo.
Execute milestone M0 only. Before editing, list paths you will change, tests,
assumptions, and things explicitly out of scope. Build a locally executable
FastAPI + React/TypeScript shell without inventing functional AI features.
Run the available tests, document precise verification and manual startup.
Update PLANS.md only with observed milestones, then stop without starting M1.
```

## Prompt C — Build a later milestone

```text
Read AGENTS.md, the current PLANS.md, relevant docs and code. Work ONLY on
milestone M<n>: <paste exact exit gate>. First verify predecessors are complete.
Propose a bounded implementation plan and test matrix. Preserve stable IDs,
source provenance, knowledge status, and the Representation/View/Personal
Cognition boundary. Implement; run tests; show a manual verification path;
update docs with actual results. Do not start the next milestone.
```

## Prompt D — Architectural review

```text
Review the current code against AGENTS.md, docs/PROJECT_SPEC.md and
DATA_CONTRACTS.md. Focus on (1) source provenance continuity,
(2) classification vs prerequisite semantics,
(3) chat/view consistency, (4) validated vs candidate vs personal objects,
(5) local-first and Skill permissions, (6) compatibility of IDs and migrations.
Report findings ordered by severity with file:line evidence and concrete tests.
Do not modify code during this review.
```

## Prompt E — Turn a product idea into a controlled change

```text
Feature request: <describe the desired user behavior>.
Use docs/PROJECT_SPEC.md as product context and examine the relevant existing
interfaces. Explain how it maps to Representation, Views, Personal Cognition,
Agent, Template or Skill. Identify the minimal data contract changes and tests.
Propose a reversible implementation and update an ADR. Do not implement until
I approve the bounded plan.
```

## Prompt F — Reproducible course demo

```text
Prepare a reproducible six-stage course demonstration using only actually
implemented features and licensed fixtures. Produce startup instructions,
a click-through scenario, data provenance inventory, an evaluation matrix,
record of test commands/outcomes and screenshots plan. Explicitly distinguish
completed features, simulated demo stubs, planned features and limitations.
Do not fabricate performance figures or learning outcomes.
```
