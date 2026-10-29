"""Bounded JSON/YAML loader with duplicate keys and aliases rejected."""

import json
from pathlib import Path
from typing import Any

import yaml
from yaml.events import AliasEvent
from yaml.nodes import MappingNode

from infinite_engine.catalog.contracts import Contract
from infinite_engine.sources.contracts import (
    AcquisitionPlan,
    SearchProfile,
    SourceAssociations,
    SourceCandidates,
)

FORMATS: dict[str, type[Contract]] = {
    "source_candidates.json": SourceCandidates,
    "source_associations.json": SourceAssociations,
    "search_profile.yaml": SearchProfile,
    "acquisition_plan.yaml": AcquisitionPlan,
}


class ManifestLoader(yaml.SafeLoader):
    def construct_mapping(self, node: MappingNode, deep: bool = False) -> dict[Any, Any]:
        keys = [self.construct_object(key, deep=deep) for key, _ in node.value]
        if any(not isinstance(key, str) for key in keys) or len(keys) != len(set(keys)):
            raise ValueError("Manifest mapping keys must be unique strings")
        return super().construct_mapping(node, deep=deep)


def unique_json_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON mapping key")
        result[key] = value
    return result


def load_manifest(path: Path) -> Contract:
    if path.name not in FORMATS:
        raise ValueError("Unknown manifest filename")
    with path.open("rb") as stream:
        data = stream.read(2_000_001)
    if len(data) > 2_000_000:
        raise ValueError("Manifest exceeds 2 MB limit")
    depth = 0
    for event in yaml.parse(data, Loader=ManifestLoader):
        if isinstance(event, AliasEvent):
            raise ValueError("YAML aliases are not supported")
        if isinstance(event, (yaml.events.MappingStartEvent, yaml.events.SequenceStartEvent)):
            depth += 1
            if depth > 40:
                raise ValueError("Manifest exceeds nesting limit")
        elif isinstance(event, (yaml.events.MappingEndEvent, yaml.events.SequenceEndEvent)):
            depth -= 1
    value = (
        json.loads(data, object_pairs_hook=unique_json_pairs)
        if path.suffix == ".json"
        else yaml.load(data, Loader=ManifestLoader)
    )
    return FORMATS[path.name].model_validate(value)
