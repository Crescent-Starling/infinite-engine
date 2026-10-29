"""Persistent identity keys are explicit and never derived from mutable display text."""

import json
import unicodedata
from uuid import UUID, uuid5

# Versioned namespace is permanent once IDs are persisted. See ADR-007.
REGISTRY_NAMESPACE = UUID("0691e948-1e99-5da2-a366-0a088a3c7869")
KINDS = frozenset(
    {
        "source_provider",
        "source_document",
        "source_anchor",
        "taxonomy_entry",
        "domain_mapping",
        "category",
        "domain_category",
        "knowledge_space",
        "domain",
        "source",
        "topic",
        "concept",
        "domain_relation",
        "domain_source",
        "domain_topic",
        "domain_concept",
    }
)


def stable_id(kind: str, identity_key: str) -> str:
    if kind not in KINDS or not identity_key or identity_key != identity_key.strip():
        raise ValueError("A known entity kind and nonblank, unpadded identity key are required")
    if unicodedata.normalize("NFC", identity_key) != identity_key:
        raise ValueError("Identity keys must use NFC Unicode normalization")
    name = json.dumps([kind, identity_key], ensure_ascii=False, separators=(",", ":"))
    return f"{kind}_{uuid5(REGISTRY_NAMESPACE, name)}"


def normalized_label(text: str) -> str:
    return " ".join(unicodedata.normalize("NFC", text).casefold().split())
