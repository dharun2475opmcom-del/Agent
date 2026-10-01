"""Company profile assembled from verified facts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from search_agent.evidence import FreshnessChecker
from search_agent.extractions import CompanyFact


@dataclass
class CompanyProfile:
    """Verified and freshness-aware profile for one Norwegian organization."""

    organization_number: str
    facts: dict[str, CompanyFact] = field(default_factory=dict)

    def add_fact(self, fact: CompanyFact) -> None:
        """Add or replace a fact after verifying organization identity."""

        if fact.organization_number != self.organization_number:
            raise ValueError(
                "Cannot add a fact belonging to another organization."
            )

        existing = self.facts.get(fact.field)

        if existing is None:
            self.facts[fact.field] = fact
            return

        checker = FreshnessChecker()

        if checker.is_newer(
            existing.evidence,
            fact.evidence,
        ):
            self.facts[fact.field] = fact

    def get(self, field: str) -> Any | None:
        """Return the value of a fact, if available."""

        fact = self.facts.get(field)

        if fact is None:
            return None

        return fact.value

    def has(self, field: str) -> bool:
        """Return whether the profile contains a fact."""

        return field in self.facts

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable profile representation."""

        return {
            "organization_number": self.organization_number,
            "facts": {
                field: {
                    "value": fact.value,
                    "evidence": {
                        "source_name": fact.evidence.source_name,
                        "source_url": fact.evidence.source_url,
                        "retrieved_at": (
                            fact.evidence.retrieved_at.isoformat()
                        ),
                        "source_date": (
                            fact.evidence.source_date.isoformat()
                            if fact.evidence.source_date
                            else None
                        ),
                        "evidence_text": fact.evidence.evidence_text,
                        "confidence": fact.evidence.confidence,
                    },
                }
                for field, fact in self.facts.items()
            },
        }