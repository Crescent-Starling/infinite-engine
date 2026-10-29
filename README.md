# Infinite Engine / 无限引擎

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

M0 foundation implemented locally: FastAPI process health, validated local configuration, React navigation shell, locked dependencies and automated checks. Registry R1 candidate storage is implemented; curated import, seeds, validated knowledge graph, RAG, tutoring and personal persistence remain planned. No verified datasets or learning outcomes are claimed. CI is configured; remote execution is reported separately.

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

## Run locally

Prerequisites: Python 3.12, Node 24, uv 0.11.7, npm and Make.

```sh
make setup
make check
# Separate terminals:
make backend
make frontend
```

Open http://127.0.0.1:5173 and switch navigation sections (all explicitly unavailable).
`curl http://127.0.0.1:8000/api/health` checks backend liveness.
No paid API key is required. First setup requires package-registry access.
See [Development](docs/DEVELOPMENT.md) for configuration, troubleshooting and GitHub settings.

## Engineering and product references

- [Domain Registry](docs/DOMAIN_REGISTRY.md): candidate collection, provenance and explicit human review.
- [Learning Engine](docs/LEARNING_ENGINE.md): motivation, goals, activities and user-led co-construction.
- [Data contracts](docs/DATA_CONTRACTS.md), [architecture decisions](docs/DECISIONS.md), [validation](docs/VALIDATION.md).
- [Changelog](CHANGELOG.md) and [roadmap](PLANS.md) separate actual delivery from future scope.

## Registry progress

R1 adds local candidate contracts, immutable SQLite revisions and provenance, typed domain relationships and an offline storage demo. It does not supply curated data, CSV review/import or ready seeds. Run `uv run --frozen python -m infinite_engine.catalog`; see [implemented contracts](docs/DATA_CONTRACTS.md) and [Registry scope](docs/DOMAIN_REGISTRY.md).
