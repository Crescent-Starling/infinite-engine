"""Synthetic offline discovery, no provider calls or source verification."""

import json
from pathlib import Path
from typing import Any

import pytest
from infinite_engine.catalog.bundles import BundleEntry, digest_json
from infinite_engine.catalog.contracts import Candidate, DomainSource, Label, Provenance, Source
from infinite_engine.catalog.discovery import DiscoveryRequest, DiscoveryResult
from infinite_engine.catalog.ids import stable_id
from pydantic import ValidationError


def exchange(origin: str = "preset") -> tuple[DiscoveryRequest, dict[str, Any]]:
    provenance = Provenance(
        origin="test_fixture",
        actor="offline test",
        rationale="Contract fixture only",
        unsupported_reason="Synthetic bibliography; not discovered or verified",
    )
    request = DiscoveryRequest.model_validate(
        {
            "domain_id": stable_id("domain", "discovery-fixture"),
            "domain_name": "Synthetic domain",
            "domain_definition": "Test scope",
            "scope_note": "No real recommendations",
            "domain_origin": origin,
            "learning_goal": "Explore",
            "requested_data_types": ["introductory explanation"],
            "preferred_languages": ["zh", "en"],
        }
    )
    source = BundleEntry(
        identity_key="discovery:reference",
        candidate=Candidate(
            payload=Source(
                labels=(Label(language="en", text="Synthetic bibliography"),),
                source_kind="book",
                bibliographic_reference="Fixture only",
            ),
            provenance=provenance,
        ),
    )
    relation = BundleEntry(
        identity_key="discovery:recommendation",
        candidate=Candidate(
            payload=DomainSource(
                domain_id=request.domain_id,
                source_id=source.entity_id,
                rationale="Test complement",
                intended_use="Orientation",
                authority_scope="Unassessed",
                limitations="Synthetic",
            ),
            provenance=provenance,
        ),
    )
    result = {
        "source_candidates": [source.model_dump(mode="json")],
        "domain_source_candidates": [relation.model_dump(mode="json")],
        "source_checks": [],
        "coverage_assessment": {
            "selected_profile": "academic",
            "profile_rationale": "Introductory scope",
            "search_status": "unavailable",
            "coverage": [],
            "gaps": ["No real sources"],
            "redundancy_notes": [],
            "provenance": provenance.model_dump(mode="json"),
            "sources": [
                {
                    "source_id": source.entity_id,
                    "expected_usefulness": "Test only",
                    "priority": "low",
                    "open_questions": ["Provide manual sources"],
                    "provenance": provenance.model_dump(mode="json"),
                }
            ],
        },
        "recommended_next_actions": [
            {
                "action": "Request manual bibliography",
                "rationale": "Search unavailable",
                "provenance": provenance.model_dump(mode="json"),
            }
        ],
    }
    return request, result


@pytest.mark.parametrize("origin", ["preset", "custom"])
def test_offline_exchange_roundtrip(origin: str) -> None:
    request, raw = exchange(origin)
    result = DiscoveryResult.model_validate_json(json.dumps(raw))
    result.validate_for(request)
    assert result.source_candidates[0].candidate.payload.kind == "source"
    assert result.source_checks == ()
    assert DiscoveryResult.model_validate_json(result.model_dump_json()) == result
    assert DiscoveryResult.model_json_schema()["additionalProperties"] is False


def test_offline_plan_without_candidates() -> None:
    request, raw = exchange()
    raw["source_candidates"] = []
    raw["domain_source_candidates"] = []
    raw["coverage_assessment"]["sources"] = []
    DiscoveryResult.model_validate(raw).validate_for(request)


@pytest.mark.parametrize("problem", ["scope", "endpoint", "duplicate", "assessment", "version"])
def test_invalid_exchange_references(problem: str) -> None:
    request, raw = exchange()
    association = raw["domain_source_candidates"][0]["candidate"]["payload"]
    if problem == "scope":
        association["domain_id"] = stable_id("domain", "other")
    elif problem == "endpoint":
        association["source_id"] = stable_id("source", "missing")
    elif problem == "duplicate":
        raw["source_candidates"] *= 2
    elif problem == "assessment":
        raw["coverage_assessment"]["sources"] = []
    else:
        raw["source_candidates"][0]["expected_version"] = 1
    with pytest.raises(ValueError):
        DiscoveryResult.model_validate(raw).validate_for(request)


@pytest.mark.parametrize("problem", ["hash", "license", "claim", "evidence", "verified"])
def test_unsupported_check_records_rejected(problem: str) -> None:
    request, raw = exchange()
    result = DiscoveryResult.model_validate(raw)
    source = result.source_candidates[0]
    check: dict[str, Any] = {
        "source_id": source.entity_id,
        "payload_hash": digest_json(source.candidate.payload.model_dump(mode="json")),
        "check_kind": "identity",
        "outcome": "inconclusive",
        "checked_at": "2026-10-29T00:00:00Z",
        "method": "Synthetic test observation",
        "actor": "test",
        "locator": "fixture:bibliography",
        "evidence_note": "Test only",
    }
    if problem == "hash":
        check["payload_hash"] = "0" * 64
    elif problem == "license":
        check.update(check_kind="license", outcome="confirmed")
    elif problem == "claim":
        check["check_kind"] = "claim_support"
    elif problem == "evidence":
        check["evidence_note"] = " "
    else:
        check["verified"] = True
    raw["source_checks"] = [check]
    with pytest.raises(ValueError):
        DiscoveryResult.model_validate(raw).validate_for(request)


def test_wrong_candidate_kind_rejected() -> None:
    _, raw = exchange()
    raw["source_candidates"] = raw["domain_source_candidates"]
    with pytest.raises(ValidationError, match="Wrong candidate kind"):
        DiscoveryResult.model_validate(raw)


def test_skill_includes_review_and_permission_boundaries() -> None:
    skill = Path("skills/source-discovery/SKILL.md").read_text()
    assert "name: source-discovery" in skill
    assert "host allowlists" in skill
    assert "accept, reject, modify, add, defer" in skill


def test_check_bound_to_candidate_and_changed_metadata_invalidates_it() -> None:
    request, raw = exchange()
    source = DiscoveryResult.model_validate(raw).source_candidates[0]
    raw["source_checks"] = [
        {
            "source_id": source.entity_id,
            "payload_hash": digest_json(source.candidate.payload.model_dump(mode="json")),
            "check_kind": "identity",
            "outcome": "inconclusive",
            "checked_at": "2026-10-29T00:00:00Z",
            "method": "Fixture inspection",
            "actor": "test",
            "locator": "fixture:reference",
            "evidence_note": "Synthetic only",
        }
    ]
    DiscoveryResult.model_validate(raw).validate_for(request)
    raw["source_candidates"][0]["candidate"]["payload"]["creator"] = "Changed metadata"
    with pytest.raises(ValueError, match="exact source payload"):
        DiscoveryResult.model_validate(raw).validate_for(request)


def test_reuse_existing_source_and_reject_duplicate_identity() -> None:
    from infinite_engine.catalog.contracts import Revision

    request, raw = exchange()
    raw["source_candidates"][0]["candidate"]["payload"]["resource_identity"] = "fixture:book"
    source = DiscoveryResult.model_validate(raw).source_candidates[0]
    revision = Revision.model_validate(
        {
            "entity_id": source.entity_id,
            "version": 1,
            "prior_version": None,
            "payload_hash": digest_json(source.candidate.model_dump(mode="json")),
            "recorded_at": "2026-10-29T00:00:00Z",
            "candidate": source.candidate,
        }
    )
    request = DiscoveryRequest.model_validate(
        {**request.model_dump(), "existing_sources": [revision]}
    )
    raw["source_candidates"] = []
    DiscoveryResult.model_validate(raw).validate_for(request)
    duplicate = source.model_dump(mode="json")
    duplicate["identity_key"] = "a-different-id-for-same-resource"
    raw["source_candidates"] = [duplicate]
    with pytest.raises(ValueError, match="Duplicate resource identity"):
        DiscoveryResult.model_validate(raw).validate_for(request)
