"""Official-company-website research."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

from search_agent.agent.profile import CompanyProfile
from search_agent.extractions import WebFactExtractor
from search_agent.identity import WebIdentityMatcher
from search_agent.sources import (
    CompanyRecord,
    HTMLTextExtractor,
    WebFetchError,
    WebFetcher,
)


@dataclass(frozen=True)
class WebsiteResearchResult:
    """Result of researching a company's official website."""

    attempted: bool
    verified: bool
    url: str | None
    facts_added: int


class OfficialWebsiteResearcher:
    """Research the official website supplied by BRREG."""

    def __init__(
        self,
        *,
        web_fetcher: WebFetcher | None = None,
        html_extractor: HTMLTextExtractor | None = None,
        identity_matcher: WebIdentityMatcher | None = None,
        fact_extractor: WebFactExtractor | None = None,
    ) -> None:
        self.web_fetcher = web_fetcher or WebFetcher()
        self.html_extractor = (
            html_extractor or HTMLTextExtractor()
        )
        self.identity_matcher = (
            identity_matcher or WebIdentityMatcher()
        )
        self.fact_extractor = (
            fact_extractor or WebFactExtractor()
        )

    def research(
        self,
        company: CompanyRecord,
        profile: CompanyProfile,
    ) -> WebsiteResearchResult:
        """Research and extract facts from the official website."""

        website = self._normalize_website(
            company.website
        )

        if website is None:
            return WebsiteResearchResult(
                attempted=False,
                verified=False,
                url=None,
                facts_added=0,
            )

        try:
            page = self.web_fetcher.fetch(website)
        except WebFetchError:
            return WebsiteResearchResult(
                attempted=True,
                verified=False,
                url=website,
                facts_added=0,
            )

        try:
            page_text = self.html_extractor.extract(
                page.text
            )
        except ValueError:
            return WebsiteResearchResult(
                attempted=True,
                verified=False,
                url=website,
                facts_added=0,
            )

        if not self.identity_matcher.matches(
            page_text,
            organization_number=company.organization_number,
        ):
            return WebsiteResearchResult(
                attempted=True,
                verified=False,
                url=website,
                facts_added=0,
            )

        facts = self.fact_extractor.extract(
            organization_number=company.organization_number,
            page_text=page_text,
            source_url=page.url,
            source_name="Official company website",
        )

        added = 0

        for fact in facts:
            before = profile.has(fact.field)

            profile.add_fact(fact)

            after = profile.has(fact.field)

            if after and not before:
                added += 1

        return WebsiteResearchResult(
            attempted=True,
            verified=True,
            url=website,
            facts_added=added,
        )

    @staticmethod
    def _normalize_website(
        website: str | None,
    ) -> str | None:
        """Normalize a BRREG website value into a fetchable URL."""

        if not website:
            return None

        # Remove accidental backslashes that can appear in
        # escaped website values returned by test data or
        # serialized sources.
        value = website.strip().replace("\\", "")

        if not value:
            return None

        if not value.startswith(
            (
                "http://",
                "https://",
            )
        ):
            value = f"https://{value}"

        parsed = urlparse(value)

        if parsed.scheme not in {
            "http",
            "https",
        }:
            return None

        if not parsed.netloc:
            return None

        return value