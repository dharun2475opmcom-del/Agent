"""Search orchestration for company research."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .models import SearchResult
from .providers import SearchProvider
from .query_builder import CompanyQueryBuilder, CompanySearchContext


@dataclass(frozen=True)
class SearchExecution:
    """Results collected from executing company search queries."""

    queries: list[str]
    results: list[SearchResult]


class CompanySearchEngine:
    """Execute targeted searches for a company."""

    def __init__(
        self,
        provider: SearchProvider,
        query_builder: CompanyQueryBuilder | None = None,
    ) -> None:
        self.provider = provider
        self.query_builder = query_builder or CompanyQueryBuilder()

    def search(
        self,
        context: CompanySearchContext,
        *,
        max_results_per_query: int = 10,
    ) -> SearchExecution:
        """Build queries and execute them through the configured provider."""

        if max_results_per_query < 1:
            raise ValueError("max_results_per_query must be at least 1.")

        queries = self.query_builder.build(context)

        all_results: list[SearchResult] = []

        for query in queries:
            results: Sequence[SearchResult] = self.provider.search(
                query,
                max_results=max_results_per_query,
            )

            all_results.extend(results)

        return SearchExecution(
            queries=queries,
            results=all_results,
        )