# Core data contracts — proposed v0 (subject to implementation ADR)

The database representation can be normalized relational tables, a property graph, or a combination. Maintain stable identity and semantic typing independent of storage engine.

## Entity types (minimum useful core)

| Entity | Key fields | Rules |
|---|---|---|
| `Domain` | `id, slug, title, category_ids, readiness` | catalog-only ≠ seed-ready |
| `DomainSeed` | `id, domain_id, version, source_ids, root_topic_ids, verified_at` | explicit reviewed status |
| `Topic` | `id, domain_id, title, parent_topic_ids` | allow multiple membership; tree projection picks path |
| `Concept` | `id, canonical_label, aliases, description?, status, version` | identity independent of view |
| `Definition` | `id, concept_id, text, level, source_anchor_ids, status` | formal/introductory/pedagogical are different |
| `Claim` | `id, statement, condition_ids, status, version` | reviewable, source-backed or explicitly unsupported |
| `Relation` | `id, source_id, predicate, target_id, qualifiers, evidence_anchor_ids, status` | typed predicate, typed endpoints, provenance |
| `Source` | `id, title, creator, uri_or_local_path, media_type, published_at?, version_tag?, license?, hash` | local files independent of graph |
| `SourceAnchor` | `id, source_id, page?, section?, start_offset?, end_offset?, image_region?, snippet?` | supports back-navigation; source locator accuracy tested |
| `MediaAsset` | `id, source_id, type, path, caption?, anchor_id?` | text + genuine image processing required |
| `KnowledgeCandidate` | `id, proposal_type, proposed_payload, evidence_anchor_ids, review_state` | candidate ≠ canonical |
| `Revision` | `id, entity_id, prior_revision_id?, change, rationale, actor, timestamp` | preserve history and attribution |
| `PersonalExplanation` | `id, concept_id, user_text, created_at, revision_id?` | never auto promoted to validated domain truth |
| `PersonalQuestion` | `id, concept_ids, text, created_at, source_context_ids` | stable retrieval target |
| `LearningEvent` | `id, event_type, entity_ids, occurred_at, payload` | objective events, not mastery |
| `SkillMetadata` | `name, description, file_path, enabled, declared_tools` | parsed SKILL.md, tool permissions enforced separately |
| `LearningTemplate` | `id, title, primitive_steps, params, version` | declarative and editable |

## Relation taxonomy (v0 examples)

- `IS_A`: subclass/instance only with typed endpoints.
- `PART_OF`: composition.
- `BELONGS_TO_TOPIC`: curriculum/taxonomy membership.
- `DEFINES` / `REQUIRES_CONCEPT`: definitional dependencies with meaning distinguished.
- `PREREQUISITE_FOR`: pedagogical prerequisite; may require a confidence/context qualifier.
- `EXPLAINS` / `AFFECTS`: must not infer causality from generic association.
- `SUPPORTS_CLAIM`: evidence anchored to source.
- `APPLIES_IN_VERSION`: revision or version-specific applicability.
- `RELATED_TO`: noncommittal relation; not a fallback for every connection.

A learning path is a **derived recommendation** based on prerequisite/goal/user state, never just `BELONGS_TO_TOPIC` traversal. Prevent circular prerequisite render errors; report cycles rather than silently erasing them.

## Knowledge status / security boundaries

- `draft_candidate` / `pending_review` / `validated` / `rejected` / `superseded`.
- LLM explanatory text in answer payload can be stored as `ai_draft`, not automatically `validated`.
- User explanations are scoped to personal storage regardless of their correctness.
- Source passages are cited by precise anchor; a reference ID without matching source support is insufficient.

## Graph projection examples

Astronomy: Domain > Topic > Concepts (classification), while nuclear fusion may be relevant for stellar evolution as explanatory relationship, not merely same child. A concept may appear in multiple domain views without duplicate IDs.

A Domain Tree should draw from `BELONGS_TO_TOPIC`/topic-parent membership; a Dependency View from `REQUIRES_CONCEPT`/pedagogically verified prerequisites; an Evidence View from `Claim` → `SourceAnchor`; personal overlay from `PersonalExplanation` and `LearningEvent` by ID.

## Example JSON: AI extraction candidate (not validated)

```json
{
  "id": "cand_example_001",
  "proposal_type": "relation",
  "proposed_payload": {
    "source_id": "concept_stellar_evolution",
    "predicate": "REQUIRES_CONCEPT",
    "target_id": "concept_stellar_structure"
  },
  "evidence_anchor_ids": ["anchor_demo_003"],
  "review_state": "pending_review"
}
```

This example is an **illustrative fixture**, not a verified astronomy dependency.

## Registry and co-construction contract clarification (proposed, not persisted in M0)

The only implemented API contract is HealthResponse `{status: "ok", service: "infinite-engine"}`. Core knowledge/learning contracts remain proposed; the later implemented Registry and ADR-010 sections specify executable contracts. No schema migration is needed for M0 because it creates no knowledge database.

| Entity | Required design fields | Semantics |
|---|---|---|
| DomainRelation | id, from_domain_id, predicate, to_domain_id, rationale, revision_id | Multiple parents via edges, not a parent column; classification distinct from dependencies |
| DomainSource | id, domain_id, source_id, role, rationale, limitations, revision_id | Recommendation within scope, not universal claim support |
| Evidence | id, source_anchor_id, source_revision_id, supported_entity_revision_id, support_kind, limitations | Anchor locator and actual claim support are separate |
| KnowledgeRelation | id, typed endpoints, predicate, qualifiers, evidence_ids, review_state, revision_id | Canonical name for the earlier Relation proposal, not a second relation store |
| KnowledgeRevision | id, entity_id, prior_revision_id, version, payload_hash, actor, reason, timestamp, provenance_ids | Canonical specialization of Revision; immutable history and optimistic concurrency |
| PersonalDefinition | id, concept_id, user_text, viewed_revision_id, created_at, prior_revision_id | Canonical name for personal explanatory definitions; PersonalExplanation stays an alias, not duplicate data |
| LearningView | id, owner_scope, view_type, root_ids, filters, layout_preferences, version | Saved projection/preferences; never duplicate canonical concept objects |
| DomainTopic / DomainConcept | id, domain_id, topic_id/concept_id, rationale, revision_id | Shared topic/concept membership, not validated definitions |
| ReviewRecord | id, entity_id, revision_id, payload_hash, decision, reviewer, reason, recorded_at | Append-only explicit review of exact content |
| SourceCheck | id, source_id, source_revision_id, kind, outcome, method, checked_at, actor, evidence_ref | Observed access/authority/license checks separately; unknown is not success |

Stable IDs must be opaque, type-prefixed and independent of mutable display labels, URLs and view location. The registry proposal uses UUIDv5 from immutable identity keys; final adoption and namespace require a schema ADR in M1/R1. Keep multilingual labels and aliases in child records with language tags. Never merge solely on a matching name; flag scoped aliases for review. Preserve external taxonomy release/code and mapping provenance. `category_ids` is a projection of dedicated DomainCategory membership, never DomainRelation (ADR-010).

Provenance carries local document IDs + stable page/section/offset anchors, author/generator when known, input artifact hashes and explicit unsupported state. Source URLs/licenses/dates may be unknown. Source authenticity does not prove a claim. DomainSeed approval requires vetted content and evidence beyond a catalog entry.

Candidates remain draft/pending; human approve creates a validated/curated revision, reject records rejection, revise creates a new pending revision, defer preserves pending review. Old approved revisions remain readable; replacing them is version checked. AI draft and personal states cannot implicitly become validated. Any subsequent persisted schema change requires migrations, compatibility tests and updated contracts. Registry approval is independent of source verification and seed readiness.

## Implemented Registry R1 contract — schema version 1

This section supersedes earlier proposed fields **only for the implemented catalog module**. `contracts.py` is authoritative for runtime validation. The API still exposes only health; Registry is a Python library and offline demo.

| Contract | Implemented shape / boundary |
|---|---|
| Domain | slug, domain_type, definition, scope_note; multilingual preferred/alias labels; no readiness or parent column |
| Source | source_kind, labels, optional creator, HTTP(S) URI, local_path, publication date, license, version tag, SHA-256; unknown stays null |
| DomainRelation | typed Domain endpoints; SUBDOMAIN_OF, OVERLAPS_WITH, RELATED_TO, APPLIES_TO; rationale |
| DomainSource | domain/source identity links, rationale, intended_use, authority_scope, limitations |
| Topic / Concept | multilingual labels and candidate description; no validated claim/definition semantics |
| DomainTopic / DomainConcept | domain + shared topic/concept identity and rationale |
| ReviewRecord | exact entity/version/hash, decision, reviewer, reason, timezone-aware time; revise requires next version; **no R1 persistence/promotion API** |
| SourceCheck | exact source version; accessibility/authority/license dimension; confirmed/failed/inconclusive observation, timezone-aware time, method/actor/locator/evidence_note |

`Candidate` wraps one discriminated payload, schema_version=1 and mandatory Provenance. Origin is human/ai/taxonomy_import/test_fixture; actor and rationale are required, generator/input hash optional. Evidence references an existing Source ID, exact source version and nonblank stable anchor locator; without evidence an explicit unsupported_reason is required. Locator existence/support in source bytes is not verified by R1. Taxonomy import origin alone does not capture external release mappings: those require R3's mapping contracts.

IDs derive from explicit immutable keys (e.g. `local:astronomy`), not titles, slugs or URLs. Keep the namespace and key forever; changing a key creates another identity, not a rename. Stored revisions have version, prior_version, schema_version, SHA-256 of canonical candidate JSON (including provenance), actual recording time and pending_review status. Caller-provided approval/readiness fields are rejected. Label order and symmetric edge direction are canonicalized; evidence order remains significant in the content hash.

Normalized SQL tables: registry_entity, entity_revision, label, domain, source, topic, concept, domain_relation, domain_source, domain_topic, domain_concept, provenance, evidence_reference, review_record, source_check and schema_migration. Snapshot JSON is an audit copy; payload fields, relationships, labels and evidence are separately queryable. UPDATE/DELETE triggers protect history; FKs protect references. Use the repository for typed endpoint, duplicate and graph validation; direct SQL writes are unsupported and local file access is not an authorization boundary.

`Registry.save(key, candidate, expected_version=0)` creates a candidate; subsequent edits require the current version. Replaying the identical latest candidate with its current or original base version returns the existing revision without adding history. A stale different payload fails. `BEGIN IMMEDIATE` serializes the read/validate/write transaction; rejected writes roll back completely. No batch import yet.

Duplicate slugs, current typed edges and memberships under different IDs are rejected. Duplicate aliases within one language/entity are invalid; cross-entity homonyms are permitted and returned by `label_matches(kind, language, text)` for human review. Normalization uses NFC, casefold and collapsed whitespace; no fuzzy or URL-based resource deduplication yet. Language tags use a documented syntactic subset of BCP-47 (language plus alphanumeric subtags), not full IANA validation.

`relations()` returns pending candidate graph edges, not curated knowledge. SUBDOMAIN_OF is child→parent, allows multiple parents and rejects cycles/self-links. OVERLAPS_WITH/RELATED_TO store sorted endpoints; APPLIES_TO is directed and may cycle. Concept prerequisites and learning paths are not accepted registry predicates. Source checks cannot change candidate status or grant a verified badge. There is no deletion, curated query, review promotion or seed-readiness operation in R1.

## Implemented Registry R2 contracts — database version 2

Candidate payload schema remains **1**, preserving all R1 IDs, snapshots and provenance. Database schema **2** adds review/import metadata; the migration runner applies 001 then 002 to new stores and only 002 to existing R1 stores. Old migration checksums are immutable.

- `CandidateBundle`: format_version=1, batch_id, nonempty entries. Each entry contains immutable identity_key, expected_version and a Candidate. Duplicate identities are rejected; dependency ordering resolves forward references. Circular/self references are rejected. The batch ID is permanently bound to a canonical content digest. Changed content under the same batch ID fails; exact replay returns its original revisions even if later edits exist.
- `ReviewExport`: UUID, immutable DB-backed manifest, entity/version/hash items. CSV protected fields are checked against the database, not merely against a user-editable manifest. Source provenance is exported as a protected sidecar.
- `ReviewRecord`: R1 exact-version/hash contract now persisted with actual operation time. `approve`, `reject` and `revise` are terminal for that revision; `defer` can receive a later decision. A previously rejected entity can be proposed again as a new changed candidate version. Changing a decision on the same terminal revision is intentionally unsupported.
- `ReviewReceipt`: digest of export ID, actor and validated rows, with operation result. Repeating the same applied packet makes no new ledger/revision/promotion entries. A different edit is revalidated and subject to stale-version/terminal-state checks.
- `CuratedEntry`: status=approved, immutable candidate Revision and matching ReviewRecord. The embedded Revision retains its historical pending_review creation marker; `review_state()` returns current ledger state and `curated_entries()` supplies explicit approved context. An unapproved replacement never changes the curated projection.

New normalized tables: candidate_batch, candidate_batch_item, review_export, review_export_item, review_receipt, curated_revision; current_curated is a view over approved versions. Append-only triggers protect the new history. Database triggers bind review hashes and require approval for curated insertion. Repository-level checks additionally enforce current version, typed references, dependency closure, semantic duplicates and cycles in the effective curated graph. Pending and curated graphs may differ, so both need validation.

Approval requires linked entities already curated or approved in the same transaction. Evidence requires the **exact referenced Source version** approved in history or the same batch. This accepts catalog metadata only: it does not verify source contents, license permission, facts, knowledge mastery or seed readiness.

Revision edits preserve the original candidate and provenance. The replacement uses human origin, the explicit actor and reason, the original payload hash as input_hash, and retained evidence/support gaps. CSV cannot silently rewrite protected provenance. Changing evidence needs a separately proposed candidate with explicit provenance; no field-level evidence editor exists yet.

See DOMAIN_REGISTRY for CSV field encoding, commands and limits. R1's pending-only API statements above describe its historical scope; the R2 review service is the explicit approval path.

## R3 implemented taxonomy contracts

Migration `003_taxonomy.sql` adds two normalized revision tables; 001/002 are unchanged. The candidate envelope stays at schema version 1 with an additive discriminated-union extension. Older readers must reject unknown kinds rather than silently discard them.

| Contract | Fields and semantics |
|---|---|
| TaxonomyEntry | `source_id`, exact `source_version`, `release_tag`, native `code`, `original_label`, `original_language`, `original_path`. The source must be taxonomy-kind and its pinned version_tag must match release_tag. Source revision, release and code cannot change under one ID. Path is the publisher's code locator; it creates no local edges. |
| DomainMapping | `domain_id`, `taxonomy_entry_id`, exact `taxonomy_entry_version`, `mapping_type`, `rationale`. `exact` means equivalent intended scope; `narrower_than`/`broader_than` compare the **local domain to the external target**; `related` asserts only a proposed association. No inference or automatic equivalence merge is performed. |

Native identity keys use an unambiguous JSON tuple of source key, release and native code; mapping identity keys use a JSON tuple of local domain key and native identity. Leading zeroes in codes are preserved. Native identity semantic duplicates (source/release/code) and multiple current mappings for the same local domain/entry are rejected. Each kind has independent provenance, immutable revisions and review CSVs. Approval closure requires exact pinned source/entry revisions to be approved, not merely a newer revision of the same identity. Old pins remain meaningful when later drafts exist.

`catalog.bootstrap` validates a `pilot-v1` manifest, hashes raw UTF-8 input bytes, parses saved BundleEntry suggestions and a selected taxonomy excerpt, generates mappings, sorts IDs and runs the real importer in a disposable in-memory database. It emits candidates and a deterministic coverage/gap report. Input checksums are provenance, not authenticity signatures. Existing input_hash metadata is preserved; otherwise each saved suggestion gains its artifact hash. Original files remain unchanged. No model calls, approval, SourceCheck, claim extraction or readiness transitions occur.

The pilot verifies multi-parent organization, shared concepts and distinct IDs with the same English label. Its catalog Concept intentionally rejects undeclared morphology, quantities/units/populations, image regions and patch/DLC fields. These failures identify future typed-knowledge contracts; they are not evidence those capabilities are implemented. See [pilot metadata and attribution](../data/domain_registry/pilot/README.md).

## Current Domain architecture — ADR-010, database version 4

This section supersedes earlier proposed Domain/category/source-management assumptions. Representation, Views and Personal Cognition remain separate. There is one Domain contract for preset/custom origin; origin is management, not credibility. Domain records and primary Knowledge Spaces are separate normalized entities.

### Domain aggregate and derived fields

| Requested field | Authoritative storage / projection |
|---|---|
| domain_id | registry_entity.id, fixed namespace + immutable key; labels never determine identity |
| slug | domain revision; unique across current Domain records |
| origin | domain.origin = preset/custom; NULL only for legacy unclassified records, excluded from normal discovery |
| name_zh / name_en | Preferred Label rows with zh/en language tags; absent translation remains unknown |
| aliases | Label rows with alias role and language; distinct domains may share a name |
| definition / scope_note / domain_type | Domain revision fields; nonempty scope/definition, typed kind independent of origin |
| category_ids | DomainCategory membership projection into Category IDs; never derived from DomainRelation |
| creation_method | manual / ai_assisted / classification_import, supplied together with origin |
| created_at / updated_at | First and selected entity_revision.recorded_at; original publisher dates are separate metadata |
| metadata_review_status | Exact revision ReviewRecord ledger via review_state; pending_review maps to candidate in UI, revise maps to revised |
| knowledge_readiness | Separate derived capabilities: catalogued, seed_ready, learning_ready, future evidence-backed source availability. No writable ready flag in candidate payload |

Category has ID/key, multilingual labels, slug and description. DomainCategory has ID, domain_id, category_id and rationale, with independent provenance/review/version. It creates no semantic parent edge. Category IDs/duplicates and membership references are validated. New data releases require explicit origin and category coverage; generic legacy readers tolerate omitted origin to preserve history. Explicit origin cannot subsequently change under one ID; a custom scope referencing a preset uses REFERENCES_PRESET.

DomainRelation keeps persisted names `from_domain_id`, `to_domain_id`, `predicate`, `rationale`; these correspond to source_domain_id, target_domain_id, relation_type and description. relation_id is the entity ID; provenance, created/updated times and review state come from shared revision/ledger records. Direction, symmetry, allowed legacy predicates, duplicates and cycle rules are authoritative in [DOMAIN_ARCHITECTURE](DOMAIN_ARCHITECTURE.md#domain-relation-semantics).

### Source and recommendation contracts

Source retains existing fields and adds optional language, coverage_description, access_conditions, bibliographic_reference, resource_identity, discovery_method and updated_on. New source kinds include local_document, book, paper, website and other; existing institution/organization/textbook/database/reference/documentation/taxonomy kinds remain valid. creator describes author/institution; title comes from multilingual labels; uri/local_path/bibliography are alternative descriptive locators. Dates/license/version/coverage/access may be unknown. None of these fields authorizes resource access or proves verification.

SourceRevision is the existing immutable Source entity_revision, not a competing table. Explicit resource_identity duplicates are rejected among current revisions; omitted identities are not guessed or globally resolved. DomainSource continues to hold domain/source references, rationale, intended_use, authority_scope and limitations. Its nullable intended_learning_level is a recommendation qualifier, not a universal trust label; unknown levels stay null.

Acceptance is exclusively a space relationship. Source check status and last_checked_at are derived per check kind/source revision from SourceCheck, and claim verification belongs to future Claim/Evidence. There is no universal verified boolean. Catalog approval does not turn an unknown license into a permission statement.

### Minimal local application contracts

| Contract | Implemented fields and invariants |
|---|---|
| KnowledgeSpace | id, unique domain_id, selected_domain_version, created_at; one primary local space per Domain; same function for preset/custom; no seed dependency |
| KnowledgeSpaceSource / SourceChoice | space_id, source_id, exact source_version, acceptance_state accepted/removed, optional note; append-only events with actual recorded_at; identical choice replay is idempotent |
| PersonalOverride | space_id, optional display_name and scope_note; append-only local snapshots; null clears that override; never changes curated Domain metadata |
| DomainDiscoveryItem | Domain Revision + exact metadata_review_status; seed_ready and learning_ready fixed false while no readiness service exists |

LocalDomains supplies substring search over normalized multilingual labels/aliases, manual/AI-assisted custom metadata creation, primary-space selection and personal source/override writes. Default preset results use approved revisions; optional candidates are explicitly pending. Custom creation can retain the same name as a preset/custom Domain; a slug collision receives a deterministic ID suffix. It does not merge identities. Public R2 approval dependency rules do not apply to private collection acceptance. Library calls are not authenticated multi-user APIs; the local process/file owner is the trust boundary.

Future space-scoped records include internal structure nodes, view configuration, conversations, personal questions/explanations/preferences and learning events. These are designed boundaries, not implemented tables or services. Space-level source collections and overrides are excluded from registry CSV export. A future curated-release exporter must additionally exclude custom/private resource metadata; do not run generic catalog exports over personal stores for publication.

### Migration and compatibility

004 adds optional columns, normalized categories and personal-space tables. Expanding SQLite relation CHECK constraints requires a transactional table copy; existing rows are copied byte-for-byte and append-only triggers recreated. Migrations 001–003 remain unchanged. Existing review receipts, source checks, snapshots and IDs are retained. New optional fields serialize as absent when unknown, preserving old snapshot hashes and batch digests; old records are never assigned a fabricated origin or creation timestamp.

CSV export includes additive metadata columns with JSON null for unknowns. Old packet columns are accepted only when all corresponding stored revisions lack those fields. Protected originals, exact hashes and provenance remain mandatory. Changing management metadata requires a pending revision; it does not silently reinterpret existing approvals. The original R3 bundle stays replayable and is explicitly not a new preset release.

Foundation tests are in test_domain_architecture.py; future full-application acceptance is specified in [custom-domain-lifecycle](../tasks/custom-domain-lifecycle.md). No UI, seed initialization or complete knowledge editor is claimed.

## Source Discovery transport v1

`catalog.discovery.DiscoveryRequest` carries Domain scope/origin, goal, requested data types, languages, optional profile/version and existing exact Source revisions. `DiscoveryResult` carries source_candidates, domain_source_candidates, source_checks, coverage_assessment and recommended_next_actions. Candidate arrays reuse BundleEntry/Candidate and enforce Source/DomainSource kinds. Coverage and actions retain Provenance; assessments retain per-source utility, audience, formats, acquisition options, priority and uncertainty.

Call both Pydantic validation and `result.validate_for(request)`: the second validates Domain/source endpoints, expected source versions, explicit resource identity duplicates, recommendation/assessment completeness and exact source payload hashes on checks. DiscoveryCheck records accessibility/identity/relevance/authority/license observations separately, with actual time/method/actor/locator/evidence. Missing checks mean not checked; unknown license cannot be confirmed. Claim verification and personal acceptance are not check kinds. Schema validation does not prove observations truthful. See the [exchange specification](../skills/source-discovery/references/contracts.md) for storage/review boundaries.

This is a transient, versioned exchange format, not a change to persisted Candidate or SourceCheck. This transport adds no database migration and does not rewrite historical snapshots. Conversion from this transport to persisted checks, provider execution and acquisition are outside this slice.

## Source discovery v1 — database version 5 (ADR-012)

Executable contracts: `sources/contracts.py`; interchange schemas: [schemas/sources](../schemas/sources). [SOURCE_DISCOVERY](SOURCE_DISCOVERY.md) defines Source Profile, stages, adapters and native anchor semantics.

SourceProvider, SourceDocument and SourceAnchor use distinct type-prefixed UUIDv5 IDs in the existing permanent namespace. SourceResource is a sidecar keyed to the existing Source ID and exact version, optionally linked to an exact Provider revision. DomainSource and SourceCheck remain existing catalog contracts; SourceReview narrows ReviewRecord to Source metadata and uses its existing approval service. Personal acceptance stays exclusively KnowledgeSpaceSource.

ArtifactEntry has immutable identity_key, version, discriminated payload and mandatory Provenance. Document binds Resource revision and content hash; Anchor binds Document revision and matching hash. Locators distinguish text section/code-point offsets, PDF page, web selector/quote, structured selector and image region/description origin. Locator checking is independent of claim verification. Access tracks unknown/public/local/login/subscription/unavailable separately from unknown/permitted/restricted reuse; permitted requires evidence, never host authorization.

Migration 005 adds source_artifact, source_artifact_reference, source_resource_revision and source_manifest, all append-only with reference FKs. Artifact snapshots preserve full typed metadata and provenance; pins are queryable in reference tables. Source Resource pins reference existing normalized Source revisions. No old snapshots or checksums are rewritten. Existing Source records need no backfill; old IDs/review hashes/space choices remain valid. A new sidecar may attach to a later existing Source revision; later sidecar updates are sequential. Catalog shape and candidate schema version remain 1. Unknown new interchange versions are rejected, not silently downgraded.

Source candidates/associations import transactionally into pending metadata only; duplicates, incompatible references, wrong hashes, changed batch content and reused revision content fail. Same batch replay is idempotent. Profiles/plans are validated files and are retained in caller-managed version control/local research storage; they are not executable jobs or persisted scheduling records. SourceReview/SourceCheck cannot be injected by these manifests. No source bytes, extracted claims or retrieval index are written.

## Proposed multimodal contracts — ADR-012 / acquisition Phase 1

**Design only:** no changes to current Pydantic models, database version 5, IDs, snapshot
hashes or migrations. The following strict records describe future runtime contracts,
not payloads currently accepted by `catalog`. Adapter requests/results and failure enums
are defined in [MULTIMODAL_ACQUISITION](MULTIMODAL_ACQUISITION.md).

### Common identity and provenance

Reuse Source and its immutable SourceRevision. `SourceRef` pins source_id, positive
source_version and revision_hash. New IDs follow ADR-007's stable opaque identity policy;
new type prefixes require explicit implementation and compatibility tests. Platform
identity uses a provider-normalized immutable tuple (platform, resource_kind, external_id),
not mutable URLs or titles. `video_id` is the existing Source ID, not another identity store.
Local imports allocate/persist an immutable import identity; content hash supports repeat
import lookup but never silently merges separate editions or provenance.

ArtifactManifest (proposed shared MediaAsset backing, bound to an exact SourceDocument revision) contains artifact_id, SourceRef,
document_ref (Document ID/version/hash), SHA-256, relative managed blob key, MIME, bytes, original locator, acquired_at,
acquisition_method, permission_receipt_id and nullable duration_ms. Blob bytes are immutable;
local paths and secrets are private, never bundle exports. Distinguish metadata-only
Sources from artifacts: no fabricated hash, duration or artifact for a discovered URL.

Every derived revision pins processing_run_id and input artifact/revision hashes.
ProcessingRun stores operation, adapter name/version, model identifier/version/hash when
used (null for deterministic parsing), sanitized config + digest, tool version, started_at,
finished_at, time mapping and output hashes. Missing model version is explicitly unknown,
not a claim of reproducibility. UTC timezone-aware observation times differ from publication
dates. Unknown language, duration, license and creator remain null.

Reuse ADR-011 SourceDocument for each acquired media/subtitle edition and its native
SourceAnchor identity/revision envelope. Video references keep the parent SourceRef plus
exact Document pins; a Source revision alone cannot identify the bytes of multiple files.
SourceDocument metadata marked available by an offline import is not proof of local bytes;
only host-verified acquisition receipts and matching manifests make it processable.

### Video entities and storage mapping

| Entity | Required design fields (nullable fields marked ?) | Rules / reuse |
|---|---|---|
| VideoSource | SourceRef, platform (`local/youtube/bilibili/other`), original_url?, platform_id?, creator_id?, duration_ms?, language?, media_artifact_id?, media_document_ref? | Typed Source extension; title, creator, publication date and license remain Source fields. Platform ID/URL required for identified remote video, nullable for local-only. Processing status is a projection of stage jobs, not a truth flag. |
| VideoCollection | collection_id, platform, external_id?, original_url?, title, creator_id?, source_ref?, revision, memberships | Reuse a Source revision if collection itself is registered; membership items contain video_source_id, observed_position?, observed_at, availability. No copied VideoSource objects; order is not identity. |
| CreatorSubscription | subscription_id, version, platform, creator_id?, collection_id?, domain_id?, space_id, filters, sync_config, processing_preferences, sync_state | At least one creator/collection target; if both, constrain to that creator's collection. Domain, when supplied, must match the primary space. Local configuration, not curated registry metadata. |
| Transcript | transcript_id, revision, video_source_ref, video_document_ref, raw_artifact_id, origin (`subtitle/local_asr/human`), language?, parent_revision?, correction_actor?, correction_reason?, processing_run_id | Immutable revision chain. Original raw subtitles/audio retained; correction records original lineage and expected base version. A translation is another track linked to its parent, not replacement of original speech. |
| TranscriptSegment | segment_id, transcript_id, transcript_revision, ordinal, text, start_ms?, end_ms?, original_cue_refs, timing_kind, timing_mapping_id? | IDs stable within immutable revision; revised segmentation produces new segments with lineage. Both times null only for untimed text, which cannot support a temporal anchor. Overlap allowed. |
| VideoChapter | chapter_id, revision, video_source_ref, title, document_ref, start_ms, end_ms, transcript_ref?, segment_ids, method, processing_run_id, review_state | Optional proposal, manual or source-provided; never canonical concept hierarchy or invented timing. |
| VideoFrame | frame_id, video_source_ref, media_artifact_id, image_artifact_id, presentation_time_ms, decode_timebase, original_pts, processing_run_id | MediaAsset specialization; actual decoded timestamp, not frame ordinal. Repeated pixels at different times remain different frame references. |
| VisualObservation | observation_id, revision, frame_refs, region?, text, kind (`ocr/description/inference`), confidence?, processing_run_id, review_state | Candidate observations, not ground truth. Coordinates tied to original frame dimensions; never mislabel inferred description as transcript quote. |
| VideoKnowledgeCandidate | candidate_id, revision, proposal_type, proposed_payload, evidence_anchor_ids, support_gaps, processing_run_id, review_state | KnowledgeCandidate specialization, not a second review system. Unsupported proposals remain candidates; exact review plus evidence rules gate canonical commits. |
| TemporalSourceAnchor | anchor_id, video_source_ref, document_ref, start_ms, end_ms, transcript_ref?, transcript_segment_id?, frame_ref?, original_source_url?, timing_kind, timing_basis_ref | SourceAnchor variant defined below; no URL-only evidence. |
| AcquisitionJob | job_id, operation, source_ref?, subscription_ref?, input_refs, permission_id, limits, idempotency_key, config_hash, state, attempts, checkpoint_refs, output_refs, failures, created_at, updated_at | Reusable discovery/acquisition/processing orchestration envelope; discovery may lack SourceRef until registered. Each attempt carries start/end/lease, error and retry metadata. |

Separate tables only where queryable collections/history justify them: jobs, subscription
configuration/checkpoints, artifact manifests, transcripts/segments and anchor lookups.
Store VideoSource extension on a pinned source revision; use shared media/processing/
candidate/review repositories for frames, observations, chapters and candidates. No
parallel video-source identity, duplicate license ledger or video-specific approval table.
Reuse migration 005 artifact/revision/reference storage for compatible extensions before
adding tables. Final table layout and indexes are a Phase 2 migration decision, not SQL
shipped here. AdapterKind/media/locator unions require a versioned extension; do not pass
video payloads to existing v1 readers or mutate generated schemas in this design task.

### Temporal citation schema and validation

`TemporalSourceAnchor` is a proposed `temporal` locator variant inside the existing
SourceAnchor artifact envelope, alongside ADR-011 native locator variants. Its Document
ID/version/hash must match the media edition; transcript and frame inputs must resolve to
that same video edition. The flattened view below is a service projection, not a second
anchor store or a currently accepted SourceAnchor payload. Integer milliseconds use
half-open intervals `[start_ms, end_ms)`: `0 <= start_ms < end_ms`. If source duration is
known, end must not exceed it. Unknown duration is retained with an explicit validation
limitation; subtitle timing alone does not prove synchronization with the media.

`transcript_ref` contains transcript_id + exact positive revision; segment_id requires that
ref and must belong to that revision and video SourceRef. For a transcript anchor, the
interval must be contained within the segment interval; choosing a smaller range requires
an explicit timing basis (word timing or human-aligned evidence). Otherwise cite the whole
cue. Multi-cue excerpts carry multiple anchors or a segment preserving all cue mappings,
never an invented sentence-level time. A frame-only anchor may omit transcript references
but must pin an actual frame whose presentation time lies in the interval; its duration
must come from decoder timing or explicit evidence, not a made-up millisecond extent.
An untimed image observation uses an image anchor instead.

`timing_kind = subtitle_declared | asr_estimated | media_pts | human_aligned` records origin,
not accuracy. `timing_basis_ref` pins original cue, model word timing, decoder data or
human alignment revision. Record any offset/scale transform and its provenance. Do not
round stored timestamps to whole seconds or interpolate missing ones. ASR time estimates
must stay labeled approximate; no precision claim exceeds the underlying evidence.

Illustrative schema instance below is **not real evidence or valid current runtime IDs**;
implementation fixtures must allocate IDs through the stable ID service:

```json
{
  "kind": "temporal",
  "anchor_id": "<allocated-anchor-id>",
  "video_source_ref": {
    "source_id": "<existing-source-id>",
    "source_version": 1,
    "revision_hash": "<sha256>"
  },
  "document_ref": {"document_id": "<media-document-id>", "version": 1, "content_hash": "<sha256>"},
  "start_ms": 1250,
  "end_ms": 2800,
  "transcript_ref": {"transcript_id": "<transcript-id>", "revision": 1},
  "transcript_segment_id": "<segment-id>",
  "frame_ref": null,
  "original_source_url": null,
  "timing_kind": "subtitle_declared",
  "timing_basis_ref": "<original-cue-ref>"
}
```

RetrievalHit pins anchor_id + anchor_revision, exact SourceRef and Document ID/version/hash, processed revision, original excerpt,
optional corrected excerpt (explicitly labeled), score and support gaps. Canonical Evidence
separately binds an anchor to an exact Claim revision and support kind. Neither a retrieval
score nor the presence of a timestamp verifies a claim. Citation rendering must resolve the
pinned revision, never silently fetch the newest transcript.

A future `SourceOpener` returns a local-player seek target or a safe platform deep link plus
displayed precise interval. Platform-specific URL builders must be allowlisted and tested;
if the platform accepts only whole seconds, seek before the anchor while displaying the
original milliseconds. Unknown URL formats fall back to the original safe link plus time
label, without claiming seeking works. No backend fetch or media download occurs on
citation construction. Platform seeking and the player UI are not implemented in Phase 1.

### Subscription and permission contracts

`filters = {published_after?, published_before?, languages: list[str], keywords: list[str]}`;
unknown publication/language is reported as unmatched/unknown, never silently fabricated.
`sync_config = {enabled: false, mode: manual, interval_seconds?, max_items, max_pages,
max_requests, deadline_ms, credential_ref?}` by default. Scheduled mode requires explicit
positive interval and finite bounds. `processing_preferences = {download: false,
transcribe: false, visual_analysis: false, extract_candidates: false, batch_permission_id?}`.
Any enabled processing stage requires the corresponding separately checked permission.

`sync_state = {config_version, cursor?, watermark?, last_attempt_at?, last_success_at?,
last_error?, complete: false}`; page commit and cursor advance are atomic. No runtime
credential value is serialized. Configuration updates use expected_version; stale writes
fail. Provider-native video identity deduplicates overlapping collections and retries;
metadata changes append revisions while old evidence remains pinned.

`AcquisitionPermission` and `Limits` have the field/operation definitions in the acquisition
architecture. Grants are host-owned and revocable, not source-supplied text, review approval
or SourceCheck outcomes. Job receipts pin the evaluated policy version, grant and decision;
resume reevaluates present permissions. Revocation stops further work without rewriting
historical receipts or silently deleting acquired evidence.

### Migration gate

Phase 1 changes documentation only. Do not alter migrations 001–005 or add video fields to
stored schema-version-1 snapshots now. Phase 2 must add a forward migration with backups,
transactional failure/reopen tests and preservation of all existing IDs, hashes, approvals,
Source choices and unknown values. New Source extensions must not regenerate old snapshots.
Readers reject unsupported new variants explicitly; old stores without media remain valid.
Migration tests must cover a populated version-5 registry and exact-revision evidence pins.
