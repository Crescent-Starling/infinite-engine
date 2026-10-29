# Preset Domain Registry and candidate curation

The registry is a durable candidate/curated data asset, separate from Domain Seeds and extended knowledge. ADR-010 distinguishes the system-maintained Preset Registry from local Custom scopes and their Knowledge Spaces; [DOMAIN_ARCHITECTURE](DOMAIN_ARCHITECTURE.md) is authoritative. Catalog coverage does not mean source verification, seed readiness, learning readiness or user mastery.

## Pipeline

Discovery → Candidate Generation → Validation → Human Review → Approval → Import → Maintenance.

- Discovery evaluates established academic/knowledge classifications using official publisher metadata, release identifiers and reuse terms. R3 selects an attributed ISCED-F excerpt with its stated license; other classification adapters remain future work. Use supplied or permitted snapshots; no autonomous crawling.
- Preserve the original taxonomy's release, native codes, multilingual labels and path. Map explicitly into local domain IDs using exact/broad/narrow/related mappings; do not blindly copy or merge taxonomies.
- Candidate generation stores original suggestions, author/generator metadata where known, input hashes, source anchors, domain definitions, relationship rationale and support gaps. Recorded outputs are replayable; fresh LLM calls are not deterministic.
- Validation checks schema version, stable IDs, duplicates/aliases, typed relationships, classification cycles, references, provenance and base revision. Validation is not approval.
- Human review uses editable UTF-8 CSVs with original and revised fields, protected identity/revision/hash, reviewer, reason and approve/reject/revise/defer actions. Preserve originals independently; revise creates a pending revision requiring explicit approval.
- Approval binds a decision to exact payload and revision. Approved replacements retain prior history. Only explicitly approved records whose references resolve to approved records can be promoted atomically and idempotently.
- Maintenance records new proposals, taxonomy release mappings and source checks; never overwrites reviewed content with model output. Source-check outcomes are dated observations, not permanent truth.

## Normalized model

Domain + localized label rows; DomainRelation; Source; DomainSource with recommendation rationale; DomainTopic and DomainConcept memberships into shared Topic/Concept identities; append-only ReviewRecord and SourceCheck. Supporting taxonomy/mapping, revision and provenance records preserve external identities and review evidence. Proposed details and decisions requiring owner review remain in [the bootstrap plan](../tasks/domain-registry-bootstrap.md).

A domain graph supports multiple parents. Classification SUBDOMAIN_OF is acyclic; OVERLAPS_WITH/RELATED_TO are symmetric; APPLIES_TO is directed. These are implemented registry predicates, separate from prerequisites and pedagogical ordering. Views may project a tree without changing identity or discarding alternate parents.

Candidate source categories include official institutions, academic organizations, open textbooks, professional databases, authoritative references and official technical documentation. Record why each is relevant, its scope and limitations. Authority is context-specific. Unknown URLs, publication dates and licenses remain unknown; no fabricated verification. A successful HTTP request does not prove authority, claim support or permission to reproduce content. When browsing is unavailable, sources remain unverified candidates.

## Pilot and boundaries

Pilot domains: Astronomy, Latin, Fitness and Nutrition, Stellaris. Use small catalog/topic/concept proposals to expose multilingual ambiguity, conditional quantities and version/DLC scope. Astronomy later becomes the primary end-to-end demo; the others initially validate extensibility. R3 supplies pending pilot metadata and R2 supplies import/review; no approved source inventory or ready seed is distributed.

Implementation proceeds in bounded slices under: [01-domain-registry.md](../tasks/01-domain-registry.md). Offline fixtures and missing-key tests must work without paid services. Review tools must defend against accidental spreadsheet formula execution, protected-column edits and stale approvals. A local operator is the trust boundary; CSV metadata is not cryptographic identity proof.

The delivery sections below record each slice chronologically; later sections extend earlier boundaries.

## R1 delivered — candidate contracts and storage

The earlier pipeline describes the target system. R1 now implements eight requested contracts, shared Topic/Concept stubs, deterministic identity, normalized SQLite revision/provenance storage, typed relation validation, multi-parent classification cycle checks, scoped alias lookup and idempotent single-candidate writes. SourceCheck observations can be recorded against existing source versions; no check is manufactured or performed automatically. ReviewRecord is a validated contract/reserved ledger only; there is no approval/import interface.

Run `uv run --frozen python -m infinite_engine.catalog` for a disposable offline demo. It prints stable identity, successful replay/history/restart checks and `pending_review`, then removes its temporary database. Run `uv run --frozen pytest tests/catalog -q` for integrity tests. Use `Registry(path)` as a context manager for application storage in an existing user-selected directory; no implicit file/network access is provided by candidate text.

R1 does not implement CSV, batch import, classification-system adapters/mappings, field-level evidence, readiness computation, source discovery or the four-domain pilot. It does not complete M1 or validate any real domain fact. Next bounded step: R2 candidate bundles, human review and atomic approved import, including migrations that preserve R1 history. Broad collection remains gated by pilot acceptance.

## R2 delivered — local review and approved import

R2 implements candidate bundles, per-kind editable CSV packets, dry-run/apply, all four review decisions, exact-revision approval, idempotent receipts and an approved projection. There is no automatic approval: the included demo is synthetic, and only the operator's explicit decision/apply promotes its records.

### Reproducible manual demo

Run from the repository root. Choose a fresh directory name if you have already run this example; export refuses to overwrite an edited packet. `.local/` is ignored by Git.

```sh
mkdir -p .local/registry-demo
uv run --frozen python -m infinite_engine.catalog.review_cli --db .local/registry-demo/registry.sqlite import-bundle tests/fixtures/domain_registry/review-bundle.json
uv run --frozen python -m infinite_engine.catalog.review_cli --db .local/registry-demo/registry.sqlite import-bundle tests/fixtures/domain_registry/review-bundle.json --apply
uv run --frozen python -m infinite_engine.catalog.review_cli --db .local/registry-demo/registry.sqlite export .local/registry-demo/review-1
```

Open `review-1/domain.csv` in a UTF-8 capable editor/spreadsheet. To correct the example, change `proposed.definition` to a JSON string such as `"Revised synthetic example"`, set decision to `revise`, reviewer to your chosen operator name (example: `owner`), and reason to a nonblank explanation. Keep protected fields and the provenance/manifest files unchanged.

```sh
uv run --frozen python -m infinite_engine.catalog.review_cli --db .local/registry-demo/registry.sqlite review .local/registry-demo/review-1 --actor owner
uv run --frozen python -m infinite_engine.catalog.review_cli --db .local/registry-demo/registry.sqlite review .local/registry-demo/review-1 --actor owner --apply
uv run --frozen python -m infinite_engine.catalog.review_cli --db .local/registry-demo/registry.sqlite export .local/registry-demo/review-2
```

In `review-2/domain.csv`, keep proposed fields unchanged, set decision=`approve`, reviewer=`owner`, and a nonblank reason. Then:

```sh
uv run --frozen python -m infinite_engine.catalog.review_cli --db .local/registry-demo/registry.sqlite review .local/registry-demo/review-2 --actor owner
uv run --frozen python -m infinite_engine.catalog.review_cli --db .local/registry-demo/registry.sqlite review .local/registry-demo/review-2 --actor owner --apply
uv run --frozen python -m infinite_engine.catalog.review_cli --db .local/registry-demo/registry.sqlite review .local/registry-demo/review-2 --actor owner --apply
uv run --frozen python -m infinite_engine.catalog.review_cli --db .local/registry-demo/registry.sqlite curated
```

The second apply returns replayed=true; curated returns the approved version 2 with its review record. Version 1 remains available through Registry.get(id, 1). `reject` records rejection without promotion. `defer` leaves the revision unpromoted and eligible for later review. Blank decision/reviewer/reason with unchanged fields leaves a row untouched. Use export's repeatable `--entity ID` option to review a subset; otherwise all latest candidate rows are exported, including previously reviewed ones whose decision cells can remain blank.

### CSV contract and boundaries

- One CSV per entity kind; each field has protected original.* and editable proposed.* columns. Nested labels are JSON cells, not separate sheets in R2. Each exported row must remain present exactly once. UTF-8 BOM and standard CSV quoting support multilingual/multiline values.
- Field values use JSON encoding: strings retain JSON double quotes, lists/objects retain JSON structure, null explicitly clears optional fields, and a blank cell is invalid. Required fields cannot be cleared. Decision/reviewer/reason are plain text. Keep headers/order unchanged.
- Formula-like plain-text cells are prefixed with an apostrophe; an original leading apostrophe is doubled. The importer checks this reversible encoding. Manually entered formula-like reviewer/reason text must use that prefix. Spreadsheet applications can change escaping/formatting on resave: inspect the exported values and run dry-run before applying. No formula is executed by the importer.
- Protected identity/version/hash/original/provenance/manifest changes, missing/duplicate rows, unknown columns and malformed values fail with diagnostics. Parsing errors include CSV filename and line; no partial rows are silently accepted.
- Editing then approving in one row is rejected. Use revise, re-export, then explicitly approve the resulting version. Revisions are current-version checked and never replace previous approved data until approved themselves.
- Batch/packet operations are atomic and replay-safe. Approval checks the full effective curated graph, including already approved versions, not just current drafts.
- Dry-run rolls back domain/review writes. Opening a database can initialize or forward-migrate its schema even for dry-run; use a backup for schema upgrades. Export intentionally records its immutable baseline. A filesystem write failure can leave an incomplete new export directory, but never overwrites an existing one; export again to a fresh directory.
- The operator and registry file owner are trusted. Actor matching records attribution and explicit intent; it is not authentication or a signature. Review files are bound to their source registry. Source authority/licenses, evidence content and seed readiness require separate assessment; R3 adds independently reviewed taxonomy mappings.

## R3 four-domain bootstrap

R3 implements a small candidate-only pilot, not broad collection. It generates 55 candidates: four representative domains plus four context categories, nine sources, four topics, four concepts and typed links/mappings. Astronomy remains the primary future end-to-end demo. Catalog coverage is independent of seed/learning readiness, both false throughout this pilot.

### Classification selection

[UNESCO ISCED](https://www.uis.unesco.org/en/methods-and-tools/isced) classifies education programmes and qualifications. Its documented codes and openly licensed field descriptions make a **selected excerpt** useful for candidate correspondence; its educational boundaries do not define the application's ontology. [OECD's Frascati framework](https://www.oecd.org/en/about/projects/frascati-manual-development.html) was considered as an R&D-oriented alternative. It is not imported or merged in R3; a release/rights adapter would need separate review. These are candidate foundations, not universal learning taxonomies.

The selected ISCED-F source retains its 2013 release/2015 descriptions, publisher, code, original label, path, license locator and PDF anchors. Astronomy is proposed narrower than 0533; Latin acquisition narrower than 0231. Fitness and Nutrition has related mappings to 1014 and 0915, neither an exact coverage claim. The latter field excludes nutrition science to 051, so the mapping rationale explicitly records incomplete fit. Stellaris remains unmapped with a reason. Local domain definitions/parents and all correspondences are AI suggestions independent from the native metadata. Review them separately.

### Reproducible local demo

Run from the repository after `make setup`; use fresh output paths to preserve earlier review edits:

```sh
mkdir -p .local
uv run --frozen python -m infinite_engine.catalog.bootstrap \
  --manifest data/domain_registry/pilot/manifest.json --output .local/r3-bootstrap
uv run --frozen python -m infinite_engine.catalog.review_cli --db .local/r3.sqlite \
  import-bundle .local/r3-bootstrap/candidates.json
uv run --frozen python -m infinite_engine.catalog.review_cli --db .local/r3.sqlite \
  import-bundle .local/r3-bootstrap/candidates.json --apply
uv run --frozen python -m infinite_engine.catalog.review_cli --db .local/r3.sqlite \
  export .local/r3-review
uv run --frozen python -m infinite_engine.catalog.review_cli --db .local/r3.sqlite curated
```

The last command returns `[]`. Inspect `report.json`, then the ten per-kind CSV files including `taxonomy_entry.csv`, `domain_mapping.csv` and `domain_source.csv`. Original suggestions and provenance are protected. Review actions remain blank until a person supplies them. Use the existing R2 review command only after actual manual review; a source or mapping approval certifies a catalog decision, not every underlying claim or reuse permission.

Generate a second bootstrap into a fresh directory: `candidates.json` and `report.json` must be byte-identical for the same manifest and inputs. Re-import the same bundle to replay exact stored revisions. DB timestamps and review-export UUIDs reflect actual operations and are intentionally not deterministic.

Changing inputs requires updating the declared SHA-256 and using a new batch identity; changing existing candidates also requires explicit expected_version values. This adapter targets a fresh pilot store and does not guess how to merge existing curated data. Malformed/missing/checksum-mismatched inputs, duplicate identities, absent references and inconsistent releases fail before publishing output. Original source pages are not bundled or revisited; the hash pins the selected local excerpt, not an archived full remote document.

### Pilot findings and boundaries

| Domain | Exercised now | Extension still required |
|---|---|---|
| Astronomy | Classification mapping, institutional/textbook/academic sources, shared evidence-context concept | Multimodal evidence anchors, dependencies, source-grounded end-to-end learning flow |
| Latin | English/Chinese/Latin labels; distinct concepts can share “Case” without merging IDs | Lexeme/form identities, morphology constraints and context-sensitive disambiguation UI |
| Fitness and Nutrition | Two local parents; partial external mappings; evidence context; official database/API source pointers | Typed quantities, units, sample bases, populations and conditions; no individualized advice |
| Stellaris | Local identity, explicitly absent academic mapping, publisher source, interest bridge to Astronomy | Per-rule patch/platform/DLC applicability and compatibility checks; fiction is not astronomy evidence |

Source authority, accessibility, claim support and reuse are independent. OpenStax yielded no readable body; the attempted Dickinson grammar root failed, so the readable index is recommended instead. These limits remain in candidate rationale/limitations. No SourceCheck records were synthesized. See [the discovery and attribution log](../data/domain_registry/pilot/README.md) for observed URLs and license scope. Broad crawling, complete Domain Seeds, automatic maintenance and specialized knowledge systems remain outside R3.


## Current broad preset construction policy (ADR-010)

Use the [domain-universe-bootstrap task](../tasks/domain-universe-bootstrap.md) for inclusion criteria, foundation/rights comparison, all 15 coverage buckets, normalized artifacts, generation stages and measurable acceptance. Bulk generation is a separate authorized task. Presets are broad established scopes at useful, not uniform, granularity. Do not prebuild global internal Subdomain/Topic/Concept hierarchies or register every game/hobby/chapter as a preset. Category memberships are separate navigation metadata; major semantic edges are sparse and reviewed independently.

Candidates can be stored before human review. Default user-facing preset discovery uses approved revisions; optional pending preview is visibly unverified and opt-in. Rejected/deferred/revised-away candidates stay in audit history, not normal discovery. Metadata approval does not certify knowledge or seed readiness. Private Custom domains and accepted sources do not need administrative approval; [SOURCE_REGISTRY](SOURCE_REGISTRY.md) defines that independent workflow.

The earlier R1–R3 sections are chronological implementation history. The 55-record R3 pilot is preserved, not silently converted into a preset release: its missing origin needs explicit proposals, context parents need category reclassification, and topic/concept stubs belong to internal-structure testing. The new 12-record architecture fixture separates preset/custom and categories without changing R3 IDs, input hashes or original suggestions. Only Astronomy and Latin are preset demos; Fitness and Nutrition and Stellaris are custom demos.

New collections use Domain.origin and creation_method, Category/DomainCategory and the ADR-010 relation taxonomy. Public release validation/packaging must filter preset-only metadata and reviewed dependency closure; generic audit CSV export is not a publication command. Source recommendations remain shared records with scoped rationale. No bulk taxonomy or broad catalog is claimed as delivered.
