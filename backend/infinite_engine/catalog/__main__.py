"""Run a disposable, offline candidate-history demo: python -m infinite_engine.catalog."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from infinite_engine.catalog.contracts import Candidate, Domain, Label, Provenance
from infinite_engine.catalog.storage import Registry


def main() -> None:
    original = Candidate(
        payload=Domain(
            slug="synthetic-domain",
            domain_type="academic",
            definition="Synthetic example only",
            scope_note="Not a real catalog entry",
            labels=(Label(language="en", text="Example"),),
        ),
        provenance=Provenance(
            origin="test_fixture",
            actor="offline-demo",
            rationale="Demonstrate revision safety",
            unsupported_reason="Synthetic, not authoritative knowledge",
        ),
    )
    with TemporaryDirectory(prefix="infinite-registry-") as directory:
        path = Path(directory) / "registry.sqlite"
        with Registry(path) as db:
            first = db.save("demo:example", original, expected_version=0)
            replay = db.save("demo:example", original, expected_version=0)
            revised = Candidate.model_validate(
                {
                    **original.model_dump(),
                    "payload": {
                        **original.payload.model_dump(),
                        "definition": "Revised synthetic draft",
                    },
                }
            )
            second = db.save("demo:example", revised, expected_version=1)
        with Registry(path) as db:
            history_preserved = db.get(first.entity_id, 1) == first
            latest = db.get(first.entity_id)
        print(
            json.dumps(
                {
                    "entity_id": first.entity_id,
                    "replay_idempotent": replay == first,
                    "history_preserved": history_preserved,
                    "latest_version": second.version,
                    "restart_persisted": latest == second,
                    "status": latest.review_status,
                    "curated_data_created": False,
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
