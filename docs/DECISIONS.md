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
