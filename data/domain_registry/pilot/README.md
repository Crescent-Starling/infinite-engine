# Four-domain candidate pilot

These saved AI suggestions are **pending human review**. They contain catalog metadata, not validated knowledge or ready Domain Seeds. No automated reviewer decisions or SourceCheck observations are included.

- `manifest.json` pins the adapter, input SHA-256 hashes, four pilot identities, unmapped rationale and extension gaps.
- `suggestions.json` retains the original AI suggestions, source recommendation reasons and limitations. Unknown publication dates, licenses and versions stay null/absent.
- `taxonomy.json` retains four selected native codes, labels, code paths and section locators, plus separately identified AI mapping suggestions. It is not a full taxonomy copy.

The 55 resulting candidates comprise 8 domains (4 pilots plus 4 local context categories), 9 sources (8 recommended resources plus the taxonomy), 4 topics, 4 concept stubs, 5 domain relations, 4 topic memberships, 5 concept memberships, 8 source recommendations, 4 taxonomy entries and 4 mappings.

Regenerate and export editable CSVs using the [R3 demo](../../../docs/DOMAIN_REGISTRY.md#r3-four-domain-bootstrap). Do not edit a generated bundle while retaining its batch ID. For a changed collection, assign a new batch ID; updates to existing entity keys must supply the expected stored revision. Bootstrap v1 is a fresh-store pilot adapter, not an automatic maintenance merger.

## Attribution and reuse

Selected classification metadata: UNESCO Institute for Statistics (2015), ISCED-F 2013 detailed descriptions, DOI [10.15220/978-92-9189-179-5-en](https://doi.org/10.15220/978-92-9189-179-5-en). The publication's PDF page 2 states [CC BY-SA 3.0 IGO](https://creativecommons.org/licenses/by-sa/3.0/igo/). The native code/label/path excerpt in `taxonomy.json` retains that attribution and license. Selection, serialization and local mapping suggestions are project changes; UNESCO has not endorsed them. No full descriptions, textbook chapters, images or game guides are distributed.

USDA's API guide states a CC0 license for FoodData Central **data**. This does not license every linked page, image or other recommended source. Other unknown licenses remain unknown. Source recommendations are pointers for review, not permission to ingest third-party works.

## Bounded source discovery — 2026-10-29

Read-only browser discovery inspected the URLs below. This is an attributed research note, not a persisted SourceCheck or human source approval. No publication day or historical retrieval timestamp is inferred from search-engine metadata. The bootstrap never revisits these URLs.

| Source | Observed locator | Observation and review limit |
|---|---|---|
| UNESCO UIS | [Official classification PDF](https://www.uis.unesco.org/sites/default/files/medias/fichiers/2025/04/international-standard-classification-of-education-fields-of-education-and-training-2013-detailed-field-descriptions-2015-en.pdf) | Read native codes and field boundaries; license on PDF page 2. Printed page numbers differ: anchors use one-based PDF pages. |
| NASA | [Universe](https://science.nasa.gov/universe/) | Readable institutional astronomy portal; individual claims/media rights not assessed. |
| IAU | [Organization homepage](https://www.iau.org/) | Readable professional organization page; linked resources need separate assessment. |
| OpenStax | [Astronomy 2e](https://openstax.org/details/books/astronomy-2e) | Title returned, body unavailable to browser extraction. Text and license remain unverified. |
| Dickinson | [Reference works index](https://dcc.dickinson.edu/home-page-ref-works) | Readable grammar/vocabulary index. Attempted grammar root returned 404; not retained as recommended URL. |
| WHO | [Physical activity](https://www.who.int/health-topics/physical-activity) | Readable public-health portal; no exercise prescription or clinical claim extracted. |
| USDA | [FoodData Central](https://fdc.nal.usda.gov/) | Readable composition database overview; no food records acquired. |
| USDA | [API guide](https://fdc.nal.usda.gov/api-guide/) | Readable official API instructions and data licensing statement; no API call/key needed for this pilot. |
| Paradox | [Stellaris overview](https://www.paradoxinteractive.com/games/stellaris/about) | Readable publisher product page; not sufficient evidence for versioned mechanics. |

ADS homepage/API help returned a JavaScript verification challenge and were not included. These access limitations must not be turned into successful verification records.
