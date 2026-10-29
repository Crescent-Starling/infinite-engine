"""Transactional, candidate-only SQLite storage. No network, approval or seed side effects."""

import hashlib
import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from importlib.resources import files
from pathlib import Path
from types import TracebackType
from typing import Self

from infinite_engine.catalog.contracts import (
    Candidate,
    DomainRelation,
    Labeled,
    Revision,
    SourceCheck,
)
from infinite_engine.catalog.ids import normalized_label, stable_id


class RegistryError(ValueError):
    """Invalid candidate or incompatible registry state; no partial write is retained."""


class VersionConflict(RegistryError):
    """Caller must read and reconcile the current revision before retrying."""


def canonical_json(candidate: Candidate) -> str:
    return json.dumps(
        candidate.model_dump(mode="json"), sort_keys=True, ensure_ascii=False, separators=(",", ":")
    )


class Registry:
    """Use a context manager; the caller chooses an existing parent directory explicitly."""

    def __init__(self, path: str | Path) -> None:
        self._db = sqlite3.connect(str(path), isolation_level=None)
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA foreign_keys = ON")
        try:
            self._migrate()
        except (sqlite3.Error, RegistryError):
            self._db.close()
            raise

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._db.close()

    def _migrate(self) -> None:
        migrations = [
            files("infinite_engine.catalog").joinpath("migrations", name).read_text()
            for name in (
                "001_registry.sql",
                "002_review.sql",
                "003_taxonomy.sql",
                "004_domain_architecture.sql",
                "005_source_discovery.sql",
            )
        ]
        version = self._db.execute("PRAGMA user_version").fetchone()[0]
        if version not in range(len(migrations) + 1):
            raise RegistryError(f"Unsupported database schema version: {version}")
        if (
            version == 0
            and self._db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchone()
        ):
            raise RegistryError("Refusing to initialize a nonempty, unversioned database")
        for number, sql in enumerate(migrations, 1):
            digest = hashlib.sha256(sql.encode()).hexdigest()
            if number <= version:
                row = self._db.execute(
                    "SELECT checksum FROM schema_migration WHERE version=?", (number,)
                ).fetchone()
                if row is None or row[0] != digest:
                    raise RegistryError("Migration checksum mismatch")
                continue
            try:
                self._db.executescript(
                    "BEGIN IMMEDIATE;\n"
                    + sql
                    + f"\nINSERT INTO schema_migration VALUES ({number}, '{digest}');"
                    + f"\nPRAGMA user_version = {number};\nCOMMIT;"
                )
            except sqlite3.Error:
                if self._db.in_transaction:
                    self._db.rollback()
                raise

    @contextmanager
    def transaction(self, *, dry_run: bool = False) -> Iterator[None]:
        """Nested savepoints keep batch writes atomic; cleanup also runs on interruption."""
        outer = not self._db.in_transaction
        if outer:
            self._db.execute("BEGIN IMMEDIATE")
        self._db.execute("SAVEPOINT registry_operation")
        success = False
        try:
            yield
            success = not dry_run
        finally:
            if not success:
                self._db.execute("ROLLBACK TO registry_operation")
            self._db.execute("RELEASE registry_operation")
            if outer:
                self._db.commit()

    def get(self, entity_id: str, version: int | None = None) -> Revision:
        if version is None:
            row = self._db.execute(
                "SELECT * FROM latest_revision WHERE entity_id=?", (entity_id,)
            ).fetchone()
        else:
            row = self._db.execute(
                "SELECT * FROM entity_revision WHERE entity_id=? AND version=?",
                (entity_id, version),
            ).fetchone()
        if row is None:
            raise KeyError((entity_id, version))
        return Revision(
            entity_id=row["entity_id"],
            version=row["version"],
            prior_version=row["prior_version"],
            payload_hash=row["payload_hash"],
            recorded_at=row["recorded_at"],
            candidate=Candidate.model_validate_json(row["snapshot"]),
        )

    def _reference(self, entity_id: str, kind: str) -> None:
        row = self._db.execute(
            "SELECT kind FROM registry_entity WHERE id=?", (entity_id,)
        ).fetchone()
        if row is None or row[0] != kind:
            raise RegistryError(f"Missing or wrong-type {kind} reference: {entity_id}")

    def _validate_links(self, candidate: Candidate, entity_id: str) -> None:
        payload = candidate.payload
        values = payload.model_dump()
        for name, kind in (
            ("category_id", "category"),
            ("domain_id", "domain"),
            ("from_domain_id", "domain"),
            ("to_domain_id", "domain"),
            ("source_id", "source"),
            ("topic_id", "topic"),
            ("concept_id", "concept"),
            ("taxonomy_entry_id", "taxonomy_entry"),
        ):
            if name in values:
                self._reference(values[name], kind)
        for evidence in candidate.provenance.evidence:
            self._reference(evidence.source_id, "source")
            if (
                self._db.execute(
                    "SELECT 1 FROM source WHERE entity_id=? AND version=?",
                    (evidence.source_id, evidence.source_version),
                ).fetchone()
                is None
            ):
                raise RegistryError("Evidence references an absent source revision")
        if payload.kind == "taxonomy_entry":
            source = self.get(payload.source_id, payload.source_version).candidate.payload
            if source.kind != "source" or source.source_kind != "taxonomy":
                raise RegistryError("Taxonomy entry requires a taxonomy source")
            if source.version_tag != payload.release_tag:
                raise RegistryError("Taxonomy release must match its pinned source revision")
            old = self._db.execute(
                "SELECT source_id,source_version,release_tag,code FROM taxonomy_entry "
                "WHERE entity_id=? LIMIT 1",
                (entity_id,),
            ).fetchone()
            identity = (
                payload.source_id,
                payload.source_version,
                payload.release_tag,
                payload.code,
            )
            if old and tuple(old) != identity:
                raise RegistryError(
                    "Taxonomy identity cannot change release, code or source revision"
                )
        if payload.kind == "domain_mapping":
            target = self.get(payload.taxonomy_entry_id, payload.taxonomy_entry_version)
            if target.candidate.payload.kind != "taxonomy_entry":
                raise RegistryError("Mapping requires an exact taxonomy entry revision")
        if payload.kind == "domain":
            old = self._db.execute(
                "SELECT origin FROM domain WHERE entity_id=? AND origin IS NOT NULL LIMIT 1",
                (entity_id,),
            ).fetchone()
            if old and old[0] != payload.origin:
                raise RegistryError("Domain origin is immutable once explicitly assigned")
        if payload.kind == "domain_relation" and payload.predicate == "REFERENCES_PRESET":
            source = self.get(payload.from_domain_id).candidate.payload
            target_domain = self.get(payload.to_domain_id).candidate.payload
            if (
                source.kind != "domain"
                or target_domain.kind != "domain"
                or source.origin != "custom"
                or target_domain.origin != "preset"
            ):
                raise RegistryError("REFERENCES_PRESET requires custom to preset endpoints")
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
            # Table and column names come exclusively from closed contract kinds/constants.
            where = " AND ".join(f"p.{key}=?" for key in keys)
            row = self._db.execute(
                f"SELECT p.entity_id FROM {payload.kind} p JOIN latest_revision r "
                "USING(entity_id,version) WHERE p.entity_id<>? AND " + where,
                (entity_id, *(values[key] for key in keys)),
            ).fetchone()
            if row:
                raise RegistryError(f"Semantic duplicate of {row[0]}")
        if isinstance(payload, DomainRelation) and payload.predicate == "SUBDOMAIN_OF":
            edges = self._db.execute(
                "SELECT p.from_domain_id,p.to_domain_id FROM domain_relation p "
                "JOIN latest_revision r USING(entity_id,version) "
                "WHERE p.predicate='SUBDOMAIN_OF' AND p.entity_id<>?",
                (entity_id,),
            ).fetchall()
            parents: dict[str, list[str]] = {}
            for child, parent in edges:
                parents.setdefault(child, []).append(parent)
            pending, seen = [payload.to_domain_id], set()
            while pending:
                node = pending.pop()
                if node == payload.from_domain_id:
                    raise RegistryError("Classification cycle")
                if node not in seen:
                    seen.add(node)
                    pending.extend(parents.get(node, []))

    def save(self, identity_key: str, candidate: Candidate, *, expected_version: int) -> Revision:
        """Append a pending revision; replay of the latest identical write returns that revision."""
        if type(expected_version) is not int or expected_version < 0:
            raise RegistryError("expected_version must be a nonnegative integer")
        # Revalidate even model_construct/model_copy input; no caller can bypass the boundary.
        candidate = Candidate.model_validate_json(candidate.model_dump_json())
        entity_id = stable_id(candidate.payload.kind, identity_key)
        snapshot = canonical_json(candidate)
        digest = hashlib.sha256(snapshot.encode()).hexdigest()
        with self.transaction():
            row = self._db.execute(
                "SELECT version,payload_hash FROM latest_revision WHERE entity_id=?", (entity_id,)
            ).fetchone()
            current = row["version"] if row else 0
            if row and digest == row["payload_hash"] and expected_version in {current, current - 1}:
                return self.get(entity_id, current)
            if current != expected_version:
                raise VersionConflict(f"Expected version {expected_version}; current is {current}")
            self._validate_links(candidate, entity_id)
            if current == 0:
                self._db.execute(
                    "INSERT INTO registry_entity VALUES (?,?,?)",
                    (entity_id, candidate.payload.kind, identity_key),
                )
            version = current + 1
            self._db.execute(
                "INSERT INTO entity_revision VALUES (?,?,?,?,?,?,?,?)",
                (
                    entity_id,
                    version,
                    current or None,
                    1,
                    digest,
                    datetime.now(UTC).isoformat(),
                    "pending_review",
                    snapshot,
                ),
            )
            self._insert_payload(entity_id, version, candidate)
            return self.get(entity_id, version)

    def _insert_payload(self, entity_id: str, version: int, candidate: Candidate) -> None:
        payload = candidate.payload
        values = payload.model_dump(mode="json", exclude={"kind", "labels"})
        columns = ["entity_id", "version", *values]
        placeholders = ",".join("?" for _ in columns)
        self._db.execute(
            f"INSERT INTO {payload.kind} ({','.join(columns)}) VALUES ({placeholders})",
            (entity_id, version, *values.values()),
        )
        if isinstance(payload, Labeled):
            self._db.executemany(
                "INSERT INTO label VALUES (?,?,?,?,?,?)",
                [
                    (
                        entity_id,
                        version,
                        label.language,
                        label.text,
                        normalized_label(label.text),
                        label.role,
                    )
                    for label in payload.labels
                ],
            )
        provenance = candidate.provenance
        self._db.execute(
            "INSERT INTO provenance VALUES (?,?,?,?,?,?,?,?)",
            (
                entity_id,
                version,
                provenance.origin,
                provenance.actor,
                provenance.rationale,
                provenance.generator,
                provenance.input_hash,
                provenance.unsupported_reason,
            ),
        )
        self._db.executemany(
            "INSERT INTO evidence_reference VALUES (?,?,?,?,?)",
            [
                (entity_id, version, evidence.source_id, evidence.source_version, evidence.anchor)
                for evidence in provenance.evidence
            ],
        )

    def label_matches(self, kind: str, language: str, text: str) -> tuple[str, ...]:
        """Return all scoped homonyms for human reconciliation; never silently merge."""
        rows = self._db.execute(
            "SELECT DISTINCT l.entity_id FROM label l "
            "JOIN latest_revision r USING(entity_id,version) "
            "JOIN registry_entity e ON e.id=l.entity_id WHERE e.kind=? AND l.language=? "
            "AND l.normalized=? ORDER BY l.entity_id",
            (kind, language.lower(), normalized_label(text)),
        )
        return tuple(row[0] for row in rows)

    def relations(self, predicate: str | None = None) -> tuple[DomainRelation, ...]:
        rows = self._db.execute(
            "SELECT r.snapshot FROM latest_revision r "
            "JOIN domain_relation p USING(entity_id,version) "
            "WHERE (? IS NULL OR p.predicate=?) ORDER BY p.entity_id",
            (predicate, predicate),
        )
        return tuple(DomainRelation.model_validate(json.loads(row[0])["payload"]) for row in rows)

    def record_source_check(self, check: SourceCheck) -> int:
        """Record a caller-supplied observation, not a verification performed by this library."""
        check = SourceCheck.model_validate_json(check.model_dump_json())
        self._reference(check.source_id, "source")
        values = check.model_dump(mode="json")
        cursor = self._db.execute(
            f"INSERT INTO source_check ({','.join(values)}) "
            f"VALUES ({','.join('?' for _ in values)})",
            tuple(values.values()),
        )
        assert cursor.lastrowid is not None
        return cursor.lastrowid
