# Knowledge foundation — planned

Objective: implement M1 stable identity, evidence and safe versioned storage before knowledge ingestion.
Dependencies: M0. Coordinate shared Domain/Source identity with DR; do not build parallel stores.
Scope: typed Pydantic contracts for core entities, SQLite repository, forward migrations, source anchors, immutable revisions and explicit review states. Keep Knowledge Views and Personal Cognition distinct.
Deliverables: schema ADR, contracts, migrations, repository tests and an offline persistence/restart demo.
Acceptance: stable identity across edits, typed endpoints, source-anchor recovery, optimistic version checks and no silent candidate/personal promotion. Unknown evidence is represented explicitly.
Required tests: invalid relations, duplicate aliases, missing evidence, foreign keys, stale revision, migration repeatability, rollback/history, restart and offline/no-key behavior. Prerequisite cycle handling is required when prerequisite writes are introduced.
Risks: premature abstraction, inconsistent canonical aliases and future migration compatibility.
Out of scope: full registry curation, parsers, embeddings, graph visualization, model calls, mentor tools or learning analytics.
