# Architecture Decision Records (ADR)

Use this format for consequential changes: `ADR-### | date | title | status | context | options | decision | consequences | migration`. Every decision here is provisional until implemented and accepted.

## ADR-001 | 2026-10-29 | Separate representation, view and personal cognition | Proposed

- **Context:** A semantic knowledge graph/backlink network is not automatically an effective beginner learning structure. Chat-based LLM explanation is valuable and should remain first-class.
- **Decision:** Keep canonical knowledge and provenance separate from derived learning views and user history; stable IDs connect them. Offer conversation-first and structure-first.
- **Consequence:** Need typed relations, view projections, UI deep links and history linkage.

## ADR-002 | 2026-10-29 | Domain Seed plus progressive extraction | Proposed

- **Context:** Eager full-corpus concept extraction may yield excessive unaudited nodes.
- **Decision:** Broad indexing + reviewed minimal domain skeleton first; deepen knowledge for user-selected topics as reviewable candidates.
- **Consequence:** Requires candidate state, idempotent update pipeline and review UI/API.

## ADR-003 | 2026-10-29 | Local-first modular monolith | Proposed

- **Context:** Solo project and personal data control.
- **Decision:** Local data persistence and single backend; remote LLM optional. Data storage adapters remain replaceable.
- **Consequence:** Keep setup low-friction; choose graph DB based on demonstrated value.

## ADR-004 | 2026-10-29 | Minimal executable foundation | Accepted for M0

- **Context:** Existing development pack has no code; the requested foundation must be reproducible without building later milestones.
- **Decision:** Python 3.12, FastAPI/Pydantic Settings, uv lockfile, pytest/Ruff/mypy; React/TypeScript/Vite, npm lockfile, ESLint/Prettier/Vitest. SQLite remains the persistence target, with no database in M0.
- **Alternatives:** Full framework/graph stack now; documentation only; system Python 3.9.
- **Rationale:** Small local shell, compatible available runtimes, actual automated checks and no paid provider dependency. Official Vite requirements: https://vite.dev/guide/ ; FastAPI setup: https://fastapi.tiangolo.com/tutorial/ .
- **Consequences:** Two runtimes, explicit package locks and CI. Graph UI candidate React Flow is deferred to M4 evaluation; no unused graph dependency.
- **Migration:** No persisted application data exists. Future data models require explicit migration files.

## ADR-005 | 2026-10-29 | Preserve registry plan without prematurely adopting schema | Accepted for foundation documentation

- **Context:** Earlier registry planning predates M0; its implementation has not been approved. New task explicitly scopes work to foundation.
- **Decision:** Retain bootstrap proposal, add registry/learning design documents and task entry points; implement none of the registry pipeline. Clarify contract naming through aliases rather than duplicate entities.
- **Alternatives:** Implement registry now; discard earlier plan; create competing Source and personal-explanation models.
- **Rationale:** Preserve product vision and review decisions while keeping one bounded task.
- **Consequences:** UUID namespace, relation vocabulary, review import policy and mapping details remain proposed until their schema task. Readiness cannot be inferred from catalog coverage.
- **Migration:** Documentation only, no existing storage to migrate.

## ADR-006 | 2026-10-29 | Git baseline for an empty remote | Accepted locally

- **Context:** Local directory was not a repository; remote ref discovery returned no commits or branches.
- **Decision:** Preserve the original development pack in a baseline commit, create local main at that baseline and work on feature/repository-foundation. Publish only without rewriting remote history; refresh remote state before delivery.
- **Alternatives:** Replace local pack by cloning; put all foundation work directly on main.
- **Rationale:** Preserve original work and enable review of the foundation diff.
- **Consequences:** Initial main publication is needed for a GitHub PR; no feature merge is authorized. GitHub settings and hosted CI outcomes must be reported separately.
- **Migration:** No published history rewritten.
