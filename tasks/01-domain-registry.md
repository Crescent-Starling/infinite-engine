# Domain Registry — R1–R3 implemented; owner data review pending

Objective: create the curated catalog/review infrastructure, without full knowledge bases.
Dependencies: M0 tooling; M1 ID/provenance contracts before persisted implementation.
Scope/deliverables: approved normalized schema, migration, source recommendations with rationale, reproducible input manifests, editable review CSVs, validation/import, four-domain candidate pilot.

Use [the retained detailed bootstrap proposal](domain-registry-bootstrap.md) as the implementation plan; do not duplicate it or assume its schema decisions are approved by M0. R1–R4 are bounded review slices, mapped to the DR track in PLANS.

Acceptance: immutable suggestions and reviews, only explicitly approved exact revisions promoted, source/mapping provenance survives idempotent imports, multi-parent classification remains distinct from dependencies, pilot readiness remains honest.
Tests: schema/FK/duplicate/cycle checks, multilingual labels, stale versions, all review actions, protected CSV fields, atomic rollback, no-key/offline replay and unknown source metadata.
Risks: taxonomy licensing, uncertain source authority, semantic duplicates, review workload and unsupported definitions.
Out of scope: broad autonomous collection, complete seeds, full knowledge databases, frontend review UI unless separately approved.

## Current progress

R1 contracts/storage implemented in the dedicated `feature/domain-registry-contracts` branch; ADR-007 defines the adopted scope. R2 and R3 follow-up implementations are described below. The minimum shared identity/source/provenance prerequisite is included in R1; full M1 is not marked complete. See the detailed bootstrap task and DATA_CONTRACTS for implemented versus deferred fields.

R2 is implemented on feature/domain-registry-review: candidate bundles, editable review packets, explicit decisions, atomic promotion and replay receipts. R3 is implemented on feature/domain-registry-pilot: pending four-domain metadata, selected external mappings, source recommendations and a pinned offline bootstrap. Owner data review and R4 acceptance remain pending. See DOMAIN_REGISTRY for the actual manual workflow and VALIDATION for observed tests.


ADR-010 now separates the broad Preset asset from Custom Domains, Knowledge Spaces and internal knowledge structures. Continue Track A via [domain-universe-bootstrap](domain-universe-bootstrap.md) or Track B via [custom-domain-lifecycle](custom-domain-lifecycle.md). The older R1–R3 plan remains historical evidence, not permission to bulk-build global topic/concept trees. The architecture fixture and migration 004 preserve the R3 pilot without silently classifying it as preset data.
