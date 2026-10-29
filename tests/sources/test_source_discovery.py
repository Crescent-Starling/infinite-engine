"""Offline source interchange, migration, citations and update safety."""

import hashlib
import json
import sqlite3
from importlib.resources import files
from pathlib import Path
from typing import Any

import pytest
import yaml
from infinite_engine.catalog.bundles import CandidateBundle, import_bundle
from infinite_engine.catalog.ids import stable_id
from infinite_engine.catalog.storage import Registry, RegistryError, VersionConflict
from infinite_engine.sources.adapters import ParseIssue, ParseResult
from infinite_engine.sources.contracts import (
    AcquisitionPlan,
    ArtifactEntry,
    Pin,
    SearchProfile,
    SourceAssociations,
    SourceCandidates,
)
from infinite_engine.sources.importer import get_artifact, import_sources, validate_plan
from infinite_engine.sources.io import FORMATS, load_manifest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "examples/sources"


def manifest(name: str = "astronomy") -> SourceCandidates:
    return SourceCandidates.model_validate_json(
        (EXAMPLES / name / "source_candidates.json").read_text()
    )


def domains(db: Registry) -> None:
    import_bundle(
        db, CandidateBundle.model_validate_json((EXAMPLES / "domains.json").read_text()), apply=True
    )


@pytest.mark.parametrize("name", ["astronomy", "latin", "fitness-nutrition", "stellaris"])
def test_examples_schema_import_replay_restart(tmp_path: Path, name: str) -> None:
    folder = EXAMPLES / name
    for filename, model in FORMATS.items():
        schema = json.loads((ROOT / "schemas/sources" / f"{filename}.schema.json").read_text())
        Draft202012Validator.check_schema(schema)
        value = load_manifest(folder / filename)
        Draft202012Validator(schema).validate(value.model_dump(mode="json"))
        assert schema == {
            **model.model_json_schema(),
            "$schema": "https://json-schema.org/draft/2020-12/schema",
        }
    candidates = manifest(name)
    associations = SourceAssociations.model_validate_json(
        (folder / "source_associations.json").read_text()
    )
    profile = SearchProfile.model_validate(
        yaml.safe_load((folder / "search_profile.yaml").read_text())
    )
    plan = AcquisitionPlan.model_validate(
        yaml.safe_load((folder / "acquisition_plan.yaml").read_text())
    )
    path = tmp_path / "db.sqlite"
    with Registry(path) as db:
        domains(db)
        import_sources(db, candidates, associations)
        assert db._db.execute("SELECT count(*) FROM source_artifact").fetchone()[0] == 0
        import_sources(db, candidates, associations, apply=True)
        import_sources(db, candidates, associations, apply=True)
        validate_plan(db, profile, plan)
        assert db._db.execute("SELECT count(*) FROM source_artifact").fetchone()[0] == 3
        for table in (
            "source_check",
            "review_record",
            "knowledge_space_source",
            "curated_revision",
        ):
            assert db._db.execute(f"SELECT count(*) FROM {table}").fetchone()[0] == 0
    with Registry(path) as db:
        assert get_artifact(db, plan.items[0].document).payload.kind == "source_document"
        assert not db._db.execute("PRAGMA foreign_key_check").fetchall()


def test_conflicts_rollback_and_provenance(tmp_path: Path) -> None:
    original = manifest()
    with Registry(tmp_path / "db.sqlite") as db:
        bad = original.model_dump(mode="json")
        bad["artifacts"][-1]["payload"]["resource"]["version"] = 99
        with pytest.raises(RegistryError):
            import_sources(db, SourceCandidates.model_validate(bad), apply=True)
        assert db._db.execute("SELECT count(*) FROM source").fetchone()[0] == 0
        import_sources(db, original, apply=True)
        bad = original.model_dump(mode="json")
        bad["artifacts"][0]["payload"]["name"] = "Changed"
        with pytest.raises(RegistryError, match="batch"):
            import_sources(db, SourceCandidates.model_validate(bad), apply=True)
        bad["batch_id"] = "different-batch"
        with pytest.raises(VersionConflict):
            import_sources(db, SourceCandidates.model_validate(bad), apply=True)
        bad["artifacts"][0]["version"] = 3
        with pytest.raises(VersionConflict):
            import_sources(db, SourceCandidates.model_validate(bad), apply=True)
        bad["artifacts"][0]["provenance"].pop("unsupported_reason")
        with pytest.raises(ValidationError):
            SourceCandidates.model_validate(bad)
        with pytest.raises(sqlite3.IntegrityError):
            db._db.execute("DELETE FROM source_artifact")


def test_anchor_exact_revision_hash_and_partial_result(tmp_path: Path) -> None:
    original = manifest("fitness-nutrition").model_dump(mode="json")
    document = original["artifacts"][-1]
    content = b"Mock text only."
    digest = hashlib.sha256(content).hexdigest()
    document["payload"].update(content_hash=digest, acquisition_state="available")
    anchor: dict[str, Any] = {
        "identity_key": "mock:anchor",
        "payload": {
            "kind": "source_anchor",
            "document": {
                "id": stable_id("source_document", document["identity_key"]),
                "version": 1,
            },
            "content_hash": digest,
            "locator": {"kind": "text", "section": "mock", "start": 0, "end": len(content)},
        },
        "provenance": document["provenance"],
    }
    original["artifacts"].insert(0, anchor)  # forward references are resolved
    with Registry(tmp_path / "db.sqlite") as db:
        import_sources(db, SourceCandidates.model_validate(original), apply=True)
        stored = get_artifact(db, Pin(id=stable_id("source_anchor", "mock:anchor"), version=1))
        assert stored.payload.model_dump()["content_hash"] == digest
        changed = json.loads(json.dumps(original))
        changed["batch_id"] = "new"
        changed["artifacts"] = [changed["artifacts"][0]]
        changed["artifacts"][0]["version"] = 2
        changed["artifacts"][0]["payload"]["content_hash"] = "0" * 64
        with pytest.raises(RegistryError, match="hash"):
            import_sources(db, SourceCandidates.model_validate(changed), apply=True)
        result = ParseResult(
            status="partial",
            anchors=(stored,),
            issues=(ParseIssue(locator="mock:second-block", message="Could not decode block"),),
        )
        assert result.anchors == (stored,) and result.issues
        anchor["payload"]["locator"]["end"] = 0
        with pytest.raises(ValidationError):
            ArtifactEntry.model_validate(anchor)


@pytest.mark.parametrize(
    "text",
    [
        "format_version: 1\nformat_version: 2",
        "a: &loop [*loop]",
        '!!python/object/apply:os.system ["echo unsafe"]',
    ],
)
def test_unsafe_yaml_rejected(tmp_path: Path, text: str) -> None:
    path = tmp_path / "search_profile.yaml"
    path.write_text(text)
    with pytest.raises((ValueError, yaml.YAMLError)):
        load_manifest(path)


def test_plan_does_not_turn_metadata_into_permission(tmp_path: Path) -> None:
    folder = EXAMPLES / "astronomy"
    profile = SearchProfile.model_validate(
        yaml.safe_load((folder / "search_profile.yaml").read_text())
    )
    raw = yaml.safe_load((folder / "acquisition_plan.yaml").read_text())
    raw["items"][0]["action"] = "download"
    with pytest.raises(ValidationError):
        AcquisitionPlan.model_validate(raw)
    raw["items"][0]["permission_evidence"] = "Caller assertion alone cannot override unknown rights"
    raw["max_requests"] = 1
    plan = AcquisitionPlan.model_validate(raw)
    with Registry(tmp_path / "db.sqlite") as db:
        domains(db)
        import_sources(db, manifest(), apply=True)
        with pytest.raises(RegistryError, match="reuse"):
            validate_plan(db, profile, plan)
        raw["profile_revision"] = 2
        with pytest.raises(RegistryError, match="profile revision"):
            validate_plan(db, profile, AcquisitionPlan.model_validate(raw))


def test_v4_migration_preserves_history(tmp_path: Path) -> None:
    path = tmp_path / "legacy.sqlite"
    with sqlite3.connect(path) as db:
        for number, name in enumerate(
            (
                "001_registry.sql",
                "002_review.sql",
                "003_taxonomy.sql",
                "004_domain_architecture.sql",
            ),
            1,
        ):
            sql = files("infinite_engine.catalog").joinpath("migrations", name).read_text()
            db.executescript(sql)
            db.execute(
                "INSERT INTO schema_migration VALUES (?,?)",
                (number, hashlib.sha256(sql.encode()).hexdigest()),
            )
            db.commit()
        db.execute("PRAGMA user_version=4")
        before = db.execute("SELECT * FROM schema_migration").fetchall()
    with Registry(path) as db:
        assert [
            tuple(r) for r in db._db.execute("SELECT * FROM schema_migration WHERE version<5")
        ] == before
        assert db._db.execute("PRAGMA user_version").fetchone()[0] == 5
        assert not db._db.execute("PRAGMA foreign_key_check").fetchall()


@pytest.mark.parametrize(
    "adapter,locator",
    [
        (
            "web",
            {
                "kind": "web",
                "url": "https://example.invalid/page",
                "selector": "#one",
                "quote": "Mock",
            },
        ),
        ("pdf", {"kind": "pdf", "page": 1}),
        ("text", {"kind": "text", "section": "one", "start": 0, "end": 4}),
        ("csv", {"kind": "structured", "syntax": "csv_row", "selector": "1", "field": "title"}),
        ("json", {"kind": "structured", "syntax": "json_pointer", "selector": "/title"}),
        ("xml", {"kind": "structured", "syntax": "xpath", "selector": "/item/title"}),
        ("api_metadata", {"kind": "structured", "syntax": "api_record", "selector": "record-1"}),
        (
            "image",
            {
                "kind": "image",
                "x": 0,
                "y": 0,
                "width": 10,
                "height": 10,
                "description": "Mock region",
                "description_origin": "human",
            },
        ),
    ],
)
def test_native_locator_persistence(adapter: str, locator: dict[str, Any]) -> None:
    raw = manifest().model_dump(mode="json")
    document = raw["artifacts"][-1]
    document["payload"].update(adapter=adapter, content_hash="a" * 64)
    raw["artifacts"].append(
        {
            "identity_key": "mock:locator",
            "payload": {
                "kind": "source_anchor",
                "content_hash": "a" * 64,
                "document": {
                    "id": stable_id("source_document", document["identity_key"]),
                    "version": 1,
                },
                "locator": locator,
            },
            "provenance": document["provenance"],
        }
    )
    with Registry(":memory:") as db:
        import_sources(db, SourceCandidates.model_validate(raw), apply=True)
        result = get_artifact(db, Pin(id=stable_id("source_anchor", "mock:locator"), version=1))
        assert result.payload.model_dump(mode="json")["locator"].items() >= locator.items()


def test_bad_association_rolls_back_all_artifacts() -> None:
    folder = EXAMPLES / "astronomy"
    associations = SourceAssociations.model_validate_json(
        (folder / "source_associations.json").read_text()
    )
    with Registry(":memory:") as db:
        with pytest.raises(RegistryError):
            import_sources(db, manifest(), associations, apply=True)  # no referenced Domain
        for table in ("source", "source_artifact", "candidate_batch", "source_manifest"):
            assert db._db.execute(f"SELECT count(*) FROM {table}").fetchone()[0] == 0


def test_partial_failures_and_checked_locators_require_evidence() -> None:
    with pytest.raises(ValidationError):
        ParseResult(status="partial")
    with pytest.raises(ValidationError):
        ParseResult(status="complete", issues=(ParseIssue(locator="x", message="failed"),))
    raw = manifest().model_dump(mode="json")
    raw["sources"][0]["candidate"]["payload"]["verified"] = True
    with pytest.raises(ValidationError):
        SourceCandidates.model_validate(raw)
    schema = SourceCandidates.model_json_schema()
    from jsonschema.exceptions import ValidationError as SchemaError

    with pytest.raises(SchemaError):
        Draft202012Validator(schema).validate(raw)
