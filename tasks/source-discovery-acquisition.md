# Bounded task: source discovery and acquisition architecture

Implemented scope: additive models, offline JSON/YAML interchange, exact-revision artifact import, Source Profile, Source Discovery Skill specification, six adapter families as interfaces/design, four mock-domain manifests and tests. See [architecture](../docs/SOURCE_DISCOVERY.md).

Acceptance gates:
- Independent Provider, Resource, Document, Anchor, DomainSource, SourceCheck and SourceReview semantics.
- Existing catalog IDs, revisions, approvals and personal choices survive additive migration 005.
- Dry-run and atomic import, exact replay, conflict/reference/hash rejection; no implied acquisition or review.
- Four manifests pass schema and runtime validation with offline mock data.
- Safe configuration parsing and tests; full repository checks reported in VALIDATION.

Excluded: actual network discovery, acquisition/parsing implementations, UI/API integrations, complete RAG and claim verification. Adapter interfaces and partial-result fixtures are not proof of working ingestion.

Next recommended bounded task: local text/Markdown acquisition with actual bytes, approved file access, UTF-8/code-point anchoring, content hashes, partial decoding and restart/round-trip tests. Subsequent image processing must genuinely process pixels and validate regions before M2 can be accepted.
