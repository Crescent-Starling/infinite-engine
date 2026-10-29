"""Check local Markdown references without fetching remote URLs."""

import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "AGENTS.md",
    "README.md",
    "PLANS.md",
    "CHANGELOG.md",
    *[
        f"docs/{name}.md"
        for name in (
            "PROJECT_SPEC",
            "ARCHITECTURE",
            "DATA_CONTRACTS",
            "DOMAIN_REGISTRY",
            "LEARNING_ENGINE",
            "DEMOS",
            "VALIDATION",
            "DECISIONS",
            "DEVELOPMENT",
        )
    ],
    *[
        f"tasks/{name}.md"
        for name in (
            "00-repository-foundation",
            "01-domain-registry",
            "02-knowledge-foundation",
        )
    ],
]


def main() -> int:
    errors = [f"Missing: {name}" for name in REQUIRED if not (ROOT / name).is_file()]
    documents = [*ROOT.glob("*.md"), *ROOT.glob("docs/*.md"), *ROOT.glob("tasks/*.md")]
    for document in documents:
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", document.read_text()):
            if "://" in target or target.startswith("#"):
                continue
            path = unquote(target.split("#")[0])
            if path and not (document.parent / path).exists():
                errors.append(f"{document.relative_to(ROOT)}: broken link {target}")
    for error in errors:
        print(error)
    print(f"Checked {len(documents)} documents; {len(errors)} errors")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
