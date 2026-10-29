# Domain coverage and demo strategy

## Domain Catalog

Broad categories: math/formal sciences; physics/astronomy/earth; chemistry/materials; life/ecology/environment; computing/AI; engineering; social science; business/management; humanities/philosophy; languages; arts; health/life knowledge; nature observation; games/interactive systems; software/tools; practical skills.

A domain may be `catalogued`, `sources_available`, `seed_ready`, `learning_ready` as independently reported capabilities. Do not represent a whole catalog as production knowledge bases. Multiple topic parents and cross-domain concept references are allowed.

## Demo A — Astronomy (complete end-to-end)

**Purpose:** hierarchical structure, conceptual dependencies, source-grounded text/image RAG, and personal learning history.

**Target journey:** choose astronomy → tree → stellar evolution concept → typed prerequisite → original source with image → grounded chat → personal explanation → reviewed local knowledge expansion → future retrieval.

**Source candidates:** public materials from NASA, IAU, OpenStax or other suitably licensed authoritative materials. Sources and usage licenses must be checked *before ingest*; no dataset is supplied by this pack.

**Expected verification:** 1 end-to-end script, typed relations and stable IDs, text and image source anchors, review/feedback update.

## Demo B — Latin (schema extension fixture)

Objects: `Lexeme`, `WordForm`, `MorphologicalFeature`, `GrammarRule`, `ExampleSentence` as domain extension candidates.

Test a grammar rule linked to example and word forms; do not treat every inflection as generic concept. Licensing of dictionary/corpus data must be checked.

## Demo C — Fitness & nutrition (condition + quantitative fixture)

Objects: `Quantity`, `Unit`, `Condition`, `Measurement`, `GuidelineClaim` as extension candidates. The same number without units, population context or assumptions should be invalid or ambiguous. Avoid individualized medical advice; use general, source-backed educational facts.

## Demo D — Stellaris (versioned rule fixture)

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

Run `make setup`, `make backend` and `make frontend` from the root (servers in separate terminals). Open http://127.0.0.1:5173; switch Chat, Knowledge, Sources and My Learning. Each must explicitly say not implemented. Fetch http://127.0.0.1:8000/api/health for process liveness. This is not Demo A–D completion and supplies no domain seed or knowledge data. Registry curation and source verification remain planned; see [DOMAIN_REGISTRY.md](DOMAIN_REGISTRY.md).

## Registry R1 offline demo

`uv run --frozen python -m infinite_engine.catalog` creates a temporary synthetic catalog candidate, replays it without duplication, edits it as version 2, reopens storage and checks version 1 is preserved. Expected outputs include replay_idempotent/history_preserved/restart_persisted=true, latest_version=2, status=pending_review, curated_data_created=false. This is a storage demonstration, not any of the four domain pilots or vetted seeds.
