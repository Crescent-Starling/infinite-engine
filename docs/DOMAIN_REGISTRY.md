# Domain Intelligence Registry — R1 storage and R2 review implemented

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
- The operator and registry file owner are trusted. Actor matching records attribution and explicit intent; it is not authentication or a signature. Review files are bound to their source registry. Source authority/licenses, evidence content, taxonomy mappings and seed readiness still need separate work.
