# Source Discovery and Acquisition Architecture

Status: offline v1 interchange, validation and metadata import implemented. Network discovery, acquisition executors, production parsers, extraction, claim verification and RAG are not implemented. Source research is an independent human/external workflow; Codex need not collect the initial catalog.

## Independent stages

| Stage | Input → output | Gate and meaning |
|---|---|---|
| Discovery | Domain + Source Profile + external research → source_candidates.json | Pending metadata, provenance, explicit support gaps; never auto-approved |
| Selection | Candidate resources + scope rationale → source_associations.json or local source choice | DomainSource is a recommendation; personal acceptance uses existing LocalDomains.choose_source without professional review |
| Acquisition planning | Exact document revisions + profile → acquisition_plan.yaml | Proposal only; rights, accessibility and host authorization are independent |
| Acquisition execution (future) | Authorized bounded plan → content-addressed bytes and document revision | Host controls network/file allowlists, redirects, request/byte limits and credentials |
| Extraction (future) | Supplied bytes + adapter → anchors, parse issues and candidate claims | Partial failures remain visible; no promotion to canonical knowledge |
| Verification (future) | Exact claims + anchored evidence + applicability → reviewed claim revisions | Metadata review, prestige, accessibility and user acceptance cannot substitute for claim evidence |

The `sources` package depends on `catalog`; catalog does not import sources. SQLite migration 005 adds immutable artifact revisions, typed-reference storage, Source revision bindings and manifest receipts. Existing Source, DomainSource, SourceCheck, ReviewRecord and KnowledgeSpaceSource remain authoritative. No UI/API or agent integration is claimed.

## Models and identity

- **SourceProvider:** publisher, institution, community or personal supplier. Name/homepage and attributed provenance do not establish authority.
- **Source Collection / Resource:** existing catalog Source describes the logical collection or standalone resource. SourceResource is an exact Source revision sidecar carrying optional Provider pin, collection/standalone classification and access metadata. It has the same Source ID/version and immutable identity key, not a second resource identity. “Collection” here is a publisher resource; a user's accepted collection remains KnowledgeSpaceSource.
- **SourceDocument:** individual web page, edition/file, dataset snapshot, API response or image. Pins Resource revision, media/adapter, original locator, publisher version, content hash and acquisition state. `available` requires a hash but import does not prove that bytes exist; the future acquisition host must establish that observation.
- **SourceAnchor:** pins exact Document revision and hash. Native text ranges, PDF pages, web selector/quote, structured selectors or image regions survive future indexing. `checked` locators require evidence but do not verify claims. Unknown/stale/unresolvable locations are explicit.
- **DomainSource:** existing independent recommendation with intended use, authority scope and limitations, shared by preset/custom Domains. It follows the current catalog identity-level reference contract; acquisition and citations additionally pin Resource/Document revisions.
- **SourceCheck:** existing append-only exact Source revision observation, independently dimensioned accessibility/authority/license. Unknown is the absence of an observation; inconclusive is a recorded uncertain result. Check observations never grant host permissions.
- **SourceReview:** source-specific validation of existing ReviewRecord shape, exact entity/version/hash, reviewer/reason/time and decision. No second review ledger. Apply reviews through existing catalog review service; candidates cannot inject decisions. Provider/Document/Anchor review workflow is future work; their import is always candidate metadata.

All new artifact entries retain immutable identity_key, positive version and mandatory Provenance. Resource identity uses existing `source_` UUIDv5; Provider/Document/Anchor extend the permanent namespace with distinct kinds. Display names, URLs and publisher versions are mutable metadata, never IDs. Importing a changed payload under an existing revision fails; append the next revision and retain old citations. A Source sidecar can first attach to an existing later Source revision; subsequent sidecars advance consecutively. Old catalog-only resources need no fabricated provider or document.

## Source Profile v1

`search_profile.yaml` is the configurable **Source Profile**; the name emphasizes its discovery purpose. It requires format_version, profile_id, revision, exact Domain pin, purpose, languages, allowed adapter types, inclusion/exclusion criteria and provenance. Optional queries, provider_allowlist, max_candidates, max_requests and network_requested bound future discovery. Defaults are offline (zero requests), ten candidates. Languages and queries are descriptive; no model or network provider runs on load.

The same profile works with preset/custom Domains. Research criteria may cover editions/translations for Latin, population/conditions and evidence type for fitness/nutrition, or patch/DLC applicability for Stellaris. Criteria guide candidate review; they are not evaluated as professional verification by this implementation. Unknown fields are rejected; future format changes require an explicit version/migration. Secrets and executable expressions have no fields.

`acquisition_plan.yaml` pins profile_id/profile_revision and exact Documents. Actions are metadata_only, request_access, use_local or download; plans always have proposed state. Local/download proposals require permission evidence, but the string is not authorization. The semantic validator resolves pins and disallows unknown/restricted reuse for content acquisition; download also needs public accessibility, a provider in the profile allowlist and a compatible network budget. Default plans do not acquire content. Per-document and Resource restrictions both apply.

At execution time a future host must recheck current permissions and access restrictions, enforce actual byte/request/time budgets and URL/path/redirect policy, and obtain authorization within the user's requested scope. No crawling, paywall bypass, automatic copyrighted downloads or credential strings in manifests. Permission expiry/revocation and authentication are not implemented.

## Interchange and import

Four generated JSON Schema 2020-12 files live in [schemas/sources](../schemas/sources). JSON Schema validates structure; Pydantic and the importer additionally enforce semantic constraints, exact pins, type-compatible anchors, hashes, duplicate identities, revisions and transaction safety. Do not use schema-only validation as authorization or referential validation.

- source_candidates.json: Source-only catalog entries plus Provider/Resource/Document/Anchor entries; batch ID is bound to the entire candidate+association content.
- source_associations.json: DomainSource-only entries; referenced Domains must already exist. Import never creates or relabels domains implicitly.
- search_profile.yaml: Source Profile above.
- acquisition_plan.yaml: proposed acquisition batch above.

The safe loader limits files to 2 MB and nesting depth 40, rejects duplicate mapping keys, YAML aliases, non-string keys, custom executable tags and extra fields. YAML represents configuration only. Catalog and artifact writes share one transaction. Missing references, bad anchors, version conflict or association failure roll back the full batch. Exact replay is idempotent; a batch ID cannot be reused for changed content. Dry run rolls back candidate data; opening a named database still initializes/applies schema migrations. Use a disposable database to avoid touching a real store during validation.

Original external research files should be retained outside git when private. Put their hash into provenance.input_hash and preserve human/AI origin, generator, actor, rationale, evidence pins or explicit support gaps. Do not replace original AI suggestions when reviewing; append attributed revisions. Artifact revisions have canonical hashes and recording timestamps; imports do not infer authenticity from hashes.

Generate schemas: `uv run --frozen python -m infinite_engine.sources schemas/sources --schemas`.

Run the disposable four-domain demo: `uv run --frozen python scripts/demo_sources.py`.

For an existing local registry containing the Domain IDs: `uv run --frozen python -m infinite_engine.sources examples/sources/astronomy --database .local/sources.sqlite`. Default is dry-run; `--apply` persists metadata. Do not publish personal stores. The example Domain bootstrap is intentionally separate, in examples/sources/domains.json; the demo imports it automatically into a temporary store.

## Adapter designs (interfaces, not implemented parsers)

`SourceAdapter.parse(content: bytes, document) -> ParseResult` only receives caller-supplied bytes. It has no network/filesystem capability. Results distinguish complete/partial/failed, retain successful anchors and localized parse issues. The host must validate anchors against the document and persist through the normal importer. No current adapter claims to parse any of these formats.

| Adapter | Future normalization and stable anchor requirements | Failure/security behavior |
|---|---|---|
| Web | Frozen response hash, original and final URL, heading/DOM selector plus exact quote; text offsets refer to a versioned extraction | Detect missing selectors/changed pages; no JS execution or recursive link following |
| PDF | Original file hash, 1-based physical page, section; image regions use original rendered page coordinates | Report unreadable/encrypted pages; distinguish OCR from original text; no password bypass |
| Local text/Markdown | Original bytes hash; documented UTF-8 normalization, section and half-open Unicode code-point offsets | Host approves a specific path/root, rejects symlink escape; report decoding failures |
| CSV/JSON/XML | Snapshot hash; CSV row ordinal + field (header excluded, data rows 1-based), JSON Pointer, XPath | Preserve duplicate keys/row identities or report ambiguity; disable XML entities/network; bound nesting and rows |
| API metadata | Exact response snapshot hash, endpoint/version and record key/field | Metadata is not downloaded full text; host handles rate/authentication and redacts secrets; no credentials in locator |
| Image + description | Original image hash, pixel x/y/width/height; description and human/publisher/AI/OCR origin | Check bounds against original dimensions; missing caption stays missing; model caption never becomes verified observation |

A future retriever returns anchor ID + anchor revision + Document ID/revision/hash with quote and extraction-version context. Never silently retarget an old anchor to a newer document or use a bare provider URL as a citation. Full-text storage, extraction normalization maps, image dimensions/OCR processing, citation viewer and RAG indexes are next-stage work.

## Acceptance and next bounded implementation

This slice establishes validated metadata import and architecture, not full M1/M2 completion. Automated tests cover four mock domains, JSON Schema agreement, reference/hash failures, rollback, replay/restart, permission proposals, safe YAML and additive migration. Existing catalog suites cover acceptance/review isolation, duplicate aliases, invalid relations, prerequisite/classification constraints and old snapshot compatibility.

Next: implement **one authorized local text/Markdown acquisition adapter** with caller-supplied bytes/path policy, actual content hashing, Unicode offset round trips, partial decoding failures and exact anchor persistence. Add no network search or RAG in that task. Then separately implement image processing with region validation, bounded web/PDF acquisition, discovery host tools and claim extraction/review. Each requires its own acceptance gate.

## Adjacent discovery and multimodal specifications

The working tree also contains `catalog.discovery.DiscoveryRequest/DiscoveryResult` for in-memory research exchange and a separate [multimodal design](MULTIMODAL_ACQUISITION.md). These are not alternative persistent Source identities. A future bridge can map exchange source_candidates/domain_source_candidates into the two import manifests while retaining assessments, checks and original research as attributed artifacts. That bridge, temporal/video locators and discovery-tool invocation are not implemented here. Do not silently drop research assessments or reinterpret proposed temporal anchors as this v1 citation format.
