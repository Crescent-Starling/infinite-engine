import csv
import hashlib
import json
import sqlite3
from importlib.resources import files
from pathlib import Path

import pytest
from infinite_engine.catalog.bundles import BundleEntry, CandidateBundle, import_bundle
from infinite_engine.catalog.contracts import Candidate, Domain, DomainRelation, Label, Provenance
from infinite_engine.catalog.ids import stable_id
from infinite_engine.catalog.review import apply_review, curated_entries, review_state
from infinite_engine.catalog.review_csv import cell, export_review, uncell
from infinite_engine.catalog.storage import Registry, RegistryError, VersionConflict


def example(key: str) -> Candidate:
    return Candidate(
        payload=Domain(
            slug=key,
            domain_type="academic",
            definition="Synthetic example",
            scope_note="Test only",
            labels=(Label(language="en", text=key),),
        ),
        provenance=Provenance(
            origin="ai",
            actor="fixture-generator",
            rationale="Synthetic suggestion",
            generator="fixture",
            unsupported_reason="Not a real knowledge claim",
        ),
    )


def edit(directory: Path, updates: dict[str, dict[str, str]]) -> None:
    for path in directory.glob("*.csv"):
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            fields = reader.fieldnames
            rows = list(reader)
        assert fields is not None
        for row in rows:
            row.update(
                {key: cell(value) for key, value in updates.get(row["entity_id"], {}).items()}
            )
        with path.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)


def decision(name: str) -> dict[str, str]:
    return {"decision": name, "reviewer": "fixture-reviewer", "reason": "Controlled test decision"}


def setup_candidates(db: Registry) -> dict[str, str]:
    return {
        key: db.save(key, example(key), expected_version=0).entity_id
        for key in ("a", "b", "c", "d")
    }


def test_review_lifecycle_dry_run_replay_and_restart(tmp_path: Path) -> None:
    path = tmp_path / "registry.sqlite"
    with Registry(path) as db:
        ids = setup_candidates(db)
        packet = tmp_path / "review"
        export_review(db, packet)
        edit(
            packet,
            {
                ids["a"]: decision("approve"),
                ids["b"]: decision("reject"),
                ids["c"]: {
                    **decision("revise"),
                    "proposed.definition": json.dumps("Human revision"),
                },
                ids["d"]: decision("defer"),
            },
        )
        dry = apply_review(db, packet, actor="fixture-reviewer")
        assert dry["approved_count"] == 1
        assert not curated_entries(db)
        assert db.get(ids["c"]).version == 1
        result = apply_review(db, packet, actor="fixture-reviewer", apply=True)
        assert result["actions"] == dry["actions"]
        replay = apply_review(db, packet, actor="fixture-reviewer", apply=True)
        assert replay["replayed"] is True
        assert review_state(db, ids["a"], 1) == "approved"
        assert review_state(db, ids["b"], 1) == "rejected"
        assert review_state(db, ids["c"], 1) == "revised"
        assert review_state(db, ids["c"], 2) == "pending_review"
        assert review_state(db, ids["d"], 1) == "deferred"
        assert db.get(ids["c"], 1).candidate.provenance.origin == "ai"
        assert db.get(ids["c"], 2).candidate.provenance.origin == "human"
        assert (
            db.get(ids["c"], 2).candidate.provenance.input_hash == db.get(ids["c"], 1).payload_hash
        )
        second = tmp_path / "second"
        export_review(db, second, (ids["c"], ids["d"]))
        edit(second, {ids["c"]: decision("approve"), ids["d"]: decision("approve")})
        apply_review(db, second, actor="fixture-reviewer", apply=True)
    with Registry(path) as db:
        assert len(curated_entries(db)) == 3
        original_payload = db.get(ids["c"], 1).candidate.payload
        assert isinstance(original_payload, Domain)
        assert original_payload.definition == "Synthetic example"
        # A new draft must not replace the previously approved revision.
        current = db.get(ids["a"])
        changed = Candidate.model_validate(
            {
                **current.candidate.model_dump(),
                "payload": {
                    **current.candidate.payload.model_dump(),
                    "definition": "Unapproved update",
                },
            }
        )
        db.save("a", changed, expected_version=1)
        curated = {entry.revision.entity_id: entry for entry in curated_entries(db)}
        assert curated[ids["a"]].revision.version == 1
        assert curated[ids["a"]].status == "approved"


@pytest.mark.parametrize(
    "column,value",
    [
        ("version", "99"),
        ("payload_hash", "0" * 64),
        ("original.definition", '"Forged original"'),
        ("entity_id", stable_id("domain", "unknown")),
    ],
)
def test_protected_columns_rejected(tmp_path: Path, column: str, value: str) -> None:
    with Registry(tmp_path / "db.sqlite") as db:
        item = db.save("a", example("a"), expected_version=0)
        packet = tmp_path / "packet"
        export_review(db, packet)
        edit(packet, {item.entity_id: {**decision("approve"), column: value}})
        with pytest.raises(RegistryError, match="domain.csv:2"):
            apply_review(db, packet, actor="fixture-reviewer", apply=True)
        assert not curated_entries(db)


def test_edits_need_revise_and_actor_must_match(tmp_path: Path) -> None:
    with Registry(tmp_path / "db.sqlite") as db:
        item = db.save("a", example("a"), expected_version=0)
        packet = tmp_path / "packet"
        export_review(db, packet)
        edit(packet, {item.entity_id: {**decision("approve"), "proposed.definition": '"Changed"'}})
        with pytest.raises(RegistryError, match="must use revise"):
            apply_review(db, packet, actor="fixture-reviewer", apply=True)
        edit(packet, {item.entity_id: {**decision("revise"), "reviewer": "different-person"}})
        with pytest.raises(RegistryError, match="operator"):
            apply_review(db, packet, actor="fixture-reviewer", apply=True)
        assert db.get(item.entity_id).version == 1


def test_stale_export_and_terminal_review(tmp_path: Path) -> None:
    with Registry(tmp_path / "db.sqlite") as db:
        item = db.save("a", example("a"), expected_version=0)
        packet = tmp_path / "packet"
        export_review(db, packet)
        edit(packet, {item.entity_id: decision("approve")})
        changed = Candidate.model_validate(
            {
                **item.candidate.model_dump(),
                "payload": {**item.candidate.payload.model_dump(), "definition": "Changed"},
            }
        )
        db.save("a", changed, expected_version=1)
        with pytest.raises(VersionConflict):
            apply_review(db, packet, actor="fixture-reviewer", apply=True)
        second = tmp_path / "second"
        export_review(db, second)
        edit(second, {item.entity_id: decision("reject")})
        apply_review(db, second, actor="fixture-reviewer", apply=True)
        third = tmp_path / "third"
        export_review(db, third)
        edit(third, {item.entity_id: decision("approve")})
        with pytest.raises(RegistryError, match="terminal"):
            apply_review(db, third, actor="fixture-reviewer", apply=True)


def test_bundle_forward_references_replay_conflict_and_atomicity(tmp_path: Path) -> None:
    with Registry(tmp_path / "db.sqlite") as db:
        edge = Candidate(
            payload=DomainRelation(
                from_domain_id=stable_id("domain", "a"),
                to_domain_id=stable_id("domain", "b"),
                predicate="SUBDOMAIN_OF",
                rationale="Test",
            ),
            provenance=example("a").provenance,
        )
        bundle = CandidateBundle(
            batch_id="first",
            entries=(
                BundleEntry(identity_key="edge", candidate=edge),
                BundleEntry(identity_key="a", candidate=example("a")),
                BundleEntry(identity_key="b", candidate=example("b")),
            ),
        )
        assert len(import_bundle(db, bundle)) == 3
        with pytest.raises(KeyError):
            db.get(stable_id("domain", "a"))
        saved = import_bundle(db, bundle, apply=True)
        assert import_bundle(db, bundle, apply=True) == saved
        with pytest.raises(RegistryError, match="different content"):
            import_bundle(
                db, CandidateBundle(batch_id="first", entries=bundle.entries[1:]), apply=True
            )
        bad = CandidateBundle(
            batch_id="bad",
            entries=(
                BundleEntry(identity_key="new", candidate=example("new")),
                BundleEntry(identity_key="duplicate", candidate=example("a")),
            ),
        )
        with pytest.raises(RegistryError):
            import_bundle(db, bad, apply=True)
        with pytest.raises(KeyError):
            db.get(stable_id("domain", "new"))


def test_dependency_closure_and_curated_cycle_validation(tmp_path: Path) -> None:
    with Registry(tmp_path / "db.sqlite") as db:
        ids = setup_candidates(db)

        def relation(left: str, right: str) -> Candidate:
            return Candidate(
                payload=DomainRelation(
                    from_domain_id=ids[left],
                    to_domain_id=ids[right],
                    predicate="SUBDOMAIN_OF",
                    rationale="Test",
                ),
                provenance=example("a").provenance,
            )

        edge = db.save("edge", relation("a", "b"), expected_version=0)
        packet = tmp_path / "packet"
        export_review(db, packet)
        edit(packet, {edge.entity_id: decision("approve")})
        with pytest.raises(RegistryError, match="closure"):
            apply_review(db, packet, actor="fixture-reviewer", apply=True)
        edit(packet, {value: decision("approve") for value in ids.values()})
        apply_review(db, packet, actor="fixture-reviewer", apply=True)
        # Candidate graph a->c,b->a is valid; mixed curated a->b,b->a is not.
        db.save("edge", relation("a", "c"), expected_version=1)
        opposite = db.save("opposite", relation("b", "a"), expected_version=0)
        second = tmp_path / "second"
        export_review(db, second, (opposite.entity_id,))
        edit(second, {opposite.entity_id: decision("approve")})
        with pytest.raises(RegistryError, match="cycle"):
            apply_review(db, second, actor="fixture-reviewer", apply=True)
        assert review_state(db, opposite.entity_id, 1) == "pending_review"


@pytest.mark.parametrize(
    "value",
    [
        "=SUM(A1:A2)",
        "+cmd",
        "-5",
        "@cmd",
        "\t=cmd",
        "  =cmd",
        "'literal",
        "normal",
        "",
        "中文\nline",
    ],
)
def test_spreadsheet_cell_roundtrip(value: str) -> None:
    assert uncell(cell(value)) == value
    if value.lstrip().startswith(("=", "+", "-", "@")):
        assert cell(value).startswith("'")


def test_partial_parse_and_provenance_tampering(tmp_path: Path) -> None:
    with Registry(tmp_path / "db.sqlite") as db:
        ids = setup_candidates(db)
        packet = tmp_path / "packet"
        export_review(db, packet)
        edit(
            packet,
            {ids["a"]: decision("approve"), ids["b"]: {"proposed.definition": "invalid JSON"}},
        )
        with pytest.raises(RegistryError, match="domain.csv"):
            apply_review(db, packet, actor="fixture-reviewer", apply=True)
        assert not curated_entries(db)
        (packet / "provenance.json").write_text("{}")
        with pytest.raises(RegistryError, match="provenance"):
            apply_review(db, packet, actor="fixture-reviewer", apply=True)


def test_sql_failure_rolls_back_reviews_and_promotions(tmp_path: Path) -> None:
    path = tmp_path / "db.sqlite"
    with Registry(path) as db:
        ids = setup_candidates(db)
        packet = tmp_path / "packet"
        export_review(db, packet)
        edit(packet, {value: decision("approve") for value in ids.values()})
        with sqlite3.connect(path) as connection:
            connection.execute(
                "CREATE TRIGGER injected_failure BEFORE INSERT ON curated_revision "
                "BEGIN SELECT RAISE(ABORT,'injected failure'); END"
            )
        with pytest.raises(sqlite3.IntegrityError, match="injected failure"):
            apply_review(db, packet, actor="fixture-reviewer", apply=True)
        assert not curated_entries(db)
        assert all(review_state(db, value, 1) == "pending_review" for value in ids.values())


def test_forward_migration_preserves_v1_history(tmp_path: Path) -> None:
    path = tmp_path / "v1.sqlite"
    sql = files("infinite_engine.catalog").joinpath("migrations/001_registry.sql").read_text()
    with sqlite3.connect(path) as connection:
        connection.executescript(sql)
        connection.execute(
            "INSERT INTO schema_migration VALUES (1,?)", (hashlib.sha256(sql.encode()).hexdigest(),)
        )
        connection.execute("PRAGMA user_version=1")
        # Persist a genuine R1 shape before opening with the R2 migration runner.
        value = example("legacy")
        identity = stable_id("domain", "legacy")
        snapshot = json.dumps(
            value.model_dump(mode="json"), sort_keys=True, ensure_ascii=False, separators=(",", ":")
        )
        connection.execute(
            "INSERT INTO registry_entity VALUES (?,?,?)", (identity, "domain", "legacy")
        )
        connection.execute(
            "INSERT INTO entity_revision VALUES (?,?,?,?,?,?,?,?)",
            (
                identity,
                1,
                None,
                1,
                hashlib.sha256(snapshot.encode()).hexdigest(),
                "2026-10-29T00:00:00+00:00",
                "pending_review",
                snapshot,
            ),
        )
    with Registry(path) as db:
        assert db.get(identity).candidate == value
    with Registry(path) as db:
        assert db.get(identity).version == 1
    with sqlite3.connect(path) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 2
        assert connection.execute("SELECT count(*) FROM schema_migration").fetchone()[0] == 2


def test_exact_source_revision_requires_approval(tmp_path: Path) -> None:
    from infinite_engine.catalog.contracts import EvidenceReference, Source

    with Registry(tmp_path / "db.sqlite") as db:
        source_payload = Source(
            source_kind="reference", labels=(Label(language="en", text="Fixture"),)
        )
        source = db.save(
            "source",
            Candidate(payload=source_payload, provenance=example("a").provenance),
            expected_version=0,
        )
        packet = tmp_path / "source-review"
        export_review(db, packet)
        edit(packet, {source.entity_id: decision("approve")})
        apply_review(db, packet, actor="fixture-reviewer", apply=True)
        updated = Source(
            source_kind="reference", labels=(Label(language="en", text="New source draft"),)
        )
        db.save(
            "source",
            Candidate(payload=updated, provenance=source.candidate.provenance),
            expected_version=1,
        )
        supported = Candidate(
            payload=example("a").payload,
            provenance=Provenance(
                origin="test_fixture",
                actor="pytest",
                rationale="Fixture",
                evidence=(
                    EvidenceReference(
                        source_id=source.entity_id, source_version=2, anchor="section:fixture"
                    ),
                ),
            ),
        )
        item = db.save("a", supported, expected_version=0)
        second = tmp_path / "second"
        export_review(db, second)
        edit(second, {item.entity_id: decision("approve")})
        with pytest.raises(RegistryError, match="source revision"):
            apply_review(db, second, actor="fixture-reviewer", apply=True)
        edit(second, {source.entity_id: decision("approve")})
        apply_review(db, second, actor="fixture-reviewer", apply=True)
        assert len(curated_entries(db)) == 2


def test_csv_null_multilingual_multiline_and_blank_semantics(tmp_path: Path) -> None:
    from infinite_engine.catalog.contracts import Source

    with Registry(tmp_path / "db.sqlite") as db:
        payload = Source(
            source_kind="reference",
            creator="Original author",
            labels=(Label(language="zh", text="中文\n第二行"),),
        )
        item = db.save(
            "s", Candidate(payload=payload, provenance=example("a").provenance), expected_version=0
        )
        packet = tmp_path / "packet"
        export_review(db, packet)
        edit(packet, {item.entity_id: {**decision("revise"), "proposed.creator": "null"}})
        apply_review(db, packet, actor="fixture-reviewer", apply=True)
        revised = db.get(item.entity_id)
        assert isinstance(revised.candidate.payload, Source)
        assert revised.candidate.payload.creator is None
        assert revised.candidate.payload.labels == payload.labels
        second = tmp_path / "second"
        export_review(db, second)
        edit(second, {item.entity_id: {"proposed.creator": ""}})
        with pytest.raises(RegistryError, match="source.csv"):
            apply_review(db, second, actor="fixture-reviewer", apply=True)


@pytest.mark.parametrize("corruption", ["missing_row", "extra_column", "manifest", "duplicate_row"])
def test_packet_completeness(tmp_path: Path, corruption: str) -> None:
    with Registry(tmp_path / "db.sqlite") as db:
        item = db.save("a", example("a"), expected_version=0)
        packet = tmp_path / "packet"
        export_review(db, packet)
        edit(packet, {item.entity_id: decision("approve")})
        path = packet / "domain.csv"
        lines = path.read_text(encoding="utf-8-sig").splitlines(keepends=True)
        if corruption == "missing_row":
            path.write_text(lines[0], encoding="utf-8-sig")
        elif corruption == "extra_column":
            path.write_text(lines[0].rstrip() + ",extra\n" + lines[1], encoding="utf-8-sig")
        elif corruption == "duplicate_row":
            path.write_text("".join(lines + lines[1:]), encoding="utf-8-sig")
        else:
            manifest = json.loads((packet / "manifest.json").read_text())
            manifest["files"] = ["../../other.csv"]
            (packet / "manifest.json").write_text(json.dumps(manifest))
        with pytest.raises(RegistryError):
            apply_review(db, packet, actor="fixture-reviewer", apply=True)
        assert not curated_entries(db)


def test_revision_rollback_and_database_approval_guard(tmp_path: Path) -> None:
    path = tmp_path / "db.sqlite"
    with Registry(path) as db:
        ids = setup_candidates(db)
        ordered = sorted(ids.values())
        packet = tmp_path / "packet"
        export_review(db, packet)
        edit(
            packet,
            {
                ordered[0]: {**decision("revise"), "proposed.definition": '"Changed"'},
                ordered[1]: {**decision("approve"), "reason": ""},
            },
        )
        with pytest.raises(ValueError):
            apply_review(db, packet, actor="fixture-reviewer", apply=True)
        assert db.get(ordered[0]).version == 1
        with sqlite3.connect(path) as connection:
            with pytest.raises(sqlite3.IntegrityError, match="explicit approval"):
                connection.execute(
                    "INSERT INTO curated_revision VALUES (?,?,?)", (ordered[0], 1, 999)
                )


def test_cli_review_roundtrip(tmp_path: Path) -> None:
    import subprocess
    import sys

    database = tmp_path / "cli.sqlite"
    root = Path(__file__).resolve().parents[2]
    fixture = root / "tests/fixtures/domain_registry/review-bundle.json"
    command = [sys.executable, "-m", "infinite_engine.catalog.review_cli", "--db", str(database)]

    def run(*arguments: str) -> object:
        result = subprocess.run([*command, *arguments], capture_output=True, text=True, check=True)
        return json.loads(result.stdout)

    run("import-bundle", str(fixture))
    run("import-bundle", str(fixture), "--apply")
    packet = tmp_path / "first"
    run("export", str(packet))
    identity = stable_id("domain", "fixture:review-demo")
    edit(
        packet,
        {identity: {**decision("revise"), "proposed.definition": '"Revised synthetic example"'}},
    )
    run("review", str(packet), "--actor", "fixture-reviewer")
    assert run("curated") == []
    run("review", str(packet), "--actor", "fixture-reviewer", "--apply")
    second = tmp_path / "second"
    run("export", str(second))
    edit(second, {identity: decision("approve")})
    run("review", str(second), "--actor", "fixture-reviewer", "--apply")
    replay = run("review", str(second), "--actor", "fixture-reviewer", "--apply")
    assert isinstance(replay, dict) and replay["replayed"] is True
    curated = run("curated")
    assert isinstance(curated, list)
    assert len(curated) == 1 and curated[0]["revision"]["version"] == 2
    assert curated[0]["status"] == "approved"


def test_bundle_never_silently_changes_identity_key() -> None:
    with pytest.raises(ValueError, match="unpadded"):
        BundleEntry(identity_key=" padded ", candidate=example("a"))
