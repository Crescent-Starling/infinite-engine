"""Validate or import a supplied directory; default to transactional dry run."""

import argparse
import json
from pathlib import Path

from infinite_engine.catalog.storage import Registry
from infinite_engine.sources.contracts import (
    AcquisitionPlan,
    SearchProfile,
    SourceAssociations,
    SourceCandidates,
)
from infinite_engine.sources.importer import import_sources, validate_plan
from infinite_engine.sources.io import FORMATS, load_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--database", default=":memory:")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--schemas", action="store_true")
    args = parser.parse_args()
    if args.schemas:
        args.directory.mkdir(parents=True, exist_ok=True)
        for name, model in FORMATS.items():
            schema = model.model_json_schema()
            schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
            (args.directory / f"{name}.schema.json").write_text(
                json.dumps(schema, ensure_ascii=False, indent=2) + "\n"
            )
        return
    candidates = load_manifest(args.directory / "source_candidates.json")
    associations = load_manifest(args.directory / "source_associations.json")
    profile = load_manifest(args.directory / "search_profile.yaml")
    plan = load_manifest(args.directory / "acquisition_plan.yaml")
    assert isinstance(candidates, SourceCandidates) and isinstance(associations, SourceAssociations)
    assert isinstance(profile, SearchProfile) and isinstance(plan, AcquisitionPlan)
    with Registry(args.database) as registry, registry.transaction(dry_run=not args.apply):
        import_sources(registry, candidates, associations, apply=True)
        validate_plan(registry, profile, plan)
    print("Metadata imported" if args.apply else "Valid; dry run rolled back")


if __name__ == "__main__":
    main()
