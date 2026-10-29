"""Replay pinned pilot suggestions and a small taxonomy excerpt, entirely offline."""

import argparse
import hashlib
import json
import sqlite3
import tempfile
from collections import Counter
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field

from infinite_engine.catalog.bundles import BundleEntry, CandidateBundle, import_bundle
from infinite_engine.catalog.contracts import (
    Candidate,
    Contract,
    Digest,
    DomainMapping,
    EvidenceReference,
    Provenance,
    TaxonomyEntry,
    Text,
)
from infinite_engine.catalog.ids import stable_id
from infinite_engine.catalog.storage import Registry, RegistryError


class InputFile(Contract):
    path: Text
    sha256: Digest


class ExtensionRequirement(Contract):
    domain_key: Text
    requirement: Text
    status: Literal["not_implemented"] = "not_implemented"
    reason: Text


class Manifest(Contract):
    adapter_version: Literal["pilot-v1"]
    schema_version: Literal[1]
    batch_id: Text
    suggestions: InputFile
    taxonomy: InputFile
    pilot_domain_keys: Annotated[tuple[Text, ...], Field(min_length=4, max_length=4)]
    unmapped: dict[str, Text]
    extensions: tuple[ExtensionRequirement, ...]


class NativeEntry(Contract):
    code: Text
    label: Text
    language: Text
    path: Text
    anchor: Text


class MappingSuggestion(Contract):
    domain_key: Text
    code: Text
    mapping_type: Literal["exact", "narrower_than", "broader_than", "related"]
    rationale: Text


class TaxonomyExcerpt(Contract):
    source_key: Text
    source_version: Annotated[int, Field(strict=True, ge=1)]
    release_tag: Text
    attribution: Text
    license: Text
    license_locator: Text
    entries: Annotated[tuple[NativeEntry, ...], Field(min_length=1)]
    mappings: tuple[MappingSuggestion, ...]


class Suggestions(Contract):
    entries: Annotated[tuple[BundleEntry, ...], Field(min_length=1)]


def native_identity(source_key: str, release_tag: str, code: str) -> str:
    """Unambiguous tuple encoding; punctuation in native codes cannot collide."""
    return json.dumps([source_key, release_tag, code], ensure_ascii=False, separators=(",", ":"))


def read_pinned(root: Path, item: InputFile) -> bytes:
    path = (root / item.path).resolve()
    if not path.is_relative_to(root.resolve()) or Path(item.path).is_absolute():
        raise RegistryError("Input paths must stay within the manifest directory")
    content = path.read_bytes()
    if hashlib.sha256(content).hexdigest() != item.sha256:
        raise RegistryError(f"Input checksum mismatch: {item.path}")
    return content


def build(manifest_path: Path) -> tuple[CandidateBundle, dict[str, object]]:
    manifest = Manifest.model_validate_json(manifest_path.read_bytes())
    raw = read_pinned(manifest_path.parent, manifest.suggestions)
    suggestions = Suggestions.model_validate_json(raw)
    taxonomy = TaxonomyExcerpt.model_validate_json(
        read_pinned(manifest_path.parent, manifest.taxonomy)
    )
    entries = []
    for entry in suggestions.entries:
        # Record the exact saved suggestion artifact; retain its original provenance fields.
        provenance = entry.candidate.provenance.model_copy(
            update={
                "input_hash": entry.candidate.provenance.input_hash or manifest.suggestions.sha256
            }
        )
        entries.append(
            entry.model_copy(
                update={"candidate": entry.candidate.model_copy(update={"provenance": provenance})}
            )
        )
    codes = {entry.code: entry for entry in taxonomy.entries}
    if len(codes) != len(taxonomy.entries):
        raise RegistryError("Duplicate native taxonomy code")
    source_id = stable_id("source", taxonomy.source_key)
    for native in taxonomy.entries:
        key = native_identity(taxonomy.source_key, taxonomy.release_tag, native.code)
        entries.append(
            BundleEntry(
                identity_key=key,
                candidate=Candidate(
                    payload=TaxonomyEntry(
                        source_id=source_id,
                        source_version=taxonomy.source_version,
                        release_tag=taxonomy.release_tag,
                        code=native.code,
                        original_label=native.label,
                        original_language=native.language,
                        original_path=native.path,
                    ),
                    provenance=Provenance(
                        origin="taxonomy_import",
                        actor="pilot-v1",
                        rationale=f"Selected native metadata. {taxonomy.attribution}",
                        input_hash=manifest.taxonomy.sha256,
                        evidence=(
                            EvidenceReference(
                                source_id=source_id,
                                source_version=taxonomy.source_version,
                                anchor=native.anchor,
                            ),
                        ),
                    ),
                ),
            )
        )
    for mapping in taxonomy.mappings:
        if mapping.code not in codes:
            raise RegistryError(f"Unknown native code: {mapping.code}")
        native_key = native_identity(taxonomy.source_key, taxonomy.release_tag, mapping.code)
        entries.append(
            BundleEntry(
                identity_key=json.dumps([mapping.domain_key, native_key], separators=(",", ":")),
                candidate=Candidate(
                    payload=DomainMapping(
                        domain_id=stable_id("domain", mapping.domain_key),
                        taxonomy_entry_id=stable_id("taxonomy_entry", native_key),
                        taxonomy_entry_version=1,
                        mapping_type=mapping.mapping_type,
                        rationale=mapping.rationale,
                    ),
                    provenance=Provenance(
                        origin="ai",
                        actor="Codex",
                        generator="saved R3 mapping suggestions",
                        rationale="Candidate correspondence; no publisher endorsement.",
                        input_hash=manifest.taxonomy.sha256,
                        evidence=(
                            EvidenceReference(
                                source_id=source_id,
                                source_version=taxonomy.source_version,
                                anchor=codes[mapping.code].anchor,
                            ),
                        ),
                        unsupported_reason=(
                            "Semantic fit requires human review; citation identifies target only."
                        ),
                    ),
                ),
            )
        )
    bundle = CandidateBundle(
        batch_id=manifest.batch_id,
        entries=tuple(sorted(entries, key=lambda entry: entry.entity_id)),
    )
    pilot = set(manifest.pilot_domain_keys)
    domain_keys = {e.identity_key for e in entries if e.candidate.payload.kind == "domain"}
    mapped = {m.domain_key for m in taxonomy.mappings}
    if len(pilot) != 4 or not pilot <= domain_keys:
        raise RegistryError("Pilot must identify four distinct existing domains")
    if mapped & manifest.unmapped.keys() or mapped | manifest.unmapped.keys() != pilot:
        raise RegistryError("Every pilot domain needs mappings or an explicit unmapped reason")
    if {item.domain_key for item in manifest.extensions} != pilot:
        raise RegistryError("Each pilot domain needs extension requirements")
    # Use the real importer for all graph/FK/duplicate checks before emitting any artifacts.
    with Registry(Path(":memory:")) as registry:
        import_bundle(registry, bundle)
    categories = Counter(
        e.candidate.payload.source_kind for e in entries if e.candidate.payload.kind == "source"
    )
    report: dict[str, object] = {
        "adapter_version": manifest.adapter_version,
        "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "inputs": {
            "suggestions": manifest.suggestions.sha256,
            "taxonomy": manifest.taxonomy.sha256,
        },
        "counts": dict(sorted(Counter(e.candidate.payload.kind for e in entries).items())),
        "source_categories": dict(sorted(categories.items())),
        "pilot_domain_keys": sorted(pilot),
        "unmapped": manifest.unmapped,
        "extensions": [item.model_dump() for item in manifest.extensions],
        "review_status": "pending_review",
        "source_checks": "none",
        "seed_ready": False,
        "learning_ready": False,
    }
    return bundle, report


def encoded(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def write_bootstrap(manifest: Path, output: Path) -> dict[str, object]:
    bundle, report = build(manifest)
    if output.exists():
        raise RegistryError("Output already exists; use a fresh directory")
    output.parent.mkdir(parents=True, exist_ok=True)
    # Publish only a complete, validated output directory on the same filesystem.
    with tempfile.TemporaryDirectory(dir=output.parent) as temporary:
        stage = Path(temporary) / "result"
        stage.mkdir()
        (stage / "candidates.json").write_text(
            encoded(bundle.model_dump(mode="json")), encoding="utf-8"
        )
        (stage / "report.json").write_text(encoded(report), encoding="utf-8")
        stage.rename(output)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(encoded(write_bootstrap(args.manifest, args.output)), end="")
    except (OSError, ValueError, KeyError, sqlite3.Error) as exc:
        parser.exit(2, f"Bootstrap failed: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
