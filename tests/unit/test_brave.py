from unittest.mock import Mock, patch

import requests

from search_agent.search import (
    BraveSearchProvider,
    SearchProviderError,
)


def make_response(
    *,
    status_code: int = 200,
    payload: dict | None = None,
) -> Mock:
    """Create a fake requests response."""

    response = Mock()
    response.status_code = status_code
    response.json.return_value = payload or {
        "web": {
            "results": [
                {
                    "title": "Example Company AS",
                    "url": "https://example.no",
                    "description": (
                        "Example Company AS, "
                        "organization number 974760673."
                    ),
                },
                {
                    "title": "Example Company - LinkedIn",
                    "url": "https://linkedin.example/company",
                    "description": "Company information.",
                },
            ]
        }
    }

    if status_code >= 400:
        response.raise_for_status.side_effect = requests.HTTPError(
            f"HTTP {status_code}"
        )
    else:
        response.raise_for_status.return_value = None

    return response


def test_brave_search_returns_search_results():
    provider = BraveSearchProvider(
        api_key="test-key",
    )

    response = make_response()

    with patch(
        "search_agent.search.brave.requests.get",
        return_value=response,
    ) as mock_get:
        results = provider.search(
            '"974760673"',
            max_results=5,
        )

    assert len(results) == 2

    assert results[0].title == "Example Company AS"
    assert results[0].url == "https://example.no"
    assert "974760673" in results[0].snippet
    assert results[0].source == "Brave Search"

    mock_get.assert_called_once()

    call_kwargs = mock_get.call_args.kwargs

    assert call_kwargs["params"]["q"] == '"974760673"'
    assert call_kwargs["params"]["count"] == 5
    assert call_kwargs["params"]["country"] == "NO"

    assert (
        call_kwargs["headers"]["X-Subscription-Token"]
        == "test-key"
    )


def test_brave_search_rejects_empty_query():
    provider = BraveSearchProvider(
        api_key="test-key",
    )

    try:
        provider.search("")
    except ValueError as exc:
        assert "query" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")


def test_brave_search_rejects_invalid_max_results():
    provider = BraveSearchProvider(
        api_key="test-key",
    )

    try:
        provider.search(
            "example",
            max_results=0,
        )
    except ValueError as exc:
        assert "max_results" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_brave_search_requires_api_key():
    try:
        BraveSearchProvider(api_key="")
    except ValueError as exc:
        assert "api key" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")


def test_brave_search_wraps_request_errors():
    provider = BraveSearchProvider(
        api_key="test-key",
    )

    with patch(
        "search_agent.search.brave.requests.get",
        side_effect=requests.RequestException(
            "connection failed"
        ),
    ):
        try:
            provider.search("example")
        except SearchProviderError as exc:
            assert "brave search" in str(exc).lower()
        else:
            raise AssertionError(
                "Expected SearchProviderError"
            )


def test_brave_search_wraps_http_errors():
    provider = BraveSearchProvider(
        api_key="test-key",
    )

    response = make_response(
        status_code=429,
    )

    with patch(
        "search_agent.search.brave.requests.get",
        return_value=response,
    ):
        try:
            provider.search("example")
        except SearchProviderError as exc:
            assert "http 429" in str(exc).lower()
        else:
            raise AssertionError(
                "Expected SearchProviderError"
            )


def test_brave_search_handles_empty_results():
    provider = BraveSearchProvider(
        api_key="test-key",
    )

    response = make_response(
        payload={
            "web": {
                "results": [],
            }
        }
    )

    with patch(
        "search_agent.search.brave.requests.get",
        return_value=response,
    ):
        results = provider.search("example")

    assert results == []


def test_brave_search_ignores_malformed_results():
    provider = BraveSearchProvider(
        api_key="test-key",
    )

    response = make_response(
        payload={
            "web": {
                "results": [
                    "not a dictionary",
                    {
                        "title": "",
                        "url": "",
                    },
                    {
                        "title": "Valid result",
                        "url": "https://example.no",
                        "description": "Valid description",
                    },
                ]
            }
        }
    )

    with patch(
        "search_agent.search.brave.requests.get",
        return_value=response,
    ):
        results = provider.search("example")

    assert len(results) == 1
    assert results[0].title == "Valid result"