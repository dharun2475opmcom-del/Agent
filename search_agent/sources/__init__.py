"""External company data sources."""

from .brreg import (
    BRREGClient,
    BRREGError,
    BRREGIdentityMismatchError,
    BRREGNotFoundError,
    CompanyRecord,
)
from .html import (
    HTMLExtractionError,
    HTMLTextExtractor,
)
from .web import (
    WebFetchError,
    WebFetcher,
    WebFetchNotFoundError,
    WebPage,
)

__all__ = [
    "BRREGClient",
    "BRREGError",
    "BRREGIdentityMismatchError",
    "BRREGNotFoundError",
    "CompanyRecord",
    "HTMLExtractionError",
    "HTMLTextExtractor",
    "WebFetchError",
    "WebFetcher",
    "WebFetchNotFoundError",
    "WebPage",
]