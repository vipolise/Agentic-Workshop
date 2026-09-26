import json

import pytest
from pydantic import ValidationError

from triage.schema import TriageDecision, TriageValidationError, validate_decision

VALID = {
    "category": "billing",
    "priority": "P2",
    "route": "billing-team",
    "rationale": "A double charge is a money problem.",
}


def test_accepts_a_valid_decision_as_dict_or_json():
    assert validate_decision(VALID) == TriageDecision(**VALID)
    assert validate_decision(json.dumps(VALID)).priority == "P2"
    assert validate_decision(json.dumps(VALID).encode()).category == "billing"


@pytest.mark.parametrize(
    "category, route",
    [
        ("billing", "billing-team"),
        ("bug", "bug-team"),
        ("access", "access-team"),
        ("performance", "performance-team"),
        ("how-to", "how-to-team"),
    ],
)
def test_accepts_each_category_route_pair(category, route):
    decision = validate_decision({**VALID, "category": category, "route": route})
    assert decision.category == category
    assert decision.route == route


@pytest.mark.parametrize("priority", ["P1", "P2", "P3", "P4"])
def test_accepts_each_priority(priority):
    assert validate_decision({**VALID, "priority": priority}).priority == priority


@pytest.mark.parametrize(
    "change, field",
    [
        ({"category": "sales"}, "category"),
        ({"category": []}, "category"),
        ({"priority": "P5"}, "priority"),
        ({"priority": 1}, "priority"),
        ({"route": "finance-team"}, "route"),
        ({"extra": "field"}, "extra"),
        ({"rationale": None}, "rationale"),
        ({"rationale": 42}, "rationale"),
        ({"rationale": b"A double charge is a money problem."}, "rationale"),
    ],
)
def test_rejects_invalid_fields_with_a_message_naming_the_field(change, field):
    with pytest.raises(TriageValidationError, match=field):
        validate_decision({**VALID, **change})


@pytest.mark.parametrize("field", ["category", "priority", "route", "rationale"])
def test_rejects_a_missing_field(field):
    payload = {key: value for key, value in VALID.items() if key != field}
    with pytest.raises(TriageValidationError, match=field):
        validate_decision(payload)


@pytest.mark.parametrize(
    "category, route",
    [
        ("billing", "bug-team"),
        ("bug", "billing-team"),
        ("access", "how-to-team"),
        ("performance", "access-team"),
        ("how-to", "performance-team"),
    ],
)
def test_rejects_a_route_that_does_not_match_its_category(category, route):
    payload = {**VALID, "category": category, "route": route}
    with pytest.raises(TriageValidationError, match="route"):
        validate_decision(payload)


@pytest.mark.parametrize("payload", ["not json", b"\x80\x81"])
def test_rejects_malformed_json(payload):
    with pytest.raises(TriageValidationError, match="valid JSON"):
        validate_decision(payload)


def test_wraps_integer_digit_limit_errors_from_json():
    oversized_integer = "9" * 5000
    with pytest.raises(TriageValidationError, match="valid JSON"):
        validate_decision(oversized_integer)


def test_rejects_duplicate_json_keys():
    duplicated = '{"category":"billing","category":"bug","priority":"P2",' \
        '"route":"bug-team","rationale":"A bug needs fixing."}'
    with pytest.raises(TriageValidationError, match="duplicate key 'category'"):
        validate_decision(duplicated)


def test_wraps_recursion_errors_from_deeply_nested_json():
    deeply_nested = "[" * 10000 + "0" + "]" * 10000
    with pytest.raises(TriageValidationError, match="valid JSON"):
        validate_decision(deeply_nested)


@pytest.mark.parametrize("payload", ["[1, 2]", "42", "null"])
def test_rejects_non_object_json(payload):
    with pytest.raises(TriageValidationError, match="JSON object"):
        validate_decision(payload)


def test_rejects_a_non_object_dict_input():
    with pytest.raises(TriageValidationError, match="JSON object"):
        validate_decision([VALID])


def test_preserves_nonblank_rationale_text():
    rationale = "  A double charge is a money problem.  "
    decision = validate_decision({**VALID, "rationale": rationale})
    assert decision.rationale == rationale


@pytest.mark.parametrize("rationale", ["", "  \t  "])
def test_accepts_empty_or_whitespace_rationale(rationale):
    assert validate_decision({**VALID, "rationale": rationale}).rationale == rationale


def test_decisions_are_immutable():
    decision = validate_decision(VALID)
    with pytest.raises(ValidationError, match="frozen"):
        decision.priority = "P1"
