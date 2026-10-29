import csv
import hashlib
import sqlite3
from datetime import UTC, datetime
from importlib.resources import files
from pathlib import Path

import pytest
from infinite_engine.catalog.bundles import CandidateBundle, import_bundle
from infinite_engine.catalog.contracts import (
    Candidate,
    Domain,
    DomainCategory,
    DomainRelation,
    Label,
    Provenance,
    Source,
)
from infinite_engine.catalog.ids import stable_id
from infinite_engine.catalog.review import apply_review, curated_entries
from infinite_engine.catalog.review_csv import export_review
from infinite_engine.catalog.spaces import LocalDomains, PersonalOverride, SourceChoice
from infinite_engine.catalog.storage import Registry, RegistryError, canonical_json
from pydantic import ValidationError

FIXTURE = Path(__file__).parents[1] / "fixtures/domain_registry/domain-architecture.json"


def provenance() -> Provenance:
    return Provenance(
        origin="test_fixture",
        actor="test",
        rationale="Synthetic example",
        unsupported_reason="No factual claim or approval",
    )


def domain(origin: str = "custom", slug: str = "example") -> Domain:
    return Domain.model_validate(
        dict(
            labels=[{"language": "en", "text": "Same name"}, {"language": "zh", "text": "同名"}],
            slug=slug,
            definition="Synthetic description",
            scope_note="Test only",
            domain_type="academic",
            origin=origin,
            creation_method="manual",
        )
    )


def approve_packet(db: Registry, packet: Path) -> None:
    export_review(db, packet)
    for path in packet.glob("*.csv"):
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            fields, rows = reader.fieldnames, list(reader)
        assert fields
        for row in rows:
            row.update(decision="approve", reviewer="test", reason="Synthetic test approval")
        with path.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    apply_review(db, packet, actor="test", apply=True)


def test_fixture_import_categories_and_review(tmp_path: Path) -> None:
    bundle = CandidateBundle.model_validate_json(FIXTURE.read_bytes())
    with Registry(tmp_path / "db.sqlite") as db:
        result = import_bundle(db, bundle, apply=True)
        assert result == import_bundle(db, bundle, apply=True)
        assert len(result) == 12
        local = LocalDomains(db)
        assert len(local.search("")) == 2  # custom only; presets are still candidates
        assert len(local.search("", include_candidates=True)) == 4
        approve_packet(db, tmp_path / "review")
        assert len(local.search("")) == 4
        assert all(not item.seed_ready for item in local.search(""))
        assert db._db.execute("SELECT count(*) FROM domain_category").fetchone()[0] == 2
        assert not db.relations("SUBDOMAIN_OF")
        before = curated_entries(db)
        for item in local.search(""):
            space = local.ensure_primary_space(item.revision.entity_id)
            assert local.ensure_primary_space(item.revision.entity_id) == space
            local.save_override(PersonalOverride(space_id=space.id, display_name="My local title"))
        assert curated_entries(db) == before
        assert db._db.execute("SELECT count(*) FROM knowledge_space").fetchone()[0] == 4


def test_offline_custom_duplicates_sources_and_restart(tmp_path: Path) -> None:
    path = tmp_path / "local.sqlite"
    with Registry(path) as db:
        local = LocalDomains(db)
        first = local.create_custom("one", domain(), provenance())
        second = local.create_custom("two", domain(), provenance())
        assert first.entity_id != second.entity_id
        assert first.candidate.payload != second.candidate.payload  # allocated distinct slug
        assert local.create_custom("two", domain(), provenance()) == second
        assert len(local.search("同名")) == 2
        assert len(local.search("  SAME name  ")) == 2
        assert not curated_entries(db)
        space = local.ensure_primary_space(first.entity_id)
        source = db.save(
            "book",
            Candidate(
                payload=Source(
                    labels=(Label(language="en", text="User's unsourced bibliographic note"),),
                    source_kind="book",
                    bibliographic_reference="Synthetic reference only",
                    discovery_method="user_added",
                ),
                provenance=provenance(),
            ),
            expected_version=0,
        )
        choice = SourceChoice(
            space_id=space.id,
            source_id=source.entity_id,
            source_version=1,
            acceptance_state="accepted",
        )
        local.choose_source(choice)
        local.choose_source(choice)
        assert db._db.execute("SELECT count(*) FROM knowledge_space_source").fetchone()[0] == 1
        local.choose_source(choice.model_copy(update={"acceptance_state": "removed"}))
        assert not db._db.execute("SELECT * FROM source_check").fetchall()
        assert not db._db.execute("SELECT * FROM review_record").fetchall()
        assert not curated_entries(db)
    with Registry(path) as db:
        assert LocalDomains(db).ensure_primary_space(first.entity_id) == space
        assert db._db.execute("SELECT count(*) FROM knowledge_space_source").fetchone()[0] == 2
        assert db.get(source.entity_id).candidate.payload.license is None  # type: ignore[union-attr]


def test_preset_space_allows_unreviewed_user_sources(tmp_path: Path) -> None:
    with Registry(tmp_path / "db.sqlite") as db:
        preset = db.save(
            "preset",
            Candidate(payload=domain("preset"), provenance=provenance()),
            expected_version=0,
        )
        local = LocalDomains(db)
        with pytest.raises(RegistryError):
            local.ensure_primary_space(preset.entity_id)
        approve_packet(db, tmp_path / "review")
        before = curated_entries(db)
        space = local.ensure_primary_space(preset.entity_id)
        source = db.save(
            "local",
            Candidate(
                payload=Source(
                    labels=(Label(language="en", text="Personal local resource"),),
                    source_kind="local_document",
                    local_path=".local/example.txt",
                    discovery_method="user_added",
                ),
                provenance=provenance(),
            ),
            expected_version=0,
        )
        local.choose_source(
            SourceChoice(
                space_id=space.id,
                source_id=source.entity_id,
                source_version=1,
                acceptance_state="accepted",
            )
        )
        assert curated_entries(db) == before
        assert not db._db.execute("SELECT * FROM source_check").fetchall()
        local.save_override(PersonalOverride(space_id=space.id, scope_note="Personal scope"))
        assert curated_entries(db) == before
        replacement = preset.candidate.model_copy(
            update={"payload": domain("preset").model_copy(update={"definition": "Pending change"})}
        )
        db.save("preset", replacement, expected_version=1)
        assert local.search("")[0].revision == preset  # curated defaults do not drift
        assert local.search("", include_candidates=True)[0].revision.version == 2


@pytest.mark.parametrize(
    "predicate,symmetric",
    [
        ("SUBDOMAIN_OF", False),
        ("OVERLAPS_WITH", True),
        ("DRAWS_ON", False),
        ("USES_METHODS_FROM", False),
        ("APPLIES_KNOWLEDGE_FROM", False),
        ("RELATED_CONTEXT", True),
    ],
)
def test_domain_relation_semantics(tmp_path: Path, predicate: str, symmetric: bool) -> None:
    with Registry(tmp_path / "db.sqlite") as db:
        ids = [
            LocalDomains(db).create_custom(key, domain(slug=key), provenance()).entity_id
            for key in ("a", "b")
        ]
        payload = DomainRelation.model_validate(
            dict(from_domain_id=ids[0], to_domain_id=ids[1], predicate=predicate, rationale="Test")
        )
        reverse = DomainRelation.model_validate(
            dict(from_domain_id=ids[1], to_domain_id=ids[0], predicate=predicate, rationale="Test")
        )
        db.save("edge", Candidate(payload=payload, provenance=provenance()), expected_version=0)
        if symmetric or predicate == "SUBDOMAIN_OF":
            with pytest.raises(RegistryError):
                db.save(
                    "reverse",
                    Candidate(payload=reverse, provenance=provenance()),
                    expected_version=0,
                )
        else:
            db.save(
                "reverse", Candidate(payload=reverse, provenance=provenance()), expected_version=0
            )
        with pytest.raises(ValidationError):
            DomainRelation.model_validate(
                dict(
                    from_domain_id=ids[0],
                    to_domain_id=ids[0],
                    predicate=predicate,
                    rationale="Test",
                )
            )
        assert not curated_entries(db)


def test_category_type_origin_and_resource_identity_checks(tmp_path: Path) -> None:
    with Registry(tmp_path / "db.sqlite") as db:
        item = LocalDomains(db).create_custom("a", domain(), provenance())
        with pytest.raises(RegistryError, match="category"):
            db.save(
                "wrong",
                Candidate(
                    payload=DomainCategory(
                        domain_id=item.entity_id, category_id=item.entity_id, rationale="Test"
                    ),
                    provenance=provenance(),
                ),
                expected_version=0,
            )
        with pytest.raises(RegistryError, match="origin"):
            db.save(
                "a",
                Candidate(payload=domain("preset"), provenance=provenance()),
                expected_version=1,
            )
        source = Source(
            labels=(Label(language="en", text="Synthetic"),),
            source_kind="website",
            resource_identity="test:same",
        )
        db.save("source", Candidate(payload=source, provenance=provenance()), expected_version=0)
        with pytest.raises(RegistryError, match="duplicate"):
            db.save(
                "duplicate", Candidate(payload=source, provenance=provenance()), expected_version=0
            )
        with pytest.raises(ValidationError):
            Source.model_validate({**source.model_dump(), "uri": "not a URL"})
        with pytest.raises(ValidationError):
            Source.model_validate({**source.model_dump(), "verified": True})
        with pytest.raises(ValidationError):
            Domain.model_validate({**domain().model_dump(), "knowledge_readiness": "ready"})
        with pytest.raises(ValidationError):
            Domain.model_validate({**domain().model_dump(), "origin": None})


def test_reference_to_preset_has_typed_direction(tmp_path: Path) -> None:
    with Registry(tmp_path / "db.sqlite") as db:
        custom = LocalDomains(db).create_custom("custom", domain(), provenance())
        preset = db.save(
            "preset",
            Candidate(payload=domain("preset", "preset"), provenance=provenance()),
            expected_version=0,
        )
        for source, target, valid in [(custom, preset, True), (preset, custom, False)]:
            candidate = Candidate(
                payload=DomainRelation(
                    from_domain_id=source.entity_id,
                    to_domain_id=target.entity_id,
                    predicate="REFERENCES_PRESET",
                    rationale="Test",
                ),
                provenance=provenance(),
            )
            if valid:
                db.save("reference", candidate, expected_version=0)
            else:
                with pytest.raises(RegistryError):
                    db.save("backwards", candidate, expected_version=0)


def test_v3_snapshots_hashes_and_approved_history_survive(tmp_path: Path) -> None:
    path = tmp_path / "v3.sqlite"
    legacy = Candidate(
        payload=Domain(
            labels=(Label(language="en", text="Legacy"),),
            slug="legacy",
            definition="Old description",
            scope_note="Old scope",
            domain_type="academic",
        ),
        provenance=provenance(),
    )
    snapshot = canonical_json(legacy)
    assert "creation_method" not in snapshot and '"origin":null' not in snapshot
    digest = hashlib.sha256(snapshot.encode()).hexdigest()
    entity_id = stable_id("domain", "legacy")
    with sqlite3.connect(path) as connection:
        for number, name in enumerate(
            ("001_registry.sql", "002_review.sql", "003_taxonomy.sql"), 1
        ):
            sql = files("infinite_engine.catalog").joinpath("migrations", name).read_text()
            connection.executescript(sql)
            connection.execute(
                "INSERT INTO schema_migration VALUES (?,?)",
                (number, hashlib.sha256(sql.encode()).hexdigest()),
            )
            connection.commit()
        connection.execute("PRAGMA user_version=3")
        connection.execute(
            "INSERT INTO registry_entity VALUES (?,?,?)", (entity_id, "domain", "legacy")
        )
        connection.execute(
            "INSERT INTO entity_revision VALUES (?,1,NULL,1,?,?,?,?)",
            (entity_id, digest, datetime.now(UTC).isoformat(), "pending_review", snapshot),
        )
        connection.execute(
            "INSERT INTO domain VALUES (?,1,'legacy','academic','Old description','Old scope')",
            (entity_id,),
        )
        connection.execute(
            "INSERT INTO review_record VALUES (1,?,1,?,'approve','test','Test',?,NULL)",
            (entity_id, digest, "2000-01-01T00:00:00Z"),
        )
        connection.execute("INSERT INTO curated_revision VALUES (?,1,1)", (entity_id,))
        other_id = stable_id("domain", "other-legacy")
        relation_id = stable_id("domain_relation", "old-edge")
        for kind, key, identifier, payload in [
            (
                "domain",
                "other-legacy",
                other_id,
                legacy.payload.model_copy(update={"slug": "other-legacy"}),
            ),
            (
                "domain_relation",
                "old-edge",
                relation_id,
                DomainRelation(
                    from_domain_id=entity_id,
                    to_domain_id=other_id,
                    predicate="APPLIES_TO",
                    rationale="Historical direction",
                ),
            ),
        ]:
            candidate = Candidate(payload=payload, provenance=provenance())
            raw = canonical_json(candidate)
            connection.execute(
                "INSERT INTO registry_entity VALUES (?,?,?)", (identifier, kind, key)
            )
            connection.execute(
                "INSERT INTO entity_revision VALUES (?,1,NULL,1,?,?,?,?)",
                (
                    identifier,
                    hashlib.sha256(raw.encode()).hexdigest(),
                    datetime.now(UTC).isoformat(),
                    "pending_review",
                    raw,
                ),
            )
            values = payload.model_dump(mode="json", exclude={"kind", "labels"})
            names = ["entity_id", "version", *values]
            placeholders = ",".join("?" for _ in names)
            connection.execute(
                f"INSERT INTO {kind} ({','.join(names)}) VALUES ({placeholders})",
                (identifier, 1, *values.values()),
            )
        old_edge = tuple(connection.execute("SELECT * FROM domain_relation").fetchone())
    with Registry(path) as db:
        row = db._db.execute(
            "SELECT snapshot,payload_hash FROM entity_revision WHERE entity_id=?", (entity_id,)
        ).fetchone()
        assert tuple(row) == (snapshot, digest)
        assert tuple(db._db.execute("SELECT * FROM domain_relation").fetchone()) == old_edge
        with pytest.raises(sqlite3.IntegrityError):
            db._db.execute("DELETE FROM domain_relation")
        assert db.save("legacy", legacy, expected_version=0).version == 1
        assert db.get(entity_id).candidate.payload.origin is None  # type: ignore[union-attr]
        assert not LocalDomains(db).search("", include_candidates=True)
        assert curated_entries(db)[0].revision.payload_hash == digest
        assert not db._db.execute("PRAGMA foreign_key_check").fetchall()
        with pytest.raises(sqlite3.IntegrityError):
            db._db.execute("UPDATE domain SET origin='preset'")


def test_legacy_review_packet_remains_readable(tmp_path: Path) -> None:
    with Registry(tmp_path / "db.sqlite") as db:
        old = Candidate(
            payload=Domain(
                labels=(Label(language="en", text="Old"),),
                slug="old",
                definition="Test",
                scope_note="Test",
                domain_type="academic",
            ),
            provenance=provenance(),
        )
        db.save("old", old, expected_version=0)
        packet = tmp_path / "packet"
        export_review(db, packet)
        path = packet / "domain.csv"
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            fields, rows = reader.fieldnames, list(reader)
        assert fields
        # Reproduce the R3 column shape, before the two additive fields existed.
        fields = [key for key in fields if not key.endswith((".origin", ".creation_method"))]
        with path.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        assert apply_review(db, packet, actor="test")["approved_count"] == 0


def test_custom_metadata_does_not_require_repeat_registry_approval(tmp_path: Path) -> None:
    with Registry(tmp_path / "db.sqlite") as db:
        local = LocalDomains(db)
        first = local.create_custom("local", domain(), provenance())
        approve_packet(db, tmp_path / "review")
        replacement = Candidate(
            payload=domain().model_copy(update={"definition": "Local update"}),
            provenance=provenance(),
        )
        second = db.save("local", replacement, expected_version=1)
        assert local.search("")[0].revision == second
        assert curated_entries(db)[0].revision == first


def test_new_csv_metadata_requires_review_and_survives_null_clearing(tmp_path: Path) -> None:
    with Registry(tmp_path / "db.sqlite") as db:
        source = Source(
            labels=(Label(language="en", text="Test source"),),
            source_kind="reference",
            coverage_description="Original description",
        )
        first = db.save(
            "source", Candidate(payload=source, provenance=provenance()), expected_version=0
        )
        packet = tmp_path / "packet"
        export_review(db, packet)
        path = packet / "source.csv"
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            fields, rows = reader.fieldnames, list(reader)
        assert fields
        rows[0].update(decision="revise", reviewer="test", reason="Explicit clearing")
        rows[0]["proposed.coverage_description"] = "null"
        with path.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        result = apply_review(db, packet, actor="test", apply=True)
        assert "coverage_description" in str(result["actions"])
        assert db.get(first.entity_id, 1).candidate.payload == source
        assert "coverage_description" not in db.get(first.entity_id).candidate.payload.model_dump()
        assert not curated_entries(db)
