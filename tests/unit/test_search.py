import pytest

from search_agent.search import (
    MockSearchProvider,
    SearchResult,
)


def test_search_result_creation():
    result = SearchResult(
        title="Example Company AS",
        url="https://example.no",
        snippet="Example Company AS official website",
        source="test",
    )

    assert result.title == "Example Company AS"
    assert result.url == "https://example.no"
    assert result.snippet == "Example Company AS official website"
    assert result.source == "test"


def test_search_result_requires_title():
    with pytest.raises(ValueError):
        SearchResult(
            title="",
            url="https://example.no",
        )


def test_search_result_requires_url():
    with pytest.raises(ValueError):
        SearchResult(
            title="Example Company AS",
            url="",
        )


def test_mock_search_provider_returns_results():
    results = [
        SearchResult(
            title="Example Company AS",
            url="https://example.no",
            snippet="Official website",
            source="test",
        ),
        SearchResult(
            title="Example Company - BRREG",
            url="https://brreg.no/example",
            snippet="Company registry information",
            source="test",
        ),
    ]

    provider = MockSearchProvider(results)

    returned = provider.search("Example Company AS")

    assert len(returned) == 2
    assert returned[0].title == "Example Company AS"
    assert returned[1].title == "Example Company - BRREG"


def test_mock_search_provider_respects_max_results():
    results = [
        SearchResult(
            title="Result 1",
            url="https://example.com/1",
        ),
        SearchResult(
            title="Result 2",
            url="https://example.com/2",
        ),
        SearchResult(
            title="Result 3",
            url="https://example.com/3",
        ),
    ]

    provider = MockSearchProvider(results)

    returned = provider.search(
        "Example Company",
        max_results=2,
    )

    assert len(returned) == 2


def test_mock_search_provider_rejects_empty_query():
    provider = MockSearchProvider()

    with pytest.raises(ValueError):
        provider.search("")


def test_mock_search_provider_rejects_invalid_max_results():
    provider = MockSearchProvider()

    with pytest.raises(ValueError):
        provider.search(
            "Example Company",
            max_results=0,
        )