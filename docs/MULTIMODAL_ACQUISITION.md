# Multimodal knowledge acquisition — Phase 1 design

Status: specification only, 2026-10-29. No adapter, media parser, downloader, ASR,
subscription scheduler, temporal retrieval or video review implementation is delivered.
Existing Source/space and Source Discovery libraries remain unchanged. [Contracts](DATA_CONTRACTS.md),
[Source Registry](SOURCE_REGISTRY.md), [ADR-012](DECISIONS.md) and the
[bounded delivery task](../tasks/multimodal-acquisition.md) define the integration.

## Four separate stages

| Stage | Input → output | Boundary |
|---|---|---|
| Source Discovery | User URL/reference, official metadata query or bounded collection page → Source metadata proposals | No content acquisition, analysis or claim support implied |
| Source Acquisition | Exact source revision + host permission → immutable local artifact and acquisition receipt | Permission is operation-specific; an accessible URL or collection choice is insufficient |
| Multimodal Content Processing | Authorized artifact → parsed text, transcripts, frames, observations | Derived output retains original bytes, timing and processing provenance; no truth promotion |
| Knowledge Extraction and Review | Selected processed evidence → candidates → explicit exact-revision review | Deterministic graph validation and human approval precede canonical commit |

The modular monolith owns orchestration and transactions. `catalog` owns source identity; `sources` owns versioned Resource/Document/Anchor
metadata and the existing supplied-bytes SourceAdapter protocol; future `ingest` owns
job/permission policy and orchestration, reusing those repositories; `knowledge`
owns candidate review; `retrieval` consumes committed processing revisions. The UI and
Agent use these services. Adapters cannot approve knowledge or grant themselves network,
filesystem or subprocess access. No autonomous crawl or implicit next-page traversal.

Text and image M2 acceptance remains required. Video is an additional bounded track,
not a replacement for text/image evidence or a prerequisite for manual Domain creation.

## Adapter interface specification (not executable Python)

Notation below describes typed service boundaries. All records have strict unknown-field
rejection and `contract_version=1` when implemented; inputs are validated before I/O.
`SourceRef` is `(source_id, source_version, revision_hash)`. `ArtifactRef` is an immutable
manifest ID + SHA-256, never an arbitrary caller path. `LocalFileGrant` is an opaque,
host-issued handle for a user-selected file. Optional values are explicit nulls.

```text
DiscoveryAdapter.discover(DiscoveryRequest, HostContext) -> Result[DiscoveryPage]
AcquisitionAdapter.acquire(AcquisitionRequest, HostContext) -> Result[AcquiredArtifact]
ProcessingAdapter.process(ProcessingRequest, HostContext) -> Result[ProcessedBatch]
ExtractionAdapter.propose(ExtractionRequest, HostContext) -> Result[CandidateBatch]
```

| Record | Typed fields / invariant |
|---|---|
| DiscoveryRequest | platform enum, discriminated target `video_url / creator_id / collection_id / webpage_url`, filter record, nullable cursor, positive max_items and max_pages; one bounded user operation |
| DiscoveryPage | metadata proposals, external identities, next_cursor?, unavailable item diagnostics, observation time; a cursor is not permission to continue |
| AcquisitionRequest | SourceRef, operation enum, discriminated locator `safe_url / LocalFileGrant`, permission_id, adapter_id/version, Limits, idempotency_key |
| AcquiredArtifact | SourceRef, ArtifactRef, detected MIME, byte count, acquisition method/time, permission receipt, original locator with private credentials excluded, nullable duration_ms; only complete validated bytes are available for processing |
| ProcessingRequest | nonempty artifact refs, operation enum, permission_id, adapter_id/version, model/configuration record, selected time/page/row ranges, Limits, idempotency_key |
| ProcessedBatch | immutable output manifest refs, input hashes, exact SourceRef, processing_run_id, warnings and rejected ranges; no canonical knowledge writes |
| ExtractionRequest | exact processed revision refs, selected evidence scope, target space_id, proposal types, model/configuration, permission_id, Limits |
| CandidateBatch | pending candidate revisions, exact anchor refs, explicit support gaps, processing_run_id; empty candidates is valid |
| HostContext | host-controlled policy, cancellation/deadline, safe transport, granted local handles, credential resolver, quota reservation; never supplied by source text |
| Limits | positive max_input_bytes, max_output_bytes, max_duration_ms, max_items, max_pages, max_frames, max_wall_time_ms and local_quota_bytes; each adapter declares applicable fields, no unbounded null defaults |

`Result[T]` is a discriminated union: `ok(value: T)`,
`partial(value: T, failures: nonempty list[Failure])`, or
`failed(error: Failure)`; partial never means completed/fully indexed.
`Failure = {code, stage, safe_message, retryable, retry_after_ms?, affected_ref?,
permitted_alternatives: list[Alternative]}`. Alternatives are descriptive action enums
(`register_metadata`, `select_local_file`, `select_subtitle`, `configure_provider`,
`request_permission`, `reduce_scope`), never commands to execute automatically.

Closed failure codes: `invalid_input`, `invalid_media`, `malformed_subtitle`,
`missing_audio`, `missing_timestamps`, `timestamp_out_of_range`, `unsupported_format`,
`unsupported_platform`, `unsupported_method`, `permission_required`, `permission_denied`,
`unsafe_url`, `file_unavailable`, `offline`, `provider_unavailable`, `size_limit`,
`duration_limit`, `quota_exceeded`, `rate_limited`, `timeout`, `interrupted`,
`version_conflict`, `integrity_error`, `parse_error`. Only transient transport/rate-limit
failures may be retried automatically; access denials never trigger a fallback downloader.

The existing `SourceAdapter.parse(content, document) -> ParseResult` stays a pure
supplied-bytes boundary. The signatures above are future host service interfaces, not a
replacement parser API. Only acquisition/orchestration receives safe host capabilities;
parser/model adapters receive validated inputs and narrowly scoped provider handles.
Wrap existing complete/partial/failed parse results explicitly in service results without
changing the stored interchange format. See [SOURCE_DISCOVERY](SOURCE_DISCOVERY.md).

### Reusable implementations to deliver later

| Adapter | Typed input → output | Constraints |
|---|---|---|
| Web page | Safe HTTP(S) URL → acquired HTML; HTML artifact → text blocks + DOM/offset anchors | No scripts, linked resources or recursive crawling; rendering is a separately authorized future capability |
| PDF | Granted file or authorized download → PDF artifact; artifact → page/text/image regions | No external references; preserve page numbering; OCR is an explicit processing option |
| Local document | LocalFileGrant → artifact; artifact + format enum → sections/spans | Allowlisted formats, no macros, archive expansion limits, unsupported format returns reason |
| Structured data | Artifact + CSV/JSON format/schema → records + row/field or JSON Pointer anchors | Preserve row identities and schema/version; no formula or embedded code execution |
| Image | Artifact + selected region → OCR/visual observations | Original pixels and coordinate system pinned; model interpretation is not source text |
| Video platform metadata | Video/creator/collection reference + cursor → bounded DiscoveryPage | Metadata only; thumbnail URL is not downloaded image content |
| Local video / audio | LocalFileGrant → probed artifact + stream metadata | Detected container/codec, size/duration limits; no network-enabled demuxing |
| Subtitle | Subtitle artifact + explicit video association + format SRT/WebVTT → Transcript + segments | Original cues preserved; no inferred exact alignment from a filename |
| Audio extraction | Validated media artifact + selected streams/range → audio artifact + time mapping | Requires local transform permission; missing audio is explicit, subtitles may still work |
| Audio transcription | Audio artifact + locally installed model/config → Transcript + timed segments | Optional, off by default; no automatic model download or remote upload |
| Visual analysis | Selected actual frames + model/config → VisualObservation records | Sampling budget, original frame timestamps; no claim that sampled frames cover unseen content |

## Video processing and recovery

1. Register source metadata and explicit local selection/permissions. Pin the Source revision.
2. Stream-copy to a quota-reserved staging area; check size while copying, hash bytes,
   detect MIME/container, probe streams and duration with bounded local tooling. Reject
   unexpected formats/unsafe references; never trust extension or reported size alone.
3. Prefer a supplied subtitle track. A subtitle-only import can reference a metadata-only
   video; local media is not mandatory. Record whether alignment/duration is unverified.
4. Parse SRT/WebVTT without executing markup; preserve raw bytes, cue order, cue IDs,
   language and all malformed-cue diagnostics. Default malformed import fails atomically;
   an explicit salvage option may retain valid cues as partial, never hide omitted spans.
5. If no usable subtitles, stop with permitted choices. Only an explicitly enabled ASR job
   extracts audio and runs a configured local model. A silent video returns missing_audio
   for that branch, while separately authorized visual work remains possible.
6. Segment using cue boundaries and deterministic configuration. Preserve the mapping
   from every segment to original cues. Overlapping speech is allowed; negative or
   reversed times are invalid. Untimed text may be retained as an untimed artifact with
   missing_timestamps; it cannot become a precise temporal citation.
7. Optional chapters use exact parent transcript/segment references and recorded method.
   Model-suggested chapters remain proposals. Chapter detection never retimes cues.
8. Optional frame sampling decodes actual presentation timestamps (including variable
   frame rate). Persist any audio trim/start-offset time mapping back to the source;
   do not derive exact timestamps from frame ordinal or chunk length.
9. On user-selected scope, propose concepts/claims with anchors and support gaps. A
   transcript saying something is evidence of speech, not verification of the claim.
10. Human corrections append transcript revisions; originals remain immutable. Text-only
    corrections preserve timing; timing edits retain old/new spans, actor and reason.
    Candidates pinned to the old revision remain pinned; re-extraction creates new ones.
11. Atomically publish artifacts/manifests and then committed index inputs. Keyword/vector
    matches include source/transcript revisions, segment IDs, time intervals, excerpt,
    timing quality and support gaps. Candidate material is explicitly labeled; canonical
    retrieval selects only reviewed knowledge. Never mix evidence across editions silently.
12. Review an exact candidate hash/revision, validate typed endpoints and prerequisites,
    then transactionally commit knowledge with evidence. Stale review fails; transcript
    correction, metadata approval and collection acceptance cannot approve a claim.

Jobs move `queued → running → succeeded | partial | failed | cancelled | interrupted`.
Permission failure is a failed job with a structured code; no artifact becomes available.
A process restart marks expired running leases interrupted. Resume creates a new attempt,
revalidates permissions, budgets and input hashes, and reuses only committed checkpoints.
Checkpoints are validation, artifact publication, transcript publication and index publication.
An index is rebuildable from committed manifests; a crash cannot expose half an index.
A retried partial job processes failed ranges without duplicating committed outputs.

Idempotency combines exact source revision, artifact hash, operation, adapter version,
model/config digest and selection. Same key with different input fails; exact replay returns
existing results. Blob hashes deduplicate bytes, not source identities, editions or rights.
Atomic staging/rename plus database manifests use recovery reconciliation: unreferenced
staging files expire, referenced blobs are retained, missing blobs report integrity_error.
Cancellation cleans staging and releases reservations; explicit deletion/retention controls
must account for referenced evidence and never silently erase history.

## Permissions and safety model

These are requirements for future runtime enforcement, not claims about current Source
URL validation. Personal source acceptance never implies downloading or external sharing.

`AcquisitionPermission` records ID, user actor/time, exact resource/version or bounded
collection scope, allowed operations, method/provider, rights basis/evidence (possibly
unknown), expiry/revocation, item/byte/time budgets and explicit remote disclosure choices.
Operations are distinct: metadata_query, read_local, download_document, download_caption,
download_media, extract_audio, transcribe_local, analyze_visual, send_to_remote_model.
The host evaluates user intent, technical allowlist, access authorization and applicable
rights constraints independently. User consent cannot override platform restrictions.
Unknown rights are preserved and never treated as confirmed licensing or redistribution
permission. Retain ADR-011 acquisition-plan rejection of unknown/restricted reuse for
content acquisition; permission evidence and an applicable host grant are both required.
This design does not weaken that existing planning validator.
Local user-supplied processing records the user's permitted-use declaration without
asserting ownership. Private derivatives are not automatically publishable.

- Safe transport accepts only HTTP(S), rejects URL credentials and unsupported ports,
  normalizes hosts, and blocks loopback, private, link-local, multicast, reserved and
  cloud-metadata destinations in IPv4/IPv6, including mapped addresses. Validate DNS
  results and the actual peer; pin resolution per request to prevent rebinding. Every
  redirect and retry receives the same checks; redirect count is bounded. Never forward
  authorization cross-origin or inherit arbitrary environment proxies. No file/FTP URLs.
- Platform endpoints are allowlisted official API hosts, not arbitrary URLs supplied in
  metadata. A deep link is a display action, not backend acquisition permission.
- Read only granted regular files; resolve symlinks and disallow path traversal and special
  devices. Hold validated handles against path substitution. Parsers/decoders have CPU,
  memory, wall-time and decompression limits, no network access, and no shell expansion.
- Reserve storage before work, cap both compressed input and decoded/output bytes,
  frames/pixels/cues, duration and total job storage. Check streaming counters rather than
  trusting Content-Length. Unknown duration requires bounded probing, not unlimited decode.
- Initial proposed host defaults: 512 MiB input, 1 GiB output, 2 hours media, 10 MiB subtitle,
  300 sampled frames, 10 GiB managed storage, 15 minutes per job; provider or user limits
  may lower these. Increasing them is explicit configuration. Phase 2 must validate them
  against small fixtures and available disk, and implement applicable limits before release.
- Network jobs have per-provider concurrency/rate/quota budgets; start at one concurrent
  request. At most three attempts for transient failures, exponential backoff with jitter,
  honor Retry-After within the deadline; exhaustion preserves a resumable state. No retry
  loops on denied/unsupported operations. API quota exhaustion pauses synchronization.
- Resolve credentials server-side from opaque credential references; never store tokens
  in manifests, source URLs, model config, browser variables or logs. Persist safe locator
  identifiers; reject credential-bearing input URLs or keep secrets only in the resolver.
  Log job IDs, codes and counters, not raw media, transcripts, tokens or personal paths.
- No cookie scraping, authentication bypass, DRM circumvention, unofficial restriction
  evasion or unrestricted third-party scripts. Unsupported methods give a reason and
  offer metadata-only registration or user-provided files/subtitles.

## Platform policy and capability negotiation

Single video, creator and collection references are separate discovery target variants.
Each connector advertises supported operations and required authorization; the host checks
these before scheduling. Metadata can exist without any acquisition capability.

YouTube metadata discovery is a future official Data API connector. Caption listing and
caption download are separate operations; listing does not return the caption content and
requires authorization. No general video downloader is proposed. Exact OAuth scopes,
account eligibility and quotas must be rechecked at Phase 5 implementation. See official
[caption listing](https://developers.google.com/youtube/v3/docs/captions/list),
[caption downloading](https://developers.google.com/youtube/v3/docs/captions/download)
and [playlist item listing](https://developers.google.com/youtube/v3/docs/playlistItems/list).

Bilibili remains unsupported until a specific official interface, permitted resource scope
and application authorization are verified. The official
[Open Platform documentation](https://openhome.bilibili.com/doc) is the starting point;
its existence is not evidence of arbitrary public-channel enumeration or media access.
No reverse-engineered web endpoints are part of this design. Reference check: 2026-10-29.

## Creator/collection synchronization

CreatorSubscription is local app configuration, not a platform follow action. Default:
disabled schedule, manual metadata-only sync, no download/transcription/visual/extraction
jobs. Domain association resolves to its primary Knowledge Space; no parallel space model.

An explicit sync configuration pins provider, creator/collection ID, filters (date window,
language, keywords), max_items/pages, quota and time budget, cadence and credential ref.
Processing preferences default false; enabling batch processing requires a separate
bounded operation grant with allowed stages, per-item/aggregate limits and a reviewable
selection. Subscription edits alone do not grant those permissions.

Use provider-native `(platform, resource_kind, external_id)` identity to upsert metadata
revisions; never key on title, URL query parameters or playlist position. Collection
membership pins source IDs plus observed order and time; one video can be in many lists.
Store opaque pagination cursor, watermark, last_success_at, last_attempt_at, failure and
configuration revision. Commit each bounded page's items and checkpoint atomically.
A failed page does not advance its cursor; replay is idempotent. Scan a bounded overlap
window where supported to find delayed items. Invalid/expired cursor starts a bounded
rescan with the same identity dedupe; never implies permission for an unlimited backfill.

Do not assume chronological APIs or complete enumeration. Missing/private/deleted items
are availability observations, not deletion of local history. A partial/failed scan cannot
remove membership; complete scans append membership changes without erasing past ones.
Changed metadata appends a source revision without repinning user choices or evidence.
Quota/offline/auth failures keep checkpoints and report the reason; offline local imports
and existing evidence inspection remain available. Synchronization never approves knowledge.
