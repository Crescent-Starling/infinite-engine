"""Disposable synthetic Domain/space demonstration; never approves fixture metadata."""

import json
import tempfile
from pathlib import Path

from infinite_engine.catalog.bundles import CandidateBundle, import_bundle
from infinite_engine.catalog.contracts import Domain, Provenance
from infinite_engine.catalog.ids import stable_id
from infinite_engine.catalog.review import curated_entries
from infinite_engine.catalog.spaces import LocalDomains, PersonalOverride, SourceChoice
from infinite_engine.catalog.storage import Registry


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    bundle = CandidateBundle.model_validate_json(
        (root / "tests/fixtures/domain_registry/domain-architecture.json").read_bytes()
    )
    with (
        tempfile.TemporaryDirectory() as temporary,
        Registry(Path(temporary) / "demo.sqlite") as db,
    ):
        imported = import_bundle(db, bundle, apply=True)
        local = LocalDomains(db)
        spaces = [
            local.ensure_primary_space(item.revision.entity_id, allow_candidate=True)
            for item in local.search("", include_candidates=True)
        ]
        preset_id = stable_id("domain", "architecture:latin")
        preset = db.get(preset_id)
        assert isinstance(preset.candidate.payload, Domain)
        custom = local.create_custom(
            "manual-overlap",
            preset.candidate.payload.model_copy(
                update={"origin": "custom", "creation_method": "manual"}
            ),
            Provenance(
                origin="test_fixture",
                actor="demo",
                rationale="Explicit same-name custom creation",
                unsupported_reason="Synthetic demonstration; no real discovery or seed",
            ),
        )
        space = local.ensure_primary_space(preset_id)
        local.choose_source(
            SourceChoice(
                space_id=space.id,
                source_id=stable_id("source", "architecture:source"),
                source_version=1,
                acceptance_state="accepted",
            )
        )
        local.save_override(
            PersonalOverride(space_id=space.id, display_name="My Latin exploration")
        )
        print(
            json.dumps(
                {
                    "fixture_records": len(imported),
                    "shared_primary_spaces": len(spaces),
                    "same_name_custom_created": custom.entity_id != preset_id,
                    "preset_unchanged": db.get(preset_id) == preset,
                    "curated_records": len(curated_entries(db)),
                    "source_checks": db._db.execute("SELECT count(*) FROM source_check").fetchone()[
                        0
                    ],
                    "seed_ready": False,
                    "network_calls": 0,
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
