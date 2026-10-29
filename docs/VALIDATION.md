# Validation and course acceptance

## Course six-stage evidence checklist

- [ ] Stage 1: user problem, needs, target context, constraints and value proposition documented.
- [ ] Stage 2: **two genuinely distinct modalities** ingested; evidence of text + image processing, cleaning, coding and provenance.
- [ ] Stage 3: typed domain knowledge graph; database storage and actual graph query with screenshot/log.
- [ ] Stage 4: LLM grounded with RAG or GraphRAG; source location can be inspected; negative evidence test.
- [ ] Stage 5: agent with substantive callable tool actions (not only a chat prompt); Skill demo if implemented.
- [ ] Stage 6: user correction/new material updates persisted knowledge and a subsequent query reflects the revision.

## Baselines and metrics (define dataset before reporting)

| Research question | Baseline | Proposed system | Measures |
|---|---|---|---|
| Learning-oriented structure | raw Wiki/backlink graph; chat-only | typed tree/dependency + linked chat | task success, prerequisite localization, steps/time, perceived workload |
| Extraction strategy | eager bulk extraction | seed + on-demand refinement | verified precision, duplicate rate, review time, token/latency cost |
| Knowledge-enhanced answering | source-only RAG | source RAG + typed relation query | correctness, citation fidelity, dependency completeness |
| Knowledge recoverability | source retrieval without history | source + personal history | correct recall of previously saved statements, steps/time |

## Fairness and rigor

- Same licensed source corpus across baselines; comparable retrieval/model settings where possible.
- Use prewritten questions and explicit correct answers/required source anchors. Document where human judgment is used.
- Compare human time and model runtime separately. Do not infer long-term mastery gains from short task studies.
- Record failures and limitations: conflicting sources, outdated versions, relation cycles, OCR/figure parsing failures, ambiguous terms.
- Distinguish source provenance from support of a claim; source authenticity does not prove inference validity.

## M0 observed verification — 2026-10-29

Environment: macOS arm64, Python 3.12.13, Node 24.15.0, npm 11.12.1, uv 0.11.7.

| Check | Actual result |
|---|---|
| `make setup` (uv frozen sync + npm ci) | Passed; npm clean install from lockfile, 0 reported npm vulnerabilities |
| `make check` | Passed after clean setup; rerun after interruption also passed |
| Ruff format/check, mypy | Passed; 5 Python source files type checked |
| pytest | 2 passed: health/no storage/API boundaries and environment config validation |
| Prettier, ESLint, tsc | Passed |
| Vitest | 1 passed: four navigation sections remain explicitly unavailable |
| Vite production build | Passed |
| `python scripts/check_docs.py` via uv | 18 documents checked, 0 errors |
| `git diff --check` | Passed |
| Ignore probes | `.env`, `.env.production`, `.local/private.json`, SQLite/log files, node_modules and virtualenv ignored |
| Real HTTP health | Passed on temporary port 18000; response exactly matches documented JSON; test server stopped |
| Browser smoke | UI loaded at 5173; Chat → Knowledge changed heading/selection and retained unavailable status; layout inspected |

Initial Ruff import ordering failure was corrected. Initial Starlette test-client deprecation was resolved by using its supported httpx2 dependency. ESLint 9's install-time unsupported-version warning was resolved by installing ESLint 10. Initial socket binding was sandbox-blocked; permitted loopback startup then revealed occupied port 8000, so HTTP verification used 18000 without stopping unrelated processes. A post-interruption curl failed because the temporary server had stopped; a fresh server verified successfully.

No domain dataset, license, source-verification, migration, AI or course benchmark tests are claimed. Those features do not exist yet. GitHub Actions is configured to run the same setup/check targets on Ubuntu; hosted outcome must be checked on the PR, separately from these macOS results. Branch protections and other manual GitHub settings remain unconfigured by this task.
