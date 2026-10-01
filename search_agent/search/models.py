"""Models used by the web search layer."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SearchResult:
    """A single result returned by a search provider."""

    title: str
    url: str
    snippet: str = ""
    source: str = ""

    def __post_init__(self) -> None:
        """Validate the basic search-result structure."""

        if not self.title.strip():
            raise ValueError("Search result title cannot be empty.")

        if not self.url.strip():
            raise ValueError("Search result URL cannot be empty.")