"""Interfaces for web search providers."""

from __future__ import annotations

from typing import Protocol, Sequence

from .models import SearchResult


class SearchProvider(Protocol):
    """Interface implemented by web search providers."""

    def search(
        self,
        query: str,
        *,
        max_results: int = 10,
    ) -> Sequence[SearchResult]:
        """Search the web and return structured results."""
        ...


class SearchProviderError(RuntimeError):
    """Raised when a search provider cannot complete a search."""