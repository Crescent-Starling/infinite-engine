# Machine-readable exchange

Authoritative Python models: [catalog/discovery.py](../../../backend/infinite_engine/catalog/discovery.py). Use `DiscoveryRequest.model_validate_json` and `DiscoveryResult.model_validate_json`, then `result.validate_for(request)` for request-bound checks. JSON Schema is available through each model's `model_json_schema()`; no generated duplicate schema is maintained.

Request contains domain_id, domain_name, domain_definition, scope_note, domain_origin, source_profile (nullable means choose a profile), learning_goal, requested_data_types, existing_sources (exact Source revisions), preferred_languages, and optional version_context. Do not include personal contents in a search query without permission.

Result format_version=1 carries exactly five substantive outputs:

- source_candidates: Source-only BundleEntry records with stable identity keys, expected revision and Candidate provenance. Existing resources retain their IDs/keys rather than receiving new ones.
- domain_source_candidates: DomainSource-only BundleEntry records, linking the requested Domain to candidate or existing Source IDs, with recommendation rationale, use, authority scope and limitations.
- source_checks: discovery observations bound to the source candidate/revision payload hash. Each specifies a check dimension, outcome, actual time, method, actor, locator and evidence note. An absent observation means not checked. These are transport observations, not automatically persisted SourceCheck records or verified claims.
- coverage_assessment: selected profile, rationale, search availability, contextual provenance, requested coverage, gaps and redundancy notes; per-source assessment records audience, usefulness, currency/version applicability, formats, acquisition options, priority and questions. Empty lists mean no known information, not guaranteed absence of formats or gaps.
- recommended_next_actions: action and rationale, each with provenance; no tool invocation or permission is encoded.

`payload_hash` is `digest_json(source.model_dump(mode="json"))`, binding observations to exact metadata. It is not an authenticity signature. Only actually observed checks belong in source_checks; inaccessible URLs produce failed or inconclusive accessibility observations, never false success. `claim_support` is deliberately excluded: specific Claim/Evidence verification is a separate future workflow. A syntactically valid check can still be false; a human must inspect its evidence.

The existing persisted SourceCheck supports accessibility, authority and license against a saved source revision. Mapping transport observations to that ledger requires an explicit, separately implemented adapter that verifies the exact stored payload. Identity/relevance observations remain in the discovery artifact until a compatible persistence contract exists. No automatic checks, approval or acquisition adapter is implemented.

Store local discovery artifacts under ignored `.local/`, keeping the original immutable result when reviewing. Personal accept/reject/modify/add/defer decisions are not catalog ReviewRecords. Save accepted source metadata as pending, then select its exact revision with LocalDomains.choose_source. Preset recommendation promotion separately uses review CSVs and exact human approval. No migration is introduced by this transient format; historical candidates remain unchanged. Reconcile any separately developed source-artifact persistence contracts before adding an adapter.
