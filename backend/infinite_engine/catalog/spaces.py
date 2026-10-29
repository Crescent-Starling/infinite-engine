"""Minimal local domain selection and source autonomy; no knowledge generation or UI."""

from datetime import UTC, datetime
from typing import Annotated, Literal

from pydantic import AwareDatetime, Field

from infinite_engine.catalog.contracts import (
    Candidate,
    Contract,
    Domain,
    EntityID,
    Provenance,
    Revision,
    Text,
)
from infinite_engine.catalog.ids import normalized_label, stable_id
from infinite_engine.catalog.review import curated_entries, review_state
from infinite_engine.catalog.storage import Registry, RegistryError


class KnowledgeSpace(Contract):
    id: EntityID
    domain_id: EntityID
    selected_domain_version: Annotated[int, Field(strict=True, ge=1)]
    created_at: AwareDatetime


class SourceChoice(Contract):
    space_id: EntityID
    source_id: EntityID
    source_version: Annotated[int, Field(strict=True, ge=1)]
    acceptance_state: Literal["accepted", "removed"]
    note: Text | None = None


class PersonalOverride(Contract):
    space_id: EntityID
    display_name: Text | None = None
    scope_note: Text | None = None


class DomainDiscoveryItem(Contract):
    revision: Revision
    metadata_review_status: str
    # Readiness has no writable promotion path in this foundation.
    seed_ready: Literal[False] = False
    learning_ready: Literal[False] = False


class LocalDomains:
    def __init__(self, registry: Registry) -> None:
        self.registry = registry

    def search(
        self, query: str, *, include_candidates: bool = False
    ) -> tuple[DomainDiscoveryItem, ...]:
        """Local normalized substring suggestions; no cross-user matching or automatic merge."""
        curated = {
            item.revision.entity_id: item.revision for item in curated_entries(self.registry)
        }
        result = []
        for row in self.registry._db.execute(
            "SELECT id FROM registry_entity WHERE kind='domain' ORDER BY id"
        ):
            latest = self.registry.get(row[0])
            # Approved preset defaults remain visible while a replacement is pending.
            is_preset = isinstance(latest.candidate.payload, Domain) and (
                latest.candidate.payload.origin == "preset"
            )
            revision = (
                curated.get(row[0], latest) if is_preset and not include_candidates else latest
            )
            domain = revision.candidate.payload
            if not isinstance(domain, Domain) or domain.origin is None:
                continue
            state = review_state(self.registry, revision.entity_id, revision.version)
            if domain.origin == "preset" and state != "approved":
                if not include_candidates or state in {"rejected", "revised", "deferred"}:
                    continue
            needle = normalized_label(query)
            if not needle or any(needle in normalized_label(label.text) for label in domain.labels):
                result.append(DomainDiscoveryItem(revision=revision, metadata_review_status=state))
        return tuple(result)

    def create_custom(self, key: str, domain: Domain, provenance: Provenance) -> Revision:
        if domain.origin != "custom" or domain.creation_method not in {"manual", "ai_assisted"}:
            raise RegistryError("Explicit custom origin and manual/AI-assisted creation required")
        entity_id = stable_id("domain", key)
        with self.registry.transaction():
            collision = self.registry._db.execute(
                "SELECT p.entity_id FROM domain p JOIN latest_revision r USING(entity_id,version) "
                "WHERE p.slug=? AND p.entity_id<>?",
                (domain.slug, entity_id),
            ).fetchone()
            if collision:
                # Slug collisions are separate from name suggestions; no identity is merged.
                domain = domain.model_copy(update={"slug": f"{domain.slug}-{entity_id[-12:]}"})
            return self.registry.save(
                key, Candidate(payload=domain, provenance=provenance), expected_version=0
            )

    def ensure_primary_space(
        self, domain_id: str, *, allow_candidate: bool = False
    ) -> KnowledgeSpace:
        with self.registry.transaction():
            self.registry._reference(domain_id, "domain")
            row = self.registry._db.execute(
                "SELECT * FROM knowledge_space WHERE domain_id=?", (domain_id,)
            ).fetchone()
            if row:
                return KnowledgeSpace.model_validate(dict(row))
            available = {
                item.revision.entity_id: item
                for item in self.search("", include_candidates=allow_candidate)
            }
            if domain_id not in available:
                raise RegistryError(
                    "Select a classified local domain or explicitly opt into candidates"
                )
            item = available[domain_id]
            space = KnowledgeSpace(
                id=stable_id("knowledge_space", f"primary:{domain_id}"),
                domain_id=domain_id,
                selected_domain_version=item.revision.version,
                created_at=datetime.now(UTC),
            )
            self.registry._db.execute(
                "INSERT INTO knowledge_space VALUES (?,?,?,?)",
                (space.id, domain_id, space.selected_domain_version, space.created_at.isoformat()),
            )
            return space

    def choose_source(self, choice: SourceChoice) -> None:
        """Explicit local acceptance never certifies source metadata or claims."""
        choice = SourceChoice.model_validate_json(choice.model_dump_json())
        with self.registry.transaction():
            self._space_exists(choice.space_id)
            self.registry._reference(choice.source_id, "source")
            self.registry.get(choice.source_id, choice.source_version)
            previous = self.registry._db.execute(
                "SELECT source_version,acceptance_state,note FROM knowledge_space_source "
                "WHERE space_id=? AND source_id=? ORDER BY id DESC LIMIT 1",
                (choice.space_id, choice.source_id),
            ).fetchone()
            values = (choice.source_version, choice.acceptance_state, choice.note)
            if previous and tuple(previous) == values:
                return
            self.registry._db.execute(
                "INSERT INTO knowledge_space_source "
                "(space_id,source_id,source_version,acceptance_state,note,recorded_at) "
                "VALUES (?,?,?,?,?,?)",
                (choice.space_id, choice.source_id, *values, datetime.now(UTC).isoformat()),
            )

    def save_override(self, override: PersonalOverride) -> None:
        override = PersonalOverride.model_validate_json(override.model_dump_json())
        with self.registry.transaction():
            self._space_exists(override.space_id)
            self.registry._db.execute(
                "INSERT INTO space_override (space_id,display_name,scope_note,recorded_at) "
                "VALUES (?,?,?,?)",
                (
                    override.space_id,
                    override.display_name,
                    override.scope_note,
                    datetime.now(UTC).isoformat(),
                ),
            )

    def _space_exists(self, space_id: str) -> None:
        if not self.registry._db.execute(
            "SELECT 1 FROM knowledge_space WHERE id=?", (space_id,)
        ).fetchone():
            raise RegistryError("Unknown Knowledge Space")
