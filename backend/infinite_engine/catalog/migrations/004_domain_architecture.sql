-- Forward-only additive metadata. Legacy NULL origin means unclassified, never preset by default.
ALTER TABLE domain ADD COLUMN origin TEXT CHECK(origin IN ('preset','custom'));
ALTER TABLE domain ADD COLUMN creation_method TEXT
 CHECK(creation_method IN ('manual','ai_assisted','classification_import'));
ALTER TABLE source ADD COLUMN language TEXT;
ALTER TABLE source ADD COLUMN coverage_description TEXT;
ALTER TABLE source ADD COLUMN access_conditions TEXT;
ALTER TABLE source ADD COLUMN bibliographic_reference TEXT;
ALTER TABLE source ADD COLUMN resource_identity TEXT;
ALTER TABLE source ADD COLUMN discovery_method TEXT
 CHECK(discovery_method IN ('system_recommendation','ai_discovery','user_added'));
ALTER TABLE source ADD COLUMN updated_on TEXT;
ALTER TABLE domain_source ADD COLUMN intended_learning_level TEXT;
CREATE TABLE category (
 entity_id TEXT NOT NULL, version INTEGER NOT NULL, slug TEXT NOT NULL, description TEXT NOT NULL,
 PRIMARY KEY(entity_id,version),
 FOREIGN KEY(entity_id,version) REFERENCES entity_revision(entity_id,version)
);
CREATE TABLE domain_category (
 entity_id TEXT NOT NULL, version INTEGER NOT NULL,
 domain_id TEXT NOT NULL REFERENCES registry_entity(id),
 category_id TEXT NOT NULL REFERENCES registry_entity(id), rationale TEXT NOT NULL,
 PRIMARY KEY(entity_id,version),
 FOREIGN KEY(entity_id,version) REFERENCES entity_revision(entity_id,version)
);
-- SQLite CHECK expansion requires a table copy. Copy all historical rows unchanged in transaction.
CREATE TABLE domain_relation_expanded (
 entity_id TEXT NOT NULL, version INTEGER NOT NULL,
 from_domain_id TEXT NOT NULL REFERENCES registry_entity(id),
 to_domain_id TEXT NOT NULL REFERENCES registry_entity(id),
 predicate TEXT NOT NULL CHECK(predicate IN (
 'SUBDOMAIN_OF','OVERLAPS_WITH','DRAWS_ON','USES_METHODS_FROM',
 'APPLIES_KNOWLEDGE_FROM','RELATED_CONTEXT','REFERENCES_PRESET','RELATED_TO','APPLIES_TO')),
 rationale TEXT NOT NULL, CHECK(from_domain_id <> to_domain_id),
 PRIMARY KEY(entity_id,version),
 FOREIGN KEY(entity_id,version) REFERENCES entity_revision(entity_id,version)
);
INSERT INTO domain_relation_expanded SELECT * FROM domain_relation;
DROP TABLE domain_relation;
ALTER TABLE domain_relation_expanded RENAME TO domain_relation;
CREATE TRIGGER immutable_domain_relation_update BEFORE UPDATE ON domain_relation
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_domain_relation_delete BEFORE DELETE ON domain_relation
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_category_update BEFORE UPDATE ON category
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_category_delete BEFORE DELETE ON category
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_domain_category_update BEFORE UPDATE ON domain_category
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_domain_category_delete BEFORE DELETE ON domain_category
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
-- Local personal state is separate from catalog review and curated revisions.
CREATE TABLE knowledge_space (
 id TEXT PRIMARY KEY, domain_id TEXT NOT NULL UNIQUE, selected_domain_version INTEGER NOT NULL,
 created_at TEXT NOT NULL,
 FOREIGN KEY(domain_id,selected_domain_version) REFERENCES domain(entity_id,version)
);
CREATE TABLE knowledge_space_source (
 id INTEGER PRIMARY KEY, space_id TEXT NOT NULL REFERENCES knowledge_space(id),
 source_id TEXT NOT NULL, source_version INTEGER NOT NULL,
 acceptance_state TEXT NOT NULL CHECK(acceptance_state IN ('accepted','removed')),
 note TEXT, recorded_at TEXT NOT NULL,
 FOREIGN KEY(source_id,source_version) REFERENCES source(entity_id,version)
);
CREATE TABLE space_override (
 id INTEGER PRIMARY KEY, space_id TEXT NOT NULL REFERENCES knowledge_space(id),
 display_name TEXT, scope_note TEXT, recorded_at TEXT NOT NULL
);
CREATE TRIGGER immutable_knowledge_space_update BEFORE UPDATE ON knowledge_space
BEGIN SELECT RAISE(ABORT, 'Space identity is immutable'); END;
CREATE TRIGGER immutable_knowledge_space_delete BEFORE DELETE ON knowledge_space
BEGIN SELECT RAISE(ABORT, 'Space identity is immutable'); END;
CREATE TRIGGER immutable_knowledge_space_source_update BEFORE UPDATE ON knowledge_space_source
BEGIN SELECT RAISE(ABORT, 'Personal history is append-only'); END;
CREATE TRIGGER immutable_knowledge_space_source_delete BEFORE DELETE ON knowledge_space_source
BEGIN SELECT RAISE(ABORT, 'Personal history is append-only'); END;
CREATE TRIGGER immutable_space_override_update BEFORE UPDATE ON space_override
BEGIN SELECT RAISE(ABORT, 'Personal history is append-only'); END;
CREATE TRIGGER immutable_space_override_delete BEFORE DELETE ON space_override
BEGIN SELECT RAISE(ABORT, 'Personal history is append-only'); END;
