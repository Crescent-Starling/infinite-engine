# Domain Intelligence Registry — R1 candidate storage implemented

The registry is a durable curated data asset, separate from Domain Seeds and extended knowledge. Catalog coverage does not mean source verification, seed readiness, learning readiness or user mastery.

## Pipeline

Discovery → Candidate Generation → Validation → Human Review → Approval → Import → Maintenance.

- Discovery evaluates established academic/knowledge classifications using official publisher metadata, release identifiers and reuse terms. No classification dataset or license has yet been selected or verified. Use supplied or permitted snapshots; no autonomous crawling.
- Preserve the original taxonomy's release, native codes, multilingual labels and path. Map explicitly into local domain IDs using exact/broad/narrow/related mappings; do not blindly copy or merge taxonomies.
- Candidate generation stores original suggestions, author/generator metadata where known, input hashes, source anchors, domain definitions, relationship rationale and support gaps. Recorded outputs are replayable; fresh LLM calls are not deterministic.
- Validation checks schema version, stable IDs, duplicates/aliases, typed relationships, classification cycles, references, provenance and base revision. Validation is not approval.
- Human review uses editable UTF-8 CSVs with original and revised fields, protected identity/revision/hash, reviewer, reason and approve/reject/revise/defer actions. Preserve originals independently; revise creates a pending revision requiring explicit approval.
- Approval binds a decision to exact payload and revision. Approved replacements retain prior history. Only explicitly approved records whose references resolve to approved records can be promoted atomically and idempotently.
- Maintenance records new proposals, taxonomy release mappings and source checks; never overwrites reviewed content with model output. Source-check outcomes are dated observations, not permanent truth.

## Normalized model

Domain + localized label rows; DomainRelation; Source; DomainSource with recommendation rationale; DomainTopic and DomainConcept memberships into shared Topic/Concept identities; append-only ReviewRecord and SourceCheck. Supporting taxonomy/mapping, revision and provenance records preserve external identities and review evidence. Proposed details and decisions requiring owner review remain in [the bootstrap plan](../tasks/domain-registry-bootstrap.md).

A domain graph supports multiple parents. Classification SUBDOMAIN_OF is acyclic; OVERLAPS_WITH/RELATED_TO are symmetric; APPLIES_TO is directed. These are proposed predicates, separate from prerequisites and pedagogical ordering. Views may project a tree without changing identity or discarding alternate parents.

Candidate source categories include official institutions, academic organizations, open textbooks, professional databases, authoritative references and official technical documentation. Record why each is relevant, its scope and limitations. Authority is context-specific. Unknown URLs, publication dates and licenses remain unknown; no fabricated verification. A successful HTTP request does not prove authority, claim support or permission to reproduce content. When browsing is unavailable, sources remain unverified candidates.

## Pilot and boundaries

Pilot domains: Astronomy, Latin, Fitness and Nutrition, Stellaris. Use small catalog/topic/concept proposals to expose multilingual ambiguity, conditional quantities and version/DLC scope. Astronomy later becomes the primary end-to-end demo; the others initially validate extensibility. No pilot data, approved source inventory, importer or seed exists in M0.

Implementation proceeds in bounded slices under: [01-domain-registry.md](../tasks/01-domain-registry.md). Offline fixtures and missing-key tests must work without paid services. Review tools must defend against accidental spreadsheet formula execution, protected-column edits and stale approvals. A local operator is the trust boundary; CSV metadata is not cryptographic identity proof.

## R1 delivered — candidate contracts and storage

The earlier pipeline describes the target system. R1 now implements eight requested contracts, shared Topic/Concept stubs, deterministic identity, normalized SQLite revision/provenance storage, typed relation validation, multi-parent classification cycle checks, scoped alias lookup and idempotent single-candidate writes. SourceCheck observations can be recorded against existing source versions; no check is manufactured or performed automatically. ReviewRecord is a validated contract/reserved ledger only; there is no approval/import interface.

Run `uv run --frozen python -m infinite_engine.catalog` for a disposable offline demo. It prints stable identity, successful replay/history/restart checks and `pending_review`, then removes its temporary database. Run `uv run --frozen pytest tests/catalog -q` for integrity tests. Use `Registry(path)` as a context manager for application storage in an existing user-selected directory; no implicit file/network access is provided by candidate text.

R1 does not implement CSV, batch import, classification-system adapters/mappings, field-level evidence, readiness computation, source discovery or the four-domain pilot. It does not complete M1 or validate any real domain fact. Next bounded step: R2 candidate bundles, human review and atomic approved import, including migrations that preserve R1 history. Broad collection remains gated by pilot acceptance.
