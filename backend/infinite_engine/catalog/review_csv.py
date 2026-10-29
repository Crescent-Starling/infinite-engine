"""Lossless editable CSV packets backed by immutable export snapshots in the local DB."""

import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from infinite_engine.catalog.contracts import Candidate, Revision
from infinite_engine.catalog.storage import Registry, RegistryError

BASE_COLUMNS = ["entity_id", "version", "payload_hash", "decision", "reviewer", "reason"]


def cell(value: str) -> str:
    """Prefix potentially executable spreadsheet cells; double existing leading apostrophes."""
    if value.startswith(("'", "\t", "\r", "\n")) or value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def uncell(value: str) -> str:
    result = value[1:] if value.startswith("'") else value
    if cell(result) != value:
        raise RegistryError(
            "Unsafe or noncanonical spreadsheet cell; prefix formulas with apostrophe"
        )
    return result


def columns(revision: Revision) -> list[str]:
    payload = revision.candidate.payload
    names = type(payload).model_fields
    added = payload.compatibility_fields
    fields = [name for name in names if name != "kind" and name not in added] + list(added)
    return BASE_COLUMNS + [f"{side}.{name}" for name in fields for side in ("original", "proposed")]


def export_review(
    registry: Registry, directory: Path, entity_ids: tuple[str, ...] | None = None
) -> str:
    """Create a new directory; never overwrite a person's previously edited review packet."""
    db = registry._db
    with registry.transaction():
        ids = (
            entity_ids
            if entity_ids is not None
            else tuple(
                row[0]
                for row in db.execute("SELECT entity_id FROM latest_revision ORDER BY entity_id")
            )
        )
        if not ids or len(set(ids)) != len(ids):
            raise RegistryError("Export requires distinct, existing candidate IDs")
        revisions = [registry.get(entity_id) for entity_id in sorted(ids)]
        export_id = str(uuid4())
        grouped: dict[str, list[Revision]] = {}
        for item in revisions:
            grouped.setdefault(item.candidate.payload.kind, []).append(item)
        manifest = {
            "format_version": 1,
            "export_id": export_id,
            "files": [f"{kind}.csv" for kind in sorted(grouped)],
        }
        provenance = {
            item.entity_id: item.candidate.provenance.model_dump(mode="json") for item in revisions
        }
        directory.mkdir(parents=False, exist_ok=False)
        for kind, items in grouped.items():
            with (directory / f"{kind}.csv").open("w", encoding="utf-8-sig", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=columns(items[0]), lineterminator="\n")
                writer.writeheader()
                for item in items:
                    row = {
                        "entity_id": item.entity_id,
                        "version": str(item.version),
                        "payload_hash": item.payload_hash,
                        "decision": "",
                        "reviewer": "",
                        "reason": "",
                    }
                    data = item.candidate.payload.model_dump(mode="json")
                    for name in type(item.candidate.payload).model_fields:
                        value = data.get(name)
                        if name != "kind":
                            for side in ("original", "proposed"):
                                row[f"{side}.{name}"] = json.dumps(
                                    value, ensure_ascii=False, sort_keys=True
                                )
                    writer.writerow({key: cell(value) for key, value in row.items()})
        (directory / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        (directory / "provenance.json").write_text(
            json.dumps(provenance, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        db.execute(
            "INSERT INTO review_export VALUES (?,?,?)",
            (export_id, json.dumps(manifest, sort_keys=True), datetime.now(UTC).isoformat()),
        )
        db.executemany(
            "INSERT INTO review_export_item VALUES (?,?,?,?)",
            [(export_id, item.entity_id, item.version, item.payload_hash) for item in revisions],
        )
        return export_id


def read_review(registry: Registry, directory: Path) -> tuple[str, list[dict[str, str]]]:
    """Validate the entire packet before any writes; errors carry CSV filename and line."""
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8-sig"))
    if not isinstance(manifest, dict) or not isinstance(manifest.get("export_id"), str):
        raise RegistryError("Invalid manifest")
    export_id = manifest["export_id"]
    db = registry._db
    baseline = db.execute("SELECT manifest FROM review_export WHERE id=?", (export_id,)).fetchone()
    if baseline is None or manifest != json.loads(baseline[0]):
        raise RegistryError("Unknown or modified export manifest")
    expected = {
        row[0]: registry.get(row[0], row[1])
        for row in db.execute(
            "SELECT entity_id,version FROM review_export_item WHERE export_id=?", (export_id,)
        )
    }
    provenance = json.loads((directory / "provenance.json").read_text(encoding="utf-8-sig"))
    if provenance != {
        key: value.candidate.provenance.model_dump(mode="json") for key, value in expected.items()
    }:
        raise RegistryError("Protected provenance was modified")
    actual_files = {path.name for path in directory.glob("*.csv")}
    if actual_files != set(manifest["files"]):
        raise RegistryError("Review packet CSV files are missing or unexpected")
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    errors: list[str] = []
    for filename in manifest["files"]:
        kind = filename.removesuffix(".csv")
        template = next(
            value for value in expected.values() if value.candidate.payload.kind == kind
        )
        with (directory / filename).open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream, strict=True)
            full_columns = columns(template)
            added = template.candidate.payload.compatibility_fields
            legacy_columns = [
                name
                for name in full_columns
                if name.removeprefix("original.").removeprefix("proposed.") not in added
            ]
            has_new_metadata = any(
                name in item.candidate.payload.model_dump()
                for item in expected.values()
                if item.candidate.payload.kind == kind
                for name in added
            )
            allowed = [full_columns] if has_new_metadata else [full_columns, legacy_columns]
            if reader.fieldnames not in allowed:
                errors.append(f"{filename}:1: columns are missing, reordered or unexpected")
                continue
            try:
                for row in reader:
                    location = f"{filename}:{reader.line_num}"
                    try:
                        if None in row or any(value is None for value in row.values()):
                            raise RegistryError("Wrong cell count")
                        decoded = {key: uncell(value) for key, value in row.items()}
                        entity_id = decoded["entity_id"]
                        if entity_id in seen or entity_id not in expected:
                            raise RegistryError("Duplicate or unknown entity_id")
                        original = expected[entity_id]
                        if original.candidate.payload.kind != kind:
                            raise RegistryError("Wrong entity table")
                        if (
                            decoded["version"] != str(original.version)
                            or decoded["payload_hash"] != original.payload_hash
                        ):
                            raise RegistryError("Protected version/payload_hash was modified")
                        payload = original.candidate.payload.model_dump(mode="json")
                        proposed = {"kind": kind}
                        for column in reader.fieldnames:
                            if column.startswith("original."):
                                name = column.removeprefix("original.")
                                value = payload.get(name)
                                if json.loads(decoded[f"original.{name}"]) != value:
                                    raise RegistryError(f"Protected original.{name} was modified")
                                proposed[name] = json.loads(decoded[f"proposed.{name}"])
                        parsed = Candidate.model_validate(
                            {"payload": proposed, "provenance": original.candidate.provenance}
                        )
                        decoded["proposed_candidate"] = parsed.model_dump_json()
                        decoded["location"] = location
                        rows.append(decoded)
                        seen.add(entity_id)
                    except (ValueError, TypeError) as exc:
                        errors.append(f"{location}: {exc}")
            except csv.Error as exc:
                errors.append(f"{filename}:{reader.line_num}: {exc}")
    missing = set(expected) - seen
    if missing:
        errors.append(f"Missing/invalid rows for {len(missing)} exported entities")
    if errors:
        raise RegistryError("\n".join(errors))
    return export_id, sorted(rows, key=lambda row: row["entity_id"])
