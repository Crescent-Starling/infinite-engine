# Domain Intelligence Registry — implementation proposal

Status: proposed; implementation requires owner approval. Planning does not approve any dataset.

## Historical planning baseline (before M0)

Read AGENTS.md, PROJECT_SPEC, DATA_CONTRACTS, DEMOS, ARCHITECTURE, PLANS and DECISIONS.
The repository currently contains specifications only: no backend, database, dependency manifest or tests.
M0–M10 remain planned. This is a bounded foundational work package, not completion of M0/M1/M3/M9.

## Proposed scope

Build a local Python 3.11+/Pydantic/SQLite catalog module and CLI with migrations, offline validation, reproducible candidate bundles, editable review CSVs and atomic promotion. No frontend, remote model integration, crawler, complete Domain Seeds or individualized health guidance.

### Schema decisions for owner review

1. **Graph classification:** Domain has no parent column. DomainRelation stores multiple parents. Initial predicates: SUBDOMAIN_OF (child → parent, acyclic), OVERLAPS_WITH and RELATED_TO (symmetric, canonical endpoint ordering), APPLIES_TO (directed). Self-edges are invalid. Cross-domain cycles are permitted outside classification; prerequisite and learning-path relations are outside this registry.
2. **Identity:** type-prefixed UUIDv5 IDs derive from a fixed namespace and immutable identity key, never an editable label, definition or URL. External taxonomy entries use taxonomy identity + release + native code; internal domains use recorded local keys. Mapping never silently merges identities. Explicit equivalence/redirect records are required for later merges, which are out of pilot scope.
3. **Versions:** stable entity identity plus immutable numbered revisions, parent revision, schema version and content hash. Append-only provenance and reviews target exact revision/hash; optimistic base-version checking rejects stale updates. Approved prior revisions remain available when a replacement is proposed or rejected.
4. **Review:** pending_review → approve/reject/revise/defer. Approve promotes only the reviewed payload; revise preserves the original and creates a new pending revision; defer remains unpromoted. A revised row requires a later explicit approval. Review actor/time and reason are required; importer never generates an approval. Local operator is the trust boundary; no multi-user authentication is added.
5. **Readiness:** catalog approval is independent from sources_available, seed_ready and learning_ready capabilities. Registry promotion cannot set seed/learning readiness. Pilot entries have no ready seeds. Future readiness derives from separately reviewed artifacts.
6. **Sources:** reuse the core Source identity rather than introduce a competing source registry. Extend Source to describe institutions, organizations, textbooks, databases, references, documentation and classification systems. Optional URI, license and publication date stay unknown when not evidenced. Availability checks, authority assessment and permission to reuse content are separate dimensions.
7. **Topics/concepts:** DomainTopic and DomainConcept are membership records pointing to reusable Topic/Concept identities. The pilot can create small catalog-only candidate stubs; they are not validated Definitions/Claims or ready knowledge bases. Latin morphology, health conditions/units and game version/DLC requirements are extension requirements, not full new subsystems.
8. **Evidence and mappings:** normalized provenance and taxonomy-mapping tables are required in addition to the eight requested entities. Distinguish exact/broad/narrow/related mappings; retain original taxonomy release, code, path and label. Mapping and generated definitions each need independent review and evidence or an explicit unsupported marker.

### Proposed normalized contracts

Every mutable catalog entity uses stable identity and revision tables. Foreign keys identify entities; evidence/reviews also pin revisions when historical meaning matters. No arrays of parents, sources, labels or edits in authoritative entity rows.

| Entity | Principal fields / companion records | Invariants |
|---|---|---|
| Domain | id, identity_key; revision: slug, kind, definition, scope_note | localized labels/aliases in DomainLabel with BCP-47 language; capabilities separately stored |
| DomainRelation | id; revision: from_domain_id, predicate, to_domain_id, rationale | typed endpoints, predicate registry, semantic duplicate/cycle checks |
| Source | id; revision: kind, title, creator, uri/local_path, media_type, publication_date?, version_tag?, license?, content_hash? | unknown is distinct from verified; localized titles and alternate locators use child rows |
| DomainSource | id; revision: domain_id, source_id, recommendation_rationale, intended_use, authority_scope, limitations | source-role child rows; recommendation is not evidence for every domain claim |
| DomainTopic | id; revision: domain_id, topic_id, rationale | unique active membership; Topic labels/revisions and TopicRelation are separate |
| DomainConcept | id; revision: domain_id, concept_id, rationale | shared concept identity; topic membership separate; catalog stub is not validated knowledge |
| ReviewRecord | id, entity_id, revision_id, payload_hash, decision, reviewer, recorded_at, reason, resulting_revision_id? | append-only; cannot approve a different or subsequently edited payload |
| SourceCheck | id, source_id, source_revision_id, check_kind, outcome, checked_at, method, actor, locator, evidence_ref?, details | append-only observation; network success proves neither authority nor license; no invented check |

Supporting tables: RegistryEntity (typed FK target), EntityRevision, localized labels/aliases, ProvenanceRecord and field-level provenance links, TaxonomyRelease, TaxonomyEntry, DomainTaxonomyMapping, CapabilityEvidence, CandidateBatch and ImportReceipt. Revision payload snapshots may be serialized for audit, but queryable relationships remain normalized.

Provenance distinguishes human-authored suggestions, AI suggestions and taxonomy imports. Store supplied generator/model/prompt metadata, input artifact hashes and local source anchors; missing metadata remains unknown. Mark pilot text authored during implementation accurately. A SourceCheck is absent/unverified until an actual check occurs; never synthesize timestamps or successful observations.

### Reproducible bootstrap design

1. Evaluate established academic/knowledge classification systems using official publisher metadata: breadth, stable codes, release availability, permitted reuse and fit. Select a small set explicitly; research/selection is an implementation deliverable, not an approval already made here.
2. Import only owner-supplied or explicitly permitted snapshots. Manifest records publisher, taxonomy release, observed URL, retrieval time, license evidence, artifact checksum and adapter version. Do not copy restricted taxonomy content.
3. Preserve original entries. Generate explicit proposed mappings into the local domain graph; unsupported domains such as game titles may have local keys without an academic classification match.
4. Produce candidate definitions/relationships with provenance, support gaps and generator metadata. Recorded AI outputs can be replayed; fresh model calls are not claimed to be deterministic. First implementation consumes saved suggestions and needs no API key.
5. Collect source recommendations through bounded manual/assisted discovery, with rationale and domain-specific limits. No autonomous crawling. Verify URLs/metadata from observed official pages where access is available; otherwise leave candidates unverified and URLs unknown unless supplied with provenance.
6. Sort outputs deterministically; pin inputs, adapter/config/schema versions and hashes. Replaying a bundle produces identical identities and payload hashes. Operational audit timestamps remain actual execution times.
7. Export editable review tables, ingest explicit decisions, validate complete promotion closure, and commit approved revisions atomically.

### CSV review boundary

Use one CSV per entity/relation/mapping/label type plus manifest and provenance files, not a single denormalized sheet. Export immutable entity/revision IDs, base version, original hash and original suggestion beside editable proposed fields, decision, reviewer and reason.

Preserve originals in SQLite/candidate artifacts; detect edits to protected columns rather than trusting the CSV copy. Distinguish blank, unknown and explicit clearing. Define UTF-8/newline/JSON-cell rules and reversible spreadsheet-formula escaping. Report row/column errors; never silently drop malformed rows.

Promotion requires explicit approval of each changed revision and all referenced objects either approved in the same transaction or already curated. Missing evidence may remain explicit for catalog metadata; it cannot yield a validated knowledge claim or verified source badge. Source approval accepts a catalog record/recommendation and does not certify source content or reuse rights.

## Incremental implementation and exit gates

### R1 — Contracts and storage (recommended first approval scope)

- Add contracts, ID functions, initial SQLite migration and repository; record ADRs and detailed DOMAIN_REGISTRY documentation.
- Tests: deterministic IDs across label edits/replay, multilingual labels, typed relation endpoints, multi-parent classification, classification cycle rejection, permitted cross-domain cycles, duplicate aliases with language/scope-aware ambiguity reporting, FK integrity, revision preservation and stale version rejection.
- Migration creates an empty store and is repeatable. Future migrations preserve stable identities. No destructive rebuild command.
- Stop after R1 checks and owner acceptance; no dataset promotion.

### R2 — Candidate/review/import vertical slice

- Add candidate bundle and CSV export/import, dry-run diff/error report, explicit review actions and atomic promotion.
- Tests: all four actions, revise then approve, unauthorized CSV approval-field tampering versus explicit operator decisions, original/provenance preservation, changed-payload approval invalidation, dependency closure, idempotent re-import, conflicting same-ID payloads, partial CSV failures/rollback, spreadsheet escaping, restart persistence and transactional failure rollback.
- Demo: export → edit → dry-run → approve → import → re-import with no change → inspect history.

### R3 — Four-domain pilot and bootstrap adapters

- Add small pending candidate bundles for Astronomy, Latin, Fitness and Nutrition, Stellaris; include representative topics/concepts, typed relationships, source recommendations and explicit unsupported/unverified fields.
- Cover all six requested source categories across the pilot where justified, without padding every domain with inappropriate sources.
- Exercise shared membership/multi-parent classification, Latin language/label ambiguity, health evidence context/units, game patch/DLC applicability. Document limitations revealed by these cases.
- Research candidate classification foundations and implement a manifest-driven offline adapter plus mapping fixtures using permitted inputs. Broad collection remains outside scope until pilot acceptance.
- Test offline/no-key operation, incomplete discovery and parsing failures, reproducible generation, duplicate detection, taxonomy release/mapping provenance and absence of automatic approval/readiness changes.
- A separate synthetic test fixture may simulate human approval; distributed pilot data stays pending until the owner reviews it.

### R4 — Acceptance and documentation reconciliation

- Update DATA_CONTRACTS, ARCHITECTURE, DEMOS and PLANS with observed outcomes and exact runnable commands. Finish DOMAIN_REGISTRY and this task's evidence log.
- Run focused pytest suite and full existing suite if one exists; perform clean local database and CSV round-trip demos.
- Report coverage, known limitations and next bounded task. Do not mark existing course milestones or four full demos complete based on registry tests.

## Intended changed paths after approval

- `pyproject.toml`, minimal `.gitignore`, `backend/infinite_engine/catalog/` (contracts, IDs, storage, validation, review, CSV, bootstrap, CLI).
- `backend/infinite_engine/catalog/migrations/001_registry.sql`.
- `tests/catalog/`, `tests/fixtures/domain_registry/`, `data/domain_registry/pilot/` (candidate-only), `data/domain_registry/manifests/`.
- `docs/DATA_CONTRACTS.md`, `docs/ARCHITECTURE.md`, `docs/DEMOS.md`, `docs/DECISIONS.md`, `docs/DOMAIN_REGISTRY.md`, `PLANS.md`, this task file; README only for actual setup/commands.

Paths are proposed because no application layout exists yet. Select one package/test layout in R1, without scaffolding unrelated UI/API work.

## Planning verification and limitations

- Document reads and repository file inventory succeeded.
- `git status --short` failed: directory is not a Git repository. No Git initialization, commit or push was attempted.
- No executable tests exist; tests and implementation commands have not been run.
- No taxonomy/source research or URL/license verification has occurred during planning.
- Owner review is requested by the task before implementation. Approve or amend schema decisions 1–8 and authorize R1 first; R2–R4 remain planned follow-on slices.

## Foundation follow-up

M0 now supplies the package/test/tooling layout. The historical baseline above records the original planning inspection, not the current repository state. Registry schema decisions and R1–R4 implementation remain proposed. Use [01-domain-registry.md](01-domain-registry.md) as the task entry point and coordinate shared contracts with M1.
