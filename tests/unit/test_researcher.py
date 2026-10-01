from search_agent.agent import (
    CompanyResearcher,
    WebsiteResearchResult,
)
from search_agent.search import (
    CompanySearchEngine,
    MockSearchProvider,
    SearchResult,
)
from search_agent.sources import CompanyRecord


class FakeBRREGClient:
    """Fake BRREG client for researcher tests."""

    def get_company(
        self,
        organization_number: str,
    ) -> CompanyRecord:
        return CompanyRecord(
            organization_number="974760673",
            name="Example Company AS",
            organization_form="AS",
            vat_registered=None,
            registration_date="2020-01-01",
            business_address="Examplegata 1",
            postal_code="0001",
            postal_place="Oslo",
            municipality="Oslo",
            industry_code="62010",
            industry_description="Computer programming activities",
            website="https://example.no",
            raw_data={},
        )


class FakeWebPage:
    """Fake web page returned by the fetcher."""

    def __init__(
        self,
        url: str,
        text: str,
    ) -> None:
        self.url = url
        self.text = text


class FakeWebFetcher:
    """Fake web fetcher for researcher tests."""

    def __init__(
        self,
        pages: dict[str, str],
    ) -> None:
        self.pages = pages

    def fetch(self, url: str) -> FakeWebPage:
        return FakeWebPage(
            url=url,
            text=self.pages[url],
        )


class FakeHTMLExtractor:
    """Fake HTML extractor that returns supplied text unchanged."""

    def extract(self, html: str) -> str:
        return html


class FakeOfficialWebsiteResearcher:
    """Fake official website researcher for isolated researcher tests."""

    def research(
        self,
        company: CompanyRecord,
        profile,
    ) -> WebsiteResearchResult:
        return WebsiteResearchResult(
            attempted=False,
            verified=False,
            url=None,
            facts_added=0,
        )


def make_search_engine(
    results: list[SearchResult],
) -> CompanySearchEngine:
    """Create a search engine using deterministic mock results."""

    provider = MockSearchProvider(results)

    return CompanySearchEngine(
        provider=provider,
    )


def test_researcher_adds_brreg_facts():
    researcher = CompanyResearcher(
        brreg_client=FakeBRREGClient(),
        search_engine=make_search_engine([]),
    )

    result = researcher.research(
        "974760673",
    )

    assert result.profile.get("name") == "Example Company AS"
    assert result.profile.get("organization_form") == "AS"
    assert result.profile.get("industry_code") == "62010"


def test_researcher_adds_verified_web_facts():
    search_result = SearchResult(
        title="Example Company AS",
        url="https://example.no",
        snippet="Example Company AS 974760673",
        source="Test search",
    )

    researcher = CompanyResearcher(
        brreg_client=FakeBRREGClient(),
        search_engine=make_search_engine(
            [search_result],
        ),
        web_fetcher=FakeWebFetcher(
            {
                "https://example.no": """
                    Example Company AS
                    Organisasjonsnummer: 974760673
                    Telefon: +47 22 33 44 55
                    Email: info@example.no
                """
            }
        ),
        html_extractor=FakeHTMLExtractor(),
    )

    result = researcher.research(
        "974760673",
    )

    assert result.profile.get("phone") == "+47 22 33 44 55"
    assert result.profile.get("email") == "info@example.no"


def test_researcher_rejects_web_page_from_wrong_company():
    search_result = SearchResult(
        title="Example Company AS",
        url="https://wrong-company.example",
        snippet="Example Company AS 974760673",
        source="Test search",
    )

    researcher = CompanyResearcher(
        brreg_client=FakeBRREGClient(),
        search_engine=make_search_engine(
            [search_result],
        ),
        web_fetcher=FakeWebFetcher(
            {
                "https://wrong-company.example": """
                    Different Company AS
                    Organisasjonsnummer: 123456789
                    Telefon: +47 99 88 77 66
                    Email: wrong@example.no
                """
            }
        ),
        html_extractor=FakeHTMLExtractor(),
        website_researcher=FakeOfficialWebsiteResearcher(),
    )

    result = researcher.research(
        "974760673",
    )

    assert not result.profile.has("phone")
    assert not result.profile.has("email")


def test_researcher_ignores_unaccepted_search_results():
    search_result = SearchResult(
        title="Completely Different Company",
        url="https://other.example",
        snippet="Some unrelated company",
        source="Test search",
    )

    researcher = CompanyResearcher(
        brreg_client=FakeBRREGClient(),
        search_engine=make_search_engine(
            [search_result],
        ),
        web_fetcher=FakeWebFetcher(
            {
                "https://other.example": """
                    Organisasjonsnummer: 974760673
                    Telefon: +47 22 33 44 55
                """
            }
        ),
        html_extractor=FakeHTMLExtractor(),
        website_researcher=FakeOfficialWebsiteResearcher(),
    )

    result = researcher.research(
        "974760673",
    )

    assert not result.profile.has("phone")