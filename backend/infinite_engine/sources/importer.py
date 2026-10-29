"""Atomic metadata-only import into the shared local registry."""

import json
from datetime import UTC, datetime

from infinite_engine.catalog.bundles import CandidateBundle, digest_json, import_bundle
from infinite_engine.catalog.storage import Registry, RegistryError, VersionConflict
from infinite_engine.sources.contracts import (
    AcquisitionPlan,
    ArtifactEntry,
    Pin,
    SearchProfile,
    SourceAnchor,
    SourceAssociations,
    SourceCandidates,
    SourceDocument,
    SourceResource,
)


def get_artifact(registry: Registry, pin: Pin) -> ArtifactEntry:
    row = registry._db.execute(
        "SELECT snapshot FROM source_artifact WHERE id=? AND version=?", (pin.id, pin.version)
    ).fetchone()
    if row is None:
        raise RegistryError(f"Missing artifact revision: {pin.id}@{pin.version}")
    return ArtifactEntry.model_validate_json(row[0])


def artifact_references(entry: ArtifactEntry) -> tuple[tuple[Pin, str], ...]:
    payload = entry.payload
    if isinstance(payload, SourceResource) and payload.provider:
        return ((payload.provider, "source_provider"),)
    if isinstance(payload, SourceDocument):
        return ((payload.resource, "source_resource"),)
    if isinstance(payload, SourceAnchor):
        return ((payload.document, "source_document"),)
    return ()


def _save_artifact(registry: Registry, entry: ArtifactEntry) -> None:
    db = registry._db
    snapshot = entry.model_dump_json()
    digest = digest_json(entry.model_dump(mode="json"))
    prior = db.execute(
        "SELECT payload_hash FROM source_artifact WHERE id=? AND version=?",
        (entry.id, entry.version),
    ).fetchone()
    if prior:
        if prior[0] != digest:
            raise VersionConflict("Artifact revision already exists with different content")
        return
    latest = db.execute(
        "SELECT max(version) FROM source_artifact WHERE id=?", (entry.id,)
    ).fetchone()[0]
    if latest is not None and entry.version != latest + 1:
        raise VersionConflict("Artifact revision must follow the latest version")
    if latest is None and entry.version != 1 and not isinstance(entry.payload, SourceResource):
        raise VersionConflict("New artifacts start at version 1")
    payload = entry.payload
    if isinstance(payload, SourceResource):
        if payload.source != Pin(id=entry.id, version=entry.version):
            raise RegistryError("Resource sidecar must match its existing Source identity/version")
        if registry.get(entry.id, entry.version).candidate.payload.kind != "source":
            raise RegistryError("Resource requires a Source")
    for pin, kind in artifact_references(entry):
        target = get_artifact(registry, pin)
        if target.payload.kind != kind:
            raise RegistryError("Wrong artifact reference type")
        if isinstance(payload, SourceAnchor):
            document = target.payload
            assert isinstance(document, SourceDocument)
            if document.content_hash != payload.content_hash:
                raise RegistryError("Anchor hash differs from exact document revision")
            allowed = {
                "web": {"web", "text"},
                "pdf": {"pdf", "text", "image"},
                "text": {"text"},
                "csv": {"structured"},
                "json": {"structured"},
                "xml": {"structured"},
                "api_metadata": {"structured"},
                "image": {"image"},
            }
            if payload.locator.kind not in allowed[document.adapter]:
                raise RegistryError("Anchor locator incompatible with document adapter")
    for evidence in entry.provenance.evidence:
        if (
            registry.get(evidence.source_id, evidence.source_version).candidate.payload.kind
            != "source"
        ):
            raise RegistryError("Provenance must reference a Source revision")
    db.execute(
        "INSERT INTO source_artifact VALUES (?,?,?,?,?,?)",
        (
            entry.id,
            entry.version,
            payload.kind,
            snapshot,
            digest,
            datetime.now(UTC).isoformat(),
        ),
    )
    db.executemany(
        "INSERT INTO source_artifact_reference VALUES (?,?,?,?)",
        [(entry.id, entry.version, pin.id, pin.version) for pin, _ in artifact_references(entry)],
    )
    if isinstance(payload, SourceResource):
        db.execute("INSERT INTO source_resource_revision VALUES (?,?)", (entry.id, entry.version))


def import_sources(
    registry: Registry,
    candidates: SourceCandidates,
    associations: SourceAssociations | None = None,
    *,
    apply: bool = False,
) -> None:
    """Dry run by default. No file/network access, acceptance, checks or review writes."""
    candidates = SourceCandidates.model_validate_json(candidates.model_dump_json())
    if associations is not None:
        associations = SourceAssociations.model_validate_json(associations.model_dump_json())
    value = [
        candidates.model_dump(mode="json"),
        associations.model_dump(mode="json") if associations else None,
    ]
    digest = digest_json(value)
    with registry.transaction(dry_run=not apply):
        prior = registry._db.execute(
            "SELECT payload_hash FROM source_manifest WHERE batch_id=?", (candidates.batch_id,)
        ).fetchone()
        if prior:
            if prior[0] != digest:
                raise RegistryError("Source batch ID already bound to different content")
            return
        if candidates.sources:
            import_bundle(
                registry,
                CandidateBundle(
                    batch_id=f"source-discovery:{candidates.batch_id}",
                    entries=candidates.sources,
                ),
                apply=True,
            )
        pending = {(e.id, e.version): e for e in candidates.artifacts}
        if len(pending) != len(candidates.artifacts):
            raise RegistryError("Duplicate artifact revision")
        while pending:
            ready = [
                key
                for key, entry in pending.items()
                if not any(
                    (pin.id, pin.version) in pending for pin, _ in artifact_references(entry)
                )
                and (entry.id, entry.version - 1) not in pending
            ]
            if not ready:
                raise RegistryError("Circular artifact references")
            for key in sorted(ready):
                _save_artifact(registry, pending.pop(key))
        if associations:
            import_bundle(
                registry,
                CandidateBundle(
                    batch_id=f"source-associations:{associations.batch_id}",
                    entries=associations.associations,
                ),
                apply=True,
            )

        registry._db.execute(
            "INSERT INTO source_manifest VALUES (?,?,?)",
            (
                candidates.batch_id,
                digest,
                json.dumps(value, ensure_ascii=False),
            ),
        )


def validate_plan(registry: Registry, profile: SearchProfile, plan: AcquisitionPlan) -> None:
    """Validate references and compatibility; never return execution authorization."""
    profile = SearchProfile.model_validate_json(profile.model_dump_json())
    plan = AcquisitionPlan.model_validate_json(plan.model_dump_json())
    if (plan.profile_id, plan.profile_revision) != (profile.profile_id, profile.revision):
        raise RegistryError("Acquisition plan refers to a different profile revision")
    if registry.get(profile.domain.id, profile.domain.version).candidate.payload.kind != "domain":
        raise RegistryError("Profile requires an exact Domain revision")
    for item in plan.items:
        document = get_artifact(registry, item.document).payload
        if not isinstance(document, SourceDocument) or document.adapter not in profile.adapters:
            raise RegistryError("Plan document is incompatible with profile")
        resource = get_artifact(registry, document.resource).payload
        assert isinstance(resource, SourceResource)
        if item.action in {"download", "use_local"}:
            if any(a.reuse != "permitted" for a in (document.access, resource.access)):
                raise RegistryError(
                    "Unknown/restricted reuse requires resolution before acquisition"
                )
        if item.action == "download":
            if not profile.network_requested or plan.max_requests > profile.max_requests:
                raise RegistryError("Download proposal exceeds profile network budget")
            if resource.provider is None or resource.provider.id not in profile.provider_allowlist:
                raise RegistryError("Provider outside profile allowlist")
            if any(a.availability != "public" for a in (document.access, resource.access)):
                raise RegistryError("Download requires public accessibility metadata")
