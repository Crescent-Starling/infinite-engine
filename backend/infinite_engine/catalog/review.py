"""Explicit, exact-revision human review with atomic curated projection updates."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from infinite_engine.catalog.bundles import digest_json, references
from infinite_engine.catalog.contracts import (
    Candidate,
    Contract,
    DomainRelation,
    ReviewRecord,
    Revision,
)
from infinite_engine.catalog.review_csv import read_review
from infinite_engine.catalog.storage import Registry, RegistryError, VersionConflict


class CuratedEntry(Contract):
    status: Literal["approved"] = "approved"
    revision: Revision
    review: ReviewRecord


def curated_entries(registry: Registry) -> tuple[CuratedEntry, ...]:
    result = []
    for row in registry._db.execute(
        "SELECT r.* FROM current_curated c JOIN review_record r ON r.id=c.review_id "
        "ORDER BY c.entity_id"
    ):
        values = dict(row)
        values.pop("id")
        result.append(
            CuratedEntry(
                revision=registry.get(row["entity_id"], row["version"]),
                review=ReviewRecord.model_validate(values),
            )
        )
    return tuple(result)


def review_state(registry: Registry, entity_id: str, version: int) -> str:
    registry.get(entity_id, version)
    row = registry._db.execute(
        "SELECT decision FROM review_record WHERE entity_id=? AND version=? "
        "ORDER BY id DESC LIMIT 1",
        (entity_id, version),
    ).fetchone()
    return (
        {"approve": "approved", "reject": "rejected", "revise": "revised", "defer": "deferred"}.get(
            row[0], "pending_review"
        )
        if row
        else "pending_review"
    )


def _validate_curated(registry: Registry, approved: list[Revision]) -> None:
    """Validate the effective approved graph, not the unrelated latest candidate graph."""
    effective = {entry.revision.entity_id: entry.revision for entry in curated_entries(registry)}
    effective.update({item.entity_id: item for item in approved})
    approved_versions = {
        (row[0], row[1])
        for row in registry._db.execute("SELECT entity_id,version FROM curated_revision")
    }
    approved_versions.update((item.entity_id, item.version) for item in approved)
    signatures: set[tuple[object, ...]] = set()
    parents: dict[str, list[str]] = {}
    for item in effective.values():
        missing = references(item.candidate) - effective.keys()
        if missing:
            raise RegistryError(f"Approval dependency closure missing: {sorted(missing)}")
        for evidence in item.candidate.provenance.evidence:
            if (evidence.source_id, evidence.source_version) not in approved_versions:
                raise RegistryError("Evidence source revision must be explicitly approved")
        payload = item.candidate.payload
        values = payload.model_dump()
        if payload.kind == "taxonomy_entry":
            if (payload.source_id, payload.source_version) not in approved_versions:
                raise RegistryError("Taxonomy source revision must be explicitly approved")
        if payload.kind == "domain_mapping":
            if (payload.taxonomy_entry_id, payload.taxonomy_entry_version) not in approved_versions:
                raise RegistryError("Taxonomy entry revision must be explicitly approved")
        if payload.kind == "domain_relation" and payload.predicate == "REFERENCES_PRESET":
            source = effective[payload.from_domain_id].candidate.payload
            target = effective[payload.to_domain_id].candidate.payload
            if (
                source.kind != "domain"
                or target.kind != "domain"
                or source.origin != "custom"
                or target.origin != "preset"
            ):
                raise RegistryError("Curated REFERENCES_PRESET requires custom to preset")
        keys = {
            "taxonomy_entry": ("source_id", "release_tag", "code"),
            "domain_mapping": ("domain_id", "taxonomy_entry_id"),
            "category": ("slug",),
            "domain_category": ("domain_id", "category_id"),
            "domain": ("slug",),
            "source": ("resource_identity",) if values.get("resource_identity") else (),
            "domain_relation": ("from_domain_id", "predicate", "to_domain_id"),
            "domain_source": ("domain_id", "source_id"),
            "domain_topic": ("domain_id", "topic_id"),
            "domain_concept": ("domain_id", "concept_id"),
        }.get(payload.kind)
        if keys:
            signature = (payload.kind, *(values[key] for key in keys))
            if signature in signatures:
                raise RegistryError("Curated projection would contain a semantic duplicate")
            signatures.add(signature)
        if isinstance(payload, DomainRelation) and payload.predicate == "SUBDOMAIN_OF":
            parents.setdefault(payload.from_domain_id, []).append(payload.to_domain_id)
    for child in parents:
        stack, seen = list(parents[child]), set()
        while stack:
            node = stack.pop()
            if node == child:
                raise RegistryError("Curated classification would contain a cycle")
            if node not in seen:
                seen.add(node)
                stack.extend(parents.get(node, []))


def apply_review(
    registry: Registry, directory: Path, *, actor: str, apply: bool = False
) -> dict[str, object]:
    """The local operator explicitly supplies actor; CSV alone is not authorization."""
    if not actor.strip() or actor != actor.strip():
        raise RegistryError("Explicit nonblank actor is required")
    export_id, rows = read_review(registry, directory)
    content_hash = digest_json(
        {
            "export_id": export_id,
            "actor": actor,
            "rows": [
                {key: value for key, value in row.items() if key != "location"} for row in rows
            ],
        }
    )
    db = registry._db
    with registry.transaction(dry_run=not apply):
        prior = db.execute(
            "SELECT result_json FROM review_receipt WHERE content_hash=?", (content_hash,)
        ).fetchone()
        if prior:
            return {**json.loads(prior[0]), "replayed": True}
        actions: list[dict[str, object]] = []
        approved: list[Revision] = []
        records: list[ReviewRecord] = []
        for row in rows:
            decision = row["decision"]
            original = registry.get(row["entity_id"], int(row["version"]))
            proposed = Candidate.model_validate_json(row["proposed_candidate"])
            changed = proposed.payload != original.candidate.payload
            if not decision:
                if changed or row["reviewer"] or row["reason"]:
                    raise RegistryError(
                        f"{row['location']}: edited row requires an explicit decision"
                    )
                continue
            if row["reviewer"] != actor:
                raise RegistryError(
                    f"{row['location']}: reviewer must match explicit operator actor"
                )
            if registry.get(original.entity_id).version != original.version:
                raise VersionConflict(
                    f"{row['location']}: stale export; re-export current revision"
                )
            if review_state(registry, original.entity_id, original.version) in {
                "approved",
                "rejected",
                "revised",
            }:
                raise RegistryError(f"{row['location']}: revision already has a terminal decision")
            if changed and decision != "revise":
                raise RegistryError(
                    f"{row['location']}: changed payload must use revise, then separate approval"
                )
            if decision == "revise" and not changed:
                raise RegistryError(f"{row['location']}: revise requires a changed payload")
            try:
                record = ReviewRecord(
                    entity_id=original.entity_id,
                    version=original.version,
                    payload_hash=original.payload_hash,
                    decision=decision,
                    reviewer=actor,
                    reason=row["reason"],
                    recorded_at=datetime.now(UTC),
                    resulting_version=original.version + 1 if decision == "revise" else None,
                )
            except ValueError as exc:
                raise RegistryError(f"{row['location']}: {exc}") from exc
            action: dict[str, object] = {
                "entity_id": original.entity_id,
                "version": original.version,
                "decision": record.decision,
                "changes": {},
            }
            if record.decision == "revise":
                before = original.candidate.payload.model_dump(mode="json")
                after = proposed.payload.model_dump(mode="json")
                action["changes"] = {
                    key: {"before": before.get(key), "after": after.get(key)}
                    for key in sorted(before.keys() | after.keys())
                    if before.get(key) != after.get(key)
                }
                provenance = original.candidate.provenance.model_dump()
                provenance.update(
                    origin="human",
                    actor=actor,
                    rationale=record.reason,
                    generator=None,
                    input_hash=original.payload_hash,
                )
                replacement = Candidate.model_validate(
                    {"payload": proposed.payload, "provenance": provenance}
                )
                identity_key = db.execute(
                    "SELECT identity_key FROM registry_entity WHERE id=?", (original.entity_id,)
                ).fetchone()[0]
                revision = registry.save(
                    identity_key, replacement, expected_version=original.version
                )
                action["resulting_version"] = revision.version
            elif record.decision == "approve":
                approved.append(original)
            records.append(record)
            actions.append(action)
        _validate_curated(registry, approved)
        for record in records:
            values = record.model_dump(mode="json")
            cursor = db.execute(
                f"INSERT INTO review_record ({','.join(values)}) "
                f"VALUES ({','.join('?' for _ in values)})",
                tuple(values.values()),
            )
            if record.decision == "approve":
                db.execute(
                    "INSERT INTO curated_revision VALUES (?,?,?)",
                    (record.entity_id, record.version, cursor.lastrowid),
                )
        result: dict[str, object] = {
            "export_id": export_id,
            "actions": actions,
            "approved_count": len(approved),
            "replayed": False,
        }
        if actions:
            db.execute(
                "INSERT INTO review_receipt VALUES (?,?,?,?,?)",
                (content_hash, export_id, actor, json.dumps(result), datetime.now(UTC).isoformat()),
            )
        return result
