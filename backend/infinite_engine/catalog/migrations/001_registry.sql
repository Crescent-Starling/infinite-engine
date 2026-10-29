CREATE TABLE schema_migration (version INTEGER PRIMARY KEY, checksum TEXT NOT NULL);
CREATE TABLE registry_entity (
 id TEXT PRIMARY KEY, kind TEXT NOT NULL, identity_key TEXT NOT NULL,
 UNIQUE(kind, identity_key)
);
CREATE TABLE entity_revision (
 entity_id TEXT NOT NULL REFERENCES registry_entity(id), version INTEGER NOT NULL CHECK(version >= 1),
 prior_version INTEGER, schema_version INTEGER NOT NULL CHECK(schema_version = 1),
 payload_hash TEXT NOT NULL, recorded_at TEXT NOT NULL,
 review_status TEXT NOT NULL DEFAULT 'pending_review' CHECK(review_status = 'pending_review'),
 snapshot TEXT NOT NULL CHECK(json_valid(snapshot)),
 PRIMARY KEY(entity_id, version),
 FOREIGN KEY(entity_id, prior_version) REFERENCES entity_revision(entity_id, version),
 CHECK((version = 1 AND prior_version IS NULL) OR (prior_version IS NOT NULL AND prior_version = version - 1))
);
CREATE TABLE label (
 entity_id TEXT NOT NULL, version INTEGER NOT NULL, language TEXT NOT NULL,
 text TEXT NOT NULL, normalized TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('preferred','alias')),
 PRIMARY KEY(entity_id, version, language, normalized),
 FOREIGN KEY(entity_id, version) REFERENCES entity_revision(entity_id, version)
);
CREATE UNIQUE INDEX preferred_label ON label(entity_id, version, language) WHERE role = 'preferred';
CREATE TABLE domain (
 entity_id TEXT NOT NULL, version INTEGER NOT NULL, slug TEXT NOT NULL,
 domain_type TEXT NOT NULL, definition TEXT NOT NULL, scope_note TEXT NOT NULL,
 PRIMARY KEY(entity_id, version),
 FOREIGN KEY(entity_id, version) REFERENCES entity_revision(entity_id, version)
);
CREATE TABLE source (
 entity_id TEXT NOT NULL, version INTEGER NOT NULL, source_kind TEXT NOT NULL,
 creator TEXT, uri TEXT, local_path TEXT, published_at TEXT, license TEXT, version_tag TEXT,
 content_hash TEXT,
 PRIMARY KEY(entity_id, version),
 FOREIGN KEY(entity_id, version) REFERENCES entity_revision(entity_id, version)
);
CREATE TABLE topic (
 entity_id TEXT NOT NULL, version INTEGER NOT NULL, description TEXT NOT NULL,
 PRIMARY KEY(entity_id, version),
 FOREIGN KEY(entity_id, version) REFERENCES entity_revision(entity_id, version)
);
CREATE TABLE concept (
 entity_id TEXT NOT NULL, version INTEGER NOT NULL, description TEXT NOT NULL,
 PRIMARY KEY(entity_id, version),
 FOREIGN KEY(entity_id, version) REFERENCES entity_revision(entity_id, version)
);
CREATE TABLE domain_relation (
 entity_id TEXT NOT NULL, version INTEGER NOT NULL,
 from_domain_id TEXT NOT NULL REFERENCES registry_entity(id),
 to_domain_id TEXT NOT NULL REFERENCES registry_entity(id),
 predicate TEXT NOT NULL CHECK(predicate IN ('SUBDOMAIN_OF','OVERLAPS_WITH','RELATED_TO','APPLIES_TO')),
 rationale TEXT NOT NULL, CHECK(from_domain_id <> to_domain_id),
 PRIMARY KEY(entity_id, version),
 FOREIGN KEY(entity_id, version) REFERENCES entity_revision(entity_id, version)
);
CREATE TABLE domain_source (
 entity_id TEXT NOT NULL, version INTEGER NOT NULL,
 domain_id TEXT NOT NULL REFERENCES registry_entity(id),
 source_id TEXT NOT NULL REFERENCES registry_entity(id), rationale TEXT NOT NULL,
 intended_use TEXT NOT NULL, authority_scope TEXT NOT NULL, limitations TEXT NOT NULL,
 PRIMARY KEY(entity_id, version),
 FOREIGN KEY(entity_id, version) REFERENCES entity_revision(entity_id, version)
);
CREATE TABLE domain_topic (
 entity_id TEXT NOT NULL, version INTEGER NOT NULL,
 domain_id TEXT NOT NULL REFERENCES registry_entity(id),
 topic_id TEXT NOT NULL REFERENCES registry_entity(id), rationale TEXT NOT NULL,
 PRIMARY KEY(entity_id, version),
 FOREIGN KEY(entity_id, version) REFERENCES entity_revision(entity_id, version)
);
CREATE TABLE domain_concept (
 entity_id TEXT NOT NULL, version INTEGER NOT NULL,
 domain_id TEXT NOT NULL REFERENCES registry_entity(id),
 concept_id TEXT NOT NULL REFERENCES registry_entity(id), rationale TEXT NOT NULL,
 PRIMARY KEY(entity_id, version),
 FOREIGN KEY(entity_id, version) REFERENCES entity_revision(entity_id, version)
);
CREATE TABLE provenance (
 entity_id TEXT NOT NULL, version INTEGER NOT NULL, origin TEXT NOT NULL,
 actor TEXT NOT NULL, rationale TEXT NOT NULL, generator TEXT, input_hash TEXT, unsupported_reason TEXT,
 PRIMARY KEY(entity_id, version),
 FOREIGN KEY(entity_id, version) REFERENCES entity_revision(entity_id, version)
);
CREATE TABLE evidence_reference (
 entity_id TEXT NOT NULL, version INTEGER NOT NULL, source_id TEXT NOT NULL,
 source_version INTEGER NOT NULL, anchor TEXT NOT NULL,
 PRIMARY KEY(entity_id, version, source_id, source_version, anchor),
 FOREIGN KEY(entity_id, version) REFERENCES provenance(entity_id, version),
 FOREIGN KEY(source_id, source_version) REFERENCES source(entity_id, version)
);
-- Reserved review ledger: no R1 repository operation inserts decisions or promotes data.
CREATE TABLE review_record (
 id INTEGER PRIMARY KEY, entity_id TEXT NOT NULL, version INTEGER NOT NULL,
 payload_hash TEXT NOT NULL, decision TEXT NOT NULL CHECK(decision IN ('approve','reject','revise','defer')),
 reviewer TEXT NOT NULL, reason TEXT NOT NULL, recorded_at TEXT NOT NULL, resulting_version INTEGER,
 FOREIGN KEY(entity_id, version) REFERENCES entity_revision(entity_id, version),
 FOREIGN KEY(entity_id, resulting_version) REFERENCES entity_revision(entity_id, version)
);
CREATE TABLE source_check (
 id INTEGER PRIMARY KEY, source_id TEXT NOT NULL, source_version INTEGER NOT NULL,
 check_kind TEXT NOT NULL CHECK(check_kind IN ('accessibility','authority','license')),
 outcome TEXT NOT NULL CHECK(outcome IN ('confirmed','failed','inconclusive')),
 checked_at TEXT NOT NULL, method TEXT NOT NULL, actor TEXT NOT NULL,
 locator TEXT NOT NULL, evidence_note TEXT NOT NULL,
 FOREIGN KEY(source_id, source_version) REFERENCES source(entity_id, version)
);
CREATE VIEW latest_revision AS
SELECT r.* FROM entity_revision r
WHERE version = (SELECT MAX(v.version) FROM entity_revision v WHERE v.entity_id = r.entity_id);
CREATE TRIGGER immutable_schema_migration_update BEFORE UPDATE ON schema_migration
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_schema_migration_delete BEFORE DELETE ON schema_migration
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_registry_entity_update BEFORE UPDATE ON registry_entity
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_registry_entity_delete BEFORE DELETE ON registry_entity
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_entity_revision_update BEFORE UPDATE ON entity_revision
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_entity_revision_delete BEFORE DELETE ON entity_revision
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_label_update BEFORE UPDATE ON label
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_label_delete BEFORE DELETE ON label
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_domain_update BEFORE UPDATE ON domain
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_domain_delete BEFORE DELETE ON domain
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_source_update BEFORE UPDATE ON source
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_source_delete BEFORE DELETE ON source
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_topic_update BEFORE UPDATE ON topic
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_topic_delete BEFORE DELETE ON topic
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_concept_update BEFORE UPDATE ON concept
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_concept_delete BEFORE DELETE ON concept
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_domain_relation_update BEFORE UPDATE ON domain_relation
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_domain_relation_delete BEFORE DELETE ON domain_relation
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_domain_source_update BEFORE UPDATE ON domain_source
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_domain_source_delete BEFORE DELETE ON domain_source
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_domain_topic_update BEFORE UPDATE ON domain_topic
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_domain_topic_delete BEFORE DELETE ON domain_topic
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_domain_concept_update BEFORE UPDATE ON domain_concept
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_domain_concept_delete BEFORE DELETE ON domain_concept
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_provenance_update BEFORE UPDATE ON provenance
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_provenance_delete BEFORE DELETE ON provenance
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_evidence_reference_update BEFORE UPDATE ON evidence_reference
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_evidence_reference_delete BEFORE DELETE ON evidence_reference
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_review_record_update BEFORE UPDATE ON review_record
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_review_record_delete BEFORE DELETE ON review_record
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_source_check_update BEFORE UPDATE ON source_check
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_source_check_delete BEFORE DELETE ON source_check
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
