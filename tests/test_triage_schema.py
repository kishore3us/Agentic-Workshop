"""Contract tests for the shared triage decision schema."""

import json

import pytest
from pydantic import ValidationError

from triage_schema import TriageDecision


@pytest.mark.parametrize(
    ("category", "route"),
    [
        ("billing", "billing-team"),
        ("bug", "bug-team"),
        ("access", "access-team"),
        ("performance", "performance-team"),
        ("how-to", "how-to-team"),
    ],
)
def test_accepts_each_category_route_pair(category: str, route: str) -> None:
    decision = TriageDecision.model_validate(
        {
            "category": category,
            "priority": "P2",
            "route": route,
            "rationale": "The ticket concerns a double charge.",
        }
    )
    assert decision.model_dump() == {
        "category": category,
        "priority": "P2",
        "route": route,
        "rationale": "The ticket concerns a double charge.",
    }


@pytest.mark.parametrize("priority", ["P1", "P2", "P3", "P4"])
def test_accepts_each_priority(priority: str) -> None:
    decision = TriageDecision(
        category="billing",
        priority=priority,
        route="billing-team",
        rationale="A billing issue was reported",
    )
    assert decision.priority == priority


@pytest.mark.parametrize(
    ("change", "error_fragment"),
    [
        ({"category": "other"}, "category"),
        ({"priority": "P5"}, "priority"),
        ({"route": "other-team"}, "route"),
        ({"route": "bug-team"}, "route must be 'billing-team'"),
        ({"rationale": ""}, "rationale must be one non-empty sentence"),
        ({"rationale": "  "}, "rationale must be one non-empty sentence"),
        ({"rationale": "First sentence. Second sentence."}, "rationale must be one sentence"),
        ({"rationale": "First.Second"}, "rationale must be one sentence"),
        ({"rationale": "First.second"}, "rationale must be one sentence"),
        ({"rationale": "Access failed, etc. Reset the account."}, "rationale must be one sentence"),
        ({"rationale": "..."}, "rationale must be one non-empty sentence"),
        ({"rationale": 42}, "rationale"),
        ({"extra": "not allowed"}, "extra"),
    ],
)
def test_rejects_invalid_decisions(change: dict, error_fragment: str) -> None:
    data = {
        "category": "billing",
        "priority": "P2",
        "route": "billing-team",
        "rationale": "The ticket concerns a charge.",
    }
    data.update(change)
    with pytest.raises(ValidationError, match=error_fragment):
        TriageDecision.model_validate(data)


def test_rejects_missing_field_and_non_object_json() -> None:
    with pytest.raises(ValidationError, match="rationale"):
        TriageDecision.model_validate(
            {"category": "billing", "priority": "P2", "route": "billing-team"}
        )
    with pytest.raises(ValidationError):
        TriageDecision.model_validate_json(json.dumps(["billing", "P2"]))


def test_accepts_single_sentence_with_abbreviation() -> None:
    for rationale in (
        "Dr. Smith asks how to reset a password.",
        "The U.S. customer needs access.",
        "Jan. 2026 charge is disputed.",
        "The example.com domain has an issue.",
    ):
        decision = TriageDecision(
            category="access", priority="P4", route="access-team", rationale=rationale
        )
        assert decision.rationale == rationale
