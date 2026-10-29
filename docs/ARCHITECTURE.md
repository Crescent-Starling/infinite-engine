# Architecture — logical separation, not mandatory microservices

## Guiding model

```
                             Human user
                     ┌──────────┴──────────┐
               Conversation UI        Knowledge Views UI
                     └──────────┬──────────┘
                       Application services
                ┌──────────────┼───────────────┐
                │              │               │
        Representation     View Engine     Personal Cognition
        sources/graph/     tree/DAG/       questions/definitions/
        retrieval index    evidence/path   events/learning state
                └──────────────┼───────────────┘
                   Mentor Agent + Skill/Tool gateway
                              │
            Ingest → candidates → review → versioned commits
```

Views, personal state and agent calls communicate via APIs/services, not duplicate knowledge data. The user may begin with chat or a tree; support switching in both directions.

## Suggested bounded contexts

- `catalog`: domain registry, readiness, source roster.
- `ingest`: parser interfaces for text/images; normalized source, chunks, media, extraction candidates.
- `knowledge`: typed entities/relations, provenance, review state, versions, domain extensions.
- `views`: domain tree, concept prerequisites, local graph, source/evidence, learning path (latter can be heuristic P1).
- `retrieval`: keyword/vector retrieval with citation anchors and graph expansion.
- `agent`: mentor orchestrator, allowlisted tools; LLM provider behind interface.
- `learning`: primitives, declarative templates, personal questions/explanations/events, retrieval of history.
- `skills`: metadata discovery; safe SKILL.md loading; no arbitrary code execution.
- `ui`: React/TS clients, multi-entry UX.

## Technical preferences and caveats

- Start with one FastAPI backend, one React/TS UI, SQLite local state; preserve interfaces for Neo4j and a local vector store. Before choosing Neo4j, confirm the academic requirement and local setup effort. Graph must be **typed and queryable**, regardless of implementation.
- Do not run two databases solely to look impressive. If adding Neo4j or Chroma, explain query benefit and startup instructions.
- Blob files stored separately from metadata. Model adapters expose `chat`, `embed`, `parse_image` as relevant; a no-key demo mode clearly labels fixed fixture responses.
- Retrieval returns `source_anchor_id`, `quote/span`, `score`, `relation_path` where applicable; answers retain exact anchors.
- Use `knowledge_candidate` → `review` → `validated_revision`. Never let LLM write directly into canonical graph.
- Project dependency views from typed relationships, guard against cycles and misleading linearization.
- Design for idempotent reingestion and deterministic reconciling, based on source hash and stable canonical IDs.

## Minimal API shape (provisional; refine via ADR)

- `GET /api/domains` ; `GET /api/domains/{domain_id}/seed`
- `POST /api/sources/import` ; `GET /api/sources/{source_id}` ; `GET /api/source-anchors/{anchor_id}`
- `GET /api/knowledge/concepts/{concept_id}` ; `GET /api/views/tree?domain_id=...`
- `GET /api/views/dependencies?concept_id=...`
- `POST /api/agent/chat` (answer + structured citations + concept IDs)
- `POST /api/knowledge/candidates` ; `POST /api/knowledge/candidates/{id}/review`
- `POST /api/personal/explanations` ; `GET /api/personal/history?concept_id=...`
- `GET /api/skills` ; `POST /api/skills/{name}/invoke` (subject to tool allowlist)

These names are **proposed**, not already implemented contracts. Maintain an OpenAPI schema once code exists.

## Architectural decision records

Maintain `docs/DECISIONS.md` for choices affecting schema, APIs, model/provider, graph DB, image extraction, and versioning. Record alternatives and migrations.
