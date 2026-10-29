# Codex repository instructions — Infinite Engine

These instructions apply to the entire repository. Read `docs/PROJECT_SPEC.md`, `docs/ARCHITECTURE.md`, `docs/DATA_CONTRACTS.md`, and `PLANS.md` before implementing cross-cutting changes.

## Role and collaboration

- You are an implementation collaborator, **not** the product owner. Respect the documented product decisions; do not silently replace the product with a generic chatbot or Obsidian clone.
- At the start of each implementation task, report: intended scope, files to change, relevant decisions, tests, and any blockers.
- Work on **one milestone or bounded task at a time**. Do not autonomously advance to the next milestone after acceptance criteria are met.
- If key requirements are genuinely ambiguous, state assumptions and log an ADR; prefer the simplest reversible interpretation.
- After each task, report what changed, commands run and their actual results, remaining problems, and a concise manual demo path.
- Never state that tests passed unless you executed them; do not fabricate sources, benchmark scores, LLM outputs or demo data.

## Product invariants

1. Local-first, single-user. No mandatory cloud account or multiplayer service.
2. **Representation != View != Personal Cognition.** Do not collapse into one notes table.
3. **Source material != validated knowledge != LLM explanation != personal opinion.** Keep explicit distinctions.
4. Knowledge graph is typed and queryable. A visually drawn graph of arbitrary backlinks alone is insufficient.
5. Domain tree (classification), concept dependencies (prerequisite/definition), and suggested learning path (pedagogical ordering) are distinct relationships/views.
6. Both **conversation-first** and **structure-first** are first-class. Navigation must preserve context across them.
7. Domain catalogs may be broad, but do not claim unbuilt domains are ready. Domain Seeds are vetted, small and extendable.
8. Ingestion is broad/lightweight; deep structured knowledge is **on-demand and reviewed** before promotion.
9. Knowledge base expansion must not be counted as proof of user mastery.
10. Every retrieval/AI-generated knowledge claim should retain source context or clearly indicate missing support.
11. User notes and personal explanations must never silently overwrite canonical/reference knowledge.
12. Preserve knowledge IDs and migration compatibility. All destructive writes require explicit safeguards.
13. Skill text is instructions, not code-execution permission. Tool access is managed by host-controlled allowlists.
14. Avoid designing addictive engagement loops (forced streaks, frequent nudges). User controls optional feedback.

## Engineering defaults (change only via documented ADR)

- Python 3.11+ backend, FastAPI/Pydantic, SQLite for local state; use repository interfaces for optional graph and vector backends. Neo4j and a local vector store are **candidates**, not compulsory services to start the app.
- React + TypeScript frontend; choose a small, maintainable graph/tree UI. APIs and data contracts are authoritative.
- Modular monolith, not microservices. Keep dependency direction explicit.
- Typed API contracts and a single, tested ID/provenance model. Avoid speculative abstractions.
- Environment/config and credentials kept outside git; `.env.example` may document nonsecret settings.
- Prefer deterministic workflows for parse/validate/write, model calls for semantic proposals; no automatic blind ingestion into validated graph.
- Keep interfaces for LLM, graph storage and vector search replaceable. Tests must work offline using fakes.

## Code and tests

- Prefer clear small modules, type hints, docstrings for nonobvious knowledge rules, and no needlessly broad catch blocks.
- Backend: pytest; frontend: automated checks with the selected toolchain. Add unit tests for contracts, view projections, permissions and update safety; add integration tests for the full knowledge loop.
- Use small controlled fixtures, never copyrighted books copied into git or undisclosed health data.
- Cite sources with local document IDs + stable anchors (page/section/quote offsets) in structured metadata; UI must allow source inspection.
- Include test cases for missing evidence, invalid relations, circular prerequisite edges, duplicate aliases, version mismatch, absent API key, offline mode, and partial parsing failures.
- Any change to data shapes requires migration + tests + updated `docs/DATA_CONTRACTS.md`.
- Update docs and `PLANS.md` status with observed outcomes only; do not mark unimplemented features complete.

## Hard prohibitions

- No arbitrary third-party Skill script execution; no unrestricted filesystem/network tools via prompt instruction.
- No autonomous web crawling, cloud provisioning, payments, account connections, git push or deployment without explicit authorization.
- No fabricated expert-ready knowledge base, psychological diagnosis, expert-percentage scoring or claim that graph coverage equals personal mastery.
- No unsourced medical/fitness individualized advice; Demo C is about evidence and conditional knowledge representation.
- No non-permissioned publication/copying of textbooks, images, game guide content or third-party data.
- Do not rewrite large parts of the repository to solve local bugs unless requested.

## Required end-of-task response

- Summary of changed paths
- Commands executed with pass/fail/skipped status
- Manual verification instructions
- Known limitations, risks, and next recommended bounded task

## Git, tooling and documentation

- Stable branch: `main`; work on `feature/*`, `fix/*`, `docs/*`. Use small Conventional Commits and a PR. No force-push, history reset or automatic merge. Push only within explicit task authorization.
- Run `make setup`, `make check`; use `make format` for formatting. Python 3.12 with Ruff/mypy/pytest; React/TypeScript with ESLint/tsc/Vitest. Commit lockfiles with dependency changes.
- Update contracts, ADRs, task acceptance and PLANS alongside behavior changes. Detailed setup and manual GitHub settings are in `docs/DEVELOPMENT.md`.
- Keep `.env`, database files, logs and personal records out of Git; use ignored `.local/` for local state. Never put secrets in browser environment variables. Bind development services to loopback.
- Source authority, accessibility, claim support and reuse permission are separate checks. Preserve unknown values and original AI suggestions. Only explicit human approval can promote the exact reviewed revision.
- View customization, personal interpretation, candidate professional revision and verified professional knowledge are distinct. Goals (Explore/Understand/Apply/Advance) and activities are not learning-style categories.
- Done means scoped acceptance met, relevant checks actually run, reproducible manual demo, docs accurate, migrations/provenance safe, risks and skipped checks disclosed. A plausible model answer or an attractive graph is not completion.
