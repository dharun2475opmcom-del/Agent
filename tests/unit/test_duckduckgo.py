from unittest.mock import Mock, patch

import requests

from search_agent.search import (
    DuckDuckGoSearchProvider,
    SearchProviderError,
)


def make_response(
    *,
    status_code: int = 200,
    html: str = "",
) -> Mock:
    """Create a fake requests response."""

    response = Mock()
    response.status_code = status_code
    response.text = html

    if status_code >= 400:
        response.raise_for_status.side_effect = requests.HTTPError(
            f"HTTP {status_code}"
        )
    else:
        response.raise_for_status.return_value = None

    return response


SAMPLE_HTML = """
<html>
<body>

<div class="result">
    <div class="result__title">
        Example Company AS
    </div>

    <a
        class="result__a"
        href="https://example.no"
    >
        Example Company AS
    </a>

    <a
        class="result__snippet"
    >
        Example Company AS, organization number 974760673.
    </a>
</div>

<div class="result">
    <div class="result__title">
        Example Company - Registry
    </div>

    <a
        class="result__a"
        href="https://example.com/company"
    >
        Example Company - Registry
    </a>

    <a
        class="result__snippet"
    >
        Company information and registration details.
    </a>
</div>

</body>
</html>
"""


def test_duckduckgo_search_returns_results():
    provider = DuckDuckGoSearchProvider()

    response = make_response(
        html=SAMPLE_HTML,
    )

    with patch(
        "search_agent.search.duckduckgo.requests.get",
        return_value=response,
    ) as mock_get:
        results = provider.search(
            '"974760673"',
            max_results=10,
        )

    assert len(results) == 2

    assert results[0].title == "Example Company AS"
    assert results[0].url == "https://example.no"
    assert "974760673" in results[0].snippet
    assert results[0].source == "DuckDuckGo"

    assert results[1].url == (
        "https://example.com/company"
    )

    mock_get.assert_called_once()

    call_kwargs = mock_get.call_args.kwargs

    assert call_kwargs["params"]["q"] == '"974760673"'
    assert "User-Agent" in call_kwargs["headers"]


def test_duckduckgo_search_limits_results():
    provider = DuckDuckGoSearchProvider()

    response = make_response(
        html=SAMPLE_HTML,
    )

    with patch(
        "search_agent.search.duckduckgo.requests.get",
        return_value=response,
    ):
        results = provider.search(
            "example",
            max_results=1,
        )

    assert len(results) == 1


def test_duckduckgo_search_rejects_empty_query():
    provider = DuckDuckGoSearchProvider()

    try:
        provider.search("")
    except ValueError as exc:
        assert "query" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")


def test_duckduckgo_search_rejects_invalid_max_results():
    provider = DuckDuckGoSearchProvider()

    try:
        provider.search(
            "example",
            max_results=0,
        )
    except ValueError as exc:
        assert "max_results" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_duckduckgo_search_wraps_request_errors():
    provider = DuckDuckGoSearchProvider()

    with patch(
        "search_agent.search.duckduckgo.requests.get",
        side_effect=requests.RequestException(
            "connection failed"
        ),
    ):
        try:
            provider.search("example")
        except SearchProviderError as exc:
            assert "duckduckgo" in str(exc).lower()
        else:
            raise AssertionError(
                "Expected SearchProviderError"
            )


def test_duckduckgo_search_wraps_http_errors():
    provider = DuckDuckGoSearchProvider()

    response = make_response(
        status_code=429,
    )

    with patch(
        "search_agent.search.duckduckgo.requests.get",
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


def test_duckduckgo_search_handles_empty_html():
    provider = DuckDuckGoSearchProvider()

    response = make_response(
        html="",
    )

    with patch(
        "search_agent.search.duckduckgo.requests.get",
        return_value=response,
    ):
        results = provider.search("example")

    assert results == []