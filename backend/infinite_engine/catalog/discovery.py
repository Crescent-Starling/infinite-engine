"""Offline Source Discovery exchange contracts; validation performs no search or writes."""

from typing import Annotated, Literal, Self

from pydantic import AwareDatetime, Field, model_validator

from infinite_engine.catalog.bundles import BundleEntry, digest_json
from infinite_engine.catalog.contracts import (
    Contract,
    Digest,
    DomainSource,
    EntityID,
    Provenance,
    Revision,
    Source,
    Text,
)

Language = Annotated[str, Field(pattern=r"^[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*$")]


class DiscoveryRequest(Contract):
    domain_id: EntityID
    domain_name: Text
    domain_definition: Text
    scope_note: Text
    domain_origin: Literal["preset", "custom"]
    source_profile: Text | None = None
    learning_goal: Literal["Explore", "Understand", "Apply", "Advance"]
    requested_data_types: tuple[Text, ...]
    existing_sources: tuple[Revision, ...] = ()
    preferred_languages: Annotated[tuple[Language, ...], Field(min_length=1)]
    version_context: Text | None = None

    @model_validator(mode="after")
    def sources_only(self) -> Self:
        if not self.domain_id.startswith("domain_"):
            raise ValueError("A Domain ID is required")
        ids = [item.entity_id for item in self.existing_sources]
        if len(ids) != len(set(ids)):
            raise ValueError("Supply one selected revision per existing source")
        if any(
            not isinstance(item.candidate.payload, Source)
            or not item.entity_id.startswith("source_")
            for item in self.existing_sources
        ):
            raise ValueError("existing_sources must contain Source revisions")
        return self


class DiscoveryCheck(Contract):
    """Observed metadata check, not a database SourceCheck or a verified claim."""

    source_id: EntityID
    payload_hash: Digest
    check_kind: Literal["accessibility", "identity", "relevance", "authority", "license"]
    outcome: Literal["confirmed", "failed", "inconclusive"]
    checked_at: AwareDatetime
    method: Text
    actor: Text
    locator: Text
    evidence_note: Text


class SourceAssessment(Contract):
    source_id: EntityID
    intended_audience: Text | None = None
    expected_usefulness: Text
    currency_and_version: Text | None = None
    available_formats: tuple[Text, ...] = ()
    acquisition_methods: tuple[Text, ...] = ()
    priority: Literal["high", "medium", "low"]
    open_questions: tuple[Text, ...]
    provenance: Provenance


class CoverageAssessment(Contract):
    selected_profile: Text
    profile_rationale: Text
    search_status: Literal["performed", "unavailable", "not_requested"]
    coverage: tuple[Text, ...]
    gaps: tuple[Text, ...]
    redundancy_notes: tuple[Text, ...]
    sources: tuple[SourceAssessment, ...]
    provenance: Provenance


class DiscoveryAction(Contract):
    action: Text
    rationale: Text
    provenance: Provenance


class DiscoveryResult(Contract):
    format_version: Literal[1] = 1
    source_candidates: tuple[BundleEntry, ...]
    domain_source_candidates: tuple[BundleEntry, ...]
    source_checks: tuple[DiscoveryCheck, ...]
    coverage_assessment: CoverageAssessment
    recommended_next_actions: tuple[DiscoveryAction, ...]

    @model_validator(mode="after")
    def candidate_kinds(self) -> Self:
        for items, kind in (
            (self.source_candidates, Source),
            (self.domain_source_candidates, DomainSource),
        ):
            if any(not isinstance(item.candidate.payload, kind) for item in items):
                raise ValueError("Wrong candidate kind in discovery output")
        ids = [entry.entity_id for entry in self.source_candidates + self.domain_source_candidates]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate candidate identity")
        return self

    def validate_for(self, request: DiscoveryRequest) -> None:
        """Check scope, references and check snapshots without touching a registry."""
        sources = {item.entity_id: item.candidate.payload for item in request.existing_sources}
        versions = {item.entity_id: item.version for item in request.existing_sources}
        for item in self.source_candidates:
            if item.expected_version != versions.get(item.entity_id, 0):
                raise ValueError("Candidate expected_version does not match existing source")
            sources[item.entity_id] = item.candidate.payload
        resources = [
            source.resource_identity
            for source in sources.values()
            if isinstance(source, Source) and source.resource_identity is not None
        ]
        if len(resources) != len(set(resources)):
            raise ValueError("Duplicate resource identity; reuse the existing source")
        linked: set[str] = set()
        for entry in self.domain_source_candidates:
            association = entry.candidate.payload
            assert isinstance(association, DomainSource)
            if association.domain_id != request.domain_id or association.source_id not in sources:
                raise ValueError("Recommendation has an unknown source or wrong Domain")
            if association.source_id in linked:
                raise ValueError("Duplicate DomainSource recommendation")
            linked.add(association.source_id)
        assessed = [item.source_id for item in self.coverage_assessment.sources]
        if len(assessed) != len(set(assessed)) or not set(assessed) <= sources.keys():
            raise ValueError("Duplicate or unknown assessed source")
        proposed = {item.entity_id for item in self.source_candidates}
        if not proposed <= linked or not (proposed | linked) <= set(assessed):
            raise ValueError("Every proposed source needs a recommendation and assessment")
        for check in self.source_checks:
            source = sources.get(check.source_id)
            if source is None or check.payload_hash != digest_json(source.model_dump(mode="json")):
                raise ValueError("Check does not match the exact source payload")
            if check.check_kind == "license" and check.outcome == "confirmed":
                if not isinstance(source, Source) or source.license is None:
                    raise ValueError("Unknown license cannot have confirmed licensing")
