"""Brave Search API provider."""

from __future__ import annotations

import os
from typing import Any

import requests

from .models import SearchResult
from .providers import SearchProviderError


BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"


class BraveSearchProvider:
    """Search the public web through the Brave Search API."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        timeout: float = 10.0,
    ) -> None:
        """Create a Brave Search provider.

        If api_key is not supplied, BRAVE_SEARCH_API_KEY is read
        from the environment.
        """

        resolved_api_key = (
            api_key
            if api_key is not None
            else os.getenv("BRAVE_SEARCH_API_KEY", "")
        )

        if not resolved_api_key.strip():
            raise ValueError(
                "Brave Search API key is required. "
                "Pass api_key or set BRAVE_SEARCH_API_KEY."
            )

        if timeout <= 0:
            raise ValueError("timeout must be greater than zero.")

        self.api_key = resolved_api_key.strip()
        self.timeout = timeout

    def search(
        self,
        query: str,
        *,
        max_results: int = 10,
    ) -> list[SearchResult]:
        """Search Brave and return normalized search results."""

        if not query.strip():
            raise ValueError("Search query cannot be empty.")

        if max_results < 1:
            raise ValueError("max_results must be at least 1.")

        try:
            response = requests.get(
                BRAVE_SEARCH_URL,
                params={
                    "q": query,
                    "count": max_results,
                    "country": "NO",
                },
                headers={
                    "Accept": "application/json",
                    "X-Subscription-Token": self.api_key,
                    "User-Agent": (
                        "Signalpost-CompanyResearch/1.0"
                    ),
                },
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise SearchProviderError(
                "Failed to contact Brave Search."
            ) from exc

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise SearchProviderError(
                "Brave Search returned HTTP "
                f"{response.status_code}."
            ) from exc

        try:
            data: dict[str, Any] = response.json()
        except ValueError as exc:
            raise SearchProviderError(
                "Brave Search returned invalid JSON."
            ) from exc

        return self._parse_results(data)

    @staticmethod
    def _parse_results(
        data: dict[str, Any],
    ) -> list[SearchResult]:
        """Convert Brave API JSON into SearchResult objects."""

        web_data = data.get("web") or {}
        raw_results = web_data.get("results") or []

        if not isinstance(raw_results, list):
            raise SearchProviderError(
                "Brave Search returned an invalid results structure."
            )

        results: list[SearchResult] = []

        for raw_result in raw_results:
            if not isinstance(raw_result, dict):
                continue

            title = str(raw_result.get("title", "")).strip()
            url = str(raw_result.get("url", "")).strip()
            snippet = str(
                raw_result.get("description", "")
            ).strip()

            if not title or not url:
                continue

            try:
                results.append(
                    SearchResult(
                        title=title,
                        url=url,
                        snippet=snippet,
                        source="Brave Search",
                    )
                )
            except ValueError:
                continue

        return results