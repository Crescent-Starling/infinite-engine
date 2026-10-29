# Track A — Broad Preset Domain data asset

Status: executable construction specification; **bulk generation is not authorized or performed by the architecture task**. Prerequisites: ADR-010, explicit batch authorization, artifact-specific reuse checks and a versioned classification selection manifest. Existing R2 import/review and R3 pinned-input patterns are reusable; a broad release adapter/validator is a follow-up deliverable.

## Scope and inclusion

Produce broad knowledge scopes, concise definitions, multilingual labels where supported, browsing memberships, sparse meaningful domain relations and provenance. No full subdomain/topic/concept hierarchies, seed payloads, learning paths or user records.

Include a scope when it has sustained disciplinary or established knowledge-area identity, a definable boundary, independent orientation value and identifiable reference communities/resources. Require a reviewer-visible inclusion rationale. Academic granularity need not be uniform. A field can overlap another and belong to several categories. Relations alone do not create new domains.

Borderline examples (decisions to record, not imported data): Artificial Intelligence and Statistics warrant standalone candidates even with strong parent/neighbor relationships. Machine Learning may be a preset candidate with a scope justification or a custom scope; never block custom creation. Latin is an explicitly retained preset demo. Black Hole Physics usually starts as an internal topic or custom scope unless later inclusion is justified. Birdwatching, Fitness and Nutrition, specific games/research questions and course chapters are not automatically global presets. Stellaris is a custom lifecycle demo. Treat fitness/nutrition academic foundations separately from the user's combined practical scope.

## Classification foundation assessment

Read-only official sources inspected on 2026-10-29. This is planning evidence, not SourceCheck approval or bulk-import permission.

| Foundation | Proposed use | Limitations and import gate |
|---|---|---|
| [OECD FORD / Frascati 2015](https://www.oecd.org/en/publications/frascati-manual-2015_9789264239012-en.html) | Primary coverage cross-check for research fields; Table 2.2 identifies broad and second-level classifications | R&D statistics, not every learnable scope. [Current terms](https://www.oecd.org/en/about/terms-conditions.html) distinguish pre/post July 2024 content and translation conditions; the 2015 PDF has its own copyright notice. Pin exact artifact, scope of reuse and adaptation/translation requirements before import; do not label the 2015 work CC BY 4.0 by default. |
| [UNESCO ISCED-F](https://www.uis.unesco.org/en/methods-and-tools/isced) | Educational-field coverage and alternative mappings | Programmes/qualifications are not the local ontology. The [R3 attributed excerpt](../data/domain_registry/pilot/README.md) records CC BY-SA 3.0 IGO for the inspected 2015 descriptions. Broader adapters must preserve that attribution and terms rather than inherit a generic repository license. |
| [Library of Congress Classification](https://www.loc.gov/aba/cataloging/classification/) | Coverage audit for humanities, arts and interdisciplinary shelving boundaries | [Schedules are downloadable](https://www.loc.gov/aba/publications/FreeLCC/freelcc.html); availability is not a blanket reuse grant. Check the selected edition/artifact and [rights information](https://www.loc.gov/legal/) before copying schedules. Not a learner curriculum or universal hierarchy. |
| [Wikidata licensing](https://www.wikidata.org/wiki/Wikidata:Licensing) | Optional multilingual aliases and candidate entity alignment | Structured data are CC0; other page text has different terms. Record exact Q/P IDs, revision/dump and retrieval provenance only when actually observed. Community alignment is neither authority certification nor permission to copy linked works. No guessed IDs. |

Do not merge all classifications. Choose a primary candidate source per run, retain parallel external mappings, and resolve local inclusion separately. Unlicensed/unclear bulk material may be referenced for research but must not enter a distributed snapshot. No FORD/LCC/Wikidata bulk data is included in this task.

## Coverage matrix for the first authorized broad release

These are navigation buckets and example scopes to investigate, not validated domain records or ontological parent claims. The first broad release should assess at least three candidate scopes per bucket; accepted omissions need explicit reasons rather than filler entries.

| Bucket | Example scopes for investigation |
|---|---|
| Formal sciences | Mathematics, Statistics, Logic |
| Natural sciences | Physics, Astronomy, Chemistry, Earth sciences |
| Life/environment | Biology, Ecology, Environmental science |
| Computing/technology | Computer Science, Artificial Intelligence, Information science |
| Engineering | Civil, Mechanical, Electrical, Chemical engineering |
| Medicine/health sciences | Medicine, Public health, Nursing, Nutrition science |
| Social/behavioral sciences | Sociology, Psychology, Anthropology |
| Economics/business/management | Economics, Business, Management, Accounting |
| Humanities | History, Philosophy, Archaeology, Religious studies |
| Languages/linguistics | Linguistics, Latin, Language acquisition, Translation studies |
| Arts/design | Visual arts, Music, Performing arts, Design |
| Law/public policy | Law, Public policy, Political science |
| Education/learning sciences | Education, Learning sciences, Educational assessment |
| Agriculture/food sciences | Agriculture, Food science, Forestry, Veterinary science |
| Other established fields | Library studies, Communication studies, Geography; justify cross-memberships |

No arbitrary target node count proves completeness. Report assessed/included/deferred/excluded counts per bucket, coverage gaps, ambiguous scopes and cross-bucket memberships. Expand only after reviewing the first bounded batch and coverage report.

## Reproducible construction procedure

1. **Freeze inputs:** assign release/batch identity and immutable keys. Manifest includes adapter/schema versions, taxonomy publisher/release, actual retrieval time when observed, source locator, artifact hash, license/permission evidence, attribution obligations and allowed operations. Unknown facts remain null with a reason. Raw copyrighted material is not committed by default.
2. **Extract candidate scopes:** deterministic adapters select native codes/labels/paths without renaming identities. Retain exact source revision and stable section/code anchors. Save all inclusion/exclusion decisions; external records and local Domain records have separate IDs.
3. **Normalize:** use the shared UUIDv5 namespace and explicit immutable keys. Trim/case-normalize only search keys, not identity keys. Preserve source spellings and leading-zero codes. Check unique slugs and ID collisions. Never silently merge homonyms or translations.
4. **Align languages:** retain original-language labels; add English/Chinese only when sourced or explicitly marked AI translation. Aliases have language and role. Missing translation is a review flag, not a made-up label. Wikidata alignments are optional, independently reviewable mappings.
5. **Propose metadata:** save model/provider/version (when actually known), prompt template version, input hashes and original generated output. Generate concise definition, boundary/exclusion notes, category memberships, inclusion rationale and a small number of justified relations. No fabricated confidence scores. Missing support and uncertain granularity are explicit flags.
6. **Recommend sources:** save shared Source records and DomainSource rationale, intended use, authority scope, limitations and unknowns. Do not demand a fixed number of sources for every domain; report zero-source gaps. Do not perform crawling, downloads or source checks as hidden generation side effects.
7. **Validate:** parse complete batch before writing; check schema, origin=preset for release entries, label consistency, slug/identity uniqueness, category and relation endpoints, symmetry, cycles, source identities, provenance, taxonomy pins and unsupported verification claims. Reject internal Topic/Concept/DomainSeed payloads from broad preset releases. Reserved legacy predicates require an explicit review/migration disposition.
8. **Store candidates:** import atomically with existing dry-run/apply conventions. No human review is required merely to store candidates. Idempotent batch receipts preserve originals; conflicting content under one batch ID fails.
9. **Review:** export original/proposed CSV fields plus immutable provenance. Review domain, category, membership, relation, mapping and source recommendation separately. Approve/reject/defer/revise exact revisions; edits require revise then later approval. Use the personal collection path, not this approval process, for private source use.
10. **Publish artifact:** export only approved dependency-closed preset metadata and its exact review ledger/manifest into a separate curated release. Candidate preview remains explicitly labeled and is never packaged as verified. Curated release export is a follow-up implementation, not provided by R3 bootstrap. Remote publication requires authorization.
11. **Maintain:** new input versions create new proposals/batch IDs with expected versions. Never overwrite approved defaults or erase rejected suggestions. Report diff, changed mappings, attribution effects and stale source checks. Readiness remains independent.

## Storage and import/export conventions

Retain existing `data/domain_registry/pilot/` unchanged as a historical pilot. The next task should add `data/domain_registry/releases/<release>/` with `manifest.json`, `categories.json`, `domains.json`, `domain_relations.json`, `sources.json`, `domain_sources.json`, `domain_categories.json`, `taxonomy.json` and a coverage report. These are normalized reviewable inputs, compiled into the existing CandidateBundle format; do not introduce a competing spreadsheet identity authority.

Future approved exports need a separate curated manifest plus exact entity versions and review records. Keep actual SQLite databases, review CSV working copies, private inputs and downloaded originals under ignored `.local/`. Domain Seeds belong to a separate versioned artifact with reviewed content; do not create empty seed directories that imply readiness. Test fixtures stay under `tests/fixtures/domain_registry/`.

Existing commands: `review_cli import-bundle` (dry run then --apply), `export`, `review` (--actor; dry run then --apply), `curated`. R3 `bootstrap` replays its specific pinned pilot inputs; it is not the new broad-release adapter. New adapter/coverage/export commands must be implemented and documented in the authorized follow-up before claiming they exist.

## Measurable acceptance and tests

- All 15 coverage buckets assessed; at least three proposed scopes per bucket or an explicit reviewed gap. No requirement to approve weak/filler candidates.
- 100% included candidates have stable keys, nonempty definitions/scope notes, explicit preset origin/creation method, at least one preferred language label, category membership, inclusion rationale and evidence or a support gap. Report missing zh/en and AI translations separately.
- Zero invalid IDs/references, duplicate identities/slugs/current edges, self-edges or classification cycles. Every external mapping pins the exact release/entry; every recommendation explains scope and limitations.
- Zero internal topic/concept/seed payloads in the global preset release; zero automatic approvals, invented source checks, assumed licenses or learning-readiness claims.
- Identical frozen inputs generate byte-identical bundles/reports offline; repeat imports leave versions unchanged; malformed/partial input rolls back; changed batches require a new identity and compatible expected versions.
- Exercise all four review actions, original-vs-revised preservation, dependency-closed promotion, mixed pending/approved default selection and migration compatibility. Curated exports contain approved exact revisions only.
- Required negative fixtures: missing origin/definitions, invalid category, unknown provenance, mixed-language duplicate aliases, invalid predicates, same resource identity, unknown license marked confirmed, personal acceptance confused with review, unsupported native mapping.
- Deliver coverage/gap report, source/rights manifest, reproducible CLI commands and actual test evidence. This task specifies these gates; it does not claim broad coverage exists.

Risks: taxonomy fit, edition/translation rights, review burden, scope drift and false multilingual equivalence. Out of scope: autonomous crawling, complete seeds, live learning services, editor UI, global entity resolution and multi-user accounts.
