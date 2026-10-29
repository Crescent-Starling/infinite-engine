"""Local review CLI: explicit --apply is required for bundle/review mutations."""

import argparse
import json
import sqlite3
from pathlib import Path

from infinite_engine.catalog.bundles import CandidateBundle, import_bundle
from infinite_engine.catalog.review import apply_review, curated_entries
from infinite_engine.catalog.review_csv import export_review
from infinite_engine.catalog.storage import Registry


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, required=True)
    commands = parser.add_subparsers(dest="command", required=True)
    bundle = commands.add_parser("import-bundle")
    bundle.add_argument("file", type=Path)
    bundle.add_argument("--apply", action="store_true")
    export = commands.add_parser("export")
    export.add_argument("directory", type=Path)
    export.add_argument("--entity", action="append", help="Limit export to these entity IDs")
    review = commands.add_parser("review")
    review.add_argument("directory", type=Path)
    review.add_argument("--actor", required=True)
    review.add_argument("--apply", action="store_true")
    commands.add_parser("curated")
    args = parser.parse_args()
    try:
        with Registry(args.db) as registry:
            if args.command == "import-bundle":
                payload = CandidateBundle.model_validate_json(
                    args.file.read_text(encoding="utf-8-sig")
                )
                items = import_bundle(registry, payload, apply=args.apply)
                print(
                    json.dumps(
                        {
                            "dry_run": not args.apply,
                            "revisions": [item.model_dump(mode="json") for item in items],
                        },
                        ensure_ascii=False,
                        indent=2,
                    )
                )
            elif args.command == "export":
                export_id = export_review(
                    registry, args.directory, tuple(args.entity) if args.entity else None
                )
                print(json.dumps({"export_id": export_id, "directory": str(args.directory)}))
            elif args.command == "review":
                result = apply_review(registry, args.directory, actor=args.actor, apply=args.apply)
                print(
                    json.dumps({"dry_run": not args.apply, **result}, ensure_ascii=False, indent=2)
                )
            else:
                print(
                    json.dumps(
                        [item.model_dump(mode="json") for item in curated_entries(registry)],
                        ensure_ascii=False,
                        indent=2,
                    )
                )
    except (OSError, ValueError, KeyError, sqlite3.Error) as exc:
        parser.exit(2, f"Registry operation failed: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
