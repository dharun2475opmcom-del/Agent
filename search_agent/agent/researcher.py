"""End-to-end company research orchestration."""

from __future__ import annotations

from dataclasses import dataclass

from search_agent.agent.profile import CompanyProfile
from search_agent.agent.website import (
    OfficialWebsiteResearcher,
    WebsiteResearchResult,
)
from search_agent.extractions import (
    BRREGFactExtractor,
    WebFactExtractor,
)
from search_agent.identity import (
    EntityMatch,
    EntityMatcher,
    WebIdentityMatcher,
)
from search_agent.search import (
    CompanySearchContext,
    CompanySearchEngine,
    SearchExecution,
)
from search_agent.sources import (
    BRREGClient,
    CompanyRecord,
    HTMLTextExtractor,
    WebFetchError,
    WebFetcher,
)


@dataclass(frozen=True)
class ResearchResult:
    """Complete result of researching one company."""

    profile: CompanyProfile
    search_execution: SearchExecution
    matched_results: list[EntityMatch]
    website_result: WebsiteResearchResult


class CompanyResearcher:
    """Coordinate registry and public web research."""

    def __init__(
        self,
        *,
        brreg_client: BRREGClient,
        search_engine: CompanySearchEngine,
        fact_extractor: BRREGFactExtractor | None = None,
        web_fact_extractor: WebFactExtractor | None = None,
        entity_matcher: EntityMatcher | None = None,
        web_identity_matcher: WebIdentityMatcher | None = None,
        web_fetcher: WebFetcher | None = None,
        html_extractor: HTMLTextExtractor | None = None,
        website_researcher: OfficialWebsiteResearcher | None = None,
    ) -> None:
        self.brreg_client = brreg_client
        self.search_engine = search_engine

        self.fact_extractor = (
            fact_extractor or BRREGFactExtractor()
        )

        self.web_fact_extractor = (
            web_fact_extractor or WebFactExtractor()
        )

        self.entity_matcher = (
            entity_matcher or EntityMatcher()
        )

        self.web_identity_matcher = (
            web_identity_matcher or WebIdentityMatcher()
        )

        self.web_fetcher = (
            web_fetcher or WebFetcher()
        )

        self.html_extractor = (
            html_extractor or HTMLTextExtractor()
        )

        self.website_researcher = (
            website_researcher
            or OfficialWebsiteResearcher(
                web_fetcher=self.web_fetcher,
                html_extractor=self.html_extractor,
                identity_matcher=self.web_identity_matcher,
                fact_extractor=self.web_fact_extractor,
            )
        )

    def research(
        self,
        organization_number: str,
    ) -> ResearchResult:
        """Research one company by organization number."""

        # ---------------------------------------------------------
        # 1. Resolve the company through the official registry.
        # ---------------------------------------------------------
        company = self.brreg_client.get_company(
            organization_number
        )

        # ---------------------------------------------------------
        # 2. Build search context using verified BRREG identity.
        # ---------------------------------------------------------
        context = CompanySearchContext(
            organization_number=company.organization_number,
            company_name=company.name,
        )

        # ---------------------------------------------------------
        # 3. Search for additional public web information.
        # ---------------------------------------------------------
        search_execution = self.search_engine.search(
            context
        )

        # ---------------------------------------------------------
        # 4. Match search results against verified identity.
        # ---------------------------------------------------------
        matched_results = [
            self.entity_matcher.match(
                result,
                organization_number=company.organization_number,
                company_name=company.name,
            )
            for result in search_execution.results
        ]

        # ---------------------------------------------------------
        # 5. Start the profile with official BRREG facts.
        # ---------------------------------------------------------
        profile = CompanyProfile(
            organization_number=company.organization_number
        )

        source_url = (
            "https://data.brreg.no/enhetsregisteret/api/"
            f"enheter/{company.organization_number}"
        )

        brreg_facts = self.fact_extractor.extract(
            company,
            source_url=source_url,
        )

        for fact in brreg_facts:
            profile.add_fact(fact)

        # ---------------------------------------------------------
        # 6. Research the official website supplied by BRREG.
        #
        # This path does not depend on a search-engine result.
        # BRREG has already associated the website with the
        # verified organization.
        # ---------------------------------------------------------
        website_result = self.website_researcher.research(
            company,
            profile,
        )

        # ---------------------------------------------------------
        # 7. Inspect additional accepted search results.
        # ---------------------------------------------------------
        for matched_result in matched_results:
            if not matched_result.accepted:
                continue

            try:
                page = self.web_fetcher.fetch(
                    matched_result.result.url
                )
            except WebFetchError:
                continue

            try:
                page_text = self.html_extractor.extract(
                    page.text
                )
            except ValueError:
                continue

            # -----------------------------------------------------
            # 8. Verify page identity before extracting facts.
            # -----------------------------------------------------
            if not self.web_identity_matcher.matches(
                page_text,
                organization_number=company.organization_number,
            ):
                continue

            # -----------------------------------------------------
            # 9. Extract evidence-backed web facts.
            # -----------------------------------------------------
            web_facts = self.web_fact_extractor.extract(
                organization_number=company.organization_number,
                page_text=page_text,
                source_url=page.url,
                source_name=(
                    matched_result.result.source
                    or "Public website"
                ),
            )

            # -----------------------------------------------------
            # 10. Add web facts using freshness rules.
            # -----------------------------------------------------
            for fact in web_facts:
                profile.add_fact(fact)

        return ResearchResult(
            profile=profile,
            search_execution=search_execution,
            matched_results=matched_results,
            website_result=website_result,
        )