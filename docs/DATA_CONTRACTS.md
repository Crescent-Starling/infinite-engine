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

The only implemented API contract is HealthResponse `{status: "ok", service: "infinite-engine"}`. All knowledge contracts in this document remain proposed. No schema migration is needed for M0 because it creates no knowledge database.

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

Stable IDs must be opaque, type-prefixed and independent of mutable display labels, URLs and view location. The registry proposal uses UUIDv5 from immutable identity keys; final adoption and namespace require a schema ADR in M1/R1. Keep multilingual labels and aliases in child records with language tags. Never merge solely on a matching name; flag scoped aliases for review. Preserve external taxonomy release/code and mapping provenance. Legacy `category_ids` becomes a projection of DomainRelation, not authoritative storage.

Provenance carries local document IDs + stable page/section/offset anchors, author/generator when known, input artifact hashes and explicit unsupported state. Source URLs/licenses/dates may be unknown. Source authenticity does not prove a claim. DomainSeed approval requires vetted content and evidence beyond a catalog entry.

Candidates remain draft/pending; human approve creates a validated/curated revision, reject records rejection, revise creates a new pending revision, defer preserves pending review. Old approved revisions remain readable; replacing them is version checked. AI draft and personal states cannot implicitly become validated. Any subsequent persisted schema change requires migrations, compatibility tests and updated contracts. Registry approval is independent of source verification and seed readiness.
