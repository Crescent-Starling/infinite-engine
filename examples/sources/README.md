# Synthetic source interchange examples

All four folders contain deliberately **mock** metadata, not researched or authoritative sources. The reserved example.invalid URLs must not be fetched. No content was acquired; no licenses, authority checks, professional reviews or factual claims are asserted. These are not the initial curated source catalog.

Astronomy and Latin use preset fixture Domains; Fitness & Nutrition and Stellaris use custom fixture Domains. All use the same contracts and import path. Their profile criteria and recommendation limitations demonstrate scientific, edition/language, health applicability and fictional game/version boundaries. Real research can replace metadata in new attributed revisions or separate identities without changing application code.

`domains.json` is a separate synthetic Domain bootstrap, not part of source_candidates.json. Run `uv run --frozen python scripts/demo_sources.py` from the repository root to import domains and sources into a disposable local database, validate proposed plans, replay imports and reopen the database. No API key or network is required. See [architecture and profile specification](../../docs/SOURCE_DISCOVERY.md) for real-store import and schema regeneration.
