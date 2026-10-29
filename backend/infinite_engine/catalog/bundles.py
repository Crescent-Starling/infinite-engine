"""Atomic offline candidate bundles. Importing candidates never approves them."""

import hashlib
import json
from datetime import UTC, datetime
from typing import Annotated, Literal

from pydantic import Field, field_validator

from infinite_engine.catalog.contracts import Candidate, Contract, Revision, Text
from infinite_engine.catalog.ids import stable_id
from infinite_engine.catalog.storage import Registry, RegistryError


class BundleEntry(Contract):
    identity_key: Text
    expected_version: Annotated[int, Field(strict=True, ge=0)] = 0
    candidate: Candidate

    @field_validator("identity_key", mode="before")
    @classmethod
    def unchanged_key(cls, value: object) -> object:
        if not isinstance(value, str) or value != value.strip():
            raise ValueError(
                "identity_key must be an unpadded string; identity is never silently edited"
            )
        return value

    @property
    def entity_id(self) -> str:
        return stable_id(self.candidate.payload.kind, self.identity_key)


class CandidateBundle(Contract):
    format_version: Literal[1] = 1
    batch_id: Text
    entries: Annotated[tuple[BundleEntry, ...], Field(min_length=1)]


def digest_json(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(encoded.encode()).hexdigest()


def references(candidate: Candidate) -> set[str]:
    values = candidate.payload.model_dump()
    names = ("domain_id", "from_domain_id", "to_domain_id", "source_id", "topic_id", "concept_id")
    return {values[name] for name in names if name in values} | {
        item.source_id for item in candidate.provenance.evidence
    }


def import_bundle(
    registry: Registry, bundle: CandidateBundle, *, apply: bool = False
) -> tuple[Revision, ...]:
    bundle = CandidateBundle.model_validate_json(bundle.model_dump_json())
    entries = {entry.entity_id: entry for entry in bundle.entries}
    if len(entries) != len(bundle.entries):
        raise RegistryError("Bundle contains duplicate identities")
    content_hash = digest_json([entries[key].model_dump(mode="json") for key in sorted(entries)])
    db = registry._db
    with registry.transaction(dry_run=not apply):
        prior = db.execute(
            "SELECT content_hash FROM candidate_batch WHERE id=?", (bundle.batch_id,)
        ).fetchone()
        if prior:
            if prior[0] != content_hash:
                raise RegistryError("Batch ID already exists with different content")
            return tuple(
                registry.get(row[0], row[1])
                for row in db.execute(
                    "SELECT entity_id,version FROM candidate_batch_item "
                    "WHERE batch_id=? ORDER BY entity_id",
                    (bundle.batch_id,),
                )
            )
        saved: list[Revision] = []
        while entries:
            ready = [
                key
                for key in sorted(entries)
                if not (references(entries[key].candidate) & entries.keys())
            ]
            if not ready:
                raise RegistryError("Bundle has circular/self-referential dependencies")
            for key in ready:
                entry = entries.pop(key)
                saved.append(
                    registry.save(
                        entry.identity_key, entry.candidate, expected_version=entry.expected_version
                    )
                )
        db.execute(
            "INSERT INTO candidate_batch VALUES (?,?,?)",
            (bundle.batch_id, content_hash, datetime.now(UTC).isoformat()),
        )
        db.executemany(
            "INSERT INTO candidate_batch_item VALUES (?,?,?)",
            [(bundle.batch_id, item.entity_id, item.version) for item in saved],
        )
        return tuple(sorted(saved, key=lambda item: item.entity_id))
