"""Deterministic search provider used for development and testing."""

from __future__ import annotations

from collections.abc import Sequence

from .models import SearchResult


class MockSearchProvider:
    """Simple in-memory search provider for development."""

    def __init__(self, results: Sequence[SearchResult] | None = None) -> None:
        self._results = list(results or [])

    def search(
        self,
        query: str,
        *,
        max_results: int = 10,
    ) -> Sequence[SearchResult]:
        """Return configured results.

        The query is currently accepted for interface compatibility.
        A real provider will use it to perform web searches.
        """

        if not query.strip():
            raise ValueError("Search query cannot be empty.")

        if max_results < 1:
            raise ValueError("max_results must be at least 1.")

        return self._results[:max_results]