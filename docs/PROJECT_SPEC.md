# Infinite Engine — Product Requirements & Scope

**Status:** design specification, not a statement of implemented functionality.  
**Primary audience:** Codex and the human project owner.  
**Project type:** solo academic course + longer-term personal product.  
**Product promise:** 从零开始，探索无限 — From Zero to Infinite Possibilities.

## 1. Problem and motivation

Existing AI knowledge systems can extract concepts, link Wiki pages, show backlink graphs, and answer questions via LLM. These are useful for retrieval and storage, but they do not automatically deliver a stable domain hierarchy, typed concept dependencies, learning-oriented navigation, reliable source provenance, or recoverable personal understanding. Conversely, an LLM can translate, explain and synthesize on demand; the product **must not** assume that a graph UI is necessary for every question. The challenge is joining immediate conversational knowledge services with enduring, inspectable knowledge structures and personal learning history.

Additional problems: repeated knowledge-base configuration for every new interest; unreliable or context-stripped answers; eager whole-corpus LLM extraction yields unaudited noisy graphs; curiosity and interest vary over months.

**Primary goal:** A local-first generalizable workspace in which users can choose a domain, inspect a vetted Domain Seed, chat with a source-grounded AI mentor or navigate structured views, deepen a local topic as needed, save their own explanations/questions, and return later to recover the knowledge context.

**Not the claim:** The app automatically makes users experts; all fields are fully built; LLM citations prove logical correctness; AI-generated summaries equal user learning.

## 2. Scope tiers

### Course end-to-end target (P0)
- Local personal data store and stable identifiers.
- Ingestion of **at least two modalities: text and images**. Image data must be genuinely processed and attached to knowledge objects with provenance; merely having a PDF image in a folder is insufficient.
- Basic schema + typed, stored/queryable scene knowledge graph.
- Source Registry, stable source anchors and status on extracted claims.
- One vetted Domain Seed with working hierarchy and linked sources.
- Conversation-first grounded Q&A and structure-first domain tree / concept detail / prerequisite navigation.
- RAG retriever + LLM service boundary; usable offline/demo fallback with labeled fixture responses, no pretending a stub is live AI.
- One orchestrating mentor Agent using >=2 meaningful tools (e.g. search source, query graph, save personal explanation).
- One reusable Learning Template, one loaded and invoked local SKILL.md.
- Save/retrieve personal question or explanation; restart/resume context.
- End-to-end feedback loop: propose candidate concept/relation/correction, verify or user-review, persist revision with provenance.
- Tests, demo script, six-stage course evidence.

### Usability extensions (P1)
- Several templates; view switching shortcuts; richer source evidence inspection.
- Controlled local domain-specific extensions for Latin, quantities/conditions, versioned game rules.
- Basic visual knowledge-state indicators; event-derived summaries.
- More developed Skill library and user-editable template configs.

### Long-term (P2)
- Broad prebuilt vetted Domain Seeds, robust continual updates, deep cross-domain semantic links.
- Learning analytics dashboard (multi-domain graph/timeline, weekly recaps), fun optional Observer interpretations and learning personas.
- Optional Perspective Challenge; Cognitive Companion using user-affirmed history.
- Local-model inference and optional multimedia modalities beyond text+image.

**Preserve P1/P2 in architecture where inexpensive; do not implement them without an approved task.**

## 3. User journeys

### J1: First-time domain entry (structure-first)
Choose Astronomy > see seed readiness and source summary > enter domain tree > open concept > see definitions & typed prerequisites > expand nested concept while preserving back navigation > inspect supporting text/image > ask mentor follow-up.

### J2: First-time domain entry (conversation-first)
Ask a question before navigating > Agent retrieves relevant source chunks and graph nodes > grounded answer with anchors > click associated concept to show tree location / prerequisite path > continue conversation with existing context.

### J3: Learning-driven refinement
On a focused concept, choose 'expand knowledge' > propose new typed nodes/relations with evidence anchors > validate + review candidate > accept, reject, or edit > commit as new version > views update while IDs and previous user notes remain stable.

### J4: Recover learning context
After an interrupted period, return to a concept > retrieve previous questions, personal explanation, original evidence, and revision history > optionally ask Agent to summarize what the user previously understood (clearly distinguish historical personal view vs current validated knowledge).

### J5: Skill
Select mathematical expression > invoke local `formula-translator` Skill > explain syntax, symbols, intuition, assumptions, and context; disclose ambiguity > user may store the generated explanation as **AI draft**, not automatically canonical or personal understanding.

## 4. Functional requirements (traceable)

| ID | Requirement | P | Acceptance evidence |
|----|-------------|---|---------------------|
| FR-01 | Catalog and readiness states | 0 | Domain list distinguishes catalog-only from seed-ready |
| FR-02 | Source registration and provenance anchors | 0 | Concept/claim click opens linked source location |
| FR-03 | Text + image ingestion | 0 | Two distinct modalities in persisted dataset |
| FR-04 | Typed graph CRUD and query | 0 | Test queries traverse classified relations |
| FR-05 | Seed-based domain tree projection | 0 | Stable hierarchy with cycle/multi-parent handling |
| FR-06 | Concept details / dependency view | 0 | Prerequisites distinguish classification and generic relatedness |
| FR-07 | Vector/keyword source retrieval | 0 | Grounded answers cite indexed chunks or admit insufficient evidence |
| FR-08 | AI mentor with tool routing | 0 | Logs show calls to at least two tools |
| FR-09 | Conversation ↔ view linking | 0 | User can navigate to concept from chat and back |
| FR-10 | Save/retrieve personal explanations/questions | 0 | Restart persists and recovers content |
| FR-11 | Reviewable incremental knowledge update | 0 | New revision preserves old revision and provenance |
| FR-12 | Learning Template engine | 0 | At least one declarative template runs |
| FR-13 | SKILL.md loader and use | 0 | Formula translator loaded by agent, constrained permissions |
| FR-14 | Four domain schema fixture tests | 1 | Astronomy end-to-end; 3 targeted extensions |
| FR-15 | Observer summary/dashboard | 2 | Event-grounded optional analytics, facts separated from guesses |

## 5. Non-functional requirements

- **Local-first:** local sources, graph, memory and logs. Remote LLM requires explicit configuration and transparent transmission.
- **Source integrity:** source anchors preserved throughout extraction, retrieval, view and final answers.
- **Safety:** separate validated domain knowledge, candidates, AI drafts and personal opinions; no silent cross-promotion.
- **Reliability:** deterministic parse/validation, idempotent ingest, recoverable failures, safe versioned updates.
- **Extensibility:** domain-specific typed properties via extensions, without forking app implementation per domain.
- **Accessibility/UX:** no enormous hairball graph by default; clear labels for relations, progress, review status and ambiguity.
- **Maintainability:** modular monolith, typed contracts, tests, manual demo and documented config.

## 6. Explicit design decisions

1. A domain hierarchy is NOT interchangeable with a concept-dependency DAG or a recommended learning path.
2. A graph backend stores semantic relations; the View Engine projects task-specific representations.
3. Raw sources + source anchors are evidence; a graph is a structured model derived from them.
4. Chat is a full entry point, not a secondary widget; the tree is a full entry point, not mandatory.
5. A domain directory may be broad; only certain Domain Seeds are genuinely ready.
6. Base ingest broad; deeper knowledge modeling progressive, user/topic triggered.
7. External knowledge growth and personal mastery are distinct dimensions.
8. Learning Templates (multi-stage flows), Skills (task instructions), and Tools (privileged capabilities) remain separate.
9. Observer Agent should include optional entertaining analyses derived from objective data, not present inferred personality traits as clinical facts.
10. Gamification is light, voluntary, outcome-oriented. No forced daily streaks.

## 7. Course six-stage alignment

1. User problem & needs: explicitly document problem and scenario.
2. Acquisition & coding: two modalities, cleanup, structured extraction.
3. Organization & storage: typed domain knowledge graph + database.
4. LLM augmentation: LLM Wiki/RAG/GraphRAG; implement RAG plus optional graph retrieval.
5. Agent application: actual tool-using Mentor Agent, optional reusable Skill.
6. Feedback/update: correction or new item triggers versioned knowledge and system changes.

## 8. Primary research / evaluation questions

- Does the learning-oriented view improve prerequisite discovery and domain navigation vs raw backlink graph or chat-only baseline?
- What are audit cost, noise, dedupe rate and latency tradeoffs of eager batch extraction vs progressive extraction?
- Can structured personal memory reduce work to recover earlier concepts/explanations?
- Does graph-assisted retrieval improve answers with dependencies vs source-only RAG? Baseline fairness and test fixtures required.

Report results only after running a defined test. Distinguish user-perceived learning from proven educational outcomes.

## 9. Out of scope for first end-to-end demo

- Training/fine-tuning LLMs; a fully autonomous universal expert system; production social graph; online marketplace; open arbitrary script plugins; unsupervised graph rewriting; complete four-domain datasets; guaranteed automatic logical proof; expert skill scores.

## 10. Current foundation and long-term co-construction

M0 implements only process health, local configuration and an unavailable-feature UI shell with engineering checks. There is no registry importer, persisted graph, retrieval or model integration yet. The course requirements and P1/P2 vision above remain intact.

The long-term Domain Intelligence Registry is a source-grounded, multilingual data asset distinct from Source Registry, vetted Domain Seeds and on-demand Extended Knowledge. Broad coverage is compatible with few ready seeds. Discovery and AI proposals require provenance and human review before curated import; see [DOMAIN_REGISTRY.md](DOMAIN_REGISTRY.md).

Human–AI co-construction distinguishes saved view customization, personal interpretation, candidate professional revision and verified professional knowledge. Users retain active reasoning and can inspect, revise and extend proposals; no silent promotion is permitted. Learning motivation, goals and activities are separate dimensions described in [LEARNING_ENGINE.md](LEARNING_ENGINE.md). Long-term insights and cognitive companionship remain optional, event-grounded and non-diagnostic.
