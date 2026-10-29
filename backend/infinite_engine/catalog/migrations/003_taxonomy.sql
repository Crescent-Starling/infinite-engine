-- Additive taxonomy records; 001/002 and all existing revision snapshots remain unchanged.
CREATE TABLE taxonomy_entry (
 entity_id TEXT NOT NULL, version INTEGER NOT NULL,
 source_id TEXT NOT NULL, source_version INTEGER NOT NULL,
 release_tag TEXT NOT NULL, code TEXT NOT NULL, original_label TEXT NOT NULL,
 original_language TEXT NOT NULL, original_path TEXT NOT NULL,
 PRIMARY KEY(entity_id,version),
 FOREIGN KEY(entity_id,version) REFERENCES entity_revision(entity_id,version),
 FOREIGN KEY(source_id,source_version) REFERENCES source(entity_id,version)
);
CREATE TABLE domain_mapping (
 entity_id TEXT NOT NULL, version INTEGER NOT NULL,
 domain_id TEXT NOT NULL REFERENCES registry_entity(id),
 taxonomy_entry_id TEXT NOT NULL, taxonomy_entry_version INTEGER NOT NULL,
 mapping_type TEXT NOT NULL CHECK(mapping_type IN ('exact','narrower_than','broader_than','related')),
 rationale TEXT NOT NULL,
 PRIMARY KEY(entity_id,version),
 FOREIGN KEY(entity_id,version) REFERENCES entity_revision(entity_id,version),
 FOREIGN KEY(taxonomy_entry_id,taxonomy_entry_version) REFERENCES taxonomy_entry(entity_id,version)
);
CREATE TRIGGER immutable_taxonomy_entry_update BEFORE UPDATE ON taxonomy_entry
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_taxonomy_entry_delete BEFORE DELETE ON taxonomy_entry
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_domain_mapping_update BEFORE UPDATE ON domain_mapping
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_domain_mapping_delete BEFORE DELETE ON domain_mapping
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
