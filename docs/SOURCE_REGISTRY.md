# Shared Source Registry and personal source autonomy

One stable Source identity can serve multiple domains and Knowledge Spaces. Preset/custom origin does not create two source systems. Exact fields and storage are in [DATA_CONTRACTS](DATA_CONTRACTS.md).

## Independent records and states

| Record | Purpose | Does not imply |
|---|---|---|
| Source + immutable revision | Resource description, locator and known metadata | Resource was read, licensed, authoritative or true |
| DomainSource | Candidate recommendation, intended use, authority scope and limitations | User accepted it or every claim is supported |
| KnowledgeSpaceSource | Accepted/removed collection choice, exact source revision and note | Metadata approval, accessibility or claim verification |
| SourceCheck | Dated access, authority or licensing observation with method and evidence | Permanent validity or all claims verified |
| ReviewRecord | Explicit decision about exact catalog metadata | Source content certified or personal use authorized |
| Claim + Evidence (planned) | Proposition with applicability and supporting/counter evidence | Every claim in its source verified |

System recommendation, AI discovery and user addition describe origin, not trust. Unknown date/license/authority/access remains null or not checked; approval cannot fill it. Latest checked time is derived per check kind and exact source revision, not one verified flag. Publisher update dates differ from local revision timestamps. Bibliography-only resources need no invented URL.

## User-controlled collections

Users can add URLs, local document metadata, books, papers, documentation or other resources to preset- or custom-based spaces. No administrator or academic-authority label is required. Adding metadata does not execute a URL, open a path, download content or bypass licensing/file-access controls. Acquisition is a separate explicit operation.

The minimal implementation stores a pending Source through the registry, then LocalDomains.choose_source appends the user's accepted/removed choice. Replaying a choice adds no duplicate event; removal preserves source history and other spaces. It never creates ReviewRecord, SourceCheck, Claim or curated entries. Private collections/overrides are excluded from preset bundle/CSV export, which traverses registry entities only. Actual private source metadata belongs in ignored local stores, never committed fixtures.

Source IDs use explicit immutable keys. An optional resource_identity (for example a deliberately chosen DOI/ISBN edition key) prevents duplicate current source records with that exact identity. Missing identities stay unknown. URL/title matches can support future local suggestions but never silently merge editions, translations, copies or revisions. This task implements explicit-identity validation, not DOI normalization, scraping or global resolution.

## Provenance and scope

Title/creator, type, language, publication/update date, version, coverage, access conditions, bibliography and license remain inspectable. discovery_method records system_recommendation/ai_discovery/user_added. Candidate provenance retains author/generator, input hash and anchors or a support gap. DomainSource carries recommendation-specific intended_use, authority_scope and limitations. Optional intended_learning_level is a recommendation qualifier; unknown stays null, never inferred from prestige.

Personal acceptance suffices for local use. System recommendation promotion still follows catalog review and dependency closure. Authenticity, context-specific authority, reuse permission and claim support are independent assessments. Fiction/game material can be useful in its scope without academic authority; it must not become evidence for real-world science.

## Maintenance and acceptance

Metadata changes append Source revisions. Collection choices remain pinned until explicitly updated. Scheduled checks, file hashing, provider identity adapters and acquisition/retrieval are not implemented. Future tests must simulate absent files, unavailable networks, conflicting editions and stale checks without real API keys. Current tests cover unknown licenses, malformed URLs, explicit identity duplicates, unreviewed acceptance in preset/custom spaces, independent check/review ledgers and restart persistence.

## Source Discovery Skill specification

[Source Discovery](../skills/source-discovery/SKILL.md) defines bounded, profile-aware candidate discovery for both origins. Its [exchange contract](../skills/source-discovery/references/contracts.md) has five reviewable outputs, independent evidence-bearing check dimensions and an offline search-plan path. `catalog.discovery` validates transport records and request-bound references without network access, database writes or approval. User acceptance and acquisition remain explicit later operations. No provider, Skill loader, review UI or automatic handoff is implemented.

## Discovery interchange extension

[Source discovery and acquisition architecture](SOURCE_DISCOVERY.md) now supplies Provider/Resource/Document/Anchor contracts, offline research manifests, Source Profiles and proposed acquisition plans. Source continues to represent the stable logical resource; a SourceResource sidecar enriches its exact revision without replacing existing IDs or checks/reviews. Acquisition executors and scheduled checks remain unimplemented. SourceReview is a constrained view of the existing metadata review ledger, not professional claim certification.

## Planned acquisition boundary

[Multimodal acquisition](MULTIMODAL_ACQUISITION.md) extends this registry with a typed
VideoSource projection over the existing Source identity and pinned revisions. Video URLs,
creator references and playlists can remain metadata-only. Source registration, user
collection acceptance, metadata approval and access/license observations grant no media
acquisition or processing permission. Host-issued operation grants and receipts are separate
from SourceCheck and ReviewRecord; a license field is neither a grant nor claim verification.

Creator subscriptions default to bounded manual metadata synchronization, with all media
processing disabled. Discovered items are not acquired artifacts, analyzed transcripts or
verified knowledge. The [proposed contracts](DATA_CONTRACTS.md) retain unknown metadata,
original media/subtitles, transcript revisions and temporal evidence. These are Phase 1
designs only; current library capabilities and database version 5 are unchanged.
