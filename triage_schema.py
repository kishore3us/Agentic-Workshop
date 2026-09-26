"""Shared validation contract for support-ticket triage decisions."""

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


Category = Literal["billing", "bug", "access", "performance", "how-to"]
Priority = Literal["P1", "P2", "P3", "P4"]
Route = Literal[
    "billing-team",
    "bug-team",
    "access-team",
    "performance-team",
    "how-to-team",
]

_ROUTES = {
    "billing": "billing-team",
    "bug": "bug-team",
    "access": "access-team",
    "performance": "performance-team",
    "how-to": "how-to-team",
}
_ABBREVIATIONS = {
    "mr.", "mrs.", "ms.", "dr.", "prof.", "sr.", "jr.", "st.",
    "jan.", "feb.", "mar.", "apr.", "jun.", "jul.", "aug.",
    "sep.", "sept.", "oct.", "nov.", "dec.", "e.g.", "i.e.",
    "u.s.", "u.k.",
}


class TriageDecision(BaseModel):
    """A decision's shape and allowed values, without ticket classification logic."""

    model_config = ConfigDict(extra="forbid", strict=True)

    category: Category
    priority: Priority
    route: Route
    rationale: str

    @field_validator("rationale")
    @classmethod
    def one_sentence(cls, value: str) -> str:
        value = value.strip()
        if not any(char.isalpha() for char in value):
            raise ValueError("rationale must be one non-empty sentence")
        for mark in re.finditer(r"[.!?]", value):
            following = value[mark.end() :]
            if not following.strip():
                continue
            preceding_word = re.search(r"[A-Za-z]+$", value[: mark.start()])
            possible_boundary = (
                following[0].isspace()
                or following[0].isupper()
                or (
                    following[0].islower()
                    and preceding_word is not None
                    and preceding_word.group()[0].isupper()
                )
            )
            if not possible_boundary:
                continue
            prefix = value[: mark.end()]
            word = re.search(r"[A-Za-z.]+\.$", prefix)
            if mark.group() == "." and word:
                if word.group().lower() in _ABBREVIATIONS:
                    continue
                if len(word.group()) == 2 and re.match(r"[A-Z]\.", following):
                    continue
            raise ValueError("rationale must be one sentence")
        return value

    @model_validator(mode="after")
    def route_matches_category(self) -> "TriageDecision":
        expected = _ROUTES[self.category]
        if self.route != expected:
            raise ValueError(f"route must be {expected!r} for category {self.category!r}")
        return self
