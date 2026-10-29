# Validation and course acceptance

## Course six-stage evidence checklist

- [ ] Stage 1: user problem, needs, target context, constraints and value proposition documented.
- [ ] Stage 2: **two genuinely distinct modalities** ingested; evidence of text + image processing, cleaning, coding and provenance.
- [ ] Stage 3: typed domain knowledge graph; database storage and actual graph query with screenshot/log.
- [ ] Stage 4: LLM grounded with RAG or GraphRAG; source location can be inspected; negative evidence test.
- [ ] Stage 5: agent with substantive callable tool actions (not only a chat prompt); Skill demo if implemented.
- [ ] Stage 6: user correction/new material updates persisted knowledge and a subsequent query reflects the revision.

## Baselines and metrics (define dataset before reporting)

| Research question | Baseline | Proposed system | Measures |
|---|---|---|---|
| Learning-oriented structure | raw Wiki/backlink graph; chat-only | typed tree/dependency + linked chat | task success, prerequisite localization, steps/time, perceived workload |
| Extraction strategy | eager bulk extraction | seed + on-demand refinement | verified precision, duplicate rate, review time, token/latency cost |
| Knowledge-enhanced answering | source-only RAG | source RAG + typed relation query | correctness, citation fidelity, dependency completeness |
| Knowledge recoverability | source retrieval without history | source + personal history | correct recall of previously saved statements, steps/time |

## Fairness and rigor

- Same licensed source corpus across baselines; comparable retrieval/model settings where possible.
- Use prewritten questions and explicit correct answers/required source anchors. Document where human judgment is used.
- Compare human time and model runtime separately. Do not infer long-term mastery gains from short task studies.
- Record failures and limitations: conflicting sources, outdated versions, relation cycles, OCR/figure parsing failures, ambiguous terms.
- Distinguish source provenance from support of a claim; source authenticity does not prove inference validity.

## M0 observed verification — 2026-10-29

Environment: macOS arm64, Python 3.12.13, Node 24.15.0, npm 11.12.1, uv 0.11.7.

| Check | Actual result |
|---|---|
| `make setup` (uv frozen sync + npm ci) | Passed; npm clean install from lockfile, 0 reported npm vulnerabilities |
| `make check` | Passed after clean setup; rerun after interruption also passed |
| Ruff format/check, mypy | Passed; 5 Python source files type checked |
| pytest | 2 passed: health/no storage/API boundaries and environment config validation |
| Prettier, ESLint, tsc | Passed |
| Vitest | 1 passed: four navigation sections remain explicitly unavailable |
| Vite production build | Passed |
| `python scripts/check_docs.py` via uv | 18 documents checked, 0 errors |
| `git diff --check` | Passed |
| Ignore probes | `.env`, `.env.production`, `.local/private.json`, SQLite/log files, node_modules and virtualenv ignored |
| Real HTTP health | Passed on temporary port 18000; response exactly matches documented JSON; test server stopped |
| Browser smoke | UI loaded at 5173; Chat → Knowledge changed heading/selection and retained unavailable status; layout inspected |

Initial Ruff import ordering failure was corrected. Initial Starlette test-client deprecation was resolved by using its supported httpx2 dependency. ESLint 9's install-time unsupported-version warning was resolved by installing ESLint 10. Initial socket binding was sandbox-blocked; permitted loopback startup then revealed occupied port 8000, so HTTP verification used 18000 without stopping unrelated processes. A post-interruption curl failed because the temporary server had stopped; a fresh server verified successfully.

No domain dataset, license, source-verification, migration, AI or course benchmark tests are claimed. Those features do not exist yet. GitHub Actions is configured to run the same setup/check targets on Ubuntu; hosted outcome must be checked on the PR, separately from these macOS results. Branch protections and other manual GitHub settings remain unconfigured by this task.

## Registry R1 observed verification — 2026-10-29

- `uv run --frozen pytest tests/catalog -q`: 17 passed. Covered deterministic IDs, multilingual labels, append-only revisions, replay, stale writers, typed/missing references, duplicate memberships/aliases, multi-parent DAG/cycles, cross-domain cycles, evidence version retention, source-check observations, invalid contracts, rollback injection, migrations and offline/no-key storage.
- `make check`: passed with 19 backend tests total, 1 frontend test, Ruff, mypy (11 source files), Prettier, ESLint, TypeScript, 18-document link check and Vite build.
- `uv run --frozen python -m infinite_engine.catalog`: passed; replay/history/restart true, latest version 2, pending_review, no curated data.
- Wheel build initially failed to resolve build dependencies because sandbox DNS could not reach PyPI. `uv build --offline --wheel --out-dir /tmp/infinite-engine-registry-dist` succeeded using cached build dependencies. Verified the SQL migration is packaged and ran the same offline demo from the extracted wheel successfully.
- Initial formatting/type-check issues were corrected before the passing full check. No new dependency was required.
- No source discovery, external URL/license verification, CSV parsing, review promotion or pilot dataset was performed. These are R2/R3 tests and deliverables, not skipped claims of R1 functionality. Local tests are synthetic and do not prove any domain knowledge.

## Registry R2 observed verification — 2026-10-29

- `make check`: passed; 50 backend tests total (17 R1, 31 R2, 2 health), 1 frontend test, all format/lint/type checks, 18-document link check and Vite build.
- R2 checks cover approve/reject/revise/defer, edit-then-approve rejection, actor matching, DB-bound original/hash/version/provenance protection, missing/duplicate/malformed rows, blank/null/multilingual/multiline handling and formula escaping.
- Transaction checks cover dry-run rollback, injected mid-promotion failure, revised-version rollback, stale exports, terminal decisions, unchanged previous curated revisions, bundle forward references and conflicting/repeated batch IDs.
- Approval checks cover exact source-version dependency closure and a cycle that exists only in the mixed curated graph, despite a valid latest-candidate graph.
- A real CLI subprocess round-trip imports the synthetic fixture, exports and revises CSV, dry-runs/applies, re-exports/approves, repeats the import and reads approved version 2. All data and reviewer identities in this test are explicitly synthetic.
- Forward-migration test opens a v1-shaped database, verifies original revision preservation, and reopens with both migration checksums. 001_registry.sql is unchanged.
- Offline wheel build passed; both SQL migrations are included, and the original offline demo initializes the v2 database successfully from the extracted wheel.
- Initial line-length/type-check issues were corrected. No dependencies added. No real data approved, external sources checked or R3 work performed. Hosted CI status is reported separately after branch publication.

## R3 observed verification — 2026-10-29

- `UV_CACHE_DIR=/tmp/infinite-engine-uv-cache make setup`: passed (`uv sync --frozen`, frontend `npm ci`); dependency manifests/locks unchanged.
- `UV_CACHE_DIR=/tmp/infinite-engine-uv-cache make check`: passed after R3 changes: Ruff format/lint, strict mypy (18 files), **71 backend tests** (21 new bootstrap/pilot tests), document references (18 documents, zero errors), frontend format/ESLint/tsc, **1 Vitest test**, Vite production build.
- Tests cover byte-identical offline/no-key generation, invalid checksums/truncated/missing/escaping inputs without output, duplicate IDs/native codes, missing mapping targets and inconsistent releases, explicit unmapped coverage, source category coverage, shared membership/multi-parent organization, homonymous concepts, unsupported extension-field rejection, pinned-revision approval closure, native identity preservation and unambiguous tuple-key encoding, migration from R2, and actual bootstrap CLI execution. Existing R1/R2 regression suites pass.
- Manual local run generated 55 candidates and ten editable CSVs, with blank decisions and no curated entries. Bootstrap into two fresh directories produced identical candidate/report bytes (`cmp` passed); re-import returned identical revision JSON. The local pilot database and review files are ignored under `.local/`. Preliminary generated artifacts were preserved separately under `.local/r3-preview/` while final identity encoding was finalized.
- `uv build --offline --wheel` passed; wheel inspection confirmed bootstrap and migrations 001/002/003 are packaged. `git diff --check` passed. No migration 001/002 edits, frontend behavior changes, source checks, human approvals, seed readiness or network model calls were introduced.

Limits: source discovery was bounded read-only inspection; some pages were incomplete/inaccessible, and recommendations remain candidates. Checksums pin local saved metadata, not full archived remote documents or authenticated publisher signatures. Specialized morphology, quantitative health applicability, multimodal evidence and version-scoped game rules remain unsupported. No spreadsheet desktop application round-trip or real owner approval was performed. R4 final acceptance and broad collection are not part of this execution; no R3 remote CI run is claimed.

## Domain architecture revision observed verification — 2026-10-29

Inspected AGENTS, README, PROJECT_SPEC, ARCHITECTURE, DATA_CONTRACTS, DEMOS and PLANS; existing DOMAIN_REGISTRY/ADRs/tasks, catalog contracts/storage/review/bootstrap, migrations 001–003, fixtures/tests, setup manifests/scripts and CI. The worktree contained the previous uncommitted R3 implementation; it was preserved on feature/domain-architecture-revision. No published history or unrelated application modules were rewritten.

Identified and corrected: missing preset/custom origin; category_ids previously conflated with semantic DomainRelation; R3 context categories modeled as Domain parents; four demo scopes not distinguished by management; implicit seed-first entry; source types/approval conventions insufficient for private collections; obsolete documentation claiming no importer. No multi-user resolution subsystem existed, and none was added. Historical R3 records remain unchanged and explicitly unclassified rather than becoming presets automatically.

Executed results:

- `UV_CACHE_DIR=/tmp/infinite-engine-uv-cache make setup`: passed; locked Python dependencies and npm install; no dependency changes.
- `UV_CACHE_DIR=/tmp/infinite-engine-uv-cache make check`: passed; Ruff format/lint, mypy (21 files), **86 backend tests** including **15 new architecture tests**, 22 documentation files with zero broken local references, frontend formatting/ESLint/tsc, **1 Vitest test**, Vite production build.
- `uv run --frozen python scripts/registry/demo_domain_architecture.py`: passed; 12 fixture records, four shared primary spaces, overlapping custom creation true, preset unchanged true, zero curated records/checks and seed_ready=false. All content is synthetic; no network calls or human approval.
- Forward migration tested from schema 3, preserving old snapshot/hash, approved history and legacy directed edge rows; append-only triggers remain active. A manual read-only backup of the existing R3 v3 database also upgraded successfully: all 55 snapshot/hash pairs and relations unchanged, original CSV packet dry-run readable, original batch replay idempotent, and generated bundle bytes unchanged. The original .local/r3.sqlite was left at v3.
- `uv build --offline --wheel`: passed. Wheel includes spaces/bootstrap modules and migrations 001–004. `git diff --check`: passed. Tracked-file checks found no .env/private-key/database files; .local database and review packets are ignored.

Tests cover shared preset/custom infrastructure, multilingual same-name custom creation, unique slug allocation, no-seed operation, preset default/candidate separation, unreviewed personal source acceptance, immutable curated defaults under personal overrides, independent source checks and review, source identity duplicates, malformed URLs, unknown licensing, category endpoint validation, relation direction/symmetry/cycles/self-edges, origin immutability, exact preset-reference types, old CSV compatibility and explicit null clearing of added fields. Custom local updates remain usable without repeat registry approval.

Not executed/implemented: API/UI lifecycle or editor tests, live AI discovery, seed loading, source acquisition/claim verification, bulk FORD/LCC/Wikidata import, broad coverage generation or curated release packaging. Their acceptance tests/dependencies are specified in the two new tasks. No new remote CI run, push, merge or source-verification result is claimed.

## Source discovery/acquisition architecture — 2026-10-29

Observed on the shared working tree (including pre-existing/concurrent Domain/discovery specification changes):

- PASS final `make setup`: frozen Python sync, locked frontend install (233 packages, npm reported zero vulnerabilities).
- PASS `make format`: Python/frontend formatting; subsequent format checks passed.
- PASS final `make check`: Ruff format/lint, mypy (31 source files), pytest (124 passed, including 21 new source architecture tests), documentation links (29 documents, zero errors), frontend Prettier/ESLint/TypeScript, Vitest (1 passed), production build.
- PASS `.venv/bin/python scripts/demo_sources.py`: four mock Domain manifests imported/replayed, proposed plans validated; restart retained 12 artifact revisions; no downloads.
- PASS `.venv/bin/python -m infinite_engine.sources schemas/sources --schemas`: generated four schemas; tests compare schema output and validate all examples with JSON Schema and runtime contracts.
- PASS `.venv/bin/python /Users/crescent/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/source-discovery`: skill format valid. This verifies structure, not actual agent execution.
- PASS `git diff --check` and a final documentation link check.

Earlier attempts: default-sandbox setup failed accessing the uv cache; approved setup succeeded. Initial full checks found three stale migration-version assertions and one skill wording assertion; updated for migration 005 and explicit human choices. A subsequent check passed all backend tests but found the frontend prettier executable missing during concurrent workspace work; locked setup restored dependencies and the final complete check passed.

No network source search, content acquisition, real parser/adapter, API/UI source integration, complete RAG or professional claim verification was tested or implemented. Tests use synthetic sources and supplied metadata only, with no API key. Existing suites retain real legacy snapshot/review compatibility checks; new source tests cover additive migration, atomic rollback, replay/restart, revision/hash/reference errors, eight native locator cases, unknown rights, malformed YAML and partial-result contracts. Full M1/M2 acceptance remains pending.
