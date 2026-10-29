import csv
import hashlib
import json
import shutil
import socket
import sqlite3
import subprocess
import sys
from importlib.resources import files
from pathlib import Path

import pytest
from infinite_engine.catalog.bootstrap import build, native_identity, write_bootstrap
from infinite_engine.catalog.bundles import import_bundle
from infinite_engine.catalog.contracts import Candidate, Concept, DomainMapping
from infinite_engine.catalog.ids import stable_id
from infinite_engine.catalog.review import apply_review, curated_entries
from infinite_engine.catalog.review_csv import export_review
from infinite_engine.catalog.storage import Registry, RegistryError
from pydantic import ValidationError

PILOT = Path(__file__).parents[2] / "data/domain_registry/pilot"


def copy_inputs(tmp_path: Path) -> Path:
    shutil.copytree(PILOT, tmp_path / "inputs")
    return tmp_path / "inputs/manifest.json"


def change_input(manifest: Path, name: str, value: object) -> None:
    data = json.dumps(value).encode()
    (manifest.parent / f"{name}.json").write_bytes(data)
    config = json.loads(manifest.read_text())
    config[name]["sha256"] = hashlib.sha256(data).hexdigest()
    manifest.write_text(json.dumps(config))


def test_offline_reproducible_and_pending(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def no_network(*args: object, **kwargs: object) -> None:
        raise AssertionError("Bootstrap must not access network")

    monkeypatch.setattr(socket, "create_connection", no_network)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    first, second = tmp_path / "first", tmp_path / "second"
    report = write_bootstrap(PILOT / "manifest.json", first)
    write_bootstrap(PILOT / "manifest.json", second)
    for name in ("candidates.json", "report.json"):
        assert (first / name).read_bytes() == (second / name).read_bytes()
    assert report["seed_ready"] is False and report["learning_ready"] is False
    assert report["review_status"] == "pending_review"
    assert report["source_checks"] == "none"
    bundle, _ = build(PILOT / "manifest.json")
    with Registry(tmp_path / "pilot.sqlite") as db:
        first_import = import_bundle(db, bundle, apply=True)
        assert first_import == import_bundle(db, bundle, apply=True)
        assert len(first_import) == 55
        assert not curated_entries(db)
        assert not db._db.execute("SELECT * FROM source_check").fetchall()
        assert all(item.review_status == "pending_review" for item in first_import)
        export_review(db, tmp_path / "review")
        assert (tmp_path / "review/domain_mapping.csv").exists()
        assert (tmp_path / "review/taxonomy_entry.csv").exists()
        assert apply_review(db, tmp_path / "review", actor="owner")["approved_count"] == 0


@pytest.mark.parametrize("mode", ["checksum", "truncated", "duplicate", "missing", "escape"])
def test_bad_inputs_emit_nothing(tmp_path: Path, mode: str) -> None:
    manifest = copy_inputs(tmp_path)
    config = json.loads(manifest.read_text())
    if mode == "checksum":
        (manifest.parent / "suggestions.json").write_text("{}")
    elif mode == "truncated":
        data = b'{"entries":['
        (manifest.parent / "suggestions.json").write_bytes(data)
        config["suggestions"]["sha256"] = hashlib.sha256(data).hexdigest()
        manifest.write_text(json.dumps(config))
    elif mode == "duplicate":
        value = json.loads((manifest.parent / "suggestions.json").read_text())
        value["entries"].append(value["entries"][0])
        change_input(manifest, "suggestions", value)
    elif mode == "missing":
        (manifest.parent / "taxonomy.json").unlink()
    else:
        config["suggestions"]["path"] = "../outside.json"
        manifest.write_text(json.dumps(config))
    output = tmp_path / "output"
    with pytest.raises((ValueError, OSError)):
        write_bootstrap(manifest, output)
    assert not output.exists()


def test_does_not_overwrite_output(tmp_path: Path) -> None:
    output = tmp_path / "output"
    output.mkdir()
    (output / "owner-notes").write_text("keep")
    with pytest.raises(RegistryError, match="already exists"):
        write_bootstrap(PILOT / "manifest.json", output)
    assert (output / "owner-notes").read_text() == "keep"


@pytest.mark.parametrize("mode", ["duplicate-code", "missing-code", "unmapped", "release"])
def test_taxonomy_input_validation(tmp_path: Path, mode: str) -> None:
    manifest = copy_inputs(tmp_path)
    taxonomy = json.loads((manifest.parent / "taxonomy.json").read_text())
    if mode == "duplicate-code":
        taxonomy["entries"].append(taxonomy["entries"][0])
    elif mode == "missing-code":
        taxonomy["mappings"][0]["code"] = "missing"
    elif mode == "unmapped":
        taxonomy["mappings"] = []
    else:
        taxonomy["release_tag"] = "wrong release"
    change_input(manifest, "taxonomy", taxonomy)
    with pytest.raises(RegistryError):
        build(manifest)


def test_shared_identity_multiparent_and_label_ambiguity(tmp_path: Path) -> None:
    bundle, report = build(PILOT / "manifest.json")
    with Registry(tmp_path / "pilot.sqlite") as db:
        import_bundle(db, bundle, apply=True)
        assert len(db.label_matches("concept", "en", "CASE")) == 2
        shared = stable_id("concept", "evidence-context")
        assert (
            db._db.execute(
                "SELECT count(*) FROM domain_concept WHERE concept_id=?", (shared,)
            ).fetchone()[0]
            == 2
        )
        fitness = stable_id("domain", "fitness-nutrition")
        assert (
            db._db.execute(
                "SELECT count(*) FROM domain_relation WHERE from_domain_id=? "
                "AND predicate='SUBDOMAIN_OF'",
                (fitness,),
            ).fetchone()[0]
            == 2
        )
    categories = report["source_categories"]
    assert isinstance(categories, dict)
    assert set(categories) == {
        "taxonomy",
        "institution",
        "academic_organization",
        "open_textbook",
        "reference",
        "database",
        "technical_documentation",
    }
    assert "stellaris" in report["unmapped"]  # type: ignore[operator]


@pytest.mark.parametrize(
    "extra",
    [
        {"image_region": [0, 0, 1, 1]},
        {"lemma": "synthetic", "morphology": {"case": "synthetic"}},
        {"quantity": 1, "unit": "synthetic", "population": "synthetic"},
        {"patch": "synthetic", "dlc": ["synthetic"], "platform": "synthetic"},
    ],
)
def test_extensions_are_explicitly_unsupported(extra: dict[str, object]) -> None:
    # These are probes, not facts: do not smuggle specialized assertions into catalog stubs.
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        Concept.model_validate(
            {
                "labels": [{"language": "en", "text": "Probe"}],
                "description": "Synthetic probe",
                **extra,
            }
        )


def test_mapping_revision_identity_and_duplicate_safety(tmp_path: Path) -> None:
    bundle, _ = build(PILOT / "manifest.json")
    with Registry(tmp_path / "db.sqlite") as db:
        import_bundle(db, bundle, apply=True)
        native = next(e for e in bundle.entries if e.candidate.payload.kind == "taxonomy_entry")
        mapping = next(e for e in bundle.entries if e.candidate.payload.kind == "domain_mapping")
        for field, value in (("code", "other"), ("release_tag", "other")):
            data = native.candidate.model_dump()
            data["payload"][field] = value
            with pytest.raises(RegistryError):
                db.save(native.identity_key, Candidate.model_validate(data), expected_version=1)
        with pytest.raises(RegistryError, match="duplicate"):
            db.save("duplicate", mapping.candidate, expected_version=0)
        data = mapping.candidate.model_dump()
        data["payload"]["taxonomy_entry_version"] = 999
        with pytest.raises(KeyError):
            db.save(mapping.identity_key, Candidate.model_validate(data), expected_version=1)
        data["payload"]["taxonomy_entry_version"] = 1
        data["payload"]["mapping_type"] = "invented"
        with pytest.raises(ValidationError):
            Candidate.model_validate(data)
        # Corrected native label is a new pending revision; mapping still pins the original.
        data = native.candidate.model_dump()
        data["payload"]["original_label"] = "Correction proposal"
        db.save(native.identity_key, Candidate.model_validate(data), expected_version=1)
        assert db.get(native.entity_id, 1).candidate == native.candidate
        assert isinstance(db.get(mapping.entity_id).candidate.payload, DomainMapping)
        assert not curated_entries(db)


def test_r2_forward_migration_preserves_review_tables(tmp_path: Path) -> None:
    path = tmp_path / "v2.sqlite"
    with sqlite3.connect(path) as connection:
        for version, name in enumerate(("001_registry.sql", "002_review.sql"), 1):
            sql = files("infinite_engine.catalog").joinpath("migrations", name).read_text()
            connection.executescript(sql)
            connection.execute(
                "INSERT INTO schema_migration VALUES (?,?)",
                (version, hashlib.sha256(sql.encode()).hexdigest()),
            )
        connection.execute("PRAGMA user_version=2")
        connection.execute("INSERT INTO candidate_batch VALUES ('old','hash','original time')")
    with Registry(path) as db:
        assert tuple(db._db.execute("SELECT * FROM candidate_batch").fetchone()) == (
            "old",
            "hash",
            "original time",
        )
        assert db._db.execute("PRAGMA user_version").fetchone()[0] == 5
        assert not db._db.execute("PRAGMA foreign_key_check").fetchall()


def test_mapping_approval_requires_exact_native_revision(tmp_path: Path) -> None:
    # Disposable simulated decisions only; no review result is distributed with the real pilot.
    bundle, _ = build(PILOT / "manifest.json")
    with Registry(tmp_path / "test.sqlite") as db:
        import_bundle(db, bundle, apply=True)
        native = next(e for e in bundle.entries if e.candidate.payload.kind == "taxonomy_entry")
        data = native.candidate.model_dump()
        data["payload"]["original_label"] = "Test correction"
        db.save(native.identity_key, Candidate.model_validate(data), expected_version=1)
        packet = tmp_path / "review"
        export_review(db, packet)
        for path in packet.glob("*.csv"):
            with path.open(encoding="utf-8-sig", newline="") as stream:
                reader = csv.DictReader(stream)
                fields, rows = reader.fieldnames, list(reader)
            assert fields
            for row in rows:
                row.update(decision="approve", reviewer="simulated-reviewer", reason="Test only")
            with path.open("w", encoding="utf-8-sig", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
        # Current entry v2 approval does not approve the original v1 used by mappings.
        with pytest.raises(RegistryError, match="Taxonomy entry revision"):
            apply_review(db, packet, actor="simulated-reviewer", apply=True)
        assert not curated_entries(db)


def test_bootstrap_cli(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "infinite_engine.catalog.bootstrap",
            "--manifest",
            str(PILOT / "manifest.json"),
            "--output",
            str(tmp_path / "out"),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["seed_ready"] is False
    assert (tmp_path / "out/candidates.json").exists()


def test_native_identity_has_unambiguous_component_boundaries() -> None:
    assert native_identity("a:b", "c", "d") != native_identity("a", "b:c", "d")
    assert native_identity("a", "b", "01") != native_identity("a", "b", "1")
