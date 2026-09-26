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
    "u.s.", "u.k.", "inc.", "ltd.", "corp.", "co.", "etc.",
}
_NAME_PREFIXES = {"mr.", "mrs.", "ms.", "dr.", "prof.", "sr.", "jr.", "st."}
_DOMAIN_SUFFIXES = {"ai", "app", "co", "com", "dev", "edu", "gov", "io", "net", "org", "uk"}
_CLOSING_MARKS = "\"'”’)]}"
_SENTENCE_MARKS = re.compile(r"[.!?。！？؟۔।॥…]+")
_DOMAIN = re.compile(r"\b(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}\b")


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
        if re.search(r"\r?\n[ \t]*\r?\n", value):
            raise ValueError("rationale must be one sentence")
        for line_break in re.finditer(r"\r\n|\r|\n", value):
            following = value[line_break.end() :].lstrip()
            if following and not following[0].islower():
                raise ValueError("rationale must be one sentence")

        domain_dots = {
            index
            for domain in _DOMAIN.finditer(value)
            if domain.group().rsplit(".", 1)[-1].lower() in _DOMAIN_SUFFIXES
            for index in range(domain.start(), domain.end())
            if value[index] == "."
        }
        for mark in _SENTENCE_MARKS.finditer(value):
            next_index = mark.end()
            while next_index < len(value) and (
                value[next_index].isspace() or value[next_index] in _CLOSING_MARKS
            ):
                next_index += 1
            if next_index == len(value):
                continue

            next_char = value[next_index]
            punctuation = mark.group()
            if punctuation in {"...", "…"} and next_char.islower():
                continue
            if punctuation == ".":
                index = mark.start()
                if index in domain_dots:
                    continue
                if (
                    index > 0
                    and index + 1 < len(value)
                    and value[index - 1].isdigit()
                    and value[index + 1].isdigit()
                ):
                    continue
                # The first dots in U.S.A. or p.m. join initials, not sentences.
                if (
                    index > 0
                    and index + 2 < len(value)
                    and value[index - 1].isalpha()
                    and value[index + 1].isalpha()
                    and value[index + 2] == "."
                ):
                    continue

                start = index
                while start > 0 and (value[start - 1].isalpha() or value[start - 1] == "."):
                    start -= 1
                token = value[start : index + 1]
                if re.fullmatch(r"(?:[A-Za-z]\.){2,}", token) and next_char.islower():
                    continue
                if token.lower() in _ABBREVIATIONS and (
                    next_char.islower()
                    or next_char.isdigit()
                    or (token.lower() in _NAME_PREFIXES and next_char.isupper())
                ):
                    continue
                if len(token) == 2 and token[0].isupper() and next_char.isupper():
                    continue
            raise ValueError("rationale must be one sentence")
        return value

    @model_validator(mode="after")
    def route_matches_category(self) -> "TriageDecision":
        expected = _ROUTES[self.category]
        if self.route != expected:
            raise ValueError(f"route must be {expected!r} for category {self.category!r}")
        return self
