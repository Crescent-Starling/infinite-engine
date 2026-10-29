# Infinite Engine — executable milestones

**Rule:** One milestone at a time. Do not mark done without passing observed tests, a reproducible manual demo, and updated docs. Implementation is not begun yet; all statuses are `planned`.

| ID | Milestone | Exit gate | Status |
|---|---|---|---|
| M0 | Repository foundation | bootable minimal backend/frontend + offline tests + consistent configs | planned |
| M1 | Core data schema, sources & IDs | stable CRUD, source anchors, status and migrations tested | planned |
| M2 | Text+image ingest, candidate extraction | one of each persisted, idempotent parse, evidence preserved | planned |
| M3 | Typed KG and Domain Seed | astronomy fixture, typed graph queries and validation | planned |
| M4 | View Engine + frontend | tree + concept dependency + evidence view, navigation works | planned |
| M5 | Source-grounded RAG and dialogue | chat returns linked concept IDs and verifiable anchors | planned |
| M6 | Mentor Agent + Skills + learning template | two real tools; local SKILL.md; configurable template | planned |
| M7 | Personal cognition & recoverability | history survives restart and supports resume | planned |
| M8 | Feedback/knowledge revision | candidate review, provenance + history, view refresh | planned |
| M9 | 3 heterogenous domain fixtures | Latin, nutrition, Stellaris extension tests | planned |
| M10 | Evaluations, polish and course demo | repeatable six-stage demo + benchmark baselines + report evidence | planned |

### Dependency constraints

M0 → M1 → M2/M3 → M4/M5 → M6/M7/M8 → M9/M10. Frontend may scaffold earlier but should not invent data models. M9 fixture design may inform the earliest Schema, but avoid prematurely building four full databases.

### Suggested per-milestone workflow

1. Read spec and relevant contracts; inspect existing code.
2. Write task-scoped implementation plan with affected modules, cases and verification commands.
3. Implement smallest vertical slice; prefer tests of invariants before broad UI polish.
4. Run tests; fix failures; check manual acceptance route.
5. Update architecture decision record, build log and milestone state from evidence.
6. Stop and ask for next task/owner acceptance; no unauthorized external actions.

### Project-wide definition of done

- The feature meets specified acceptance tests; no claims unsupported by observed tests.
- Data can persist across restart; error cases are handled and surfaced.
- Sources and knowledge status are not lost in transforms.
- Tests documented and reproducible without personal secrets.
- README and relevant specs remain accurate.

See `tasks/00-repository-foundation.md` for first bounded task.
