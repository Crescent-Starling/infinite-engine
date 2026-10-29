# Domain coverage and demo strategy

## Domain Catalog

The preset catalog covers broad established knowledge areas through independent browsing categories. It is not a universal hierarchy of every hobby, game, chapter or concept. Astronomy and Latin are preset demo scopes; Fitness and Nutrition and Stellaris are custom demo scopes. All four share one Domain/Knowledge Space/source infrastructure.

Catalog presence, recommended sources, source checks, seed readiness and learning readiness are independent. Selecting a Domain can create an empty primary Knowledge Space; no seed is required. Internal Subdomains/Topics/Concepts appear from a compatible approved seed or progressive exploration, not from bulk global catalog construction. See [DOMAIN_ARCHITECTURE](DOMAIN_ARCHITECTURE.md).

## Demo A — Astronomy (Preset; primary end-to-end target)

**Purpose:** hierarchical structure, conceptual dependencies, source-grounded text/image RAG, and personal learning history.

**Target journey:** select Astronomy preset → initialize primary Knowledge Space → load approved seed when available → tree → stellar evolution concept → typed prerequisite → original source with image → grounded chat → personal explanation → reviewed local knowledge expansion → future retrieval.

**Source candidates:** public materials from NASA, IAU, OpenStax or other suitably licensed authoritative materials. Sources and usage licenses must be checked *before ingest*; no dataset is supplied by this pack.

**Expected verification:** 1 end-to-end script, typed relations and stable IDs, text and image source anchors, review/feedback update.

## Demo B — Latin (Preset; language extension target)

Objects: `Lexeme`, `WordForm`, `MorphologicalFeature`, `GrammarRule`, `ExampleSentence` as domain extension candidates.

Test a grammar rule linked to example and word forms; do not treat every inflection as generic concept. Licensing of dictionary/corpus data must be checked.

## Demo C — Fitness & Nutrition (Custom; condition and quantity target)

Objects: `Quantity`, `Unit`, `Condition`, `Measurement`, `GuidelineClaim` as extension candidates. The same number without units, population context or assumptions should be invalid or ambiguous. Avoid individualized medical advice; use general, source-backed educational facts.

## Demo D — Stellaris (Custom; primary lifecycle target)

Target lifecycle: manual custom creation (also offline) → optional explicit metadata/source discovery → edit proposals and related-domain suggestions → enter space → add personal/discovered sources → initialize an optional knowledge tree → customize personal structure → retain patch/platform/DLC applicability through updates. No mandatory global Stellaris preset. These are future application acceptance steps.

Objects: `GameMechanic`, `GameVersion`, `RuleChange`, `AppliesToVersion`. Knowledge may differ by patch/DLC/game mode; never flatten conflicting revisions into one timeless statement. Official game documentation and terms must be checked.

## Test grid

| Test | Astronomy | Latin | Fitness/nutrition | Stellaris |
|---|---|---|---|---|
| hierarchy/dependencies | full | light | light | light |
| text+image provenance | full | optional | optional | optional |
| domain extension | basic | morphology | quantities & conditions | versions |
| RAG+agent workflow | full | smoke | smoke | smoke |
| feedback/version | full | schema test | qualifiers | primary extension test |

**Readiness condition:** a demo is only marked ready if its seed or fixture exists, is licensed appropriately, and has passing verifications.

## Available foundation demo (M0 only)

Run `make setup`, `make backend` and `make frontend` from the root (servers in separate terminals). Open http://127.0.0.1:5173; switch Chat, Knowledge, Sources and My Learning. Each must explicitly say not implemented. Fetch http://127.0.0.1:8000/api/health for process liveness. This is not Demo A–D completion and supplies no domain seed or knowledge data. Registry curation now has library/CLI support; actual source verification and full demo loops remain separate; see [DOMAIN_REGISTRY.md](DOMAIN_REGISTRY.md).

## Registry R1 offline demo

`uv run --frozen python -m infinite_engine.catalog` creates a temporary synthetic catalog candidate, replays it without duplication, edits it as version 2, reopens storage and checks version 1 is preserved. Expected outputs include replay_idempotent/history_preserved/restart_persisted=true, latest_version=2, status=pending_review, curated_data_created=false. This is a storage demonstration, not any of the four domain pilots or vetted seeds.

## Registry R2 synthetic review demo

Follow [the Registry manual demo](DOMAIN_REGISTRY.md#reproducible-manual-demo): import the synthetic review-bundle fixture, export CSV, revise a field, dry-run/apply, re-export, approve, replay and inspect curated version 2. No external facts, sources or seeds are supplied. The four domain demos remain planned.

## R3 registry pilot available

The [offline bootstrap demo](DOMAIN_REGISTRY.md#r3-four-domain-bootstrap) now generates four-domain pending metadata and editable review CSVs. It includes multi-parent classification, shared concept membership, label ambiguity, partial taxonomy mappings, an explicit unmapped game domain, and six resource categories across the pilot. All 55 records remain candidates; source checks and curated records are empty before owner action.

This is a registry inspection demo, not any full Demo A–D learning loop. Astronomy still requires multimodal/dependency contracts; Latin needs morphology; health knowledge needs units and applicability; Stellaris rules need patch/platform/DLC scope. Automated probes reject those unsupported fields rather than pretend the specialized systems exist. See the [candidate data](../data/domain_registry/pilot/README.md) for attribution and observed access limits.


## ADR-010 minimal architecture fixture

`tests/fixtures/domain_registry/domain-architecture.json` is a 12-record synthetic fixture: two presets, two customs, two browsing categories, two memberships, one contextual edge, one shared bibliographic source and two recommendations. No internal knowledge hierarchy, real reference, approved data or ready seed is supplied. It is separate from the preserved R3 source-discovery pilot.

Run `uv run --frozen python scripts/registry/demo_domain_architecture.py` for a disposable local demonstration. It imports the fixture, shows explicit candidate preview, creates the same kind of primary space for all four domains, permits a same-name custom scope, accepts an unreviewed source in a preset space and stores a personal override. It prints that curated records/source checks remain zero; the temporary database is removed afterward. The API/UI and optional web discovery are not implemented.

User-editing acceptance belongs to M4/M8: add/hide/reorganize personal structure without deleting canonical knowledge, retain stable IDs, save personal explanations separately, propose professional corrections and review exact revisions. No deliberate AI errors. Full demo readiness requires these implemented behaviors and actual seed/evidence checks, not merely this fixture passing.
