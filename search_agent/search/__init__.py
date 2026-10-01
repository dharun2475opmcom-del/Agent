"""Search layer for discovering public company information."""

from .brave import BraveSearchProvider
from .duckduckgo import DuckDuckGoSearchProvider
from .engine import CompanySearchEngine, SearchExecution
from .mock_provider import MockSearchProvider
from .models import SearchResult
from .providers import SearchProvider, SearchProviderError
from .query_builder import CompanyQueryBuilder, CompanySearchContext

__all__ = [
    "BraveSearchProvider",
    "DuckDuckGoSearchProvider",
    "CompanyQueryBuilder",
    "CompanySearchContext",
    "CompanySearchEngine",
    "MockSearchProvider",
    "SearchExecution",
    "SearchProvider",
    "SearchProviderError",
    "SearchResult",
]