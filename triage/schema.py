"""Validation for the triage agent's structured decisions."""

import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, ValidationInfo, field_validator

Category = Literal["billing", "bug", "access", "performance", "how-to"]
Priority = Literal["P1", "P2", "P3", "P4"]
Route = Literal["billing-team", "bug-team", "access-team", "performance-team", "how-to-team"]

_CATEGORY_ROUTES: dict[str, str] = {
    "billing": "billing-team",
    "bug": "bug-team",
    "access": "access-team",
    "performance": "performance-team",
    "how-to": "how-to-team",
}


class TriageDecision(BaseModel):
    """A ticket category, priority, destination, and policy rationale."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    category: Category = Field(description="The ticket's category from the triage policy.")
    priority: Priority = Field(description="P1 is most urgent; P4 is least urgent.")
    route: Route = Field(description="The team that handles this category.")
    rationale: str = Field(description="A rationale naming the policy rule that was applied.")

    @field_validator("route")
    @classmethod
    def route_matches_category(cls, value: str, info: ValidationInfo) -> str:
        category = info.data.get("category")
        expected_route = _CATEGORY_ROUTES.get(category)
        if expected_route is not None and value != expected_route:
            raise ValueError(f"route must be {expected_route!r} for category {category!r}")
        return value

class TriageValidationError(ValueError):
    """Raised when a decision does not match the schema."""


class _DuplicateJSONKeyError(ValueError):
    """Raised when a JSON object repeats a property name."""


def _object_without_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateJSONKeyError(f"duplicate key {key!r}")
        result[key] = value
    return result


def validate_decision(payload: str | bytes | dict) -> TriageDecision:
    """Parse JSON text or validate a dict, raising a readable error on failure."""
    if isinstance(payload, (str, bytes)):
        try:
            payload = json.loads(payload, object_pairs_hook=_object_without_duplicate_keys)
        except (json.JSONDecodeError, UnicodeDecodeError, _DuplicateJSONKeyError, RecursionError) as error:
            raise TriageValidationError(f"Decision is not valid JSON: {error}") from error

    if not isinstance(payload, dict):
        raise TriageValidationError(
            f"Decision must be a JSON object, got {type(payload).__name__}"
        )

    try:
        return TriageDecision.model_validate(payload)
    except ValidationError as error:
        problems = "; ".join(
            f"{'.'.join(map(str, item['loc'])) or 'decision'}: {item['msg']}"
            for item in error.errors()
        )
        raise TriageValidationError(f"Invalid triage decision: {problems}") from error
