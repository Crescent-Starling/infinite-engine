# Track B — Local Domain discovery and Custom lifecycle

Status: domain/space/source-choice library foundation exists after ADR-010. UI, API lifecycle, optional AI discovery and seed loading remain planned. Dependencies: M0, shared Domain/Source IDs and review contracts; broad preset dataset completion is **not** a prerequisite.

## Next bounded slice

Expose local domain search, manual custom creation and primary-space entry through typed API/UI. Use LocalDomains as the foundation, with explicit request validation and visible metadata/review state. Keep provider discovery and tree generation out of that first slice. Reuse exact IDs; do not implement a second custom-domain schema.

Manual flow: type name → view preset/custom multilingual suggestions → select existing or create new despite a match → supply/edit definition and scope → create custom metadata → enter empty persistent primary space → add URL/local/bibliographic Source metadata → accept/remove from personal collection. Duplicate names do not block; generated unique slugs are visible to callers. Selecting a preset does not forbid user sources or personal overrides.

Follow-up discovery flow: explicit user action → configured search provider or offline fallback → saved AI proposals with observed URLs/evidence or support gaps → user edits/accepts metadata → persist original and revision → optional relation suggestions → initialize from approved compatible seed or empty space. No seed, web, API key or academic authority gate for manual use.

Stellaris is the primary Custom lifecycle demo; Fitness and Nutrition validates a combined practical scope. Astronomy and Latin select presets. All four use the same space and source services; they are never hard-coded into separate workflows.

## Deliverables and acceptance

- Typed endpoints and minimal screens for local search/create/select, one primary space, source collection and basic overrides; endpoints do not yet exist.
- Offline custom creation and restart recovery; candidate preset selection requires explicit opt-in and a pending label. Normal preset selection retains approved defaults while newer drafts exist.
- Sources can be added to preset spaces without catalog approval. User acceptance never creates a source check or validates a claim. Show unknown licensing/access clearly without blocking metadata entry.
- Local duplicate suggestions are advisory; identical names can have distinct IDs and unique slugs. No automatic merging or cross-user calls.
- Empty spaces are useful containers; no fabricated tree, conversation, seed or mastery indicator. Readiness display remains conservative.
- Personal title/scope overrides affect only the space presentation. Later layout/learning-structure edits must not mutate curated defaults.

## Required automated tests

Current library tests cover shared preset/custom space creation, no-seed operation, local multilingual duplicate suggestions, manual creation without web, unreviewed source acceptance, independent check/review ledgers, overrides and restart persistence. The API/UI task must add request/response validation, keyboard/manual flow, visible uncertainty, local input rejection, API failure and stale update handling. Use fakes; no paid credentials.

Later editor acceptance: add/hide/reparent personal nodes, restore hidden nodes, retain canonical IDs, save personal explanation separately, propose professional correction, reject it without altering reviewed knowledge, approve exact reviewed revision with history. Validate hierarchy cycles and source inspection. Do not deliberately inject errors into generated trees.

Later domain-specific fixtures: Latin lexemes/morphology/examples; health quantities/units/population/conditions; Stellaris patch/platform/DLC rules and updates; Astronomy multimodal seed/dependency/RAG/history. These are planned tests, not implemented capabilities.

Risks/open decisions: request authorization for local file access, private file storage/retention, seed compatibility, hierarchy overlays and concurrent pending edits. Out of scope for the next slice: full knowledge editor, RAG/Agents, live search/model providers, advanced multiple spaces, accounts or global identity resolution.
