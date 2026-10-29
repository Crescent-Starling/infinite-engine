# Multimodal acquisition — six bounded phases

Scope of this task: **Phase 1 only**, architecture and contract specifications. No executable
media or platform capability. See [architecture](../docs/MULTIMODAL_ACQUISITION.md),
[contracts](../docs/DATA_CONTRACTS.md) and [ADR-012](../docs/DECISIONS.md).

| Phase | Deliverables and dependencies | Exit gate | Status |
|---|---|---|---|
| 1 | Four-stage architecture; typed adapter specs; video entities, pipeline, temporal schema, subscriptions, safety and migration plan | Cross-document review; local Markdown checks; report actual repository check results | Documentation delivered; repository checks passed; verification below |
| 2 | Local video and SRT/WebVTT ingestion; host file grants, bounded media validation, immutable blobs, jobs/recovery; additive migration on ADR-010 foundation | Offline import/restart/replay, failures below, no remote fetching; reproducible local demo | Planned |
| 3 | Transcript segmentation/corrections, optional configured local ASR, timestamped keyword retrieval; depends on Phase 2 and M1 anchors | Exact cue citations, preserved revisions and labeled approximate timing; subtitles preferred | Planned |
| 4 | Video candidates in shared KG/RAG/review; depends on Phase 3 plus M3/M5/M8 services | Explicit exact-revision review, graph validation, evidence-preserving answers or support gaps | Planned |
| 5 | Official authorized platform metadata connectors; depends on Phase 2 policy/jobs, independently of full KG | Bounded video/creator/collection metadata lookup with offline fakes, quota/auth/error handling; capability-specific live verification only if authorized | Planned |
| 6 | User-controlled incremental creator/collection sync; depends on Phase 5 | Page checkpoint/replay, no duplicate videos, default metadata-only, explicit bounded processing configuration | Planned |

Phases preserve M1–M10 and text/image M2 acceptance. Phase 5 does not require completing
knowledge verification to register metadata. No batch discovery, crawling, download, model
installation or external account connection is authorized by this specification. Each later
phase is its own implementation task; completion never automatically advances to the next.

## Acceptance and planned tests

Fixtures must be tiny synthetic/self-created media and subtitles with declared reuse rights.
No copied platform content, real personal records or API secrets. Providers use offline
fakes; optional live authorization checks are separately reported, never simulated as live.

| Case | Phase | Required assertion |
|---|---|---|
| Invalid media / format mismatch | 2 | Reject truncated or mislabeled container; no published artifact or transcript |
| Malformed subtitles | 2 | Fail atomically by default; explicit salvage reports rejected cue/range and partial state |
| Missing audio | 2/3 | Probe reports silent stream; subtitle-only import still works; ASR returns missing_audio |
| Missing timestamps | 2/3 | Preserve untimed original with diagnostic; no fabricated temporal anchor |
| Timestamp accuracy | 2/3 | Synthetic SRT 00:00:01,250–00:00:02,800 persists as 1250–2800 ms; WebVTT, overlaps, variable-frame-rate and trim offsets preserve measured timing; no invented sub-cue precision |
| Duplicate imports | 2 | Same idempotency key/input replays once; changed bytes/config under same key conflicts; same bytes from different source identities preserve provenance |
| Interrupted processing | 2/3 | Crash before/after blob and manifest/index publication exposes no partial success; restart marks expired lease interrupted and resumes committed checkpoints |
| Offline operation | 2/3/5 | Local imports/retrieval work with network blocked; absent model/key returns explicit unavailable, never downloads model |
| Unauthorized acquisition | 2/5/6 | No/expired/revoked/wrong-scope grant fails before I/O; metadata grant cannot download/transcribe; resume checks current grant |
| Oversized files and quotas | 2/5 | Reject at stream/decode counters even with false or absent size metadata; duration/output/local quota limits release reservations |
| Unsupported platform URLs | 5 | Return unsupported_platform/method and permitted alternatives; no scraping or fallback download |
| Version and provenance | 2/3/4 | Populated v5 upgrade preserves hashes/IDs/approvals; correction retains original; stale edits/review fail; retrieval resolves pinned older anchors |
| Source isolation | 3/4 | Cross-video segment/frame refs and out-of-range times fail; insufficient evidence is explicit; metadata review never promotes a claim |
| Graph review | 4 | Invalid relation endpoints and circular prerequisites rejected; duplicate aliases handled by shared contracts; candidate rejection leaves canonical graph unchanged |
| SSRF and secrets | 5 | Local/private IPv4/IPv6, DNS rebinding, redirect chains and cross-host credentials blocked; diagnostics/logs redact tokens and private content |
| Incremental synchronization | 6 | Overlapping playlists, repeated pages, expired cursors, partial scans, deleted/private items, configuration races and quota retries preserve history without duplicates or unintended media jobs |

Phase 1 has no executable runtime schema or safety behavior to test. Do not add token
presence tests pretending to validate media/security semantics. Existing docs checker and
repository regression checks provide structural verification only; cases above remain future
acceptance requirements, not passing tests.

## Manual design review

1. Follow the four stages in the architecture: a discovered video URL produces metadata only.
2. Trace a locally supplied SRT through immutable raw artifact, transcript revision, segment,
   TemporalSourceAnchor and future retrieval result; verify every revision pin is retained.
3. Trace a transcript correction: originals and old citations remain; claim review is separate.
4. Trace creator/playlist registration: default manual metadata-only; no media permission follows.
5. Inspect current `catalog/contracts.py` and migrations to confirm this task adds no runtime
   video contracts; the application's UI remains a shell.

## Observed verification

Observed on 2026-10-29 (Asia/Shanghai):

- Initial `make setup`: failed because the default uv cache was sandbox-restricted.
- Retried with `UV_CACHE_DIR=/private/tmp/infinite-engine-ma-uv-cache` and
  `npm_config_cache=/private/tmp/infinite-engine-ma-npm-cache`: uv succeeded; npm failed
  with registry DNS ENOTFOUND and “Exit handler never called”.
- The same setup command with approved network/filesystem execution: passed, 233 npm
  packages installed, audit reported zero vulnerabilities; locked dependencies unchanged
  by this task.
- First `make check` while installation was incomplete: backend 114 tests and docs passed;
  frontend stopped because Prettier was unavailable. This was not a complete pass.
- Final `make check` with the temporary cache variables after setup: passed. Ruff formatting
  and lint, mypy (31 source files), pytest (124 passed), local links (29 documents, zero
  errors), frontend Prettier/ESLint/TypeScript, Vitest (1 passed) and production build passed.
  Concurrent Source Discovery work added tests during the task, explaining the count change;
  those runtime tests are not newly implemented video tests.
- `git diff --check`: passed. No formatter mutation was needed; format checks passed.
- Manual document trace reviewed metadata-only discovery, subtitle/correction revision pins,
  temporal citation lineage and default metadata-only subscriptions. This is a design review,
  not an executed media demo or user acceptance.

Runtime tests in the matrix remain planned and have not been implemented or run. No
migration, parser, media fixture, remote acquisition or platform integration is delivered by
Phase 1. Existing and concurrent work was preserved; no push or PR was performed because
publication was not authorized. Next bounded MA task is Phase 2, not automatically started.
