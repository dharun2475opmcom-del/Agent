"""Models for structured company facts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from search_agent.evidence import Evidence


@dataclass(frozen=True)
class CompanyFact:
    """A structured company fact supported by evidence."""

    organization_number: str
    field: str
    value: Any
    evidence: Evidence

    def __post_init__(self) -> None:
        if not self.organization_number:
            raise ValueError("organization_number cannot be empty.")

        if not self.field:
            raise ValueError("field cannot be empty.")

        if self.evidence.organization_number != self.organization_number:
            raise ValueError(
                "Evidence organization number must match the company fact."
            )

        if self.evidence.field != self.field:
            raise ValueError(
                "Evidence field must match the company fact."
            )

        if self.evidence.value != self.value:
            raise ValueError(
                "Evidence value must match the company fact."
            )