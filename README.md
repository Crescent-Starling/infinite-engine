# Infinite Engine / 无限引擎 — Codex Development Pack

> From Zero to Infinite Possibilities.  从零开始，探索无限。

本仓库的目标是构建一个 **local-first, single-user, general-purpose AI knowledge learning and management system**，而不只是一个“上传 PDF 后聊天”的 RAG 示例。

## Start here

1. Read [`docs/PROJECT_SPEC.md`](docs/PROJECT_SPEC.md): product vision, exact scope, interaction patterns and deliverables.
2. Read [`AGENTS.md`](AGENTS.md): binding development instructions for Codex.
3. Read [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) and [`docs/DATA_CONTRACTS.md`](docs/DATA_CONTRACTS.md): domain boundaries, core contracts, knowledge views.
4. Read [`PLANS.md`](PLANS.md): incremental milestone roadmap and gates.
5. Read [`tasks/00-repository-foundation.md`](tasks/00-repository-foundation.md) for the first task. **Do not implement everything at once.**
6. Follow [`PROMPTS.md`](PROMPTS.md) for copy-paste-ready Codex prompts.

## Product thesis

Reliable **knowledge representation** (graph + provenance + source index), **learning-oriented views** (domain tree, dependency view, evidence view, conversation), and **personal cognition** (questions, explanations, histories) are separate but linked by stable IDs. An LLM is a flexible interface across all three; neither the graph UI nor the conversation UI is mandatory.

Knowledge management loop: acquire multimodal resources → clean/code → graph/database → RAG → agent/service → feedback and updates.

## Current status

Specification only. No working app, domain datasets, verified sources or completed benchmark results are claimed in this package. All milestones are **planned**, not implemented.

## Terminology

- **Domain Catalog:** broad registration/directory; listing ≠ knowledge readiness.
- **Domain Seed:** small, vetted domain skeleton and source registry.
- **Knowledge Graph:** typed concepts, claims, relations and provenance; not the UI graph.
- **Knowledge Views:** task-dependent projections for users, including tree, prerequisites and evidence.
- **Personal Cognition:** personal definitions, questions, events, state — not authoritative domain knowledge.
- **Learning Template:** sequence/configuration of learning primitives.
- **Skill:** reusable instructions for one task, stored in SKILL.md; cannot grant permissions.

## Initial demo plan

Astronomy: full end-to-end workflow. Latin: morphological/grammar schema extension. Fitness and nutrition: quantities, units, conditions, evidence. Stellaris: versioned rules. See [`docs/DEMOS.md`](docs/DEMOS.md).
