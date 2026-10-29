# Infinite Engine — executable milestones

**Rule:** One milestone at a time. Do not mark done without passing observed tests, a reproducible manual demo, and updated docs. M0 has a local executable foundation; acceptance evidence is recorded below. Later application milestones remain planned; the Domain architecture foundation and independent data construction specification are recorded below.

| ID | Milestone | Exit gate | Status |
|---|---|---|---|
| M0 | Repository foundation | bootable minimal backend/frontend + offline tests + consistent configs | implemented; local checks passed |
| DA | Broad preset data asset | all coverage buckets assessed; provenance/review/release gates | specified; bulk build not started |
| DL | Domain discovery and local spaces | preset/custom lifecycle and user-controlled sources | library foundation implemented; API/UI planned |
| M1 | Core data schema, sources & IDs | stable CRUD, source anchors, status and migrations tested | planned |
| M2 | Text+image ingest, candidate extraction | one of each persisted, idempotent parse, evidence preserved | planned |
| M3 | Typed KG and Domain Seed | astronomy fixture, typed graph queries and validation | planned |
| M4 | View Engine + frontend | tree + concept dependency + evidence view, navigation works | planned |
| M5 | Source-grounded RAG and dialogue | chat returns linked concept IDs and verifiable anchors | planned |
| M6 | Mentor Agent + Skills + learning template | two real tools; local SKILL.md; configurable template | planned |
| M7 | Personal cognition & recoverability | history survives restart and supports resume | planned |
| M8 | Feedback/knowledge revision | candidate review, provenance + history, view refresh | planned |
| M9 | 3 heterogenous domain fixtures | Latin, nutrition, Stellaris extension tests | planned |
| M10 | Evaluations, polish and course demo | repeatable six-stage demo + benchmark baselines + report evidence | planned |

### Dependency constraints

M0 → shared Domain/source foundation → M1 → M2/M3 → M4/M5 → M6/M7/M8 → M9/M10. DA data work and DL application work can proceed independently after the shared foundation; neither broad catalog completion nor seeds gate DL manual creation. Frontend may scaffold earlier but should not invent data models. M9 fixture design may inform the earliest Schema, but avoid prematurely building four full databases.

### Suggested per-milestone workflow

1. Read spec and relevant contracts; inspect existing code.
2. Write task-scoped implementation plan with affected modules, cases and verification commands.
3. Implement smallest vertical slice; prefer tests of invariants before broad UI polish.
4. Run tests; fix failures; check manual acceptance route.
5. Update architecture decision record, build log and milestone state from evidence.
6. Stop and ask for next task/owner acceptance; no unauthorized external actions.

### Project-wide definition of done

- The feature meets specified acceptance tests; no claims unsupported by observed tests.
- Data can persist across restart; error cases are handled and surfaced.
- Sources and knowledge status are not lost in transforms.
- Tests documented and reproducible without personal secrets.
- README and relevant specs remain accurate.

See `tasks/00-repository-foundation.md` for first bounded task.

## Track details and review gates

Each entry below is a bounded milestone: implement only the currently authorized scope. Existing M IDs remain stable. DR is the additional registry track; LT is the learning-template/growth track. None implies expertise or full domain readiness.

### M0 — Repository foundation

- Objective/scope/deliverables: Local health/config and honest UI shell; locks, scripts, CI and governance docs.
- Dependencies: None.
- Acceptance: make setup/check and local health/UI demo.
- Required tests: Backend liveness/config; UI entry-point honesty; lint/type/build/docs.
- Known risks: Toolchain/network access; hosted CI differs from local.
- Out of scope: All knowledge features.

### M1 — Knowledge data contracts

- Objective/scope/deliverables: Stable IDs, evidence, review/version model, SQLite repositories and migrations.
- Dependencies: M0.
- Acceptance: Safe versioned CRUD and anchored provenance survive restart.
- Required tests: IDs, malformed contracts, missing evidence, FK, migration/rollback, version mismatch.
- Known risks: Identity and migration compatibility.
- Out of scope: Ingestion and AI generation.

### DR — Domain Registry and human review

Status: R1 candidate storage and R2 local review/import implemented; verification recorded in VALIDATION. R3 four-domain candidate pilot and offline bootstrap implemented; owner data review and R4 final acceptance remain pending. Shared ID/source/provenance prerequisites are included in R1; full M1 remains planned.

- Objective/scope/deliverables: Normalized registry; candidate manifests, source rationale, CSV reviews/import; four-domain pilot.
- Dependencies: M0; M1 shared IDs/provenance.
- Acceptance: Candidates may be imported idempotently before review; only approved exact revisions promoted; taxonomy mappings retained.
- Required tests: Duplicate aliases, multi-parent/cycles, review actions, rollback, offline/no key.
- Known risks: Licensing, uncertain authority, review workload.
- Out of scope: Broad crawling and complete knowledge bases.

### M2 — Knowledge acquisition and multimodal encoding

- Objective/scope/deliverables: Text and image parsing, anchors, candidate extraction.
- Dependencies: M1.
- Acceptance: Both modalities genuinely processed and persisted with provenance.
- Required tests: Idempotence, partial parsing, missing evidence, image anchors.
- Known risks: OCR errors and content rights.
- Out of scope: Unreviewed canonical ingestion.

### M3 — Typed knowledge storage and Astronomy seed

- Objective/scope/deliverables: Typed graph queries and a small vetted Astronomy seed.
- Dependencies: M1; M2 evidence; a reviewed Astronomy preset record, not completion of the broad DA catalog.
- Acceptance: Queryable relationships and seed evidence recoverable across restart.
- Required tests: Invalid endpoints, circular prerequisites, multi-parent projection input.
- Known risks: False source support and seed overclaiming.
- Out of scope: Full multi-domain databases.

### M4 — Knowledge View Engine

- Objective/scope/deliverables: Tree/DAG/evidence/local views with shared context and graph-library evaluation.
- Dependencies: M3.
- Acceptance: Conversation/structure navigation preserve IDs and source inspection; personal layout/learning-structure edits never mutate curated defaults.
- Required tests: Cycle/multi-parent projection, back navigation, keyboard access; add/hide/reparent/restore personal nodes, canonical isolation and revision-safe overlays.
- Known risks: Hairball UI and duplicated objects.
- Out of scope: Learning analytics.

### M5 — Source-grounded RAG

- Objective/scope/deliverables: Retrieval interface, baseline keyword search, optional provider adapter.
- Dependencies: M2/M3.
- Acceptance: Anchored answers or explicit insufficient evidence.
- Required tests: Citation fidelity, no key/offline, network failure, retrieval baseline.
- Known risks: Unsupported synthesis and latency.
- Out of scope: Autonomous agent workflows.

### M6 — AI tutor and Skills

- Objective/scope/deliverables: Mentor uses two meaningful allowlisted tools; one safe Skill/template.
- Dependencies: M5; M4 context.
- Acceptance: Observable tool calls and source-grounded responses.
- Required tests: Permissions, malformed calls, hostile Skill text, fake provider fixtures.
- Known risks: Tool privilege escalation.
- Out of scope: Arbitrary scripts and marketplace.

### M7 — Personal Cognition and recoverability

- Objective/scope/deliverables: Personal questions/definitions/events and resume services.
- Dependencies: M1; M4/M5 contexts.
- Acceptance: User records survive restart without canonical overwrite.
- Required tests: History/context recovery, privacy and isolation.
- Known risks: Confusing personal interpretation with truth.
- Out of scope: Psychological inference.

### M8 — Progressive refinement and revision

- Objective/scope/deliverables: Propose, review, correct and version knowledge; refresh views.
- Dependencies: M3/M5; DR review conventions.
- Acceptance: Accepted change affects later query while prior evidence/history remain.
- Required tests: Reject/revise/defer, stale writes, evidence preservation, rollback.
- Known risks: Review fatigue and semantic conflict.
- Out of scope: Blind AI graph mutation.

### LT — Learning templates and growth visualization

- Objective/scope/deliverables: Optional declarative activities and event-grounded history views.
- Dependencies: M6/M7; M8 for co-construction.
- Acceptance: Goals/activities remain separate; users can skip and customize.
- Required tests: Template validation, view-only edits, personal/canonical isolation.
- Known risks: Misleading mastery indicators.
- Out of scope: Expert scores and addictive nudges.

### M9 — Cross-domain extensibility

- Objective/scope/deliverables: Latin morphology, fitness/nutrition conditions/units, Stellaris version fixtures.
- Dependencies: M3/M8; DR pilot.
- Acceptance: Latin preset plus fitness/nutrition and Stellaris custom fixtures demonstrate domain-specific constraints through shared infrastructure. Stellaris manual lifecycle starts earlier in DL; versioned rules stay here.
- Required tests: Language aliases, units/population, patch/DLC applicability.
- Known risks: Licensing and unsafe health interpretation.
- Out of scope: Three complete knowledge bases.

### M10 — Evaluation and course demo

- Objective/scope/deliverables: Astronomy end-to-end course demo and fair baseline report.
- Dependencies: M2–M9; LT only for optional growth evaluation.
- Acceptance: Six-stage evidence and reproducible measured results.
- Required tests: Full loop, offline/failure paths, source and benchmark audit.
- Known risks: Unsupported learning claims and unfair baselines.
- Out of scope: Unmeasured expertise claims.

## M0 evidence

Local `make setup` and `make check` passed on 2026-10-29; 2 backend tests, 1 frontend test, type/lint/format/build and documentation checks passed. Real HTTP health and browser navigation were verified; see docs/VALIDATION.md. GitHub rulesets and hosted CI are separate from local acceptance. Next recommended task: M1 via tasks/02-knowledge-foundation.md, followed by DR's approved schema/review slice. No Registry schema decision is automatically approved by this foundation task.


## ADR-010 parallel workstreams

### DA / Track A — Preset Domain data asset

- Objective/scope: broad established fields, concise scopes, categories, sparse typed relationships, shared source recommendations and provenance; no global detailed knowledge hierarchies.
- Deliverables: foundation/rights manifests, frozen candidate inputs, broad adapter/validator, coverage/gap reports, CSV review and approved release packaging. The [construction task](tasks/domain-universe-bootstrap.md) specifies all 15 coverage buckets, inclusion/borderline rules and measurable gates.
- Dependencies: shared schema/IDs/review from R1–R3/ADR-010; explicit authorization per collection batch. No dependency on UI, RAG, seeds or all of M1.
- Acceptance: three assessed scopes per bucket or justified gaps; complete provenance/support-gap metadata; no invalid references, auto-approvals or seed claims; deterministic offline replay and dependency-closed approved export.
- Tests: schema/category/relation/rights metadata validation, multilingual duplicates, preserved native mapping, malformed input rollback, review history and idempotence.
- Risks: source license/translation conditions, granularity drift, multilingual alignment and review workload.
- Out of scope: hundreds of domains in this architecture task, full topic/concept content, autonomous crawling and learning services.
- Status: plan and minimal contracts/fixture implemented; broad generation and curated release exporter not implemented.

### DL / Track B — Domain discovery, Custom creation and personal spaces

- Objective/scope: preset selection, local duplicate suggestions, unrestricted custom scopes, one primary space, personal sources and overrides, followed by optional discovery/seed integration.
- Deliverables: library foundation now; typed API and minimal UI next, per [custom-domain-lifecycle](tasks/custom-domain-lifecycle.md).
- Dependencies: shared Domain/Source contracts and local SQLite; no broad release, network, account or ready seed requirement.
- Acceptance: same downstream services for all four demos, no duplicate-name creation block, source acceptance without admin approval, explicit candidate preview and no curated mutation from private edits.
- Tests: offline/manual creation, multilingual search, preset/custom space identity, unreviewed source choice, restart, overrides, unknown license/check separation; API/UI tests added when those surfaces exist.
- Risks: private file access, existing-draft reconciliation and later overlay conflicts.
- Out of scope now: full custom UI, automatic web discovery, internal tree editor, RAG/Agents or multi-space/multi-user features.
- Status: minimal library and migration foundation implemented; full lifecycle application remains planned.

Recommended next bounded task: DA first small classification/coverage batch and release-validator implementation, or DL local search/create API/UI. Select one explicitly; neither automatically advances from this architecture task. R4's old review gate remains applicable to the historical R3 pilot and does not imply the new broad asset has been accepted.

### Source Discovery — bounded Skill and transport foundation

- Scope: repository-local instruction artifact, general/four-domain profiles, request/result contracts and offline validation. Does not complete M6 or implement a search provider.
- Deliverables: `skills/source-discovery/`, `catalog/discovery.py`, `tests/catalog/test_discovery.py`; Source Registry and data-contract documentation.
- Acceptance: preset/custom use the same exchange, offline plan is valid, recommendations have rationale/provenance, unknown checks stay unknown, source checks bind exact payloads, scope/identity/version errors are rejected.
- Next bounded task: implement an explicitly invoked provider adapter with mocked network failures and evidence capture; validate the result before presenting it. No acquisition or approval side effects.
- Observed validation (2026-10-29): setup passed; 17 focused tests, scoped Ruff/mypy, Skill format validation and 25-document link check passed. Full backend run: 100 passed, 3 failed because concurrent migration 005 changed version expectations in existing tests. `make check` stopped on formatting in concurrently added `sources/` files. Those files were not changed by this slice; integration with that work remains outstanding.

## SD — Source discovery and acquisition architecture

Bounded slice: offline Source candidate/association import; Provider/Resource/Document/Anchor contracts, migration 005, configurable Source Profile/acquisition plan schemas, Source Discovery Skill specification, adapter interfaces and four synthetic examples. Implementation and next task are documented in [source-discovery-acquisition](tasks/source-discovery-acquisition.md). Full M1/M2 remain planned: actual acquisition/parsing, source inspection UI, extraction and claim verification are not complete. No autonomous source research, bulk crawling or RAG is included. Validation evidence is recorded in docs/VALIDATION.md after running checks.

## MA — Multimodal knowledge acquisition extension

Phase 1 architecture and data contracts are specified in
[MULTIMODAL_ACQUISITION](docs/MULTIMODAL_ACQUISITION.md) and the
[six-phase task](tasks/multimodal-acquisition.md). ADR-012 preserves Source identity,
separates discovery/acquisition/processing/review, and defines subtitle-first processing,
temporal evidence, host permissions and metadata-only subscriptions. This is documentation
only: adapters, parsing, ASR, temporal retrieval, KG integration, platform connectors and
synchronization are not implemented. Database version 5 and existing runtime contracts
remain unchanged.

Phases 2–6 are planned and require separate bounded tasks. M2 text/image and M1/M3/M5/M8
acceptance remain in force; video does not replace them. Phase 1 verification outcomes are
recorded in the linked task. Recommended next task within MA: Phase 2 local video/subtitle
ingestion and its migration/security tests; do not advance automatically.

SD observed validation: final make setup/check passed on 2026-10-29 (124 backend tests including 21 source architecture tests; 1 frontend test; lint/type/docs/build passed). Four-domain disposable import/replay/restart and Skill format checks passed. This bounded metadata architecture slice is implemented; next recommendation is the separately scoped local text/Markdown acquisition adapter, with host file policy and real citation round trips.
