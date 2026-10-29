# M0 — Repository foundation

## Goal
Create an executable, maintainable shell **without** fake advanced AI behavior.

## In scope
- `backend/`: Python FastAPI minimal app with `/api/health`, config loader and deterministic offline test.
- `frontend/`: React + TypeScript minimal UI with basic navigation placeholders for Chat, Knowledge, Sources, My Learning (label not yet implemented).
- `tests/` and frontend checks, minimal CI-compatible local commands.
- Local configuration example (`.env.example` with no secrets), `.gitignore`, start instructions.
- Documentation/update decision log capturing framework/toolchain exact choices.

## Out of scope
Actual KG, embeddings, external LLM calls, domain seeds, remote sources, users/accounts, graph viz, Observer or Skills execution.

## Acceptance
1. Fresh checkout dependency installation documented.
2. Backend and frontend start locally; UI shows unavailable modules as not yet implemented (no misleading claims).
3. `/api/health` returns deterministic JSON and has an automated test.
4. No hard-coded key, endpoint credentials or invented research data.
5. Codex reports exact commands run and outcomes, and stops.

## Implementation instruction
Plan affected files first, then implement. Keep module names consistent with `docs/ARCHITECTURE.md`. Do not build M1+ in this task.
