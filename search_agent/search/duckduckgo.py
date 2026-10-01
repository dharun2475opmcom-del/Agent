"""Free DuckDuckGo HTML search provider."""

from __future__ import annotations

from bs4 import BeautifulSoup
import requests

from .models import SearchResult
from .providers import SearchProviderError


DUCKDUCKGO_HTML_URL = "https://html.duckduckgo.com/html/"


class DuckDuckGoSearchProvider:
    """Search the public web through DuckDuckGo's HTML interface."""

    def __init__(
        self,
        *,
        timeout: float = 10.0,
    ) -> None:
        """Create a DuckDuckGo search provider."""

        if timeout <= 0:
            raise ValueError("timeout must be greater than zero.")

        self.timeout = timeout

    def search(
        self,
        query: str,
        *,
        max_results: int = 10,
    ) -> list[SearchResult]:
        """Search DuckDuckGo and return normalized search results."""

        if not query.strip():
            raise ValueError("Search query cannot be empty.")

        if max_results < 1:
            raise ValueError("max_results must be at least 1.")

        try:
            response = requests.get(
                DUCKDUCKGO_HTML_URL,
                params={
                    "q": query,
                },
                headers={
                    "User-Agent": (
                        "Signalpost-CompanyResearch/1.0"
                    ),
                    "Accept": "text/html,application/xhtml+xml",
                },
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise SearchProviderError(
                "Failed to contact DuckDuckGo."
            ) from exc

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise SearchProviderError(
                "DuckDuckGo returned HTTP "
                f"{response.status_code}."
            ) from exc

        return self._parse_results(
            response.text,
            max_results=max_results,
        )

    @staticmethod
    def _parse_results(
        html: str,
        *,
        max_results: int,
    ) -> list[SearchResult]:
        """Parse DuckDuckGo HTML results."""

        if not isinstance(html, str):
            raise SearchProviderError(
                "DuckDuckGo returned invalid HTML."
            )

        if not html.strip():
            return []

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        results: list[SearchResult] = []

        for result in soup.select(".result"):
            if len(results) >= max_results:
                break

            title_element = result.select_one(
                ".result__title"
            )

            link_element = result.select_one(
                ".result__a"
            )

            snippet_element = result.select_one(
                ".result__snippet"
            )

            if link_element is None:
                continue

            title = (
                title_element.get_text(
                    " ",
                    strip=True,
                )
                if title_element is not None
                else link_element.get_text(
                    " ",
                    strip=True,
                )
            )

            url = (
                link_element.get("href", "")
                if link_element is not None
                else ""
            )

            snippet = (
                snippet_element.get_text(
                    " ",
                    strip=True,
                )
                if snippet_element is not None
                else ""
            )

            if not title.strip() or not url.strip():
                continue

            try:
                results.append(
                    SearchResult(
                        title=title,
                        url=url,
                        snippet=snippet,
                        source="DuckDuckGo",
                    )
                )
            except ValueError:
                continue

        return results