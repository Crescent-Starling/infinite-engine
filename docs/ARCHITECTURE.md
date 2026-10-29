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

- `catalog`: preset/custom Domain contracts, independent browsing categories, semantic domain relations, review/readiness and shared source metadata.
- Local space services: one primary space, private source choices and overrides; future learning/view/conversation services reference its ID.
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

## M0 implementation and future interfaces

Implemented package: `backend/infinite_engine` contains Pydantic Settings and a FastAPI application factory with `GET /api/health`. `frontend/` is React/TypeScript/Vite with unavailable navigation sections. Tests use in-process HTTP and DOM fixtures. No runtime database or external provider is initialized. Dependency locks are authoritative; see [DEVELOPMENT.md](DEVELOPMENT.md).

Planned typed interfaces (design only): SourceRepository retrieves Source/Evidence by stable ID; KnowledgeRepository queries typed relations and commits reviewed revisions with expected-version checks; Retriever accepts query/domain/filter context and returns anchored matches plus support gaps; ModelProvider accepts explicit context and returns labeled proposals; ToolGateway validates tool name/arguments against host allowlists. Agent orchestration consumes these interfaces, never direct arbitrary SQL/filesystem/network access. Provider absence produces an explicit unavailable/insufficient-evidence result, never a fabricated answer.

The View Engine projects internal learning structures, concept dependencies, evidence and learning paths without duplicating canonical objects. Global browsing categories are separate from semantic DomainRelation edges. Personal Cognition stores user-authored records/events keyed to stable knowledge IDs and viewed revisions; it cannot overwrite Representation. Conversation and structure-first clients share services and navigation context.

Future flow: source registration → anchored parsing → candidate generation → deterministic validation → human review → transactional versioned persistence → retrieval/view projections. Personal interpretation goes to personal storage, not that promotion path. Catalog review and source checks do not certify knowledge claims or seed readiness.

Persistence target: local SQLite metadata/typed relationships with blob files outside the database, migrations and repository interfaces. No Neo4j/vector database/framework dependency until a measured requirement justifies one. Future retrieval can begin with SQLite/keyword search; graph/vector adapters must preserve IDs/provenance.

Error handling: input/config validation is explicit; future APIs distinguish malformed input, missing objects, stale revision conflicts, insufficient evidence, provider unavailable and partial parse failure. Validate before transactional writes; preserve retry/idempotency keys and prior revisions. Logs must be structured and omit raw personal content/secrets; structured request logging is not implemented in M0.

Deployment: one local backend and browser UI, loopback-bound by default. No cloud account, network model call or public deployment. The Vite proxy is for development only. Production authentication, TLS and hosting are separate future decisions. Health is liveness, not readiness of unfinished modules.

## Registry R1 implementation

`catalog/contracts.py` validates candidate-only payloads and attributed provenance; `ids.py` owns persistent registry identity; `storage.py` owns SQLite migration/transactions and graph/duplicate/reference checks. A disposable `python -m infinite_engine.catalog` demo exercises replay, revision history and restart. No frontend/API integration, model call or automatic source verification is added.

Data flow: caller-supplied candidate → strict contract validation → typed references/duplicate/classification checks → atomic normalized pending revision + provenance → candidate queries. Every write is version checked. Labels and membership edges connect shared objects; they do not duplicate canonical knowledge for views. ReviewRecord is reserved for R2, which must add hash-bound approval and curated projections via a new migration. SourceCheck records observations independently of review and readiness. See ADR-007 and the implemented section in DATA_CONTRACTS.

## Registry R2 implementation

`bundles.py` validates and transactionally stages candidate bundles. `review_csv.py` exports per-kind field tables and checks them against immutable local export baselines. `review.py` applies operator decisions, validates approval dependency closure/effective curated graph, and reads the approved projection. `review_cli.py` exposes local commands with dry-run defaults and explicit --apply/--actor. No HTTP endpoint or frontend feature is added.

Registry transactions now use nested savepoints, so existing single-candidate writes participate in outer bundle/review transactions without committing partial state. Errors or interruptions roll back the operation. CSV parsing and protected-field checks happen before mutation; stale/current state is rechecked inside the transaction. Source checks remain independent observations. R3 adds taxonomy mapping, bounded source discovery and a four-domain pilot as described below.

## Registry R3 implementation

`catalog/bootstrap.py` adapts a pinned local taxonomy excerpt plus recorded AI suggestions into an R2 CandidateBundle and coverage/extension report. It validates in a disposable SQLite store before atomically publishing a new output directory; it never opens a network client or approves data. Discovery is a separate bounded human/AI research activity, recorded with source URLs and uncertainty in `data/domain_registry/pilot/`.

TaxonomyEntry and DomainMapping participate in the same repository, provenance, immutable revisions and per-kind CSV review path as other registry objects. Migration 003 adds their tables and exact-revision references. Source revision + release tag acts as the bounded release record; original external paths are locators, not local classification relationships. Curated closure checks the exact source/entry pins. The four-domain pilot stops at candidate review and extension-gap validation; no knowledge API, ingestion, graph UI or seed-readiness service is added.


## ADR-010 Domain and source foundation

The current boundaries and workflow are in [DOMAIN_ARCHITECTURE](DOMAIN_ARCHITECTURE.md); source autonomy is in [SOURCE_REGISTRY](SOURCE_REGISTRY.md). Domain is one scope contract with explicit preset/custom origin. Category/DomainCategory provide navigation independently from DomainRelation. The broad preset asset carries no requirement for globally populated Topics/Concepts.

Migration 004 extends the existing registry and adds local knowledge_space, knowledge_space_source and space_override tables. LocalDomains in catalog/spaces.py provides shared manual creation/search/selection and local collection/override writes. All four domain origins use the same path; no seed or network is required. Personal source choice can point to unreviewed metadata without invoking the curated approval service. Library interfaces only: no new HTTP endpoints, frontend lifecycle or model discovery.

Track A data flow: licensed/versioned foundation reference → recorded candidate metadata → deterministic validation → pending store → human review → approved dependency-closed release (release packaging remains planned). Track B flow: local discovery/custom creation → primary space → personal sources/overrides → optional compatible seed → progressive internal structures → shared views/RAG/learning history (later stages planned). Personal changes stay local; professional corrections re-enter the explicit proposal/review path.

Do not instantiate multi-user identity or merge services. The local owner/process is the current trust boundary. Low-level registry writes are curation tools; future UI must route personal edits to overrides and preserve approved default revisions. Neither local acceptance nor SourceCheck outcomes establish claim truth.

## Source discovery and acquisition boundary — ADR-012

The `sources` package adds offline research interchange and metadata import, depending on the existing catalog/review/local-space services. Provider, Resource sidecar, Document and Anchor revisions persist through additive migration 005; SourceReview reuses the existing metadata review ledger. Acquisition plans and profiles are declarative proposals; adapter Protocols receive supplied bytes and have no tool privileges. Discovery, selection, acquisition, extraction and claim verification remain independent stages. See [SOURCE_DISCOVERY](SOURCE_DISCOVERY.md) for executable scope, format specifications, adapter designs and future host boundaries. No RAG/search Agent or production parser is integrated.

## Multimodal acquisition extension — Phase 1 design

[Multimodal acquisition](MULTIMODAL_ACQUISITION.md) separates Source Discovery, Source
Acquisition, Multimodal Content Processing and Knowledge Extraction/Review. It defines
adapter signatures, typed results/failures, subtitle-first video processing, immutable
transcript corrections, temporal evidence, metadata-only subscriptions and host-enforced
permissions. It extends the same Source identity and primary Knowledge Space, not a second
video catalog. `catalog → ingest → knowledge/retrieval` denotes data flow; orchestration
uses repository interfaces and adapters cannot invoke canonical promotion.

This is design-only ADR-012. No acquisition adapters, media runtime, retrieval, platform
connector or safety enforcement is implemented here. Existing M2 text/image requirements
remain unchanged. See the [six bounded phases](../tasks/multimodal-acquisition.md).
