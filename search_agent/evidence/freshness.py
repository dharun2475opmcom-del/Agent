"""Freshness and change detection for company evidence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .models import Evidence


@dataclass(frozen=True)
class EvidenceChange:
    """Describes a change between two observations of a fact."""

    field: str
    old_value: object
    new_value: object
    changed: bool


class FreshnessChecker:
    """Compare evidence observations and determine whether facts changed."""

    def compare(
        self,
        old: Evidence,
        new: Evidence,
    ) -> EvidenceChange:
        """Compare two evidence records for the same company field."""

        if old.organization_number != new.organization_number:
            raise ValueError(
                "Cannot compare evidence from different organizations."
            )

        if old.field != new.field:
            raise ValueError(
                "Cannot compare evidence for different fields."
            )

        return EvidenceChange(
            field=new.field,
            old_value=old.value,
            new_value=new.value,
            changed=old.value != new.value,
        )

    def is_newer(
        self,
        old: Evidence,
        new: Evidence,
    ) -> bool:
        """Return True when the new observation was retrieved later."""

        return new.retrieved_at > old.retrieved_at