"""Version 1 candidate contracts. Validation does not establish truth or approval."""

from datetime import date
from typing import Annotated, Any, ClassVar, Literal, Self

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    SerializerFunctionWrapHandler,
    field_validator,
    model_serializer,
    model_validator,
)

from infinite_engine.catalog.ids import normalized_label

Text = Annotated[str, Field(min_length=1)]
Digest = Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
EntityID = Annotated[str, Field(pattern=r"^[a-z_]+_[0-9a-f-]{36}$")]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)
    compatibility_fields: ClassVar[tuple[str, ...]] = ()

    @model_serializer(mode="wrap")
    def preserve_legacy_shape(self, handler: SerializerFunctionWrapHandler) -> dict[str, Any]:
        # Additive optional metadata must not change historical snapshot hashes or bundle receipts.
        values: dict[str, Any] = handler(self)
        for name in self.compatibility_fields:
            if values.get(name) is None:
                values.pop(name, None)
        return values


class Label(Contract):
    # Deliberately a documented subset, not a claim of complete BCP-47 validation.
    language: Annotated[str, Field(pattern=r"^(?:[A-Za-z]{2,8})(?:-[A-Za-z0-9]{1,8})*$")]
    text: Text
    role: Literal["preferred", "alias"] = "preferred"

    @field_validator("language")
    @classmethod
    def language_case(cls, value: str) -> str:
        return value.lower()


class Labeled(Contract):
    labels: Annotated[tuple[Label, ...], Field(min_length=1)]

    @field_validator("labels")
    @classmethod
    def unique_labels(cls, labels: tuple[Label, ...]) -> tuple[Label, ...]:
        names = [(label.language, normalized_label(label.text)) for label in labels]
        preferred = [label.language for label in labels if label.role == "preferred"]
        if len(names) != len(set(names)) or len(preferred) != len(set(preferred)):
            raise ValueError("Duplicate labels or preferred labels within a language")
        if not preferred:
            raise ValueError("At least one preferred label is required")
        return tuple(sorted(labels, key=lambda label: (label.language, label.role, label.text)))


class Domain(Labeled):
    compatibility_fields = ("origin", "creation_method")
    # None is a legacy missing value, never an inferred preset/custom classification.
    origin: Literal["preset", "custom"] | None = None
    creation_method: Literal["manual", "ai_assisted", "classification_import"] | None = None

    @model_validator(mode="after")
    def management_metadata(self) -> Self:
        if (self.origin is None) != (self.creation_method is None):
            raise ValueError("origin and creation_method must be supplied together")
        return self

    kind: Literal["domain"] = "domain"
    slug: Annotated[str, Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")]
    definition: Text
    scope_note: Text
    domain_type: Literal["academic", "practical", "language", "game", "interdisciplinary"]


class Source(Labeled):
    compatibility_fields = (
        "language",
        "coverage_description",
        "access_conditions",
        "bibliographic_reference",
        "resource_identity",
        "discovery_method",
        "updated_on",
    )
    language: Annotated[str, Field(pattern=r"^[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*$")] | None = None
    coverage_description: Text | None = None
    access_conditions: Text | None = None
    bibliographic_reference: Text | None = None
    resource_identity: Text | None = None
    discovery_method: Literal["system_recommendation", "ai_discovery", "user_added"] | None = None
    updated_on: date | None = None

    kind: Literal["source"] = "source"
    source_kind: Literal[
        "institution",
        "academic_organization",
        "open_textbook",
        "database",
        "reference",
        "technical_documentation",
        "taxonomy",
        "local_document",
        "book",
        "paper",
        "website",
        "other",
    ]
    creator: Text | None = None
    uri: HttpUrl | None = None
    local_path: Text | None = None
    published_at: date | None = None
    license: Text | None = None
    version_tag: Text | None = None
    content_hash: Digest | None = None


class Category(Labeled):
    kind: Literal["category"] = "category"
    slug: Annotated[str, Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")]
    description: Text


class DomainCategory(Contract):
    kind: Literal["domain_category"] = "domain_category"
    domain_id: EntityID
    category_id: EntityID
    rationale: Text


class Topic(Labeled):
    kind: Literal["topic"] = "topic"
    description: Text


class Concept(Labeled):
    kind: Literal["concept"] = "concept"
    description: Text
    # Catalog descriptions are not validated Definitions or Claims.


class DomainRelation(Contract):
    kind: Literal["domain_relation"] = "domain_relation"
    from_domain_id: EntityID
    to_domain_id: EntityID
    predicate: Literal[
        "SUBDOMAIN_OF",
        "OVERLAPS_WITH",
        "DRAWS_ON",
        "USES_METHODS_FROM",
        "APPLIES_KNOWLEDGE_FROM",
        "RELATED_CONTEXT",
        "REFERENCES_PRESET",
        "RELATED_TO",
        "APPLIES_TO",  # Legacy only; no silent direction/meaning conversion.
    ]
    rationale: Text

    @model_validator(mode="after")
    def endpoints(self) -> Self:
        if self.from_domain_id == self.to_domain_id:
            raise ValueError("Self relations are invalid")
        if self.predicate in {"OVERLAPS_WITH", "RELATED_TO", "RELATED_CONTEXT"}:
            first, second = sorted((self.from_domain_id, self.to_domain_id))
            object.__setattr__(self, "from_domain_id", first)
            object.__setattr__(self, "to_domain_id", second)
        return self


class DomainSource(Contract):
    compatibility_fields = ("intended_learning_level",)
    intended_learning_level: Text | None = None
    kind: Literal["domain_source"] = "domain_source"
    domain_id: EntityID
    source_id: EntityID
    rationale: Text
    intended_use: Text
    authority_scope: Text
    limitations: Text


class DomainTopic(Contract):
    kind: Literal["domain_topic"] = "domain_topic"
    domain_id: EntityID
    topic_id: EntityID
    rationale: Text


class DomainConcept(Contract):
    kind: Literal["domain_concept"] = "domain_concept"
    domain_id: EntityID
    concept_id: EntityID
    rationale: Text


class TaxonomyEntry(Contract):
    """A native classification record pinned to a source release revision."""

    kind: Literal["taxonomy_entry"] = "taxonomy_entry"
    source_id: EntityID
    source_version: Annotated[int, Field(strict=True, ge=1)]
    release_tag: Text
    code: Text
    original_label: Text
    original_language: Text
    original_path: Text  # Publisher code path, a locator rather than local graph edges.


class DomainMapping(Contract):
    kind: Literal["domain_mapping"] = "domain_mapping"
    domain_id: EntityID
    taxonomy_entry_id: EntityID
    taxonomy_entry_version: Annotated[int, Field(strict=True, ge=1)]
    mapping_type: Literal["exact", "narrower_than", "broader_than", "related"]
    rationale: Text


Payload = Annotated[
    Domain
    | Source
    | Topic
    | Concept
    | DomainRelation
    | DomainSource
    | DomainTopic
    | DomainConcept
    | TaxonomyEntry
    | DomainMapping
    | Category
    | DomainCategory,
    Field(discriminator="kind"),
]


class EvidenceReference(Contract):
    source_id: EntityID
    source_version: Annotated[int, Field(strict=True, ge=1)]
    anchor: Text  # Stable local section/page/offset locator, never an inferred citation.


class Provenance(Contract):
    origin: Literal["human", "ai", "taxonomy_import", "test_fixture"]
    actor: Text
    rationale: Text
    generator: Text | None = None
    input_hash: Digest | None = None
    evidence: tuple[EvidenceReference, ...] = ()
    unsupported_reason: Text | None = None

    @model_validator(mode="after")
    def support(self) -> Self:
        if not self.evidence and not self.unsupported_reason:
            raise ValueError("Evidence or an explicit unsupported reason is required")
        if len(self.evidence) != len(set(self.evidence)):
            raise ValueError("Duplicate evidence references")
        return self


class Candidate(Contract):
    schema_version: Literal[1] = 1
    payload: Payload
    provenance: Provenance


class Revision(Contract):
    entity_id: EntityID
    version: Annotated[int, Field(strict=True, ge=1)]
    prior_version: int | None
    payload_hash: Digest
    recorded_at: AwareDatetime
    review_status: Literal["pending_review"] = "pending_review"
    candidate: Candidate


class ReviewRecord(Contract):
    """Append-only operator decision bound to an exact candidate version and hash."""

    entity_id: EntityID
    version: Annotated[int, Field(strict=True, ge=1)]
    payload_hash: Digest
    decision: Literal["approve", "reject", "revise", "defer"]
    reviewer: Text
    reason: Text
    recorded_at: AwareDatetime
    resulting_version: Annotated[int, Field(strict=True, ge=1)] | None = None

    @model_validator(mode="after")
    def revised_version(self) -> Self:
        if self.decision == "revise":
            if self.resulting_version != self.version + 1:
                raise ValueError("Revise must identify the next pending version")
        elif self.resulting_version is not None:
            raise ValueError("Only revise identifies a resulting version")
        return self


class SourceCheck(Contract):
    source_id: EntityID
    source_version: Annotated[int, Field(strict=True, ge=1)]
    check_kind: Literal["accessibility", "authority", "license"]
    outcome: Literal["confirmed", "failed", "inconclusive"]
    checked_at: AwareDatetime
    method: Text
    actor: Text
    locator: Text
    evidence_note: Text
