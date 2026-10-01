"""HTTP web-page fetching for public company research."""

from __future__ import annotations

from dataclasses import dataclass

import requests


class WebFetchError(RuntimeError):
    """Base exception for web fetching failures."""


class WebFetchNotFoundError(WebFetchError):
    """Raised when a requested page does not exist."""


@dataclass(frozen=True)
class WebPage:
    """Fetched public web page."""

    url: str
    status_code: int
    content_type: str
    text: str


class WebFetcher:
    """Fetch public web pages over HTTP."""

    def __init__(
        self,
        *,
        timeout: float = 15.0,
        user_agent: str = "Signalpost-CompanyResearch/1.0",
    ) -> None:
        self.timeout = timeout
        self.user_agent = user_agent

    def fetch(self, url: str) -> WebPage:
        """Fetch a public web page."""

        if not url.strip():
            raise ValueError("URL cannot be empty.")

        try:
            response = requests.get(
                url,
                timeout=self.timeout,
                headers={
                    "User-Agent": self.user_agent,
                    "Accept": "text/html,application/xhtml+xml",
                },
            )
        except requests.RequestException as exc:
            raise WebFetchError(
                f"Failed to fetch URL: {url}"
            ) from exc

        if response.status_code == 404:
            raise WebFetchNotFoundError(
                f"Page not found: {url}"
            )

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise WebFetchError(
                f"HTTP {response.status_code} while fetching {url}"
            ) from exc

        content_type = response.headers.get(
            "Content-Type",
            "",
        )

        return WebPage(
            url=url,
            status_code=response.status_code,
            content_type=content_type,
            text=response.text,
        )