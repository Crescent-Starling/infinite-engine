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

## ADR-007 | 2026-10-29 | Registry R1 identity and candidate storage | Accepted for R1

- **Context:** Owner requested Registry implementation after foundation. Shared M1 IDs/provenance are a dependency, but implementing the full knowledge subsystem would exceed R1.
- **Decision:** Implement the shared minimum inside `catalog`: type-prefixed UUIDv5 from immutable NFC identity keys and permanent namespace `0691e948-1e99-5da2-a366-0a088a3c7869`; normalized SQLite candidate tables; immutable revision/provenance/observation history. Labels never determine identity. DomainSource, DomainTopic and DomainConcept link existing typed identities. Classification is a multi-parent DAG; symmetric cross-domain edges canonicalize endpoints, APPLIES_TO may cycle.
- **Alternatives:** Random IDs with a separate replay mapping; label-derived IDs; a JSON-only store; implementing full M1 and the review workflow at once.
- **Rationale:** Deterministic offline replay and queryable relationships with a small reversible scope. No duplicate Source store or canonical knowledge model is introduced.
- **Consequences:** R1 accepts only pending candidates, never curated data; reviews are contracts/reserved storage only. Homonymous labels are returned for human resolution, not automatically merged. Topic/Concept entries remain catalog stubs. Source checks record attributed observations, not a network-verification guarantee. Full BCP-47 validation, taxonomy mappings, field-level evidence, import manifests, review promotion and readiness capabilities remain R2/R3 work. The bootstrap plan's supporting-table list describes the eventual scope, not all of R1.
- **Migration:** `001_registry.sql` initializes an empty database atomically, checks its digest on reopen and refuses unknown versions/nonempty unversioned databases. Published migrations must never be edited; add later migrations. R1 is the first persisted schema; it does not complete M1's claims, anchors, knowledge revision or seed contracts.

## ADR-008 | 2026-10-29 | Exact-revision review packets and curated projection | Accepted for R2

- **Context:** R1 deliberately persists only candidates. R2 must make human edits auditable and prevent candidate updates from silently replacing approved data.
- **Decision:** Add a forward-only 002 migration with candidate-batch manifests, immutable review-export baselines, review receipts and approved-revision references. Keep R1 candidate snapshots immutable and derive review state from the ledger. Curated queries select the latest explicitly approved revision, which may differ from the latest candidate.
- **Alternatives:** Mutate candidate review_status in place; trust CSV hash columns; approve edits in the same action; flatten everything into a single sheet.
- **Rationale:** Separate candidate history, operator decisions and curated visibility. Require explicit CLI --apply and matching --actor/reviewer; dry-run executes the same validations then rolls back. The local operator/file owner remains the trust boundary, not cryptographic reviewer identity.
- **Consequences:** Export one CSV per entity kind with original/proposed field pairs and a protected provenance JSON sidecar. Nested labels remain JSON cells in R2 instead of separate label sheets; this reversible UI simplification keeps one atomic entity review decision. Null is JSON null, empty string is JSON "", and a blank field is an error. Approve cannot also edit content; revise records a human-authored next candidate plus an input hash pointing to the original. Review/export files must originate from the same registry. No taxonomy mappings, bulk discovery, review UI or source verification is added.
- **Migration:** 001 is unchanged. 002 adds tables/views/triggers without copying or deleting R1 data. Reopen verifies both migration checksums. Curated insertion requires a matching approve ledger entry; all actions, new revisions and promotions in a packet commit or roll back together. Candidate-bundle and review receipts make exact replay idempotent.

## ADR-009 — R3 external mappings and offline pilot

- Status/date: adopted for the explicitly requested R3 slice, 2026-10-29.
- Context: native taxonomy identity must survive local edits without treating an educational classification as a universal domain tree. R2 already supplies per-kind review and exact-revision approvals.
- Decision: add normalized TaxonomyEntry and DomainMapping payloads with migration 003. A Source revision represents one identified external release; entries pin that revision. Mappings pin exact entry revisions. Native code paths are publisher locators, not local parent edges. Use an attributed four-entry ISCED-F excerpt and saved AI suggestions through a hash-pinned offline adapter. Stellaris remains explicitly unmapped.
- Alternatives: embedding mapping text in Domain would prevent independent review; wholesale taxonomy merging would conflate identities; remote model calls during bootstrap would prevent deterministic replay. A separate TaxonomyRelease entity is deferred because Source revision plus release_tag supplies the bounded release identity.
- Rationale: reuse R2 validation/review closure, preserve multilingual local labels and original external labels, keep discovery separate from verification and readiness.
- Consequences: existing schema-version-1 payloads and migration checksums remain unchanged; the union gains two kinds, requiring new readers for new kinds. Code/release/source revision cannot be retargeted under an existing TaxonomyEntry ID. Native label corrections append revisions; mappings keep their old pins until reviewed updates. Full external hierarchy ingestion, per-field provenance, specialized knowledge contracts and automatic maintenance merging remain future work.

## ADR-010 — Domain scopes, local spaces and independent source choices

- Status/date: adopted for the explicit Domain Architecture Revision request, 2026-10-29. Supersedes category-as-parent and undifferentiated global-pilot assumptions in ADR-007/009; preserves historical records and unrelated product decisions.
- Context: the registry must not grow into prebuilt global topic/concept trees. Local interests must work without expert seeds or administrative approval. R1–R3 supply stable IDs and exact-version review but lacked origin/category/space boundaries.
- Decision: one Domain schema with preset/custom origin; independent Category memberships, typed DomainRelation and one primary local Knowledge Space. Curated defaults and private overrides are separate. Source review, collection acceptance, checks and claim verification are independent. Local duplicate suggestions never merge or block overlapping custom scopes. Editing distinguishes layout, personal structure, explanation, professional proposal and reviewed knowledge. Registry data and application development proceed independently; catalog coverage requires no seeds.
- Alternatives: separate preset/custom schemas duplicate infrastructure; universal granularity excludes valid user scopes; seed-gated creation blocks exploration; authority approval for personal sources removes autonomy; multi-user resolution and advanced multi-space management add no current value.
- Rationale: preserve learning continuity and source-aware co-construction with simple local services, without conflating management, truth or readiness.
- Consequences: migration 004 adds nullable legacy-compatible metadata, categories, spaces/choices/overrides and expands relation checks through a transactional row-preserving table copy. Old snapshots, IDs, hashes and migration checksums remain unchanged. Absent new fields serialize as absent; old origin stays unknown. Explicit origin is immutable after assignment. New fixtures supply origin; R3 remains an audit pilot requiring deliberate reclassification. Normal preset discovery uses approved revisions; pending preview is explicit. Custom/source use is independent of promotion. Editors, remote discovery, seed loading and bulk generation remain future work.

## ADR-012 — Source discovery interchange and exact acquisition artifacts

Status: implemented for offline metadata contracts/import; execution integrations deferred.

Context: externally researched sources must be reusable across preset/custom Domains without conflating provider identity, a collection, acquired bytes, citations or professional verification. Existing Source IDs/review history and local acceptance are already persisted.

Decision: retain Source as logical Resource and existing DomainSource/SourceCheck/ReviewRecord. Add an exact-revision SourceResource sidecar plus independently versioned Provider, Document and Anchor artifacts via additive migration 005. SourceReview narrows the existing review shape; no parallel approval system. Keep mandatory attributed provenance, exact pins, native locators and immutable hashes. Search Profile is declarative YAML; acquisition plans are always proposals. Import validates offline atomically; host-controlled acquisition is a future separate service. Use PyYAML SafeLoader with bounded input, duplicate/alias rejection; generate JSON Schema from Pydantic and test agreement.

Assumptions: initial research arrives from human/external workflows; four examples are synthetic and not authority endorsements. Resource can be a collection or standalone work. Catalog recommendations retain their existing identity references, while actual documents/citations pin revisions. Legacy provider-kind Sources remain intact until explicit reclassification; do not guess a migration from titles.

Alternatives rejected: replacing Source IDs, duplicating review/acceptance stores, making profiles executable permissions, or implementing speculative crawlers/RAG. Consequences: additive storage and preserved old snapshots; artifact review UI, actual acquisition/parsers, byte verification, extraction and claim verification remain future work. See SOURCE_DISCOVERY and tasks/source-discovery-acquisition.md.

## ADR-012 | 2026-10-29 | Four-stage multimodal acquisition and temporal evidence | Proposed for Phase 1

- **Context:** The requested six-phase extension makes video a first-class source without conflating discovery, acquisition, interpretation or verification. Source Registry already has stable identities and separate source choices/checks/review. The working tree includes ADR-010 and concurrent ADR-011 Source Discovery work.
- **Decision:** Bound this task to architecture and contract specifications. Reuse Source/SourceRevision, ADR-011 Resource/Document/Anchor artifacts, shared MediaAsset and KnowledgeCandidate concepts. Use typed adapter requests/results with explicit failures and host-granted operations. Prefer supplied subtitles, preserve raw transcript and correction revisions, and require evidence-backed temporal anchors. Creator/collection subscriptions default to metadata-only manual synchronization.
- **Assumptions:** “Implement or design” permits interface specifications in Phase 1; no new executable adapter, database shape, dependency or API is required yet. Processing states are independent of source and claim review. Existing text/image course requirements and roadmap IDs remain intact.
- **Alternatives:** New standalone video registry duplicates identity/provenance; downloaded-media-first processing adds cost and permission risk; implementing all phases exceeds the explicit scope; runtime model stubs without persistence could misleadingly imply a working acquisition feature.
- **Consequences:** Phase 2 must implement and test applicable host permissions, bounded local parsing and recovery before claiming support. ASR, graph/RAG, platform connectors and synchronization remain separately authorized tasks. No unsupported platform behavior is claimed. Unknown rights/timing stay unknown.
- **Migration:** None in Phase 1. Future additive migrations preserve 001–005 checksums, source IDs, exact snapshots, approvals and collection pins; migration/rollback and provenance tests gate runtime contract adoption.
