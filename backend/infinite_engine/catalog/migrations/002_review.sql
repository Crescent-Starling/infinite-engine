CREATE TABLE candidate_batch (
 id TEXT PRIMARY KEY, content_hash TEXT NOT NULL, recorded_at TEXT NOT NULL
);
CREATE TABLE candidate_batch_item (
 batch_id TEXT NOT NULL REFERENCES candidate_batch(id), entity_id TEXT NOT NULL,
 version INTEGER NOT NULL, PRIMARY KEY(batch_id, entity_id),
 FOREIGN KEY(entity_id,version) REFERENCES entity_revision(entity_id,version)
);
CREATE TABLE review_export (
 id TEXT PRIMARY KEY, manifest TEXT NOT NULL CHECK(json_valid(manifest)), recorded_at TEXT NOT NULL
);
CREATE TABLE review_export_item (
 export_id TEXT NOT NULL REFERENCES review_export(id), entity_id TEXT NOT NULL,
 version INTEGER NOT NULL, payload_hash TEXT NOT NULL,
 PRIMARY KEY(export_id,entity_id),
 FOREIGN KEY(entity_id,version) REFERENCES entity_revision(entity_id,version)
);
CREATE TABLE review_receipt (
 content_hash TEXT PRIMARY KEY, export_id TEXT NOT NULL REFERENCES review_export(id),
 actor TEXT NOT NULL, result_json TEXT NOT NULL CHECK(json_valid(result_json)), recorded_at TEXT NOT NULL
);
CREATE TABLE curated_revision (
 entity_id TEXT NOT NULL, version INTEGER NOT NULL, review_id INTEGER NOT NULL UNIQUE REFERENCES review_record(id),
 PRIMARY KEY(entity_id,version),
 FOREIGN KEY(entity_id,version) REFERENCES entity_revision(entity_id,version)
);
CREATE VIEW current_curated AS
SELECT c.* FROM curated_revision c
WHERE version=(SELECT MAX(other.version) FROM curated_revision other WHERE other.entity_id=c.entity_id);
CREATE TRIGGER review_hash_binding BEFORE INSERT ON review_record
WHEN NOT EXISTS(SELECT 1 FROM entity_revision r WHERE r.entity_id=NEW.entity_id
 AND r.version=NEW.version AND r.payload_hash=NEW.payload_hash)
BEGIN SELECT RAISE(ABORT, 'Review does not match exact revision'); END;
CREATE TRIGGER review_terminal BEFORE INSERT ON review_record
WHEN EXISTS(SELECT 1 FROM review_record r WHERE r.entity_id=NEW.entity_id AND r.version=NEW.version
 AND r.decision IN ('approve','reject','revise'))
BEGIN SELECT RAISE(ABORT, 'Revision already has a terminal decision'); END;
CREATE TRIGGER curated_approval BEFORE INSERT ON curated_revision
WHEN NOT EXISTS(SELECT 1 FROM review_record r WHERE r.id=NEW.review_id AND r.entity_id=NEW.entity_id
 AND r.version=NEW.version AND r.decision='approve')
BEGIN SELECT RAISE(ABORT, 'Curated revision requires explicit approval'); END;
CREATE TRIGGER immutable_candidate_batch_update BEFORE UPDATE ON candidate_batch
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_candidate_batch_delete BEFORE DELETE ON candidate_batch
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_candidate_batch_item_update BEFORE UPDATE ON candidate_batch_item
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_candidate_batch_item_delete BEFORE DELETE ON candidate_batch_item
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_review_export_update BEFORE UPDATE ON review_export
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_review_export_delete BEFORE DELETE ON review_export
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_review_export_item_update BEFORE UPDATE ON review_export_item
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_review_export_item_delete BEFORE DELETE ON review_export_item
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_review_receipt_update BEFORE UPDATE ON review_receipt
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_review_receipt_delete BEFORE DELETE ON review_receipt
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_curated_revision_update BEFORE UPDATE ON curated_revision
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
CREATE TRIGGER immutable_curated_revision_delete BEFORE DELETE ON curated_revision
BEGIN SELECT RAISE(ABORT, 'Registry history is append-only'); END;
