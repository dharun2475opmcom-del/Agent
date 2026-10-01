from search_agent.agent import (
    CompanyProfile,
    OfficialWebsiteResearcher,
)
from search_agent.sources import CompanyRecord


class FakeWebPage:
    """Fake web page for website research tests."""

    def __init__(
        self,
        url: str,
        text: str,
    ) -> None:
        self.url = url
        self.text = text


class FakeWebFetcher:
    """Fake web fetcher for website research tests."""

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
    """Fake HTML extractor."""

    def extract(self, html: str) -> str:
        return html


def make_company(
    website: str | None = "example.no",
) -> CompanyRecord:
    """Create a test company record."""

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
        industry_description="Computer programming",
        website=website,
        raw_data={},
    )


def test_official_website_research_adds_verified_facts():
    company = make_company()

    profile = CompanyProfile(
        organization_number=company.organization_number,
    )

    researcher = OfficialWebsiteResearcher(
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
        company,
        profile,
    )

    assert result.attempted is True
    assert result.verified is True
    assert result.url == "https://example.no"
    assert result.facts_added >= 1

    assert profile.get("organization_number") == "974760673"
    assert profile.get("phone") == "+47 22 33 44 55"
    assert profile.get("email") == "info@example.no"


def test_official_website_research_rejects_wrong_company():
    company = make_company()

    profile = CompanyProfile(
        organization_number=company.organization_number,
    )

    researcher = OfficialWebsiteResearcher(
        web_fetcher=FakeWebFetcher(
            {
                "https://example.no": """
                    Different Company AS
                    Organisasjonsnummer: 123456789
                    Telefon: +47 99 88 77 66
                    Email: wrong@example.no
                """
            }
        ),
        html_extractor=FakeHTMLExtractor(),
    )

    result = researcher.research(
        company,
        profile,
    )

    assert result.attempted is True
    assert result.verified is False
    assert result.facts_added == 0

    assert not profile.has("phone")
    assert not profile.has("email")


def test_official_website_research_handles_missing_website():
    company = make_company(
        website=None,
    )

    profile = CompanyProfile(
        organization_number=company.organization_number,
    )

    researcher = OfficialWebsiteResearcher(
        web_fetcher=FakeWebFetcher({}),
        html_extractor=FakeHTMLExtractor(),
    )

    result = researcher.research(
        company,
        profile,
    )

    assert result.attempted is False
    assert result.verified is False
    assert result.url is None
    assert result.facts_added == 0


def test_official_website_adds_https_to_domain():
    company = make_company(
        website="example.no",
    )

    profile = CompanyProfile(
        organization_number=company.organization_number,
    )

    researcher = OfficialWebsiteResearcher(
        web_fetcher=FakeWebFetcher(
            {
                "https://example.no": """
                    Example Company AS
                    Organisasjonsnummer: 974760673
                """
            }
        ),
        html_extractor=FakeHTMLExtractor(),
    )

    result = researcher.research(
        company,
        profile,
    )

    assert result.attempted is True
    assert result.verified is True
    assert result.url == "https://example.no"