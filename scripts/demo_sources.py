"""Offline disposable four-domain source import demo. No content acquisition."""

import tempfile
from pathlib import Path

from infinite_engine.catalog.bundles import CandidateBundle, import_bundle
from infinite_engine.catalog.storage import Registry
from infinite_engine.sources.contracts import (
    AcquisitionPlan,
    SearchProfile,
    SourceAssociations,
    SourceCandidates,
)
from infinite_engine.sources.importer import import_sources, validate_plan
from infinite_engine.sources.io import load_manifest

ROOT = Path(__file__).resolve().parents[1] / "examples/sources"


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "demo.sqlite"
        with Registry(path) as registry:
            import_bundle(
                registry,
                CandidateBundle.model_validate_json((ROOT / "domains.json").read_text()),
                apply=True,
            )
            for folder in sorted(p for p in ROOT.iterdir() if p.is_dir()):
                candidates = load_manifest(folder / "source_candidates.json")
                associations = load_manifest(folder / "source_associations.json")
                profile = load_manifest(folder / "search_profile.yaml")
                plan = load_manifest(folder / "acquisition_plan.yaml")
                assert isinstance(candidates, SourceCandidates)
                assert isinstance(associations, SourceAssociations)
                assert isinstance(profile, SearchProfile) and isinstance(plan, AcquisitionPlan)
                import_sources(registry, candidates, associations, apply=True)
                import_sources(registry, candidates, associations, apply=True)
                validate_plan(registry, profile, plan)
                print(
                    f"{folder.name}: imported, replayed, plan validated; unverified mock metadata"
                )
        with Registry(path) as registry:
            count = registry._db.execute("SELECT count(*) FROM source_artifact").fetchone()[0]
            print(f"Restart: {count} artifact revisions retained; no content downloaded")


if __name__ == "__main__":
    main()
