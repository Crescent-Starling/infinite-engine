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
