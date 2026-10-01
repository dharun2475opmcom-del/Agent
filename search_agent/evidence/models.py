"""Evidence models used to support company facts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class Evidence:
    """Evidence supporting a single company fact."""

    organization_number: str
    field: str
    value: Any
    source_name: str
    source_url: str
    retrieved_at: datetime
    source_date: datetime | None = None
    evidence_text: str | None = None
    confidence: float = 1.0

    def __post_init__(self) -> None:
        """Validate evidence invariants."""

        if not self.organization_number:
            raise ValueError("organization_number cannot be empty.")

        if not self.field:
            raise ValueError("field cannot be empty.")

        if not self.source_name:
            raise ValueError("source_name cannot be empty.")

        if not self.source_url:
            raise ValueError("source_url cannot be empty.")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0.0 and 1.0."
            )