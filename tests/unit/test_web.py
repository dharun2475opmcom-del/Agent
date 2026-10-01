from unittest.mock import Mock, patch

import pytest
import requests

from search_agent.sources import (
    WebFetchError,
    WebFetcher,
    WebFetchNotFoundError,
)


def make_response(
    *,
    status_code: int = 200,
    text: str = "<html>Hello</html>",
    content_type: str = "text/html",
) -> Mock:
    response = Mock()
    response.status_code = status_code
    response.text = text
    response.headers = {
        "Content-Type": content_type,
    }

    response.raise_for_status.side_effect = (
        requests.HTTPError()
        if status_code >= 400
        else None
    )

    return response


@patch("search_agent.sources.web.requests.get")
def test_web_fetcher_returns_page(mock_get):
    mock_get.return_value = make_response()

    page = WebFetcher().fetch(
        "https://example.no"
    )

    assert page.url == "https://example.no"
    assert page.status_code == 200
    assert page.content_type == "text/html"
    assert page.text == "<html>Hello</html>"


@patch("search_agent.sources.web.requests.get")
def test_web_fetcher_sends_user_agent(mock_get):
    mock_get.return_value = make_response()

    WebFetcher().fetch(
        "https://example.no"
    )

    kwargs = mock_get.call_args.kwargs

    assert kwargs["headers"]["User-Agent"] == (
        "Signalpost-CompanyResearch/1.0"
    )


@patch("search_agent.sources.web.requests.get")
def test_web_fetcher_handles_404(mock_get):
    mock_get.return_value = make_response(
        status_code=404,
    )

    with pytest.raises(WebFetchNotFoundError):
        WebFetcher().fetch(
            "https://example.no/missing"
        )


@patch("search_agent.sources.web.requests.get")
def test_web_fetcher_handles_http_error(mock_get):
    mock_get.return_value = make_response(
        status_code=500,
    )

    with pytest.raises(WebFetchError):
        WebFetcher().fetch(
            "https://example.no/error"
        )


@patch("search_agent.sources.web.requests.get")
def test_web_fetcher_handles_network_error(mock_get):
    mock_get.side_effect = requests.ConnectionError()

    with pytest.raises(WebFetchError):
        WebFetcher().fetch(
            "https://example.no"
        )


def test_web_fetcher_rejects_empty_url():
    with pytest.raises(ValueError):
        WebFetcher().fetch("")