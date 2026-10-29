# Development

## Prerequisites and setup

Use Python 3.12, Node 24, npm, uv and Make. `.python-version` and `.node-version` record the tested runtime lines. Python 3.9 supplied by macOS is insufficient. Dependencies are pinned in `uv.lock` and `frontend/package-lock.json`; initial installation needs package-registry access, while tests make no external service calls.

```sh
make setup
make check
```

`make setup` runs `uv sync --frozen` and `npm --prefix frontend ci`. Use uv 0.11.7 as in CI. Optional: copy `.env.example` to `.env` and edit local paths. No key is required. Configuration validates IE_DATA_DIR and IE_LOG_LEVEL; no data directory is created until future persistence work needs it. IE_LOG_LEVEL is reserved configuration, not a logging implementation; configure uvicorn logging via its CLI.

In two terminals:

```sh
make backend
make frontend
```

Open http://127.0.0.1:5173. The four navigation buttons switch unavailable sections. `curl http://127.0.0.1:8000/api/health` returns `{"status":"ok","service":"infinite-engine"}`. OpenAPI is at http://127.0.0.1:8000/docs. The Vite development server proxies `/api` to the backend; the shell currently makes no API calls. No chat, seed, graph, source upload or persistence is implemented.

`make format` applies Python/frontend formatting; `make check` verifies formatting, Ruff, mypy, pytest, local Markdown links, Prettier, ESLint, TypeScript, Vitest and production compilation. CI executes these same targets. `npm --prefix frontend run preview` serves built static files only; a future deployment must explicitly configure API routing.

## Workflow and dependency changes

Use main as stable integration; branch feature/*, fix/* or docs/*. Keep commits reviewable using Conventional Commits. Inspect the working tree before edits. Never reset published history, force-push or merge automatically. Every PR includes motivation, affected modules, migration impact, actual tests, risks and UI screenshots/manual demo. Update specs, ADRs and milestone evidence in the same change. Do not treat a foundation task as permission to implement the next milestone.

Use `uv add` / `uv add --dev` and `npm --prefix frontend install --save-exact` to change dependencies intentionally. Commit both manifests and locks; rerun `make setup` and `make check`. Do not upgrade unrelated packages opportunistically. Graph visualization candidate: React Flow (`@xyflow/react`); evaluate accessibility, multi-parent projections and license at M4 before installation. No graph library is needed for this shell.

## Security, privacy and future providers

Bind local services to 127.0.0.1; this unauthenticated development shell is not an internet deployment. Store private files/learning history under ignored `.local/`, credentials in ignored `.env` or process environment. VITE_* values are public and cannot hold secrets. Do not commit personal records, generated logs, source books or database files. Remote LLM access will be explicit/configurable, with provider-specific secrets kept server-side, transparent transmission and offline fakes. No generated script or Skill text grants filesystem/network permissions.

Future persistence uses SQLite and explicit forward migrations with backups, version checks and rollback tests; database/retrieval adapters sit behind typed module boundaries. Current health checks only process liveness, not database/AI readiness.

## Troubleshooting

- Python 3.9 or missing uv: install uv and Python 3.12 using your approved package manager, then rerun setup. Do not modify system Python.
- Network/proxy restrictions: installation needs PyPI and npm registry access. Report the failing host/error; tests do not require API credentials.
- Occupied ports: pass a different uvicorn `--port` and adjust Vite proxy together, or stop your own existing process. Vite may choose the next available UI port; use its printed URL.
- Invalid IE_LOG_LEVEL: choose DEBUG, INFO, WARNING or ERROR. Do not log secrets to diagnose config.
- Missing module/dependency: run setup from repository root; do not bypass lockfiles.
- CI fails while local checks pass: compare runtime versions, clean locked installs, case-sensitive paths and committed files.

## Manual GitHub settings (not automated)

After the initial branches exist, set main as default. Add a ruleset requiring PRs, the `foundation` CI check, resolved conversations and suitable review approval; disable force pushes/deletion and require review for workflow changes. Enable secret scanning/push protection and dependency alerts where available. Review Actions permissions (workflow requests contents: read), repository visibility, licensing and merge policy. These settings are not claimed to be enabled by adding a workflow file.
