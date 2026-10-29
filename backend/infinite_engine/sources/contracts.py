"""Source architecture v1: metadata never grants access or verifies claims."""

from typing import Annotated, Literal, Self

from pydantic import Field, HttpUrl, model_validator

from infinite_engine.catalog.bundles import BundleEntry
from infinite_engine.catalog.contracts import (
    Candidate,
    Contract,
    Digest,
    DomainSource,
    EntityID,
    Provenance,
    ReviewRecord,
    Source,
    Text,
)
from infinite_engine.catalog.ids import stable_id

Version = Annotated[int, Field(strict=True, ge=1)]
AdapterKind = Literal["web", "pdf", "text", "csv", "json", "xml", "api_metadata", "image"]


class Pin(Contract):
    id: EntityID
    version: Version


class Access(Contract):
    availability: Literal["unknown", "public", "local", "login", "subscription", "unavailable"] = (
        "unknown"
    )
    reuse: Literal["unknown", "permitted", "restricted"] = "unknown"
    conditions: Text | None = None
    permission_evidence: Text | None = None

    @model_validator(mode="after")
    def permission_basis(self) -> Self:
        if self.reuse == "permitted" and not self.permission_evidence:
            raise ValueError("Permitted reuse requires an explicit permission basis")
        return self


class SourceProvider(Contract):
    kind: Literal["source_provider"] = "source_provider"
    name: Text
    homepage: HttpUrl | None = None
    provider_type: Literal["publisher", "institution", "community", "personal", "unknown"]


class SourceResource(Contract):
    """Sidecar of an existing Source revision, not a replacement Source identity."""

    kind: Literal["source_resource"] = "source_resource"
    source: Pin
    provider: Pin | None = None
    resource_type: Literal["collection", "standalone"]
    access: Access = Access()


class SourceDocument(Contract):
    kind: Literal["source_document"] = "source_document"
    resource: Pin
    title: Text
    media_type: Text
    adapter: AdapterKind
    locator: Text
    publisher_version: Text | None = None
    content_hash: Digest | None = None
    acquisition_state: Literal["not_acquired", "available", "failed"] = "not_acquired"
    access: Access = Access()

    @model_validator(mode="after")
    def acquired_hash(self) -> Self:
        if self.acquisition_state == "available" and self.content_hash is None:
            raise ValueError("Available documents require a content hash")
        return self


class TextLocator(Contract):
    kind: Literal["text"] = "text"
    section: Text
    start: Annotated[int, Field(strict=True, ge=0)]
    end: Annotated[int, Field(strict=True, ge=1)]

    @model_validator(mode="after")
    def ordered(self) -> Self:
        if self.end <= self.start:
            raise ValueError("Text offsets must form a nonempty half-open interval")
        return self


class PageLocator(Contract):
    kind: Literal["pdf"] = "pdf"
    page: Annotated[int, Field(strict=True, ge=1)]
    section: Text | None = None


class StructuredLocator(Contract):
    kind: Literal["structured"] = "structured"
    syntax: Literal["json_pointer", "xpath", "csv_row", "api_record"]
    selector: Text
    field: Text | None = None


class WebLocator(Contract):
    kind: Literal["web"] = "web"
    url: HttpUrl
    selector: Text
    quote: Text


class ImageLocator(Contract):
    kind: Literal["image"] = "image"
    # Pixel coordinates in the original image, not a resized preview.
    x: Annotated[int, Field(strict=True, ge=0)]
    y: Annotated[int, Field(strict=True, ge=0)]
    width: Annotated[int, Field(strict=True, ge=1)]
    height: Annotated[int, Field(strict=True, ge=1)]
    description: Text
    description_origin: Literal["human", "publisher", "ai", "ocr"]


Locator = Annotated[
    TextLocator | PageLocator | StructuredLocator | WebLocator | ImageLocator,
    Field(discriminator="kind"),
]


class SourceAnchor(Contract):
    kind: Literal["source_anchor"] = "source_anchor"
    document: Pin
    content_hash: Digest
    locator: Locator
    locator_status: Literal["proposed", "checked", "unresolved"] = "proposed"
    check_evidence: Text | None = None

    @model_validator(mode="after")
    def checked_basis(self) -> Self:
        if self.locator_status == "checked" and not self.check_evidence:
            raise ValueError("Checked locator requires evidence; this does not verify a claim")
        return self


Artifact = Annotated[
    SourceProvider | SourceResource | SourceDocument | SourceAnchor,
    Field(discriminator="kind"),
]


class ArtifactEntry(Contract):
    identity_key: Text
    version: Version = 1
    payload: Artifact
    provenance: Provenance

    @model_validator(mode="before")
    @classmethod
    def key_is_immutable(cls, value: object) -> object:
        if isinstance(value, dict):
            key = value.get("identity_key")
            if not isinstance(key, str) or key != key.strip():
                raise ValueError("Unpadded immutable identity_key required")
        return value

    @property
    def id(self) -> str:
        if isinstance(self.payload, SourceResource):
            return stable_id("source", self.identity_key)
        return stable_id(self.payload.kind, self.identity_key)


class SourceCandidate(Candidate):
    payload: Source


class SourceEntry(BundleEntry):
    candidate: SourceCandidate


class AssociationCandidate(Candidate):
    payload: DomainSource


class AssociationEntry(BundleEntry):
    candidate: AssociationCandidate


class SourceCandidates(Contract):
    format_version: Literal[1] = 1
    batch_id: Text
    sources: tuple[SourceEntry, ...] = ()
    artifacts: tuple[ArtifactEntry, ...] = ()

    @model_validator(mode="after")
    def only_sources(self) -> Self:
        if not self.sources and not self.artifacts:
            raise ValueError("Empty candidate manifest")
        if any(e.candidate.payload.kind != "source" for e in self.sources):
            raise ValueError("source_candidates accepts only Source catalog entries")
        return self


class SourceAssociations(Contract):
    format_version: Literal[1] = 1
    batch_id: Text
    associations: Annotated[tuple[AssociationEntry, ...], Field(min_length=1)]

    @model_validator(mode="after")
    def only_associations(self) -> Self:
        if any(e.candidate.payload.kind != "domain_source" for e in self.associations):
            raise ValueError("source_associations accepts only DomainSource entries")
        return self


class SourceReview(ReviewRecord):
    """Source-specific view of the existing exact-revision metadata review ledger."""

    entity_id: Annotated[str, Field(pattern=r"^source_[0-9a-f-]{36}$")]

    @model_validator(mode="after")
    def source_only(self) -> Self:
        if not self.entity_id.startswith("source_"):
            raise ValueError("SourceReview must reference a Source")
        return self


class SearchProfile(Contract):
    format_version: Literal[1] = 1
    profile_id: Text
    revision: Version
    domain: Pin
    purpose: Text
    languages: Annotated[tuple[Text, ...], Field(min_length=1)]
    queries: tuple[Text, ...] = ()
    provider_allowlist: tuple[EntityID, ...] = ()
    adapters: Annotated[tuple[AdapterKind, ...], Field(min_length=1)]
    inclusion: Annotated[tuple[Text, ...], Field(min_length=1)]
    exclusion: Annotated[tuple[Text, ...], Field(min_length=1)]
    max_candidates: Annotated[int, Field(strict=True, ge=1, le=100)] = 10
    max_requests: Annotated[int, Field(strict=True, ge=0, le=100)] = 0
    network_requested: bool = False
    provenance: Provenance

    @model_validator(mode="after")
    def bounded_search(self) -> Self:
        if not self.network_requested and self.max_requests:
            raise ValueError("Offline profiles cannot request network calls")
        if self.network_requested and (not self.provider_allowlist or not self.max_requests):
            raise ValueError("Network proposals require explicit provider and request bounds")
        return self


class AcquisitionItem(Contract):
    document: Pin
    action: Literal["metadata_only", "request_access", "use_local", "download"]
    rationale: Text
    permission_evidence: Text | None = None

    @model_validator(mode="after")
    def explicit_permission(self) -> Self:
        if self.action in {"use_local", "download"} and not self.permission_evidence:
            raise ValueError("Content acquisition proposals require permission evidence")
        return self


class AcquisitionPlan(Contract):
    format_version: Literal[1] = 1
    plan_id: Text
    revision: Version
    profile_id: Text
    profile_revision: Version
    state: Literal["proposed"] = "proposed"
    max_bytes: Annotated[int, Field(strict=True, ge=1, le=100_000_000)] = 1_000_000
    max_requests: Annotated[int, Field(strict=True, ge=0, le=100)] = 0
    items: Annotated[tuple[AcquisitionItem, ...], Field(min_length=1, max_length=100)]
    provenance: Provenance

    @model_validator(mode="after")
    def bounded_plan(self) -> Self:
        pins = [(i.document.id, i.document.version) for i in self.items]
        if len(pins) != len(set(pins)):
            raise ValueError("Duplicate acquisition target")
        if any(i.action == "download" for i in self.items) and not self.max_requests:
            raise ValueError("Download proposals require a positive request budget")
        return self
