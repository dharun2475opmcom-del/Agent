"""Match search results to the correct company identity."""

from __future__ import annotations

from dataclasses import dataclass

from search_agent.search.models import SearchResult


@dataclass(frozen=True)
class EntityMatch:
    """Result of matching a search result to a company."""

    result: SearchResult
    organization_number_match: bool
    company_name_match: bool
    score: float
    accepted: bool


class EntityMatcher:
    """Determine whether a search result belongs to the target company."""

    def __init__(
        self,
        *,
        acceptance_threshold: float = 0.5,
    ) -> None:
        if not 0.0 <= acceptance_threshold <= 1.0:
            raise ValueError(
                "acceptance_threshold must be between 0.0 and 1.0."
            )

        self.acceptance_threshold = acceptance_threshold

    def match(
        self,
        result: SearchResult,
        *,
        organization_number: str,
        company_name: str,
    ) -> EntityMatch:
        """Score a search result against the target company."""

        if not organization_number.strip():
            raise ValueError("organization_number cannot be empty.")

        if not company_name.strip():
            raise ValueError("company_name cannot be empty.")

        searchable_text = " ".join(
            [
                result.title,
                result.snippet,
                result.url,
            ]
        ).lower()

        normalized_org_number = organization_number.replace(
            " ",
            "",
        ).replace(
            "-",
            "",
        )

        organization_number_match = (
            normalized_org_number.lower() in searchable_text
        )

        company_name_match = (
            company_name.strip().lower() in searchable_text
        )

        score = 0.0

        if organization_number_match:
            score += 0.8

        if company_name_match:
            score += 0.2

        score = min(score, 1.0)

        return EntityMatch(
            result=result,
            organization_number_match=organization_number_match,
            company_name_match=company_name_match,
            score=score,
            accepted=score >= self.acceptance_threshold,
        )