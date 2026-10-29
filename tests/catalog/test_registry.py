import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest
from infinite_engine.catalog.contracts import (
    Candidate,
    Concept,
    Domain,
    DomainConcept,
    DomainRelation,
    DomainSource,
    DomainTopic,
    EvidenceReference,
    Label,
    Provenance,
    ReviewRecord,
    Source,
    SourceCheck,
    Topic,
)
from infinite_engine.catalog.ids import stable_id
from infinite_engine.catalog.storage import Registry, RegistryError, VersionConflict
from pydantic import ValidationError


def domain(key: str, label: str | None = None) -> Domain:
    return Domain(
        slug=key,
        domain_type="academic",
        definition="Synthetic test definition",
        scope_note="Test only",
        labels=(Label(language="en", text=label or key),),
    )


def candidate(
    payload: Domain
    | Source
    | Topic
    | Concept
    | DomainRelation
    | DomainSource
    | DomainTopic
    | DomainConcept,
) -> Candidate:
    return Candidate(
        payload=payload,
        provenance=Provenance(
            origin="test_fixture",
            actor="pytest",
            rationale="Controlled fixture",
            unsupported_reason="Not a vetted knowledge claim",
        ),
    )


def save_domain(db: Registry, key: str) -> str:
    return db.save(key, candidate(domain(key)), expected_version=0).entity_id


def test_identity_multilingual_history_and_restart(tmp_path: Path) -> None:
    path = tmp_path / "registry.sqlite"
    first = candidate(domain("astronomy"))
    with Registry(path) as db:
        old = db.save("local:astronomy", first, expected_version=0)
        assert db.save("local:astronomy", first, expected_version=0) == old
        revised = candidate(
            Domain(
                slug="astronomy",
                domain_type="academic",
                definition="New draft",
                scope_note="Test",
                labels=(
                    Label(language="zh-Hans", text="天文学"),
                    Label(language="EN", text="Astronomy"),
                ),
            )
        )
        new = db.save("local:astronomy", revised, expected_version=1)
        assert new.entity_id == old.entity_id == stable_id("domain", "local:astronomy")
        assert new.version == 2 and new.prior_version == 1
        assert new.payload_hash != old.payload_hash
        assert new.review_status == "pending_review"
        with pytest.raises(VersionConflict):
            db.save("local:astronomy", first, expected_version=1)
    with Registry(path) as db:
        assert db.get(old.entity_id, 1) == old
        assert db.get(old.entity_id) == new
        assert db.label_matches("domain", "ZH-hans", "天文学") == (old.entity_id,)
    with sqlite3.connect(path) as connection:
        assert connection.execute("SELECT count(*) FROM schema_migration").fetchone()[0] == 2
        assert connection.execute("SELECT count(*) FROM review_record").fetchone()[0] == 0


def test_multiparent_classification_and_cross_domain_cycles(tmp_path: Path) -> None:
    with Registry(tmp_path / "registry.sqlite") as db:
        a, b, c = (save_domain(db, key) for key in ("a", "b", "c"))

        def relation(left: str, right: str, predicate: str = "SUBDOMAIN_OF") -> Candidate:
            return Candidate.model_validate(
                {
                    "payload": {
                        "kind": "domain_relation",
                        "from_domain_id": left,
                        "to_domain_id": right,
                        "predicate": predicate,
                        "rationale": "Fixture",
                    },
                    "provenance": candidate(domain("x")).provenance,
                }
            )

        db.save("ab", relation(a, b), expected_version=0)
        db.save("ac", relation(a, c), expected_version=0)
        assert len(db.relations("SUBDOMAIN_OF")) == 2
        with pytest.raises(RegistryError, match="cycle"):
            db.save("ba", relation(b, a), expected_version=0)
        # Failed insertion leaves no identity or history behind.
        with pytest.raises(KeyError):
            db.get(stable_id("domain_relation", "ba"))
        db.save("bc", relation(b, c, "APPLIES_TO"), expected_version=0)
        db.save("cb", relation(c, b, "APPLIES_TO"), expected_version=0)
        db.save("related", relation(b, c, "RELATED_TO"), expected_version=0)
        with pytest.raises(RegistryError, match="duplicate"):
            db.save("related-reversed", relation(c, b, "RELATED_TO"), expected_version=0)
        # Updating an edge excludes its own old revision from duplicate/cycle checks.
        db.save("ac", relation(b, c), expected_version=1)
        assert len(db.relations("SUBDOMAIN_OF")) == 2


def test_typed_membership_evidence_and_source_observations(tmp_path: Path) -> None:
    path = tmp_path / "registry.sqlite"
    with Registry(path) as db:
        d = save_domain(db, "astronomy")
        source = Source(source_kind="reference", labels=(Label(language="en", text="Fixture"),))
        s = db.save("fixture-source", candidate(source), expected_version=0)
        assert s.candidate.payload == source
        assert source.uri is None and source.license is None and source.published_at is None
        topic = db.save(
            "topic",
            candidate(Topic(description="Fixture", labels=source.labels)),
            expected_version=0,
        )
        concept = db.save(
            "concept",
            candidate(Concept(description="Fixture", labels=source.labels)),
            expected_version=0,
        )
        for key, payload in (
            (
                "ds",
                DomainSource(
                    domain_id=d,
                    source_id=s.entity_id,
                    rationale="Fixture source",
                    intended_use="Test",
                    authority_scope="None",
                    limitations="Not verified",
                ),
            ),
            ("dt", DomainTopic(domain_id=d, topic_id=topic.entity_id, rationale="Test")),
            ("dc", DomainConcept(domain_id=d, concept_id=concept.entity_id, rationale="Test")),
        ):
            db.save(key, candidate(payload), expected_version=0)
            with pytest.raises(RegistryError, match="duplicate"):
                db.save(key + "-duplicate", candidate(payload), expected_version=0)
        with pytest.raises(RegistryError, match="wrong-type"):
            db.save(
                "bad-topic",
                candidate(DomainTopic(domain_id=d, topic_id=s.entity_id, rationale="Test")),
                expected_version=0,
            )
        supported = Candidate(
            payload=domain("b"),
            provenance=Provenance(
                origin="test_fixture",
                actor="pytest",
                rationale="Fixture link",
                evidence=(
                    EvidenceReference(
                        source_id=s.entity_id, source_version=1, anchor="section:fixture-1"
                    ),
                ),
            ),
        )
        db.save("b", supported, expected_version=0)
        observation = SourceCheck(
            source_id=s.entity_id,
            source_version=1,
            check_kind="accessibility",
            outcome="inconclusive",
            checked_at=datetime.now(UTC),
            method="synthetic fixture",
            actor="pytest",
            locator="local fixture",
            evidence_note="No network check performed",
        )
        db.record_source_check(observation)
        with pytest.raises(sqlite3.IntegrityError):
            db.record_source_check(observation.model_copy(update={"source_version": 99}))
    with sqlite3.connect(path) as connection:
        assert (
            connection.execute("SELECT anchor FROM evidence_reference").fetchone()[0]
            == "section:fixture-1"
        )
        assert connection.execute("SELECT count(*) FROM source_check").fetchone()[0] == 1
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []


def test_alias_ambiguity_is_scoped_and_not_silently_merged(tmp_path: Path) -> None:
    with Registry(tmp_path / "registry.sqlite") as db:
        ids = {
            db.save(key, candidate(domain(key, "Shared name")), expected_version=0).entity_id
            for key in ("one", "two")
        }
        assert set(db.label_matches("domain", "EN", "  SHARED   NAME ")) == ids
        assert not db.label_matches("source", "en", "Shared name")
        assert not db.label_matches("domain", "la", "Shared name")
        with pytest.raises(RegistryError, match="duplicate"):
            db.save("other-identity", candidate(domain("one")), expected_version=0)
    with pytest.raises(ValidationError, match="Duplicate"):
        Domain(
            slug="x",
            domain_type="language",
            definition="Test",
            scope_note="Test",
            labels=(
                Label(language="la", text="Latin"),
                Label(language="LA", text="LATIN", role="alias"),
            ),
        )


@pytest.mark.parametrize(
    "field,value", [("schema_version", 2), ("review_status", "approved"), ("seed_ready", True)]
)
def test_unknown_versions_and_promotion_fields_rejected(field: str, value: object) -> None:
    data = candidate(domain("x")).model_dump()
    data[field] = value
    with pytest.raises(ValidationError):
        Candidate.model_validate(data)


def test_evidence_and_predicate_validation() -> None:
    with pytest.raises(ValidationError):
        Provenance(origin="ai", actor="test", rationale="Missing support")
    for predicate in ("PREREQUISITE_FOR", "UNKNOWN"):
        with pytest.raises(ValidationError):
            DomainRelation.model_validate(
                dict(
                    from_domain_id=stable_id("domain", "a"),
                    to_domain_id=stable_id("domain", "b"),
                    predicate=predicate,
                    rationale="Test",
                )
            )
    with pytest.raises(ValidationError):
        DomainRelation(
            from_domain_id=stable_id("domain", "a"),
            to_domain_id=stable_id("domain", "a"),
            predicate="RELATED_TO",
            rationale="Test",
        )
    with pytest.raises(ValueError):
        stable_id("domain", " padded ")


def test_missing_evidence_revision_and_stale_writer(tmp_path: Path) -> None:
    path = tmp_path / "registry.sqlite"
    with Registry(path) as first, Registry(path) as second:
        item = first.save("a", candidate(domain("a")), expected_version=0)
        first.save("a", candidate(domain("a", "New label")), expected_version=1)
        with pytest.raises(VersionConflict):
            second.save("a", candidate(domain("a", "Stale label")), expected_version=1)
        bad = Candidate(
            payload=domain("bad"),
            provenance=Provenance(
                origin="test_fixture",
                actor="pytest",
                rationale="Invalid reference",
                evidence=(
                    EvidenceReference(
                        source_id=item.entity_id, source_version=1, anchor="section:test"
                    ),
                ),
            ),
        )
        with pytest.raises(RegistryError):
            first.save("bad", bad, expected_version=0)
        assert first.get(item.entity_id).version == 2


def test_append_only_and_failed_write_rolls_back(tmp_path: Path) -> None:
    path = tmp_path / "registry.sqlite"
    with Registry(path) as db:
        save_domain(db, "a")
        with sqlite3.connect(path) as connection:
            for table in ("registry_entity", "entity_revision", "domain", "label", "provenance"):
                with pytest.raises(sqlite3.IntegrityError, match="append-only"):
                    connection.execute(f"DELETE FROM {table}")
            connection.execute(
                "CREATE TRIGGER fail_provenance BEFORE INSERT ON provenance "
                "BEGIN SELECT RAISE(ABORT, 'test injection'); END"
            )
        with pytest.raises(sqlite3.IntegrityError, match="test injection"):
            db.save("b", candidate(domain("b")), expected_version=0)
        with pytest.raises(KeyError):
            db.get(stable_id("domain", "b"))
    with sqlite3.connect(path) as connection:
        assert connection.execute("SELECT count(*) FROM registry_entity").fetchone()[0] == 1
        assert connection.execute("SELECT count(*) FROM domain").fetchone()[0] == 1


@pytest.mark.parametrize("mode", ["unknown_version", "existing_tables", "wrong_checksum"])
def test_migration_refuses_incompatible_databases(tmp_path: Path, mode: str) -> None:
    path = tmp_path / "registry.sqlite"
    with sqlite3.connect(path) as connection:
        if mode == "unknown_version":
            connection.execute("PRAGMA user_version=99")
        elif mode == "existing_tables":
            connection.execute("CREATE TABLE unrelated (id TEXT)")
        else:
            connection.execute("PRAGMA user_version=1")
            connection.execute("CREATE TABLE schema_migration (version INTEGER, checksum TEXT)")
            connection.execute("INSERT INTO schema_migration VALUES (1,'wrong')")
    with pytest.raises(RegistryError):
        Registry(path)


def test_review_contract_cannot_be_used_to_promote_candidate(tmp_path: Path) -> None:
    with Registry(tmp_path / "registry.sqlite") as db:
        revision = db.save("a", candidate(domain("a")), expected_version=0)
        record = ReviewRecord(
            entity_id=revision.entity_id,
            version=1,
            payload_hash=revision.payload_hash,
            decision="approve",
            reviewer="fixture operator",
            reason="Contract test only",
            recorded_at=datetime.now(UTC),
        )
        assert record.decision == "approve"
        assert db.get(revision.entity_id).review_status == "pending_review"
        with pytest.raises(ValidationError):
            ReviewRecord.model_validate({**record.model_dump(), "decision": "revise"})


def test_offline_no_credentials(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("HTTP_PROXY", "http://127.0.0.1:1")
    with Registry(tmp_path / "registry.sqlite") as db:
        assert db.get(save_domain(db, "offline")).review_status == "pending_review"


def test_source_evidence_keeps_original_version_when_source_changes(tmp_path: Path) -> None:
    path = tmp_path / "registry.sqlite"
    with Registry(path) as db:
        original = Source(source_kind="reference", labels=(Label(language="en", text="Original"),))
        source = db.save("s", candidate(original), expected_version=0)
        evidence = EvidenceReference(source_id=source.entity_id, source_version=1, anchor="page:1")
        item = Candidate(
            payload=domain("a"),
            provenance=Provenance(
                origin="test_fixture",
                actor="pytest",
                rationale="Versioned fixture",
                evidence=(evidence,),
            ),
        )
        revision = db.save("a", item, expected_version=0)
        changed = Source(source_kind="reference", labels=(Label(language="en", text="Revised"),))
        db.save("s", candidate(changed), expected_version=1)
        assert db.get(revision.entity_id).candidate.provenance.evidence == (evidence,)
        assert db.get(source.entity_id, 1).candidate.payload == original
        assert db.get(source.entity_id).version == 2
        missing = item.model_copy(
            update={
                "provenance": item.provenance.model_copy(
                    update={"evidence": (evidence.model_copy(update={"source_version": 99}),)}
                )
            }
        )
        with pytest.raises(RegistryError, match="absent source revision"):
            db.save("a", missing, expected_version=1)


def test_nonexistent_reference_and_bypassed_validation_are_rejected(tmp_path: Path) -> None:
    with Registry(tmp_path / "registry.sqlite") as db:
        d = save_domain(db, "a")
        edge = DomainRelation(
            from_domain_id=d,
            to_domain_id=stable_id("domain", "missing"),
            predicate="RELATED_TO",
            rationale="Fixture",
        )
        with pytest.raises(RegistryError, match="Missing"):
            db.save("edge", candidate(edge), expected_version=0)
        # Pydantic's model_copy does not validate updates; the write boundary must do so.
        unsafe = candidate(domain("unsafe")).model_copy(update={"schema_version": 2})
        with pytest.raises(ValidationError):
            db.save("unsafe", unsafe, expected_version=0)
        with pytest.raises(KeyError):
            db.get(stable_id("domain", "unsafe"))
