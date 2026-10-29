-- Additive discovery metadata; legacy Source IDs, revisions and approvals are untouched.
CREATE TABLE source_artifact (
    id TEXT NOT NULL,
    version INTEGER NOT NULL CHECK(version >= 1),
    kind TEXT NOT NULL CHECK(kind IN ('source_provider','source_resource','source_document','source_anchor')),
    snapshot TEXT NOT NULL,
    payload_hash TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    PRIMARY KEY(id, version)
);
CREATE TABLE source_artifact_reference (
    artifact_id TEXT NOT NULL,
    artifact_version INTEGER NOT NULL,
    target_id TEXT NOT NULL,
    target_version INTEGER NOT NULL,
    PRIMARY KEY(artifact_id, artifact_version, target_id, target_version),
    FOREIGN KEY(artifact_id,artifact_version) REFERENCES source_artifact(id,version),
    FOREIGN KEY(target_id,target_version) REFERENCES source_artifact(id,version)
);
CREATE TABLE source_resource_revision (
    source_id TEXT NOT NULL,
    source_version INTEGER NOT NULL,
    PRIMARY KEY(source_id,source_version),
    FOREIGN KEY(source_id,source_version) REFERENCES source(entity_id,version),
    FOREIGN KEY(source_id,source_version) REFERENCES source_artifact(id,version)
);
CREATE TABLE source_manifest (
    batch_id TEXT PRIMARY KEY,
    payload_hash TEXT NOT NULL,
    snapshot TEXT NOT NULL
);
CREATE TRIGGER source_artifact_no_update BEFORE UPDATE ON source_artifact
BEGIN SELECT RAISE(ABORT, 'immutable source artifact'); END;
CREATE TRIGGER source_artifact_no_delete BEFORE DELETE ON source_artifact
BEGIN SELECT RAISE(ABORT, 'immutable source artifact'); END;
CREATE TRIGGER source_artifact_reference_no_update BEFORE UPDATE ON source_artifact_reference
BEGIN SELECT RAISE(ABORT, 'immutable reference'); END;
CREATE TRIGGER source_artifact_reference_no_delete BEFORE DELETE ON source_artifact_reference
BEGIN SELECT RAISE(ABORT, 'immutable reference'); END;
CREATE TRIGGER source_resource_revision_no_update BEFORE UPDATE ON source_resource_revision
BEGIN SELECT RAISE(ABORT, 'immutable resource pin'); END;
CREATE TRIGGER source_resource_revision_no_delete BEFORE DELETE ON source_resource_revision
BEGIN SELECT RAISE(ABORT, 'immutable resource pin'); END;
CREATE TRIGGER source_manifest_no_update BEFORE UPDATE ON source_manifest
BEGIN SELECT RAISE(ABORT, 'immutable manifest'); END;
CREATE TRIGGER source_manifest_no_delete BEFORE DELETE ON source_manifest
BEGIN SELECT RAISE(ABORT, 'immutable manifest'); END;
